import requests,json,re,os,random,time,hashlib

from multiprocessing import Pool
import multiprocessing

from network_file import Networkfile


def gettid(cid):
    url='https://www.icourse163.org/learn/DUT-'+cid
    r=requests.get(url)
    if re.search(r'"currentTermId": \d{10}',r.text):
        return re.search(r'"currentTermId": \d{10}',r.text).group(0)[-10:]
    else:
        print('未找到currentTermId')
        return ''


def get_courseinfo(cid,mob_token):
    headers={'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.0; SM-G9300 Build/NRD90M)'}
    data={'cid':cid,#可缺省\
          'tid':gettid(cid),\
          'mob-token':mob_token}
    url='https://www.icourse163.org/mob/course/courseLearn/v1'
    r=requests.post(url,data=data,timeout=30).content
    return json.loads(r.decode('utf8'))#.get('results').get('termDto').get('chapters')#.keys()

def rename(name):
    for i in ['\n','\r','\b','\t','\\','/',':','*','?','"','<','>','|']:
        name=name.replace(i,'')
    return name

def gettogen(username,passwd):
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

class Courseware():
    def __init__(self,courseinfo,chapternum,lessonnum,unitnum,root,mob_token,sharpness):
        courseDto=courseinfo.get('results').get('courseDto')
        cid=courseDto.get('id')
        coursename=courseDto.get('name')
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

        self.coursedir=root+os.sep+rename(coursename)
        self.chaptername=rename(self.chapter.get('name'))
        self.chapterdir=self.coursedir+os.sep+self.chaptername
        self.lessonname=rename(self.lesson.get('name'))
        self.lessondir=self.chapterdir+os.sep+self.lessonname
        self.unitname=rename(self.unit.get('name'))
        self.contentType=self.unit.get('contentType')
        self.unitid=self.unit.get('id')

        if self.contentType==1:#视频
            self.resourceInfo=self.unit.get('resourceInfo')
            if self.resourceInfo.get(shdict2[sharpness]):
                self.extension=shdict1[sharpness]
                self.vurl=self.resourceInfo.get(shdict2[sharpness])
            elif self.resourceInfo.get('videoHDUrl'):
                self.extension='.mp4'
                self.vurl=self.resourceInfo.get('videoHDUrl')
            else:
                self.extension='.mp4'
                self.vurl=self.resourceInfo.get('sdMp4Url')
            self.path=self.lessondir+os.sep+self.unitname+self.extension
            self.name=self.unitname+self.extension
            self.size0=50*1024*1024#预设值

        elif self.contentType==3:#文档
            self.extension='.pdf'
            self.contentId=self.unit.get('contentId')
            self.path=self.lessondir+os.sep+self.unitname+self.extension
            self.name=self.unitname+self.extension
            self.size0=3*1024*1024#预设值

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
            self.size0=3*1024*1024#预设值

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
                            f=self.getvideo()
                        elif self.contentType==3:
                            f=self.getpdf()
                        elif self.contentType==4:
                            f=self.getenclosure()
                        break
                    except:
                        if i<2:
                            print('[Loading]{}资源请求失败！正在重试'.format(self.name))
                        else:
                            print('[Error]{}资源请求失败！请稍后重试！'.format(self.name))

            
                if f.local_size<f.size:
                    print('[Loading]开始下载{}'.format(self.name))
                    try:
                        f.download()
                        if f.local_size>=f.size:
                            print('[Success]{}下载成功！'.format(self.name))
                        else:
                            print('[Error]{}文件不完整！')
                    except:
                        print('[Info]{}下载失败！'.format(self.name))
                else:
                    print('[Info]文件{}已存在2'.format(self.name))
            else:
                print('[Info]文件{}已存在1'.format(self.name))

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
        return Networkfile(self.vurl,self.path,params)

    def getpdf(self):
        url='http://www.icourse163.org/mob/course/learn/v1'
        data={'t':3,\
              'cid':self.contentId,\
              'unitId': self.unitid,\
              'mob-token': self.mob_token}
        r=requests.post(url,data=data).content
        pdf=json.loads(r.decode('utf8')).get("results").get('learnInfo').get("textOrigUrl")    
        return Networkfile(pdf,self.path)

    def getenclosure(self):
        url='http://www.icourse163.org/mob/course/attachment.htm'
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}
        params=self.jsonContent
        return Networkfile(url,self.path,params)



