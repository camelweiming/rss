import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# 缓存文件
CACHE_FILE = "rss_cache.json"


def read_cache():
    """读取缓存
    
    Returns:
        dict: 缓存数据，包含 last_time 字段
    """
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        print(f"✅ 缓存读取成功，上次处理时间：{cache.get('last_time', '无')}")
    except FileNotFoundError:
        cache = {'last_time': None}
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
        print(f"✅ 缓存文件不存在，已创建空缓存")
    return cache


def update_cache(last_time):
    """更新缓存
    
    Args:
        last_time (str): 上次处理时间
    """
    cache = {'last_time': last_time}
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"💾 缓存已更新，上次处理时间：{last_time}")