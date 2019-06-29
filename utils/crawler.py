import os
import re
import requests


class Crawler(requests.Session):

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    }

    def __init__(self):
        super().__init__()
        self.headers.update(Crawler.header)

    def download_bin(self, url, file_name, **kw):
        """下载二进制文件"""
        if os.path.exists(file_name):
            return
        if kw.pop('stream', True):
            chunk_size = kw.pop('chunk_size', 1024)
            res = self.get(url, stream=True, **kw)
            with open(file_name, 'wb') as f:
                for chunk in res.iter_content(chunk_size=chunk_size):
                    if not chunk:
                        break
                    f.write(chunk)

        else:
            res = self.get(url, **kw)
            with open(file_name, 'wb') as f:
                f.write(res.content)

    def download_text(self, url, file_name, **kw):
        """下载文本，以 UTF-8 编码保存文件"""
        if os.path.exists(file_name):
            return
        res = self.get(url, **kw)
        res.encoding = res.apparent_encoding
        with open(file_name, 'w', encoding='utf_8') as f:
            f.write(res.text)

if __name__ == '__main__':
    spider = Crawler()
    spider.download_text('https://www.baidu.com', 'tmp/tmp2.html')
    spider.download_bin('https://www.baidu.com', 'tmp/tmp3.html')
