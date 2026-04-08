import feedparser
import requests
from datetime import datetime
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

from config import RSS_SOURCES, REQUEST_HEADERS
from email_sender import send_email
from util import get_timestamp, convert_to_beijing_time, convert_to_beijing_time_full
from rss_manager import RSSManager


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


def process_rss_entries(feed, source_name):
    """处理RSS条目"""
    entries = []
    count = 0
    
    for entry in feed.entries[:5]:
        entry['source_name'] = source_name
        entries.append(entry)
        count += 1
    
    print(f"✨ {source_name} 处理 {count} 条内容（总计{len(feed.entries)}条）")
    return entries


def filter_new_entries(entries, last_time):
    """过滤出新的条目
    
    Args:
        entries (list): RSS条目列表
        last_time (str): 上次处理时间
    
    Returns:
        list: 新的条目列表
    """
    if not last_time:
        return entries
    
    new_entries = []
    last_timestamp = None
    
    # 解析上次处理时间
    try:
        from dateutil.parser import parse
        from zoneinfo import ZoneInfo
        last_dt = parse(last_time)
        # 添加北京时间时区信息
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=ZoneInfo('Asia/Shanghai'))
        last_timestamp = last_dt.timestamp()
    except:
        return entries
    
    # 过滤出时间戳大于上次处理时间的条目
    for entry in entries:
        entry_timestamp = get_timestamp(entry)
        if entry_timestamp > last_timestamp:
            new_entries.append(entry)
    
    print(f"✅ 过滤出 {len(new_entries)} 条新内容")
    return new_entries


def generate_email_content(entries, last_time, source_stats):
    """生成邮件内容"""
    email_content = ""
    
    for entry in entries:
        title = entry.get('title', '无标题').replace('<', '&lt;').replace('>', '&gt;')
        link = entry.get('link', '#')
        pub_date = entry.get('published', '')
        
        # 转换为北京时间
        pub_date = convert_to_beijing_time(pub_date)
            
        source = entry.get('source_name', '未知来源')
        
        # 取正文（兼容各种RSS格式）
        summary = entry.get('summary', entry.get('description', ''))
        # 移除 HTML 标签
        import re
        summary = re.sub('<[^<]+?>', '', summary)
        # 替换特殊字符
        summary = summary.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', ' ')
        # 不去截取长度
        
        email_content += f"""
        <div style="margin:0 0 15px; padding:12px; border-left:4px solid #007bff; background:#f8f9fa;">
        <div style="font-size:15px; font-weight:600; color:#222; margin-bottom:6px;">{title}</div>
        <div style="font-size:12px; margin-bottom:8px;"><span style="font-weight:700; color:#007bff; background:#e3f2fd; padding:2px 6px; border-radius:3px;">{source}</span> <span style="color:#666;">{pub_date}</span></div>
        <div style="font-size:14px; color:#333; line-height:1.5;">{summary}</div>
        <div style="font-size:12px; margin-top:8px;"><a href="{link}" style="color:#007bff; text-decoration:none;">查看原文</a></div>
        </div>
        """

    # last_time 已经是北京时间格式，直接使用
    last_time_beijing = last_time if last_time else '无'
    
    # 构建统计信息
    stats_html = ""
    for source_name, stats in source_stats.items():
        stats_html += f"<div style='margin:2px 0;'><span style='font-weight:500; color:#495057;'>{source_name} : </span> ( <span style='color:#28a745;'>{stats['success']}</span> / <span style='color:#dc3545;'>{stats['failure']}</span> )</div>"
    
    email_content += f"""
    <div style="margin-top:15px; padding:12px; background:#f8f9fa; border-radius:6px; border:1px solid #e9ecef;">
    <div style="font-size:12px; font-weight:600; color:#495057; margin-bottom:8px;">运行信息</div>
    <div style="font-size:11px; color:#6c757d; line-height:1.4;">
    <div style="margin:2px 0;">最后更新时间：<span style='color:#495057;'>{last_time_beijing}</span></div>
    </div>
    <div style="font-size:11px; color:#6c757d; line-height:1.4; margin-top:8px;">
    <div style="font-size:12px; font-weight:600; color:#495057; margin-bottom:6px;">源站统计</div>
    {stats_html}
    </div>
    </div>
    """

    
    return email_content


def main():
    """主函数"""
    # 初始化RSS管理器
    rss_manager = RSSManager()
    
    # 读取上次更新时间
    last_time = rss_manager.get_last_update_time()
    
    # 收集所有内容
    all_entries = []
    
    # 初始化源站统计信息
    source_stats = {}
    for source_name in RSS_SOURCES.keys():
        source_stats[source_name] = {'success': 0, 'failure': 0}
    
    # 遍历所有RSS源
    for source_name, rss_url in RSS_SOURCES.items():
        feed = fetch_rss_content(source_name, rss_url)
        if feed:
            entries = process_rss_entries(feed, source_name)
            all_entries.extend(entries)
            source_stats[source_name]['success'] += 1
        else:
            source_stats[source_name]['failure'] += 1
    
    # 按发布时间排序（降序）
    all_entries.sort(key=get_timestamp, reverse=True)
    print(f"\n✅ 总计处理 {len(all_entries)} 条内容，按时间倒序排列")
    
    # 过滤出新内容
    new_entries = filter_new_entries(all_entries, last_time)
    
    # 无新内容则更新RSS数据并退出
    if not new_entries:
        print(f"\n📝 最终结果：无新内容")
        # 更新RSS数据（包括统计信息）
        rss_manager.update_rss_data(all_entries, source_stats)
        exit(0)
    
    print(f"\n✅ 总计找到 {len(new_entries)} 条新内容，开始发送邮件")
    
    # 生成邮件内容
    email_content = generate_email_content(new_entries, last_time, source_stats)
    
    # 暂时屏蔽邮件发送
    print(f"⚠️ 邮件发送已暂时屏蔽")
    # 更新RSS数据
    rss_manager.update_rss_data(all_entries, source_stats)
    print(f"✅ 已更新RSS数据")


if __name__ == "__main__":
    main()