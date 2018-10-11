# _*_ coding:utf-8 _*_
from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import os
import time
from tkinter.filedialog import *
import threading
import getfile
class MyApp(Tk):
    def __init__(self):
        super().__init__()
        self.title('下载任务')
        self.geometry('+400+230') 
        self.minsize(810,440)  #设置窗口的最小尺寸
        self.resizable(width=False,height=False)  #设置不可改变窗口大小
        self.attributes("-alpha",1)  #背景虚化
        self["bg"]="gray"                          #设置窗口的背景颜色
        self.protocol('WM_DELETE_WINDOW',self.exit_window)#绑定窗口退出事件
        self.setupUI()
    def setupUI(self):  #设置根窗口的UI

        #创建fm1
        fm1=Frame(self,bg='white',bd=2)
        l=Label(fm1,text='新建任务',bg='white',cursor='hand2',font=('宋体',15))
        l.pack(padx=40,pady=95)
        l.bind("<Button-1>",self.down_top)  #默认会把鼠标左键单击事件作为参数传入函数中
        fm1.pack(side=LEFT,fill=Y)
        #创建fm2
        self.fm2=Frame(self,bg='gray',bd=2)
        self.fm2.pack(side=TOP,fill=BOTH,expand=1) 

    def down_top(self,event):  #创建新的窗口
        down=TopWindow(self)
        self.wait_window(down)

    def exit_window(self): #退出程序执行的函数
        if len(self.fm2.pack_slaves())==0:
            exit()
        else:
            if tkinter.messagebox.askyesno('退出','还有任务没完成\n确定退出吗？'):
                exit()
        #print(e)

class TopWindow(Toplevel): #创建窗口类
    def __init__(self,parent):
        super().__init__()
        self.parent=parent
        self.title('新建下载任务')
        self.geometry('360x200+600+290') 
        self.resizable(width=False,height=False)  #设置不可改变窗口大小
        self.grab_set()  #不可操作根窗口
        self.setUI()
    def setUI(self):
        l1=Label(self,text='填写下载文件链接',fg='blue')
        l1.pack(pady=10)
        url=StringVar()
        Entry(self,textvariable=url,font=(35),width=40).pack()
        b=Button(self,text='开始下载',width=15,font=(10),bg="blue",fg='white',command=lambda:self.ok(url))
        b.pack(side=BOTTOM,pady=25)

    def ok(self,e):
        if not re.match('^(https?|ftp)://.+$',e.get()):
            tkinter.messagebox.showerror("错误", "无效的网址或目标路径")
        else:
            try:
                self.gf=getfile.Getfile(e.get())
            except Exception as e:
                tkinter.messagebox.showinfo("提示","无法访问该网址"+str(e))
                return
            name=self.gf.getfilename()
            self.filename = asksaveasfilename(filetypes=[('all files','.*')],initialfile=name,defaultextension='')
            if self.filename!='':
                self.destroy()
                sp=Showpro(self.parent.fm2,self.filename,self.gf)
                sp.fn.set(os.path.basename(self.filename))
                t1=threading.Thread(target=sp.progressbar_thread)
                t1.setDaemon(True)
                t1.start()
                t2=threading.Thread(target=self.gf.downfile,args=(self.filename,))
                t2.setDaemon(True)
                t2.start()

class Showpro():#配置进度条
    def __init__ (self,fm2,filename,gf):
        #设置下载进度条的UI
        self.fm2=fm2
        self.filename=filename
        self.gf=gf
        self.fm4=Frame(self.fm2,bg='white',bd=2)
        self.photo1 = PhotoImage(file='icon\\start.png')
        self.photo2 = PhotoImage(file='icon\\cancel.png')
        self.photo3 = PhotoImage(file='icon\\pause.png')
        self.photo = PhotoImage(file='icon\\file.png')
        self.photo4 = PhotoImage(file='icon\\dir.png')
        self.fn=StringVar()
        Label(self.fm4,image=self.photo,width=150,textvariable=self.fn,compound='left',bg='white',anchor='w').grid(row=0,padx=5)
        self.value=IntVar()
        pb=ttk.Progressbar(self.fm4,length=200,variable=self.value)
        pb.grid(row=0,column=1,padx=10)
        self.tv=StringVar()
        self.label_1=Label(self.fm4,textvariable=self.tv,image=self.photo3,bg='white',cursor='hand2')
        self.tv.set('暂停')
        self.label_1.grid(row=0,column=2,padx=5)
        self.label_1.bind('<Button-1>',self.pause_start)
        self.label_2=Label(self.fm4,image=self.photo2,bg='white',cursor='hand2')
        self.label_2.grid(row=0,column=3)
        self.label_2.bind('<Button-1>',self.cancel)
        self.label_3=Label(self.fm4,text=os.path.dirname(self.filename),image=self.photo4,bg='white',cursor='hand2')
        self.label_3.grid(row=0,column=4)
        self.label_3.bind('<Button-1>',self.opendir)
        self.downsize=StringVar()
        Label(self.fm4,textvariable=self.downsize,bg='white').grid(row=1,column=0)
        self.downspeed=StringVar()
        Label(self.fm4,textvariable=self.downspeed,bg='white').grid(row=1,column=1)
        self.downspeed.set('等待下载...')
        self.fm4.pack(fill=X,pady=1)

    def progressbar_thread (self) :  #实时显示下载进度
        self.file_size=0
        self.file_total=self.gf.getsize()  #获取下载文件大小
        while self.file_size<self.file_total and self.gf.flag:
            time.sleep(1)
            if os.path.exists(self.filename):
                self.downspeed.set('{:.1f}KB/S'.format((os.path.getsize(self.filename)-self.file_size)/1024))
                try:
                    self.file_size=os.path.getsize(self.filename)
                except:
                    self.file_size=0
                self.value.set(self.file_size/self.file_total*100)
                self.downsize.set('{:.1f}M/{:.1f}M'.format(self.file_size/1024/1024,self.file_total/1024/1024))
        if self.file_size==self.file_total:  #当下载完成时，执行的命令
            self.fm4.pack_forget() 
            #把下载记录写入download.log中
            f=open('download.log','a')
            file_name=os.path.basename(self.filename)
            filepath=os.path.dirname(self.filename)
            cu_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            f.write('{}  {}  {}\n'.format(file_name,filepath,cu_time))
            f.close
            tkinter.messagebox.showinfo("提示",self.fn.get()+"下载完成")
        self.downspeed.set('暂停中...')

    def pause_start(self,e):  #暂停或继续下载
        if self.tv.get()=='开始': #继续下载
            self.label_1.configure(image=self.photo3)
            self.tv.set('暂停')
            self.downspeed.set('等待下载...')
            self.gf.flag=True
            self.gf.header_flag=True
            t1=threading.Thread(target=self.progressbar_thread)
            t1.setDaemon(True)
            t1.start()
            t2=threading.Thread(target=self.gf.downfile,args=(self.filename,))
            t2.setDaemon(True)
            t2.start()
            
        else : #暂停下载
            self.label_1.configure(image=self.photo1)
            self.downspeed.set('暂停中...')
            self.gf.flag=False
            self.tv.set('开始')
    
    def cancel(self,e): #取消下载
        if tkinter.messagebox.askyesno('取消','确定取消下载{}吗？'.format(os.path.basename(self.filename))):
            self.gf.cancel(self.filename)
            self.fm4.pack_forget() 

    def opendir(self,e): #打开文件所在目录
        dirname=os.path.dirname(self.filename).replace('/','\\')
        os.system('explorer '+dirname)

if __name__ == '__main__':
    app=MyApp()
    app.mainloop()
