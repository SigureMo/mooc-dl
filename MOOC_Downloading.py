import requests,json,re,os,random,time

from multiprocessing import Pool
import multiprocessing


def gettid(lid):
    url='https://www.icourse163.org/learn/DUT-'+lid
    r=requests.get(url)
    if re.search(r'"currentTermId": \d{10}',r.text):
        return re.search(r'"currentTermId": \d{10}',r.text).group(0)[-10:]
    else:
        print('未找到currentTermId')
        return ''

def getname(lid):
    url='https://www.icourse163.org/learn/DUT-'+lid
    r=requests.get(url)
    if re.search(r'<title>.+_中国大学MOOC\(慕课\)</title>',r.text):
        return re.search(r'<title>.+_中国大学MOOC\(慕课\)</title>',r.text)\
               .group(0).replace('<title>','')\
               .replace('_中国大学MOOC(慕课)</title>','')
    else:
        return ''

def getchapters():
    headers={'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.0; SM-G9300 Build/NRD90M)'}
    data={'cid':lid,#可缺省\
          'tid':gettid(lid),\
          'mob-token':m}
    url='https://www.icourse163.org/mob/course/courseLearn/v1'
    r=requests.post(url,data=data,timeout=30).content
    return json.loads(r).get('results').get('termDto').get('chapters')#.keys()
    
def tree():
    weeks=[]
    for chapter in getchapters():
        parts=[]
        for part in chapter.get('lessons'):
            lessons=[]
            for lesson in part.get('units'):
                lessons.append([chapter.get('name'),\
                                part.get('name'),\
                                lesson.get('name'),\
                                lesson.get('contentId'),\
                                lesson.get('id'),\
                                lesson.get('contentType'),\
                                lesson.get('resourceInfo')])
            parts.append([part.get('name'),lessons])
        weeks.append([chapter.get('name'),parts])
    return weeks

def load_urls(week,tp='all',sharpness='sd'):
    urls=[]
    shdict={'sd':'sdMp4Url','hd':'videoHDUrl','shd':'videoSHDUrl'}
    tr=tree()
    for wk in week:
        w=tr[wk-1]
        for i in w[1]:
            for j in i[1]:
                #print(j)#Debugging
                if j[5]==1:
                    if tp in ['all','video']:#视频
                        if j[6].get(shdict[sharpness]):
                            urls.append(j[:-1]+[j[6].get(shdict[sharpness])])
                        elif j[6].get('videoHDUrl'):
                            urls.append(j[:-1]+[j[6].get('videoHDUrl')])
                        else:
                            urls.append(j[:-1]+[j[6].get('sdMp4Url')])
                elif j[5]==4 or j[2]==5:#文本和随堂测验
                    continue
                elif j[5]==3:
                    if tp in ['all','pdf']:#pdf
                        urls.append(j[:-1]+[''])
    return urls

def rename(name):
    return name\
           .replace('\n','')\
           .replace('\r','')\
           .replace('\b','')\
           .replace('\\','')\
           .replace('/','')\
           .replace(':','')\
           .replace('*','')\
           .replace('?','')\
           .replace('"','')\
           .replace('<','')\
           .replace('>','')\
           .replace('|','')

class Courseware():
    def __init__(self,url,glo):
        lid=glo[0]
        m=glo[1]
        path0=glo[2]
        coursename=glo[3]
        if url[5]==3:
            n='.pdf'
        elif url[5]==1:
            if '.flv' in url[-1]:
                n='.flv'
            else:
                n='.mp4'
        self.url=url
        self.root=path0
        self.coursename=path0+os.sep+rename(coursename)
        self.weekname=self.coursename+os.sep+rename(url[0])
        self.partname=self.weekname+os.sep+rename(url[1])
        self.name=self.partname+os.sep+rename(url[2])+n
        self.type=url[5]
        self.n=n

