<<<<<<< HEAD
import os
import requests
class Networkfile():
    def __init__(self, url, path, params={}):
        self.url = url
        self.flag = True
        self.path = path
        self.params = params
        if not os.path.exists(path):
            f = open(path,'wb')
            f.close()
        self.r_h = requests.head(url, params=self.params, allow_redirects=True, timeout=20)
        if self.r_h.headers.get('Content-Length'):
            self.size = int(self.r_h.headers['Content-Length'])
        else:
            self.size = 0
            
    @property
    def local_size(self):
        return os.path.getsize(self.path)

    def download(self):
        headers={'Range': 'bytes=%d-' %self.local_size }
        r = requests.get(self.url,stream=True,headers=headers,params=self.params)
        with open(self.path, 'ab') as f:
            for chunk in r.iter_content(chunk_size=1024): #边下载边存硬盘
                if chunk and self.flag:
                    f.write(chunk)
                else:
                    break

    def cancel(self):
        self.flag = False
        if os.path.exists(self.path):
            os.remove(path)

if __name__ == '__main__':
    root = 'C:/Users/asus/Desktop'
    path = root + os.sep + 'test.zip'
    url = 'https://www.icourse163.org/course/attachment.htm?fileName=castle.zip&nosKey=1D39E2D179B81B5432D77F05F5EA548E-1464747919231'
    f = Networkfile(url, path)
    f.download()
=======
import os
import requests
class Networkfile():
    def __init__(self, url, path, params={}):
        self.url = url
        self.flag = True
        self.path = path
        self.params = params
        if not os.path.exists(path):
            f = open(path,'wb')
            f.close()
        self.r_h = requests.head(url, params=self.params, allow_redirects=True, timeout=20)
        if self.r_h.headers.get('Content-Length'):
            self.size = int(self.r_h.headers['Content-Length'])
        else:
            self.size = 0
            
    @property
    def local_size(self):
        return os.path.getsize(self.path)

    def download(self):
        headers={'Range': 'bytes=%d-' %self.local_size }
        r = requests.get(self.url,stream=True,headers=headers,params=self.params)
        with open(self.path, 'ab') as f:
            for chunk in r.iter_content(chunk_size=1024): #边下载边存硬盘
                if chunk and self.flag:
                    f.write(chunk)
                else:
                    break

    def cancel(self):
        self.flag = False
        if os.path.exists(self.path):
            os.remove(path)

if __name__ == '__main__':
    root = 'C:/Users/asus/Desktop'
    path = root + os.sep + 'test.zip'
    url = 'https://www.icourse163.org/course/attachment.htm?fileName=castle.zip&nosKey=1D39E2D179B81B5432D77F05F5EA548E-1464747919231'
    f = Networkfile(url, path)
    f.download()
>>>>>>> history
