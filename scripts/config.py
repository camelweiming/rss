# RSS 源配置
RSS_SOURCES = {
    "路透社": "https://feeds.reuters.com/reuters/worldNews",
    "FT": "https://www.ft.com/?format=rss",
    "美联社": "https://apnews.com/rss",
    "BBC": "https://www.bbc.com/news/rss.xml",
    "DeItaone": "https://nitter.net/DeItaone/rss"
}

# 缓存文件路径
CACHE_FILE = "rss_cache.json"

# 模拟真人请求头（关键：避开反爬）
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.google.com/',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
}