def download(courseware,glo):
    lid=glo[0]
    m=glo[1]
    path0=glo[2]
    n=courseware.n
    url=courseware.url
    if not os.path.exists(courseware.weekname):
        os.mkdir(courseware.weekname)
    if not os.path.exists(courseware.partname):
        os.mkdir(courseware.partname)

    if not os.path.exists(courseware.name):
        print('[Loading]开始下载{}'.format(url[2]+n))
        for i in range(3):
            try:
                r=(getpdf(url,glo) if courseware.type==3 else getvideo(url,glo))
                break
            except:
                if i<2:
                    print('[Loading]{}资源请求失败！正在重试'.format(url[2]+n))
                else:
                    print('[Error]{}资源请求失败！请稍后重试！'.format(os.sep.join([getname(lid)]+url[0:3])+n))
        try:
            with open(courseware.name,'wb') as f:
                f.write(r)
            print('[Success]{}下载成功！'.format(url[2]+n))
        except:
            print('[Info]{}下载失败！正在尝试重新命名……'.format(repr(url[2])+n))
            tempname='Courseware'+str(random.randint(0,9999))
            try:
                with open(tempname,'wb') as f:
                    f.write(r)
                print('[Success]原：{} 更名为：{} 后下载成功！'.format(repr(url[2]+n),tempname+n))
            except:
                print('[Error]{}文件保存失败！请联系开发人员！'.format(os.sep.join([getname(lid)]+url[0:3])+n))
    else:
        print('[Info]文件{}已存在'.format(url[2]+n))


def getpdf(purl,glo):
    lid=glo[0]
    m=glo[1]
    #path0=glo[2]
    url='http://www.icourse163.org/mob/course/learn/v1'
    data={'t':3,\
          'cid':purl[3],\
          'unitId': purl[4],\
          'mob-token': m}
    r=requests.post(url,data=data).content
    pdf=json.loads(r).get("results").get('learnInfo').get("textOrigUrl")    
    return requests.get(pdf).content

def getvideo(vurl,glo):
    lid=glo[0]
    m=glo[1]
    #path0=glo[2]
    headers={'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.0; SM-G9300 Build/NRD90M)',\
             'mob-token': m\
             }
    url='http://www.icourse163.org/mob/course/getVideoAuthorityToken/v1'
    r=requests.post(url,headers=headers).content
    k=json.loads(r).get("results").get("videoKey")
        
    headers={'User-Agent': 'AndroidDownloadManager'}
    params={'key':k,\
            'Xtask':lid+'_'+gettid(lid)+'_'+str(vurl[4])}
    return requests.get(vurl[-1],params=params,headers=headers).content



def gettogen(username,passwd):
    headers={'edu-app-type': 'android',\
             'edu-app-version': '2.6.1'}
    data={'username':username,\
          'passwd':passwd,\
          'mob-token':''}
    r=requests.post('http://www.icourse163.org/mob/logonByIcourse',\
                    headers=headers,\
                    data=data).content
    j=json.loads(r)
    if j.get("status").get("code")==0:
        return [j.get("results").get("mob-token"),\
                j.get("status").get("code")]
    elif j.get("status").get("code")==100:
        return [None,\
                j.get("status").get("code")]

