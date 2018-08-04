import requests
import json
import re
import os
import random
import time
import hashlib
import platform
import queue
#import multiprocessing

from bs4 import BeautifulSoup
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 

from tools.network_file import Networkfile
from tools.config import Config

version = (1, 6, 6)

def getterminfos(cid):
    response=requests.get('https://www.icourse163.org/course/DUT-{}#/info'.format(cid))
    soup=BeautifulSoup(response.text,'html.parser')
    scripts=soup.find_all('script',string=re.compile('termId'))
    if len(scripts)>1:
        script=scripts[-1].string
    elif len(scripts)<1:
        script=''
    else:
        script=scripts[0].string
    cinfo=re.search(r'window.courseDto[\s\S]*window.chiefLector',script)
    if cinfo:
        coursename=eval(re.search(r'name:[\s\S]*?(?P<coursename>"[\s\S]*?")[\s\S]',cinfo.group(0)).group('coursename'))
    else:
        coursename=''
    tinfo=re.search(r'window.termInfoList[\s\S]*(?P<termInfoList>\[[\s\S]*\])[\s\S]*window.categories',script)
    if tinfo:
        termInfoList=json.loads(tinfo.group('termInfoList')\
                                .replace('id','"id"')\
                                .replace('courseId','"courseId"')\
                                .replace('startTime','"startTime"')\
                                .replace('endTime','"endTime"')\
                                .replace('duration','"duration"')\
                                .replace('text','"text"')
                                )
    else:
        termInfoList=[]
    return coursename,termInfoList

def get_courseinfo(tid,mob_token):
    headers={'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.0; SM-G9300 Build/NRD90M)'}
    data={#'cid':cid,#可缺省\
          'tid':tid,\
          'mob-token':mob_token}
    url='https://www.icourse163.org/mob/course/courseLearn/v1'
    r=requests.post(url,data=data,timeout=30).content
    return json.loads(r.decode('utf8'))#.get('results').get('termDto').get('chapters')#.keys()

def rename(name):
    for i in ['\n','\r','\b','\t','\\','/',':','*','?','"','<','>','|']:
        name=name.replace(i,'')
    return name

def gettoken(username,passwd):
    headers={'edu-app-type': 'android',\
             'edu-app-version': '2.6.1'}
    data={'username':username,\
          'passwd':passwd,\
          'mob-token':''}
    r=requests.post('http://www.icourse163.org/mob/logonByIcourse',\
                    headers=headers,\
                    data=data).content
    j=json.loads(r.decode('utf8'))
    if j.get("status").get("code")==0:
        return [j.get("results").get("mob-token"),\
                j.get("status").get("code")]
    elif j.get("status").get("code")==100:
        return [None,\
                j.get("status").get("code")]
    else:
        return [None,\
                j.get("status").get("code")]

