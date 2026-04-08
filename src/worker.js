// Cloudflare Worker RSS中转脚本（ES Modules版本，2026兼容）
// 部署后使用方式：https://你的worker域名.dev/?url=需要中转的RSS地址

// 替换旧的addEventListener，改用模块化导出
export default {
    async fetch(request, env, ctx) {
        return handleRequest(request);
    }
};

async function handleRequest(request) {
    // 获取要中转的RSS地址（从URL参数url中提取）
    const urlParams = new URL(request.url).searchParams;
    const targetUrl = urlParams.get('url');

    // 无目标地址时返回提示
    if (!targetUrl) {
        return new Response('请添加RSS地址参数，例：?url=https://nitter.poast.org/DeItaone/rss', {
            status: 400,
            headers: { 'Content-Type': 'text/plain; charset=utf-8' }
        });
    }

    try {
        // 构建中转请求，模拟浏览器请求头（关键：绕过反爬）
        const proxyRequest = new Request(targetUrl, {
            method: 'GET',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'application/rss+xml,application/xml,text/xml,*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://google.com',
                'Cache-Control': 'no-cache'
            },
            cf: {
                cacheTtl: 300, // 缓存5分钟，减少请求频率
                cacheEverything: true
            }
        });

        // 发送请求并获取响应
        const response = await fetch(proxyRequest);
        // 复制响应头，添加跨域允许
        const headers = new Headers(response.headers);
        headers.set('Access-Control-Allow-Origin', '*'); // 允许所有域名访问
        headers.set('Content-Type', 'application/rss+xml; charset=utf-8'); // 强制RSS格式

        // 返回中转后的内容
        return new Response(response.body, {
            status: response.status,
            headers: headers
        });
    } catch (error) {
        // 异常处理
        return new Response(`中转失败：${error.message}`, {
            status: 500,
            headers: { 'Content-Type': 'text/plain; charset=utf-8' }
        });
    }
}