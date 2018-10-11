import os,requests
class Networkfile():
    def __init__(self,url,path,params={}):
        self.url=url
        self.path=path
        self.params=params
        if not os.path.exists(path):
            f=open(path,'wb')
            f.close()
        self.r_h=requests.head(url,allow_redirects=True,timeout=20)
        print(self.r_h.headers)
        if self.r_h.headers.get('Content-Length'):
            self.size=int(self.r_h.headers['Content-Length'])
        else:
            self.size=0
        if self.size==179:
            print(self.url)
            
    @property
    def local_size(self):
        return os.path.getsize(self.path)

    def download(self):
        headers={'Range': 'bytes=%d-' %self.local_size }
        r=requests.get(self.url,stream=True,headers=headers,params=self.params)
        with open(self.path, 'ab') as f:
            for chunk in r.iter_content(chunk_size=1024): #边下载边存硬盘
                if chunk:
                    f.write(chunk)
                else:
                    break
f=Networkfile('http://v.stu.126.net/mooc-video/nos/flv/2016/05/06/1004370105_84502b501f5247f09ef50a26977de493_shd.flv','test.flv')
print(f.size,f.local_size)

