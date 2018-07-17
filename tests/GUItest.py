from tkinter import *
from Easyload import *
import multiprocessing   
import threading  
class My_Gui(threading.Thread):  
    """docstring for My_Gui"""  
    def __init__(self,qss,qgs,event_1):  
        super(My_Gui,self).__init__()  
        self.queue_1=queue_1  
        self.queue_2=queue_2  
        self.root=Tk()  
        self.root.title="MOOC_Downloading..."
        
        self.frmL=Frame(width=300,height=400,bg='white')
        self.frmM=Frame(width=400,height=400,bg='white')
        self.frmR=Frame(width=300,height=400,bg='white')
        
        self.label_1=Label(self.frmL,text='info')  
        self.entry_1=Entry(self.root,)  
        self.entry_2=Entry(self.root,)  
        self.entry_3=Entry(self.root,)  
        #button的command调用函数需要参数时 用lambda  
        self.button_1=Button(self.root,text='SEND',command=lambda:self.button_click(queue_1,event_1))  
        self.label_1.pack()  
        self.entry_1.pack()  
        self.entry_2.pack()  
        self.entry_3.pack()  
        self.button_1.pack()  
        # self.root.mainloop()  


    def button_click(self,queue,event_1):  
        if not self.entry_1.get()=='':  
            queue.put(self.entry_1.get())#获取三个输入框内容依次进入队列发送给后台进程  
            queue.put(self.entry_2.get())  
            queue.put(self.entry_3.get())  
            event_1.set()  
            self.label_1['text']='sending email'  
    #多线程等待后台进程返回消息，防止UI卡顿  
    def run(self):  
        self.button_1['text']='Send'  
        while True:  
            if not self.queue_2.empty():
                info=self.queue_2.get()  
                if info=='succeed':  
                    self.label_1['text']='succeed'  
                elif info=='failure':  
                    self.label_1['text']='failure'  
                else:  
                    self.label_1['text']='file not found'  

class Download(multiprocessing.Process):
    def __init__(self,q1,q2,e):
        super(Download,self).__init__()
        self.q1=q1
        self.q2=q2

    def run():
        while True:
            e.wait()
            if not self.q1.empty():
                courseware=self.q1.get()
                self.download(courseware)
            e.clear()
                
    def download(self,courseware):
        url=courseware.url
        n=courseware.n
        path0=courseware.root
        mob_token=courseware.mob_token
        lid=courseware.lid
        if not os.path.exists(courseware.weekname):
            os.mkdir(courseware.weekname)
        if not os.path.exists(courseware.partname):
            os.mkdir(courseware.partname)

        if not os.path.exists(courseware.name):
            self.q2.put('[Loading]开始下载{}'.format(url[2]+n))
            for i in range(3):
                try:
                    r=(getpdf(url,(lid,mob_token)) if courseware.type==3 else getvideo(url,(lid,mob_token)))
                    break
                except:
                    if i<2:
                        self.q2.put('[Loading]{}资源请求失败！正在重试'.format(url[2]+n))
                    else:
                        self.q2.put('[Error]{}资源请求失败！请稍后重试！'.format(os.sep.join([getname(lid)]+url[0:3])+n))
            try:
                with open(courseware.name,'wb') as f:
                    f.write(r)
                self.q2.put('[Success]{}下载成功！'.format(url[2]+n))
            except:
                self.q2.put('[Info]{}下载失败！正在尝试重新命名……'.format(repr(url[2])+n))
                tempname='Courseware'+str(random.randint(0,9999))
                try:
                    with open(tempname,'wb') as f:
                        f.write(r)
                    self.q2.put('[Success]原：{} 更名为：{} 后下载成功！'.format(repr(url[2]+n),tempname+n))
                except:
                    self.q2.put('[Error]{}文件保存失败！请联系开发人员！'.format(os.sep.join([getname(lid)]+url[0:3])+n))
        else:
            self.q2.put('[Info]文件{}已存在'.format(url[2]+n))
                

def back_process(queue_1,queue_2,event_1):  
    while True:  
        event_1.wait()  
        subject=queue_1.get()#后台进程获取UI进程“主题”输入框内容  
        body=queue_1.get()#后台进程获取UI进程“正文”输入框内容  
        img=queue_1.get()#附件      
        flage_1=send_my_mail(subject,body,img)#调用发送邮件函数  
        queue_2.put(flage_1)#将发送邮件函数的返回 发送给UI进程  
        event_1.clear()  
  
if __name__=='__main__':  
    #多线程多进程都必须在mainloop之前去执行  
    multiprocessing.freeze_support() #在Windows下编译需要加这行  
    queue_1=multiprocessing.Queue()#用来UI进程向后台发送邮件进程发送消息  
    queue_2=multiprocessing.Queue()#用来后台进程向UI进程发送消息  
    event_1=multiprocessing.Event()#控制后台进程是否阻塞  
    t=multiprocessing.Process(target=back_process,args=(queue_1,queue_2,event_1))  
    t.daemon=True  
    t.start()#要先于mainloop调用start 不然 进程不会启动  
    my_Gui=My_Gui(queue_1,queue_2,event_1)#GUI之后的代码不执行  
    my_Gui.daemon=True  #主线程结束自动销毁
    my_Gui.start()#要先于mainloop调用start 不然 线程不会启动  
    my_Gui.root.mainloop()#mainloop必须要在最后去执行，相当于while阻塞  
