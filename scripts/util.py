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


def get_timestamp(item):
    """获取条目的时间戳用于排序
    
    Args:
        item (dict): RSS条目
    
    Returns:
        float: 时间戳
    """
    published = item.get('published', '')
    if not published:
        return 0
    try:
        # 尝试解析日期
        dt = dateutil.parser.parse(published)
        # 转换为时间戳
        return dt.timestamp()
    except:
        # 如果解析失败，使用缓存时间
        cached_at = item.get('cached_at', '')
        if cached_at:
            try:
                dt = datetime.fromisoformat(cached_at)
                return dt.timestamp()
            except:
                pass
        return 0


def convert_to_beijing_time_full(pub_date):
    """将发布时间转换为北京时间（完整格式）
    
    Args:
        pub_date (str): 原始发布时间字符串
    
    Returns:
        str: 转换后的北京时间字符串，格式为 'YYYY-MM-DD HH:MM:SS'
    """
    if not pub_date:
        return '无'
    
    try:
        # 解析原始时间
        dt = dateutil.parser.parse(pub_date)
        # 确保dt有时区信息
        if dt.tzinfo is None:
            # 假设是UTC时间
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        # 转换为北京时间
        beijing_time = dt.astimezone(ZoneInfo('Asia/Shanghai'))
        return beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    except:
        # 如果解析失败，使用原始时间
        return pub_date