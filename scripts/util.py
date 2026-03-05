from datetime import datetime
from zoneinfo import ZoneInfo
import feedparser
import dateutil.parser


def convert_to_beijing_time(pub_date):
    """将发布时间转换为北京时间
    
    Args:
        pub_date (str): 原始发布时间字符串
    
    Returns:
        str: 转换后的北京时间字符串，格式为 'YYYY-MM-DD HH:MM'
    """
    if not pub_date:
        return ''
    
    try:
        # 解析原始时间
        parsed = feedparser.parse(pub_date)
        if hasattr(parsed, 'published_parsed') and parsed.published_parsed:
            original_time = parsed.published_parsed
            # 转换为北京时间
            beijing_time = datetime(*original_time[:6], tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Asia/Shanghai'))
            return beijing_time.strftime('%Y-%m-%d %H:%M')
        else:
            # 如果feedparser解析失败，尝试使用datetime.strptime解析
            dt = dateutil.parser.parse(pub_date)
            # 确保dt有时区信息
            if dt.tzinfo is None:
                # 假设是UTC时间
                dt = dt.replace(tzinfo=ZoneInfo('UTC'))
            # 转换为北京时间
            beijing_time = dt.astimezone(ZoneInfo('Asia/Shanghai'))
            return beijing_time.strftime('%Y-%m-%d %H:%M')
    except:
        # 如果解析失败，使用原始时间
        return pub_date[:30]