class Courseware():
    def __init__(self,courseinfo,chapternum,lessonnum,unitnum,root,mob_token,sharpness,infoQ):
        self.infoQ = infoQ
        courseDto=courseinfo.get('results').get('courseDto')
        cid=courseDto.get('id')
        self.coursename=courseDto.get('name')
        tid=courseDto.get('currentTermId')
        shdict1={'sd':'.mp4','hd':'.mp4','shd':'.flv'}
        shdict2={'sd':'sdMp4Url','hd':'videoHDUrl','shd':'videoSHDUrl'}
        # exdict={1:shdict1[sharpness],#视频
        #         2:'',#暂未知
        #         3:'.pdf',#文档
        #         4:'.zip',#富文本
        #         5:'',#随堂测验
        #         6:'',#讨论
        #         }

        self.chapternum=chapternum
        self.mob_token=mob_token
        self.root=root
        self.cid=cid
        self.tid=tid
        self.sharpness=sharpness

        self.chapter=courseinfo.get('results').get('termDto').get('chapters')[chapternum]
        self.lesson=self.chapter.get('lessons')[lessonnum]
        self.unit=self.lesson.get('units')[unitnum]

        self.coursedir=root+os.sep+rename(self.coursename)
        self.chaptername=rename(self.chapter.get('name'))
        self.chapterdir=self.coursedir+os.sep+self.chaptername
        self.lessonname=rename(self.lesson.get('name'))
        self.lessondir=self.chapterdir+os.sep+self.lessonname
        self.unitname=rename(self.unit.get('name'))
        self.contentType=self.unit.get('contentType')
        self.unitid=self.unit.get('id')

        if self.contentType==1:#视频
            self.resourceInfo=self.unit.get('resourceInfo')
            self.contentId=self.unit.get('contentId')
            if self.resourceInfo.get(shdict2[sharpness]):
                self.extension=shdict1[sharpness]
                self.vurl=self.resourceInfo.get(shdict2[sharpness])
            elif self.resourceInfo.get('videoHDUrl'):
                self.extension='.mp4'
                self.vurl=self.resourceInfo.get('videoHDUrl')
            else:
                self.extension='.mp4'
                self.vurl=self.resourceInfo.get('sdMp4Url')
            self.srtKeys = self.resourceInfo.get('srtKeys')
            if self.srtKeys:
                self.srtDict = {
                    0: 'zh-cn',
                    1: 'en',
                    }
            self.path=self.lessondir+os.sep+self.unitname+self.extension
            self.name=self.unitname+self.extension
            self.size0=95*1024*1024#预设值

        elif self.contentType==3:#文档
            self.extension='.pdf'
            self.contentId=self.unit.get('contentId')
            self.path=self.lessondir+os.sep+self.unitname+self.extension
            self.name=self.unitname+self.extension
            self.size0=0.61*1024*1024#预设值

        elif self.contentType==4:#富文本
            if self.unit.get('jsonContent'):
                self.jsonContent=eval(self.unit.get('jsonContent'))
                self.extension='.'+self.jsonContent.get('fileName').split('.')[-1]
                self.path=self.lessondir+os.sep+self.jsonContent.get('fileName')
                self.name=self.jsonContent.get('fileName')
            else:
                self.extension=''
                self.jsonContent={}
                self.path=''
                self.name=self.unitname
            self.size0=1.02*1024*1024#预设值

        elif self.contentType not in [1,3,4,5,6]:
            self.extension=''
            self.path=''
            self.name=self.unitname+self.extension
            print('您发现了新类型！快点告诉开发人员！')
            print(cid,chapternum,lessonnum,unitnum)

        else:
            self.extension=''
            self.path=''
            self.name=self.unitname+self.extension
 
    def download(self,weeknum,loadtype):
        if self.chapternum in weeknum and self.contentType in loadtype and self.path:
            if not os.path.exists(self.chapterdir):
                os.mkdir(self.chapterdir)
            if not os.path.exists(self.lessondir):
                os.mkdir(self.lessondir)
            if not os.path.exists(self.path) or os.path.getsize(self.path)<self.size0:
                for i in range(3):
                    try:
                        if self.contentType==1:
                            p = self.getvideo()
                            if self.srtKeys:
                                self.getSrts()
                        elif self.contentType==3:
                            p = self.getpdf()
                        elif self.contentType==4:
                            p = self.getenclosure()
                        self.f = Networkfile(*p)
                        break
                    except:
                        if i<2:
                            self.print('[Loading]{}资源请求失败！正在重试'.format(self.name))
                        else:
                            self.print('[Error]{}资源请求失败！请稍后重试！'.format(self.name))

                if self.f.local_size<self.f.size:
                    self.print('[Loading]开始下载{}'.format(self.name))
                    try:
                        self.f.download()
                        if self.f.local_size>=self.f.size:
                            self.print('[Success]{}下载成功！'.format(self.name))
                        else:
                            self.print('[Error]{}文件不完整！')
                    except:
                        self.print('[Info]{}下载失败！'.format(self.name))
                else:
                    self.print('[Info]文件{}已存在2'.format(self.name))
            else:
                self.print('[Info]文件{}已存在1'.format(self.name))

    def getCourseJSON(self, jsonData):
        try:
            if self.contentType==1:
                p = self.getvideo()
            elif self.contentType==3:
                p = self.getpdf()
            elif self.contentType==4:
                p = self.getenclosure()
        except:
            p = (None, self.path)
        jsonData.append(list(p))
        return jsonData

    def getvideo(self):
        headers={'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.0; SM-G9300 Build/NRD90M)',\
                 'mob-token': self.mob_token\
                 }
        url='http://www.icourse163.org/mob/course/getVideoAuthorityToken/v1'
        r=requests.post(url,headers=headers).content
        k=json.loads(r.decode('utf8')).get("results").get("videoKey")

        headers={'User-Agent': 'AndroidDownloadManager'}
        params={'key':k,\
                'Xtask':str(self.cid)+'_'+str(self.tid)+'_'+str(self.unitid)}
        return self.vurl, self.path, params

    def getSrts(self):
        self.srtPaths = []
        headers = {
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 8.0.0; SM-G9300 Build/R16NW)',
            }
        data = {
            't': 1,
            'mob-token': self.mob_token,
            'unitId': self.unitid,
            'cid': self.contentId,
            }
        response = requests.post('https://www.icourse163.org/mob/course/learn/v1',data = data)
        for srtKey in response.json()['results']['learnInfo']['srtKeys']:
            path = self.lessondir + os.sep + self.unitname + \
                   '[' + self.srtDict.get(srtKey['lang'], '未知语言') + ']' + '.srt'
            url = srtKey['nosUrl']
            self.srtPaths.append(path)
            with open(path, 'wb') as f:
                f.write(requests.get(url).content)
        
    def getpdf(self):
        url='http://www.icourse163.org/mob/course/learn/v1'
        data={'t':3,\
              'cid':self.contentId,\
              'unitId': self.unitid,\
              'mob-token': self.mob_token}
        r=requests.post(url,data=data).content
        pdf=json.loads(r.decode('utf8')).get("results").get('learnInfo').get("textOrigUrl")    
        return pdf, self.path

    def getenclosure(self):
        url='http://www.icourse163.org/mob/course/attachment.htm'
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}
        params=self.jsonContent
        return url, self.path, params

    def print(self, string):
        if self.infoQ:
            self.infoQ.put(string)
        else:
            print(string)
        
