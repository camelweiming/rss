import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# 缓存文件
# 使用绝对路径，确保始终使用同一个缓存文件
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rss_cache.json")


def check_and_reset_stats(cache, rss_sources):
    """检查并重置统计信息（每天0点）
    
    Args:
        cache (dict): 缓存数据
        rss_sources (dict): RSS源配置
    
    Returns:
        dict: 更新后的缓存数据
    """
    # 获取当前北京时间日期
    current_date = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d')
    
    # 检查缓存中的统计日期
    stats_date = cache.get('stats_date')
    
    # 如果日期不同，重置统计信息
    if stats_date != current_date:
        print(f"📅 日期变更，重置统计信息（{stats_date} → {current_date}")
        cache['stats_date'] = current_date
        cache['source_stats'] = {}
        for source_name in rss_sources.keys():
            cache['source_stats'][source_name] = {'success': 0, 'failure': 0}
    
    # 确保统计信息存在
    if 'source_stats' not in cache:
        cache['source_stats'] = {}
        for source_name in rss_sources.keys():
            cache['source_stats'][source_name] = {'success': 0, 'failure': 0}
    
    return cache


def read_cache(rss_sources):
    """读取缓存
    
    Args:
        rss_sources (dict): RSS源配置
    
    Returns:
        dict: 缓存数据，包含 last_time 和 source_stats 字段
    """
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        
        # 处理旧格式的缓存（列表）
        if isinstance(cache, list):
            print(f"⚠️ 检测到旧格式缓存，已转换为新格式")
            cache = {'last_time': None}
        
        # 检查并重置统计信息
        cache = check_and_reset_stats(cache, rss_sources)
        
        print(f"✅ 缓存读取成功，上次处理时间：{cache.get('last_time', '无')}")
        print(f"📊 当前统计日期：{cache.get('stats_date', '无')}")
    except FileNotFoundError:
        cache = {'last_time': None}
        # 检查并重置统计信息
        cache = check_and_reset_stats(cache, rss_sources)
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
        print(f"✅ 缓存文件不存在，已创建空缓存")
    except Exception as e:
        print(f"⚠️ 缓存格式错误：{str(e)}，已重置缓存")
        cache = {'last_time': None}
        # 检查并重置统计信息
        cache = check_and_reset_stats(cache, rss_sources)
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    return cache


def update_cache(last_time, source_stats):
    """更新缓存
    
    Args:
        last_time (str): 上次处理时间
        source_stats (dict): 源站统计信息
    """
    # 读取现有缓存
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    except:
        cache = {}
    
    # 获取当前北京时间日期
    current_date = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d')
    
    # 更新缓存数据
    cache['last_time'] = last_time
    cache['source_stats'] = source_stats
    cache['stats_date'] = current_date
    
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"💾 缓存已更新，上次处理时间：{last_time}")
    print(f"📊 统计信息已更新")
    print(f"📅 统计日期：{current_date}")