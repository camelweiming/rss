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
        
        # 处理旧格式的缓存（列表）
        if isinstance(cache, list):
            print(f"⚠️ 检测到旧格式缓存，已转换为新格式")
            cache = {'last_time': None}
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache, f)
        
        print(f"✅ 缓存读取成功，上次处理时间：{cache.get('last_time', '无')}")
    except FileNotFoundError:
        cache = {'last_time': None}
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
        print(f"✅ 缓存文件不存在，已创建空缓存")
    except Exception as e:
        print(f"⚠️ 缓存格式错误：{str(e)}，已重置缓存")
        cache = {'last_time': None}
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
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