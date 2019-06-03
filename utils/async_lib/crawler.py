import asyncio
import aiohttp
import aiofiles

from .utils import Coroutine, Task, ExecuteError


async def Crawler_async(*tasks, **kw):
    """用于执行爬虫任务"""

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    }
    session = aiohttp.ClientSession(
        connector = aiohttp.TCPConnector(ssl=False),
        headers = kw.get('headers', header),
        cookies = kw.get('cookies', {}),
        )
    for task in tasks:
        task.args = (session, *task.args)
        try:
            await task.execute()
        except ExecuteError as e:
            print(e.message)
    await session.close()

async def download_bin(session, url, file_name, **kw):
    """下载二进制文件"""

    if kw.pop('stream', True):
        chunk_size = kw.pop('chunk_size', 1024)
        async with session.get(url, **kw) as res:
            async with aiofiles.open(file_name, 'wb') as f:
                while True:
                    chunk = await res.content.read(chunk_size)
                    if not chunk:
                        break
                    await f.write(chunk)

    else:
        async with session.get(url, **kw) as res:
            content = await res.read()
            async with aiofiles.open(file_name, 'wb') as f:
                await f.write(content)

async def download_text(session, url, file_name, **kw):
    """下载文本，以 UTF-8 编码保存文件"""

    async with session.get(url, **kw) as res:
        text = await res.text()
        async with aiofiles.open(file_name, 'w', encoding='utf_8') as f:
            await f.write(text)


if __name__ == '__main__':
    coroutine = Coroutine()
    coroutine.set_task([
        Crawler_async(
            Task(download_text, ('https://www.baidu.com', 'tmp/tmp0.html')),
            Task(download_bin, ('https://www.baidu.com', 'tmp/tmp1.html'))
        ),
    ])
    coroutine.run()
