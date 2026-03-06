import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


def get_smtp_config():
    """获取SMTP配置
    
    Returns:
        dict: SMTP配置
    """
    return {
        'host': os.environ.get('SMTP_HOST', ''),
        'port': os.environ.get('SMTP_PORT', ''),
        'user': os.environ.get('SMTP_USER', ''),
        'pass': os.environ.get('SMTP_PASS', ''),
        'to_email': os.environ.get('TO_EMAIL', '')
    }


def send_email(email_content, entries_count):
    """发送邮件
    
    Args:
        email_content (str): 邮件内容
        entries_count (int): 条目数量
    
    Returns:
        bool: 发送是否成功
    """
    # 获取SMTP配置
    smtp_config = get_smtp_config()
    
    # 检查配置是否完整
    required_fields = ['host', 'port', 'user', 'pass', 'to_email']
    for field in required_fields:
        if not smtp_config[field]:
            print(f"❌ 缺少SMTP配置：{field}")
            return False
    
    msg = MIMEText(email_content, 'html', 'utf-8')
    # 转换为北京时间
    beijing_time = datetime.now(ZoneInfo('Asia/Shanghai'))
    msg['Subject'] = f"{beijing_time.strftime('%Y-%m-%d %H:%M')} ({entries_count})"
    msg['From'] = formataddr(('全球资讯推送', smtp_config['user']))
    msg['To'] = smtp_config['to_email']

    server = None
    try:
        server = smtplib.SMTP_SSL(smtp_config['host'], int(smtp_config['port']), timeout=30)
        server.login(smtp_config['user'], smtp_config['pass'])
        server.send_message(msg)
        print(f"📧 邮件发送成功！已发送到 {smtp_config['to_email']}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{str(e)}")
        return False
    finally:
        if server:
            server.quit()


if __name__ == "__main__":
    # 测试用例
    test_content = """
    <div style="margin:0 0 15px; padding:12px; border-left:4px solid #007bff; background:#f8f9fa;">
    <div style="font-size:15px; font-weight:600; color:#222; margin-bottom:6px;">测试邮件</div>
    <div style="font-size:12px; margin-bottom:8px;"><span style="font-weight:700; color:#007bff; background:#e3f2fd; padding:2px 6px; border-radius:3px;">测试来源</span> <span style="color:#666;">2026-03-05 14:00</span></div>
    <div style="font-size:14px; color:#333; line-height:1.5;">这是一封测试邮件，用于验证邮件发送功能是否正常工作。</div>
    <div style="font-size:12px; margin-top:8px;"><a href="https://example.com" style="color:#007bff; text-decoration:none;">查看原文</a></div>
    </div>
    """
    
    print("开始测试邮件发送...")
    success = send_email(test_content, 1)
    if success:
        print("测试成功！")
    else:
        print("测试失败，请检查配置。")