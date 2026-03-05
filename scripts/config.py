# RSS 源配置
RSS_SOURCES = {
    "reuters": "https://feeds.reuters.com/reuters/topNews",
    "ft": "https://www.ft.com/?format=rss",
    "美联社": "https://hosted2.ap.org/APDEFAULT/3d826f4870f84218835fca680356a236/Article_90000000000000000000000000000000/feed/rss.xml",
    "DeItaone": "https://rsshub.app/nitter/DeItaone"
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