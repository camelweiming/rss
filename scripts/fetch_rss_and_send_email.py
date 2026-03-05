import feedparser
import smtplib
import requests
from email.mime.text import MIMEText
from email.utils import formataddr
import json
from datetime import datetime
import os
from config import RSS_SOURCES, CACHE_FILE, REQUEST_HEADERS


def read_cache():
    """读取缓存文件"""
    try:
        with open(CACHE_FILE, 'r') as f:
            cached_guids = set(json.load(f))
        print(f"✅ 缓存文件读取成功，已缓存 {len(cached_guids)} 条内容")
    except FileNotFoundError:
        cached_guids = set()
        with open(CACHE_FILE, 'w') as f:
            json.dump(list(cached_guids), f)
        print(f"✅ 缓存文件不存在，已创建空缓存")
    return cached_guids


def fetch_rss_content(source_name, rss_url):
    """抓取单个RSS源的内容"""
    print(f"\n========== 开始抓取 {source_name} ==========")
    print(f"📌 RSS地址：{rss_url}")

    # 第一步：手动请求，查看HTTP状态和原始内容
    try:
        resp = requests.get(
            rss_url, 
            timeout=15, 
            headers=REQUEST_HEADERS,
            verify=False  # 忽略SSL验证（避免镜像源证书问题）
        )
        print(f"🌐 HTTP状态码：{resp.status_code}")
        print(f"📄 返回内容长度：{len(resp.text)} 字符")
        print(f"🔍 前200字符内容：{resp.text[:200]}")

        if resp.status_code != 200:
            print(f"❌ {source_name} 请求失败，HTTP状态码：{resp.status_code}")
            return None
    except Exception as e:
        print(f"❌ {source_name} 请求失败：{str(e)}")
        return None

    # 第二步：用feedparser解析RSS
    try:
        feed = feedparser.parse(resp.text)
        entry_count = len(feed.entries)
        print(f"📊 feedparser解析到条目数：{entry_count}")

        if entry_count == 0:
            # 尝试手动解析XML
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(resp.text)
                xml_items = root.findall('.//item')
                print(f"📊 手动XML解析到条目数：{len(xml_items)}")
                if len(xml_items) > 0:
                    print(f"⚠️ feedparser解析失败，但XML本身有内容！")
            except:
                print(f"❌ XML格式错误，无法手动解析")
            print(f"❌ {source_name} 无可用内容")
            return None
    except Exception as e:
        print(f"❌ {source_name} 解析失败：{str(e)}")
        return None

    return feed


def process_rss_entries(feed, source_name, cached_guids):
    """处理RSS条目，筛选新内容"""
    new_entries = []
    new_count = 0
    
    for entry in feed.entries[:5]:
        unique_id = entry.get('guid', entry.get('link', ''))
        if unique_id and unique_id not in cached_guids:
            entry['source_name'] = source_name
            new_entries.append(entry)
            cached_guids.add(unique_id)
            new_count += 1
    
    print(f"✨ {source_name} 找到 {new_count} 条新内容（总计{len(feed.entries)}条）")
    return new_entries


def generate_email_content(entries):
    """生成邮件内容"""
    email_content = ""
    
    for entry in entries:
        title = entry.get('title', '无标题').replace('<', '&lt;').replace('>', '&gt;')
        link = entry.get('link', '#')
        pub_date = entry.get('published', '')[:30]  # 只留前30位，不冗长
        source = entry.get('source_name', '未知来源')
        
        # 取正文（兼容各种RSS格式）
        summary = entry.get('summary', entry.get('description', ''))
        summary = summary.replace('<', '&lt;').replace('>', '&gt;').replace('\n', ' ')
        summary = summary[:180]  # 控制长度，不刷屏
        
        email_content += f"""
        <div style="margin:0 0 10px; padding:8px; border-left:3px solid #007bff; background:#f8f9fa;">
        <div style="font-size:15px; font-weight:600; color:#222;">{title}</div>
        <div style="font-size:12px; color:#666; margin:2px 0;">{source} • {pub_date}</div>
        <div style="font-size:14px; color:#333; margin:4px 0; line-height:1.4;">{summary}</div>
        <div style="font-size:12px;"><a href="{link}" style="color:#007bff; text-decoration:none;">查看原文</a></div>
        </div>
        """
    
    return email_content


def send_email(email_content, entries_count, smtp_config):
    """发送邮件"""
    msg = MIMEText(email_content, 'html', 'utf-8')
    msg['Subject'] = f"【全球资讯】{datetime.now().strftime('%Y-%m-%d %H:%M')}"
    msg['From'] = formataddr(('全球资讯推送', smtp_config['user']))
    msg['To'] = smtp_config['to_email']

    try:
        server = smtplib.SMTP_SSL(smtp_config['host'], int(smtp_config['port']), timeout=30)
        server.login(smtp_config['user'], smtp_config['pass'])
        server.send_message(msg)
        print(f"📧 邮件发送成功！已发送到 {smtp_config['to_email']}")
    except Exception as e:
        print(f"❌ 邮件发送失败：{str(e)}")
        return False
    finally:
        server.quit()
    
    return True


def update_cache(cached_guids):
    """更新缓存"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(list(cached_guids), f)
    print(f"💾 缓存已更新，当前缓存 {len(cached_guids)} 条内容")


def main():
    """主函数"""
    # 读取缓存
    cached_guids = read_cache()
    
    # 收集所有新内容
    all_new_entries = []
    
    # 遍历所有RSS源
    for source_name, rss_url in RSS_SOURCES.items():
        feed = fetch_rss_content(source_name, rss_url)
        if feed:
            new_entries = process_rss_entries(feed, source_name, cached_guids)
            all_new_entries.extend(new_entries)
    
    # 无新内容则退出
    if not all_new_entries:
        print(f"\n📝 最终结果：所有源均无新内容")
        exit(0)
    
    # 按发布时间排序
    all_new_entries.sort(key=lambda x: x.get('published', ''), reverse=True)
    print(f"\n✅ 总计找到 {len(all_new_entries)} 条新内容，开始发送邮件")
    
    # 生成邮件内容
    email_content = generate_email_content(all_new_entries)
    
    # 准备SMTP配置
    smtp_config = {
        'host': os.environ['SMTP_HOST'],
        'port': os.environ['SMTP_PORT'],
        'user': os.environ['SMTP_USER'],
        'pass': os.environ['SMTP_PASS'],
        'to_email': os.environ['TO_EMAIL']
    }
    
    # 发送邮件
    if send_email(email_content, len(all_new_entries), smtp_config):
        # 更新缓存
        update_cache(cached_guids)


if __name__ == "__main__":
    main()