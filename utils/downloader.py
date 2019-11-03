import os
import re
import time
import math

from utils.common import Task, size_format
from utils.crawler import Crawler
from utils.thread import ThreadPool


INITIALIZED = 1
DOWNLOADING = 2
DONE = 4


class NetworkFile():
    """ 网络文件类，对应一个网络文件资源

    属性
        url: 文件的网络地址
        path: 文件的本地存储路径
        name: 文件的名称
        overwrite: 是否强制覆盖，默认不强制覆盖
        spider: 爬虫会话，requests.Session() 的封装
        size: 本地已下载部分大小
        initialized: 文件是否处于刚刚初始化的状态
        downloading: 文件是否处于下载中的状态
        done: 文件是否处于下载完成的状态
        total: 文件的完整大小
    """

    def __init__(self, url, path, overwrite=False, spider=Crawler()):
        self.url = url
        self.path = path
        self.tmp_path = self.path + '.t'
        self.name = os.path.split(self.path)[-1]
        self.overwrite = overwrite
        self.spider = spider
        self._status = INITIALIZED
        self.total = 0
        self.size = 0

    def _get_head(self):
        """ 连接测试，获取文件大小与是否可分段 """
        headers = dict(self.spider.headers)
        headers['Range'] = 'bytes=0-4'
        try:
            res = self.spider.head(
                self.url, headers=headers, allow_redirects=True, timeout=20)
            crange = res.headers['Content-Range']
            self.total = int(re.match(r'^bytes 0-4/(\d+)$', crange).group(1))
            return
        except:
            pass
        try:
            res = self.spider.head(self.url, allow_redirects=True, timeout=20)
            self.total = int(res.headers['Content-Length'])
        except:
            self.total = 0

    def download(self, stream=True, chunk_size=1024):
        """ 下载片段 """

        # 更改状态
        self.switch_status()

        # 获取信息
        self._get_head()

        if self.overwrite:
            self.remove()
        self.size = self.get_size()

        if not os.path.exists(self.path):
            # 设置 headers
            headers = dict(self.spider.headers)
            if self.total:
                headers["Range"] = "bytes={}-".format(self.size)

            # 建立连接并下载
            connected = False
            while not connected:
                try:
                    res = self.spider.get(
                        self.url, stream=True, headers=headers)
                    connected = True
                except:
                    print("[warn] content failed, try again...")
            with open(self.tmp_path, 'ab') as f:
                if stream:
                    for chunk in res.iter_content(chunk_size=chunk_size):
                        if not chunk:
                            break
                        f.write(chunk)
                        self.size += len(chunk)
                else:
                    f.write(res.content)
            # 从临时文件迁移，并删除临时文件
            if os.path.exists(self.path):
                os.remove(self.path)
            else:
                os.rename(self.tmp_path, self.path)
        self.switch_status()

    def remove(self):
        """ 删除文件 """
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)
        if os.path.exists(self.path):
            os.remove(self.path)

    def switch_status(self):
        """ 切换到下一状态 """
        self._status <<= 1

    def get_size(self):
        """ 获取本地文件大小 """

        try:
            if os.path.exists(self.tmp_path):
                size = os.path.getsize(self.tmp_path)
            elif os.path.exists(self.path):
                size = os.path.getsize(self.path)
            else:
                size = 0
        except FileNotFoundError:
            size = 0
        return size

    @property
    def initialized(self):
        """ 返回状态字段是否是 INITIALIZED """
        return self._status == INITIALIZED

    @property
    def downloading(self):
        """ 返回状态字段是否是 DOWNLOADING """
        return self._status == DOWNLOADING

    @property
    def done(self):
        """ 返回状态字段是否是 DONE """
        return self._status == DONE


class FileManager():
    """ 文件管理器

    负责资源的分发与文件监控

    属性
        files: 待管理文件 List
        pool: 线程池
        overwrite: 是否强制覆盖，默认不强制覆盖
        spider: 爬虫会话，requests.Session() 的封装
    """

    def __init__(self, num_thread, overwrite=False, spider=Crawler()):
        self.files = []
        self.pool = ThreadPool(num_thread)
        self.overwrite = overwrite
        self.spider = spider

    def dispense_resources(self, resources, log=True):
        """ 资源分发，将资源切分为片段，并分发至线程池 """

        for i, (url, file_path) in enumerate(resources):
            print("dispenser resources {}/{}".format(i, len(resources)), end="\r")
            file_name = os.path.split(file_path)[-1]
            if os.path.exists(file_path) and not self.overwrite:
                if log:
                    print("------! {} already exist".format(file_name))
            else:
                if log:
                    print("------> {}".format(file_name))
                file = NetworkFile(url, file_path, overwrite=self.overwrite, spider=self.spider)
                task = Task(file.download)
                self.pool.add_task(task)
                self.files.append(file)

    def run(self):
        """ 启动任务 """
        self.pool.run()

    def monitoring(self):
        """ 启动监控器 """
        files = self.files
        size, t = sum([file.size for file in files]), time.time()
        total_size = sum([file.total for file in files])
        center_placeholder = "%(center)s"
        size_flag = False
        while len(files):
            bar_length = 50
            max_length = 80
            log_string = " Downloading... ".center(max_length, "=") + "\n"

            # 校正总大小
            if not size_flag:
                size_list = [file.size for file in files]
                size_flag = all(size_list)
                total_size = sum(size_list)

            # 下载速度
            now_size, now_t = sum([file.size for file in files]), time.time()
            delta_size, delta_t = now_size - size, now_t - t
            size, t = now_size, now_t
            if delta_t < 1e-6:
                delta_t = 1e-6
            speed = delta_size / delta_t

            # 单个下载进度
            for file in files:
                if file.downloading:
                    line = "{}{} {}/{}".format(file.name, center_placeholder, size_format(file.size),
                                                size_format(file.total))
                    line = line.replace(center_placeholder, max(
                        max_length-len(line)+len(center_placeholder), 0)*"-")
                    log_string += line + "\n"

            # 下载进度
            if total_size != 0:
                len_done = bar_length * size // total_size
                len_undone = bar_length - len_done
                log_string += '{}{} {}/{} {:12}'.format("#" * len_done, "_" * len_undone,
                                                        size_format(size), size_format(
                                                            total_size),
                                                        size_format(speed)+"/s")
            else:
                num_done = sum([file.done for file in files])
                num_total = len(files)
                len_done = bar_length * num_done // num_total
                len_undone = bar_length - len_done
                log_string += '{}{} {} {:12}'.format("#" * len_done, "_" * len_undone,
                                                     size_format(size), size_format(speed)+"/s")

            # 清空控制台并打印新的 log
            os.system('cls' if os.name == 'nt' else 'clear')
            print(log_string)

            # 监控是否全部完成
            if all([file.done for file in files]):
                break

            try:
                time.sleep(max(1-(time.time()-now_t), 0.01))
            except (SystemExit, KeyboardInterrupt):
                raise

        # 清空控制台
        os.system('cls' if os.name == 'nt' else 'clear')