#用户界面：（命令行）
def login(ignore=False):
    loginflag=not ignore
    config=Config('data/config.txt','$')
    print('登录：（当前仅支持爱课程账号）')
    flag=0
    if config.get('username') and config.get('passwd') and \
       gettoken(config.username,config.passwd)[1]==0:
        if loginflag:
            k=input('已检测到您上次使用账号：{}，是否继续使用该账号？[y/n]'.format(config.username))
            if k[0] in 'Yy':
                flag=1
        else:
            print('自动登录成功')
            flag=1
    if flag:
        username=config.username
        passwd=config.passwd
        mob_token=gettoken(username,passwd)[0]
    else:
        while True:
            username=input('请输入账号：')
            password=input('请输入密码：')
            flag=hashlib.md5()
            flag.update(password.encode('utf-8'))
            passwd=flag.hexdigest()
            #############Sharing###############
            if username=='sharing':
                username='s_sharing@126.com'
                passwd='e10adc3949ba59abbe56e057f20f883e'
            ################################
            k=gettoken(username,passwd)
            if k[1]==0:
                print('登陆成功！')
                mob_token=k[0]
                break
            elif k[1]==100:
                print('账号或密码错误，请重新输入')
            else:
                print('发生未知错误！')
    config.username=username
    config.passwd=passwd
    config.save()
    return mob_token

def getroot(ignore=False):
    rootflag=not ignore
    config=Config('data/config.txt','$')
    flag=0
    rootname=platform.system()+'Root'
    if config.get(rootname) and os.path.exists(config.get(rootname)):
        if rootflag:
            k=input('您上次把课件存到了：{}，要不要继续使用这个路径呀？[y/n]'.format(config.get(rootname)))
            if k[0] in 'Yy':
                flag=1
        else:
            print('路径已自动配置:'+config.get(rootname))
            flag=1
    if flag:
        root=config.get(rootname)
    else:
        while True:
            root=input('想存到哪里呢？：')
            if os.path.exists(root):
                print('嗯嗯，我记住啦')
                break
            else:
                print('这个路径不存在呀！')
    config.set(rootname,root)
    config.save()
    return root

def gettid(terminfos,ignore=False):
    termnumflag=not ignore
    config=Config('data/config.txt','$')
    k=config.get('termnum')
    if not termnumflag and \
       k and \
       re.match(r'\d+$',k) and \
       0<=eval(k)<=len(terminfos)+1:
        if 1<=int(k)<=len(terminfos)+1:
            t='第'+str(k)
        elif k=='0':
            t='最新'
        termnum=int(k)-1
        print('已自动配置下载{}学期课程'.format(t))
    else:
        for termnum in range(len(terminfos)):
            terminfo=terminfos[termnum]
            print('第%d次开课：'%(termnum+1)+terminfo['text']+'，课程号：'+terminfo['id'])
        while True:
            k=input('想下哪个学期的课呢？（最新学期请输入0）')
            try:
                if 0<=int(k)<=len(terminfos)+1:
                    termnum=int(k)-1
                    break
                else:
                    print('我可不会穿越哦~')
            except:
                print('这是啥？')
    config.termnum=str(termnum+1)
    config.save()
    return terminfos[termnum]['id']

