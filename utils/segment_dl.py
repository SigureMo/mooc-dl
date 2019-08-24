import os
import time

from utils.common import Task, size_format
from utils.crawler import Crawler
from utils.thread import ThreadPool


class NetworkFile():
    """ 网络文件类，对应一个网络文件资源 """

    def __init__(self, url, path, segment_size=10*1024*1024,
                 spider=Crawler()):
        self.url = url
        self.path = path
        self.name = os.path.split(self.path)[-1]
        self.spider = spider
        self.segment_size = segment_size
        self.segmentable = False
        self.total = 0
        self.segments = []
        self.done = False
        self._get_head()
        self._segmentation()

    def _get_head(self):
        """ 连接测试，获取文件大小与是否可分段 """
        headers = dict(self.spider.headers)
        headers['Range'] = 'bytes=0-4'
        try:
            res = self.spider.head(
                self.url, headers=headers, allow_redirects=True, timeout=20)
            crange = res.headers['Content-Range']
            self.total = int(re.match(r'^bytes 0-4/(\d+)$', crange).group(1))
            self.segmentable = True
            return
        except:
            self.segmentable = False
        try:
            res = self.spider.head(self.url, allow_redirects=True, timeout=20)
            self.total = int(res.headers['Content-Length'])
        except:
            self.total = 0

    def _segmentation(self):
        """ 分段，将各个片段添加至 self.segments """
        if self.total and self.segmentable:
            for i in range(self.total//self.segment_size):
                segment = Segment(self, i)
                self.segments.append(segment)
        else:
            segment = Segment(self, 0)
            self.segments.append(segment)

    def merge(self):
        """ 合并各个片段 """
        with open(self.path, "wb") as fw:
            for segment in self.segments:
                with open(segment.path, "rb") as fr:
                    fw.write(fr.read())
                segment.remove()

    @property
    def size(self):
        """ 获取本地文件大小 """
        if self.done:
            size = os.path.getsize(self.path)
        else:
            size = sum([segment.size for segment in self.segments])
        return size

    @property
    def downloading(self):
        """ 检查是否有片段正在下载 """
        return any([segment.downloading for segment in self.segments])


class Segment():
    """ 网络片段类，对应一个网络文件片段 """

    def __init__(self, file, num):
        self.file = file
        name, ext = os.path.splitext(file.path)
        self.path = "{}_{:06}{}".format(name, num, ext)
        self.name = os.path.split(self.path)[-1]
        self.tmp_path = self.path + ".downloading"
        self.num = num
        self.segment_size = file.segment_size
        self.url = file.url
        self.spider = file.spider
        self.downloading = False
        self.done = False

    def download(self, stream=True, chunk_size=1024):
        """ 下载片段 """
        if not os.path.exists(self.path):
            self.downloading = True
            # 设置 headers
            headers = dict(self.spider.headers)
            if self.file.segmentable and self.file.total:
                headers["Range"] = "bytes={}-{}".format(
                    self.num * self.segment_size + self.size,
                    (self.num+1) * self.segment_size - 1)
            elif self.file.total:
                headers["Range"] = "bytes={}-".format(
                    self.num * self.segment_size + self.size)

            # 建立连接并下载
            res = self.spider.get(self.url, stream=True, headers=headers)
            with open(self.tmp_path, 'ab') as f:
                if stream:
                    for chunk in res.iter_content(chunk_size=chunk_size):
                        if not chunk:
                            break
                        f.write(chunk)
                else:
                    f.write(res.content)
            self.downloading = False
            # 从临时文件迁移，并删除临时文件
            with open(self.tmp_path, "rb") as fr:
                with open(self.path, "wb") as fw:
                    fw.write(fr.read())
            os.remove(self.tmp_path)
        self.done = True
        # 检查是否所有片段均已下载完成，如果是则合并
        if all([segment.done for segment in self.file.segments]):
            self.file.merge()
            self.file.done = True

    @property
    def size(self):
        """ 获取片段大小 """
        if os.path.exists(self.tmp_path):
            size = os.path.getsize(self.tmp_path)
        elif os.path.exists(self.path):
            size = os.path.getsize(self.path)
        else:
            size = 0
        return size

    def remove(self):
        """ 删除文件及其临时文件 """
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)
        elif os.path.exists(self.path):
            os.remove(self.path)


class ResourceDispenser():
    """ 资源分发器 """

    def __init__(self, resources, num_thread, segment_size, spider=Crawler()):
        self.files = []
        self.pool = ThreadPool(num_thread)
        self.resources = resources
        self.spider = spider
        self.segment_size = segment_size

    def dispense(self):
        """ 资源分发 """
        for i, (url, file_path) in enumerate(self.resources):
            print("dispenser resource {}/{}".format(i,
                                                    len(self.resources)), end="\r")
            file_name = os.path.split(file_path)[-1]
            if os.path.exists(file_path):
                print("-----! {} already exist".format(file_name))
            else:
                print("-----> {}".format(file_name))
                file = NetworkFile(url, file_path, segment_size=self.segment_size,
                                   spider=self.spider)
                for segment in file.segments:
                    task = Task(segment.download)
                    self.pool.add_task(task)
                self.files.append(file)

    def run(self):
        """ 启动任务 """
        self.pool.run()


class DownloadManager():
    """ 下载监控器 """

    def __init__(self, files):
        self.files = files

    def run(self):
        """ 启动监控器 """
        files = self.files
        size, t = sum([file.size for file in files]), time.time()
        total_size = sum([file.total for file in files])
        while len(files):
            os.system('cls' if os.name == 'nt' else 'clear')
            bar_length = 50
            max_length = 80
            print(" Downloading... ".center(max_length, "="))
            # 单个下载进度
            for file in files:
                if file.downloading:
                    if file.total:
                        print("{} {}/{}".format(file.name, size_format(file.size),
                                                size_format(file.total)))
                    else:
                        print("{} {}".format(file.name, size_format(file.size)))

            # 下载速度
            now_size, now_t = sum([file.size for file in files]), time.time()
            delta_size, delta_t = now_size - size, now_t - t
            size, t = now_size, now_t
            if delta_t < 1e-6:
                delta_t = 1e-6
            speed = delta_size / delta_t

            # 下载进度
            if total_size != 0:
                len_done = bar_length * size // total_size
                len_undone = bar_length - len_done
                print('{}{} {}/{} {:12}'.format("#" * len_done, "_" * len_undone,
                                                size_format(size), size_format(
                                                    total_size),
                                                size_format(speed)+"/s"))
            else:
                num_done = sum([file.done for file in files])
                num_total = len(files)
                len_done = bar_length * num_done // num_total
                len_undone = bar_length - len_done
                print('{}{} {} {:12}'.format("#" * len_done, "_" * len_undone,
                                             size_format(size), size_format(speed)+"/s"))

            # 监控是否全部完成
            if all([file.done for file in files]):
                break

            try:
                time.sleep(0.5)
            except (SystemExit, KeyboardInterrupt):
                raise
