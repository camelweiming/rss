import sys
import os

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from fetch_rss_and_send_email import generate_email_content

# 测试数据
entries = []
last_time = '2024-01-01T00:00:00'
source_stats = {
    'FT': {'success': 1, 'failure': 0},
    'BBC': {'success': 1, 'failure': 0},
    'DeItaone': {'success': 1, 'failure': 0}
}

# 生成邮件内容
email_content = generate_email_content(entries, last_time, source_stats)

# 打印调试信息部分
print("=== 邮件调试信息 ===")
print(email_content)