def getweeknum(chapters,ignore=False):
    def check_weeknum(k):
        if k=='0' or k=='all':
            weeknum=list(range(len(chapters)))
        elif re.search(r'\d+-\d+',k):
            se=re.search(r'\d+-\d+',k).group(0).split('-')
            if 0<eval(se[0])<=len(chapters) and 0<eval(se[1])<=len(chapters):
                weeknum=list(range(eval(se[0])-1,eval(se[1])))
            else:
                print('这个数字不在范围内呀')
                weeknum=''
        elif re.match(r'\d+$',k):
            if 0<eval(k)<=len(chapters):
                weeknum=[eval(k)-1]
            else:
                print('这个数字不在范围内呀')
                weeknum=''
        return weeknum
    weeknumflag=not ignore
    config=Config('data/config.txt','$')
    k=config.get('weeknum')
    if not weeknumflag and \
       check_weeknum(k):
        weeknum=check_weeknum(k)
        print('已自动配置下载周次为:'+k)
    else:
        print('以下课程已开放：')
        for chapter in chapters:
            print(chapter.get('name'))
        while True:
            k=input('您想下载哪几周的呀？（单个数字 or 起-止 or 0和all）')
            if check_weeknum(k):
                weeknum=check_weeknum(k)
                break
            else:
                print('输错啦！')
    config.weeknum=k
    config.save()
    return weeknum

def getloadtype(ignore=False):
    def check_loadtype(k):
        if '1' in k or '3' in k or '4' in k or 'all' in k:
            if 'all' in k:
                loadtype=[1,3,4]
            else:
                loadtype=[]
                for i in k:
                    if i in '134':
                        loadtype.append(int(i))
        else:
            print('不对不对，这个我不认识！')
            loadtype=[]
        return loadtype
    loadtypeflag=not ignore
    config=Config('data/config.txt','$')
    k=config.get('loadtype')
    if not loadtypeflag and \
       check_loadtype(k):
        loadtype=check_loadtype(k)
        print('已自动配置下载类型为:'+k+'(1:视频,3:pdf,4:附件,all:全部)')
    else:
        while True:
            k=input('您想下载哪种课件呐？(1:视频,3:pdf,4:附件,all:全部)')
            loadtype=check_loadtype(k)
            if loadtype:
                break
    config.loadtype=k
    config.save()
    return loadtype

def getsharpness(ignore=False):
    sharpnessflag=not ignore
    config=Config('data/config.txt','$')
    k=config.get('sharpness')
    if not sharpnessflag and \
       k in ['sd','hd','shd']:
        sharpness=k
        print('已自动配置视频清晰度为:'+k+'(标清"sd",高清"hd",超高清"shd")')
    else:
        while True:
            k=input('选个清晰度吧(标清"sd",高清"hd",超高清"shd")')
            if k in ['sd','hd','shd']:
                sharpness=k
                break
            else:
                print('输错啦！')
    config.sharpness=k
    config.save()
    return sharpness

def general_view(courseinfo,root):
    chapters=courseinfo.get('results').get('termDto').get('chapters')
    results=courseinfo.get('results')
    courseDto=results.get('courseDto')#课程信息
    cid=courseDto.get('id')#1001542001
    coursename=courseDto.get('name')#"面向对象程序设计——Java语言"
    if not os.path.exists(root+os.sep+rename(coursename)):
        os.mkdir(root+os.sep+rename(coursename))
    tpdict={1:'视频',
            # 2:'',#暂未知
            3:'文档',#文档
            4:'富文本',#富文本
            5:'测验',#随堂测验
            6:'讨论',#讨论
            }
    with open(root+os.sep+rename(coursename)+os.sep+\
        'General_View.txt','w',encoding='utf-8', newline='\r\n') as f:
        s='{}_课程概览'.format(rename(coursename)).center(60,'=')+'\n'
        for chapter in chapters:
            s+='{}\n'.format(chapter.get('name'))
            for lesson in chapter.get('lessons'):
                s+='      {}\n'.format(lesson.get('name'))
                for unit in lesson.get('units'):
                    s+='            {}\n'.format('['+tpdict.get(unit.get('contentType'),'未知')+']'\
                            +unit.get('name').replace('\n',''))
        f.write(s)

