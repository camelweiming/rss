import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from util import get_timestamp

# 内容缓存文件
CONTENT_CACHE_FILE = "docs/rss_content_cache.json"
# 保留的最大条目数
MAX_CACHE_SIZE = 100


def read_content_cache():
    """读取内容缓存
    
    Returns:
        list: 缓存的 RSS 条目列表
    """
    try:
        with open(CONTENT_CACHE_FILE, 'r') as f:
            cache = json.load(f)
        print(f"✅ 内容缓存读取成功，已缓存 {len(cache)} 条内容")
    except FileNotFoundError:
        cache = []
        with open(CONTENT_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
        print(f"✅ 内容缓存文件不存在，已创建空缓存")
    return cache


def update_content_cache(new_entries):
    """更新内容缓存
    
    Args:
        new_entries (list): 新的 RSS 条目列表
    """
    # 读取现有缓存
    cache = read_content_cache()
    
    # 合并新条目
    for entry in new_entries:
        # 检查是否已存在
        entry_id = entry.get('guid', entry.get('link', ''))
        if not entry_id:
            continue
        
        # 检查是否已在缓存中
        exists = False
        for cached_entry in cache:
            if cached_entry.get('guid', cached_entry.get('link', '')) == entry_id:
                exists = True
                break
        
        if not exists:
            # 添加到缓存
            cache.append({
                'guid': entry.get('guid', entry.get('link', '')),
                'title': entry.get('title', '无标题'),
                'link': entry.get('link', '#'),
                'published': entry.get('published', ''),
                'source_name': entry.get('source_name', '未知来源'),
                'summary': entry.get('summary', entry.get('description', '')),
                'cached_at': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
            })
    
    # 按时间戳降序排序
    cache.sort(key=get_timestamp, reverse=True)
    
    # 限制缓存大小
    if len(cache) > MAX_CACHE_SIZE:
        cache = cache[:MAX_CACHE_SIZE]
    
    # 保存缓存
    with open(CONTENT_CACHE_FILE, 'w') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    
    print(f"💾 内容缓存已更新，当前缓存 {len(cache)} 条内容")
    return cache


def get_content_cache():
    """获取内容缓存
    
    Returns:
        list: 缓存的 RSS 条目列表，按发布时间降序排序
    """
    cache = read_content_cache()
    # 按时间戳降序排序
    cache.sort(key=get_timestamp, reverse=True)
    return cache