if __name__=='__main__':
    '''print('登录：（当前仅支持爱课程账号，且密码为加密后的，需要自行抓包获取）')'''
    #################login###################
    from config import Config
    config=Config('config.txt')
    '''flag=0
    if config.get('username') and config.get('passwd') and \
       gettogen(config.username,config.passwd)[1]==0:
        k=input('已检测到您上次使用账号：{}，是否继续使用该账号？[y/n]'.format(config.username))
        if k[0] in 'Yy':
            flag=1
            username=config.username
            passwd=config.passwd
            m=gettogen(username,passwd)[0]
    if not flag:
        while True:
            username=input('请输入账号：')
            passwd=input('请输入密码：')
            #############Test###############
            if username=='test':
                username='240377379@qq.com'
                passwd=' '
            ################################
            k=gettogen(username,passwd)
            if k[1]==0:
                print('登陆成功！')
                m=k[0]
                break
            elif k[1]==100:
                print('账号或密码错误，请重新输入')
            else:
                print('发生未知错误！')
    config.username=username
    config.passwd=passwd
    config.save()'''
    ########################################
    m=gettogen('240377379@qq.com',' ')[0]
    ##################path0#################
    config=Config('config.txt')
    flag=0
    if config.get('path0') and os.path.exists(config.path0):
        k=input('您上次把课件存到了：{}，要不要继续使用这个路径呀？[y/n]'.format(config.path0))
        if k[0] in 'Yy':
            flag=1
            path0=config.path0
    if not flag:
        while True:
            path0=input('想存到哪里呢？：')
            if os.path.exists(path0):
                print('嗯嗯，我记住啦')
                break
            else:
                print('这个路径不存在呀！')
    config.path0=path0
    config.save()
    #####################################
    while True:
        while True:
            lid=input('课程号课程号！')
            #############Test###############
            if lid=='test':
                lid='1001541001'
            ################################
            if getname(lid):
                print('课程名是 {} 吧？'.format(getname(lid)))
                k=input('我找的对不对对不对！[y/n]')
                if k and k[0] in 'Yy':
                    break
            else:
                print('噫，我没找到这个课程！')
            
        w=[]
        for i in tree():
            w.append(i[0])
            print(i[0])
        while True:
            k=input('您想下载哪几周的呀？（单个数字 or 起-止 or 0和all）')
            if k=='0' or k=='all':
                week=list(range(1,len(w)+1))
                break
            elif re.search(r'\d+-\d+',k):
                se=re.search(r'\d+-\d+',k).group(0).split('-')
                if 0<eval(se[0])<=len(w) and 0<eval(se[1])<=len(w):
                    week=list(range(eval(se[0]),eval(se[1])+1))
                    break
                else:
                    print('这个数字不在范围内呀')
            elif re.match(r'\d+$',k):
                if 0<eval(k)<=len(w):
                    week=[eval(k)]
                    break
                else:
                    print('这个数字不在范围内呀')
            else:
                print('输错啦！')
        while True:
            k=input('您想下载哪种课件呐？("video","pdf","all")')
            if k in ["video","pdf","all"]:
                tp=k
                break
            else:
                print('不对不对，这个我不认识！')
        sharpness='sd'
        if tp in ["video","all"]:
            while True:
                k=input('选个清晰度吧(标清"sd",高清"hd",超高清"shd")')
                if k in ['sd','hd','shd']:
                    sharpness=k
                    break
                else:
                    print('输错啦！')
        print('获取链接中，很快就好哒！')
        urls=load_urls(week,tp,sharpness)
        coursewares=[]
        glo=[lid,m,path0,getname(lid)]
        for url in urls:
            coursewares.append(Courseware(url,glo))
        for i in['-','\\','|','/']*5:
            time.sleep(0.2)
            print('\r开始启动下载进程，请小等片刻喔'+i,end='')
        print()
        #########################概览################################
        if not os.path.exists(path0+os.sep+rename(getname(lid))):
            os.mkdir(path0+os.sep+getname(lid))
        with open(path0+os.sep+getname(lid)+os.sep+\
                                 'General_View.txt','w',encoding='utf-8') as f:
            s='{}_课程概览'.format(getname(lid)).center(60,'=')+'\n'
            for i in tree():
                s+='{}\n'.format(i[0])
                for j in i[1]:
                    s+='\t{}\n'.format(j[0])
                    for k in j[1]:
                        s+='\t\t{}\n'.format(k[2])
            f.write(s)
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
            pool.apply_async(download, args=(courseware,glo))
        #pool.map(download,urls)
        pool.close()
        pool.join()
        # ##########################单进程#################################
        # for url in urls:
        #     glo=[lid,m,path0]
        #     download(url,glo)
        ##########################check#################################
        for courseware in coursewares:
            if not os.path.exists(courseware.name):
                print('噫，{}刚才下载失败啦，我再试试，稍等下哈'.format(courseware.name))
                download(courseware,glo)
        print('哇，全都下完啦！快点去看吧！')
        ct=input('对了，要不要下载其他课程呐？[y/n]')
        if ct and ct[0] in 'Nn':
            break
    input('Press <Enter>')