def playlist(coursename,coursewares,root):
    with open(root+os.sep+rename(coursename)+os.sep+\
        'Playlist.m3u','w',encoding='utf-8') as f:
        s=''
        for courseware in coursewares:
            if courseware.contentType==1:
                s+='{}/{}/{}\n'.format(courseware.chaptername,courseware.lessonname,courseware.name)
        f.write(s)
    with open(root+os.sep+rename(coursename)+os.sep+\
        'Playlist.dpl','w',encoding='utf-8') as f:
        s='DAUMPLAYLIST\n'
        num = 1
        for courseware in coursewares:
            if courseware.contentType==1:
                s+='{}*file*{}\n'.format(num, courseware.path.replace(r'\\', '\\'))
                num += 1
        f.write(s)

def getcoursewares(courseinfo,root,mob_token,sharpness,infoQ = ''):
    chapters=courseinfo.get('results').get('termDto').get('chapters')
    coursewares=[]
    chapternum=0 
    for chapter in chapters:
        lessonnum=0
        for lesson in chapter.get('lessons'):
            unitnum=0
            for unit in lesson.get('units'):
                coursewares.append(Courseware(\
                        courseinfo,\
                        chapternum,\
                        lessonnum,\
                        unitnum,\
                        root,\
                        mob_token,\
                        sharpness,\
                        infoQ,
                        ))
                unitnum+=1
            lessonnum+=1
        chapternum+=1
    return coursewares


if __name__=='__main__':
    def isignore(config,attr):
        try:
            if eval(config.get(attr))==True:
                return True
            else:
                config.set(attr,'False')
                return False
        except:
            config.set(attr,'False')
            return False
        finally:
            config.save()
    config=Config('data/config.txt','$')
    ignoreconfig=Config('data/IgnoreOptions.txt',' is ignore? ')

    mob_token=login(isignore(ignoreconfig,'login'))   #登录
    root=getroot(isignore(ignoreconfig,'root'))       #设置下载路径
    
    while True:
        while True:
            cid=input('课程号课程号！')
            try:
                coursename,terminfos=getterminfos(cid)
                if coursename:
                    print('课程名是 {} 吧？'.format(coursename))
                    k=input('我找的对不对对不对！[y/n]')
                    if k and k[0] in 'Yy':
                        break
                else:
                    print('噫，我没找到这个课程！')
            except:
                print('噫，我没找到这个课程！')
                
        tid=gettid(terminfos,isignore(ignoreconfig,'termnum'))#获取学期课程号
        courseinfo=get_courseinfo(tid,mob_token)              #获取课程信息
        courseDto=courseinfo.get('results').get('courseDto')  #课程全信息
        cid=courseDto.get('id')                               #校正cid:1001542001
        coursename=courseDto.get('name')                      #校正课程名："面向对象程序设计——Java语言"

        chapters=courseinfo.get('results').get('termDto').get('chapters')#获取课件信息
        weeknum=getweeknum(chapters,isignore(ignoreconfig,'weeknum'))    #下载周次
        loadtype=getloadtype(isignore(ignoreconfig,'loadtype'))          #下载类型
        sharpness='sd'
        if 1 in loadtype:
            sharpness=getsharpness(isignore(ignoreconfig,'sharpness'))   #视频清晰度
            
        print('获取链接中，很快就好哒！')
        
        coursewares=getcoursewares(courseinfo,root,mob_token,sharpness)  #实例化各课件为Courseware
        
        for i in['-','\\','|','/']*5:
            time.sleep(0.2)
            print('\r下载进程召唤术'+i,end='')
        print()
        general_view(courseinfo,root)             #课程概览
        playlist(coursename,coursewares,root)     #播放列表
        #########################processes##########################
        #import mul_process_package         #for_多进程打包
        #multiprocessing.freeze_support()  #for_多进程打包
        if config.get('process_num'):
            try:
                if 3<=eval(config.process_num)<=10:
                    process_num=eval(config.process_num)
                else:
                    process_num=5
            except:
                process_num=5
        else:
            process_num=5
        config.process_num=str(process_num)
        config.save()
        pool=Pool(process_num)                     #同时启动的进程数
        for courseware in coursewares:
            pool.apply_async(courseware.download, args=(weeknum,loadtype))
        pool.close()
        pool.join()
        ##########################单进程#################################
        # for courseware in coursewares:
        #     courseware.download(weeknum,loadtype)
        ##########################check#################################
        for courseware in coursewares:
            if  courseware.path and not os.path.exists(courseware.path):
                print('噫，{}刚才下载失败啦，我再试试，稍等下哈'.format(courseware.name))
                courseware.download(weeknum,loadtype)
        print('哇，全都下完啦！记得要看哦！')
        ct=input('对了，要不要下载其他课程呐？[y/n]')
        if ct and ct[0] in 'Nn':
            break
    input('Press <Enter>')