if __name__=='__main__':
    print('登录：（当前仅支持爱课程账号）')
    #################login###################
    from config import Config
    config=Config('config.txt','$')
    flag=0
    if config.get('username') and config.get('passwd') and \
       gettogen(config.username,config.passwd)[1]==0:
        k=input('已检测到您上次使用账号：{}，是否继续使用该账号？[y/n]'.format(config.username))
        if k[0] in 'Yy':
            flag=1
            username=config.username
            passwd=config.passwd
            mob_token=gettogen(username,passwd)[0]
    if not flag:
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
            k=gettogen(username,passwd)
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
    ########################################
    ##################root#################
    flag=0
    if config.get('root') and os.path.exists(config.root):
        k=input('您上次把课件存到了：{}，要不要继续使用这个路径呀？[y/n]'.format(config.root))
        if k[0] in 'Yy':
            flag=1
            root=config.root
    if not flag:
        while True:
            root=input('想存到哪里呢？：')
            if os.path.exists(root):
                print('嗯嗯，我记住啦')
                break
            else:
                print('这个路径不存在呀！')
    config.root=root
    config.save()
    #####################################
    while True:
        while True:
            cid=input('课程号课程号！')
            try:
                courseinfo=get_courseinfo(cid,mob_token)
                results=courseinfo.get('results')
                courseDto=results.get('courseDto')#课程信息
                cid=courseDto.get('id')#1001542001
                coursename=courseDto.get('name')#"面向对象程序设计——Java语言"
                schoolName=courseDto.get('schoolName')#"浙江大学"
                tid=courseDto.get('currentTermId')#1002776001
                print('课程名是 {} 吧？'.format(coursename))
                k=input('我找的对不对对不对！[y/n]')
                if k and k[0] in 'Yy':
                    break
            except:
                print('噫，我没找到这个课程！')
            
        chapters=courseinfo.get('results').get('termDto').get('chapters')
        print('以下课程已开放：')
        for chapter in chapters:
            print(chapter.get('name'))
        while True:
            k=input('您想下载哪几周的呀？（单个数字 or 起-止 or 0和all）')
            if k=='0' or k=='all':
                weeknum=list(range(len(chapters)))
                break
            elif re.search(r'\d+-\d+',k):
                se=re.search(r'\d+-\d+',k).group(0).split('-')
                if 0<eval(se[0])<=len(chapters) and 0<eval(se[1])<=len(chapters):
                    weeknum=list(range(eval(se[0])-1,eval(se[1])))
                    break
                else:
                    print('这个数字不在范围内呀')
            elif re.match(r'\d+$',k):
                if 0<eval(k)<=len(chapters):
                    weeknum=[eval(k)-1]
                    break
                else:
                    print('这个数字不在范围内呀')
            else:
                print('输错啦！')

        while True:
            k=input('您想下载哪种课件呐？(1:视频,3:pdf,4:附件,all:全部)')
            if '1' in k or '3' in k or '4' in k or 'all' in k:
                if 'all' in k:
                    loadtype=[1,3,4]
                    break
                else:
                    loadtype=[]
                    for i in k:
                        if i in '134':
                            loadtype.append(int(i))
                    break
            else:
                print('不对不对，这个我不认识！')

        sharpness='sd'
        if 1 in loadtype:
            while True:
                k=input('选个清晰度吧(标清"sd",高清"hd",超高清"shd")')
                if k in ['sd','hd','shd']:
                    sharpness=k
                    break
                else:
                    print('输错啦！')
        print('获取链接中，很快就好哒！')
        # chapters=courseinfo.get('results').get('termDto').get('chapters')
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
                            ))
                    unitnum+=1
                lessonnum+=1
            chapternum+=1
        for i in['-','\\','|','/']*5:
            time.sleep(0.2)
            print('\r下载进程召唤术'+i,end='')
        print()
        #########################概览################################
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
            'General_View.txt','w',encoding='utf-8') as f:
            s='{}_课程概览'.format(rename(coursename)).center(60,'=')+'\n'
            for chapter in chapters:
                s+='{}\n'.format(chapter.get('name'))
                for lesson in chapter.get('lessons'):
                    s+='      {}\n'.format(lesson.get('name'))
                    for unit in lesson.get('units'):
                        s+='            {}\n'.format('['+tpdict.get(unit.get('contentType'),'未知')+']'\
                        	+unit.get('name').replace('\n',''))
            f.write(s)
        #########################processes##########################
        import mul_process_package         #for_多进程打包
        multiprocessing.freeze_support()  #for_多进程打包
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

#####################################test#############################################
# with open('test.json','rb') as f:
#     courseinfo=json.loads(f.read())

# results=courseinfo.get('results')
# courseDto=results.get('courseDto')#课程信息
# cid=courseDto.get('id')#1001542001
# coursename=courseDto.get('name')#"面向对象程序设计——Java语言"
# schoolName=courseDto.get('schoolName')#"浙江大学"
# tid=courseDto.get('currentTermId')#1002776001


# termDto=results.get('termDto')#本学期信息
# chiefLectorDto=termDto.get('chiefLectorDto')#教师信息
# realname=chiefLectorDto.get('realName')#姓名
# lectorJob=chiefLectorDto.get('lectorJob')#职称
# lectureDesc=chiefLectorDto.get('lectureDesc')#描述

# chapternum=0
# lessonnum=0
# unitnum=1
# root='D:\\MOOC'
# username='s_sharing@126.com'
# password='123456'
# flag=hashlib.md5()
# flag.update(password.encode('utf-8'))
# passwd=flag.hexdigest()
# k=gettogen(username,passwd)
# mob_token=k[0]
# sharpness='shd'

# chapters=courseinfo.get('results').get('termDto').get('chapters')
# coursewares=[]
# chapternum=0 
# for chapter in chapters:
#     lessonnum=0
#     for lesson in chapter.get('lessons'):
#         unitnum=0
#         for unit in lesson.get('units'):
#             coursewares.append(Courseware(\
#                     courseinfo,\
#                     chapternum,\
#                     lessonnum,\
#                     unitnum,\
#                     root,\
#                     mob_token,\
#                     sharpness,\
#                     ))
#             unitnum+=1
#         lessonnum+=1
#     chapternum+=1


# weeknum=[0,1,2,3,4]
# loadtype=[1,3,4]
# for courseware in coursewares:
#     courseware.download(weeknum,loadtype)
# # c=Courseware(courseinfo,chapternum,lessonnum,unitnum,root,mob_token,sharpness)
# # # print(c.name)
# # c.download(weeknum,loadtype=[1,2,3,4,5,6])



# input('blabla')




