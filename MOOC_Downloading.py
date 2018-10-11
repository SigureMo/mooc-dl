import requests,json,re,os,random

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
    for wk in week:
        w=tree()[wk-1]
        for i in w[1]:
            for j in i[1]:
                if j[5]==1:
                    if tp in ['all','video']:#视频
                        urls.append(j[:-1]+[j[6].get(shdict[sharpness])])
                elif j[5]==4 or j[2]==5:#文本和随堂测验
                    continue
                elif j[5]==3:
                    if tp in ['all','pdf']:#pdf
                        urls.append(j[:-1]+[''])
    return urls

def download(url,glo):
    lid=glo[0]
    m=glo[1]
    path0=glo[2]
    if not os.path.exists(path0+os.sep+getname(lid)):
        os.mkdir(path0+os.sep+getname(lid))
    if not os.path.exists(path0+os.sep+getname(lid)+os.sep+url[0]):
        os.mkdir(path0+os.sep+getname(lid)+os.sep+url[0])
    if not os.path.exists(path0+os.sep+getname(lid)+os.sep+url[0]+os.sep+url[1]):
        os.mkdir(path0+os.sep+getname(lid)+os.sep+url[0]+os.sep+url[1])
            
    if url[5]==3:
        n='.pdf'
    elif url[5]==1:
        if '.flv' in url[-1]:
            n='.flv'
        else:
            n='.mp4'
    if not os.path.exists(os.sep.join([path0]+[getname(lid)]+url[0:3])+n):
        print('开始下载'+url[2]+n)
        try:
            r=(getpdf(url,glo) if url[5]==3 else getvideo(url,glo))
            try:
                with open(os.sep.join([path0]+[getname(lid)]+url[0:3])+n,'wb') as f:
                    f.write(r)
                print('***{}下载成功！***'.format(url[2]+n))
            except:
                print('{}下载失败！正在尝试重新命名……'.format(url[2]+n))
                tempname='Courseware'+str(random.randint(0,9999))
                try:
                    with open(os.sep.join([path0]+[getname(lid)]+url[0:2]+[tempname])+n,'wb') as f:
                        f.write(r)
                    print('原：{} 更名为：{} 后下载成功！请自行重命名……'.format(url[2]+n,tempname+n))
                except:
                    print('！！！{}下载失败！请手动下载！'.format(os.sep.join([getname(lid)]+url[0:3])+n))
        except:
            print('！！！{}请求失败！请手动下载！'.format(os.sep.join([getname(lid)]+url[0:3])+n))
            
    else:
        print('文件{}已存在'.format(url[2]+n))


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
'''
'videoHDUrl'高清
'videoSHDUrl'超高清flv
'sdMp4Url'标清
'''

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
                passwd='77*****85f3*************df5****'
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
    m=gettogen('240377379@qq.com','77***38685***d125b***80c***50***')[0]#for Easyload
    ##################path0#################
    config=Config('config.txt')
    flag=0
    if config.get('path0') and os.path.exists(config.path0):
        k=input('已检测到您曾使用过路径：{}，是否继续使用该路径？[y/n]'.format(config.path0))
        if k[0] in 'Yy':
            flag=1
            path0=config.path0
    if not flag:
        while True:
            path0=input('请设置存储路径：')
            if os.path.exists(path0):
                print('设置成功')
                break
            else:
                print('路径不存在')
    config.path0=path0
    config.save()
    #####################################
    while True:
        while True:
            lid=input('请输入课程号：')
            #############Test###############
            if lid=='test':
                lid='1001541001'
            ################################
            if getname(lid):
                print('课程名为：'+getname(lid))
                k=input('请核实课程号是否正确[y/n]')
                if k and k[0] in 'Yy':
                    break
            else:
                print('课程不存在！')
            
        w=[]
        for i in tree():
            w.append(i[0])
            print(i[0])
        while True:
            k=input('请选择周次（也可按照"起始-结束"这样的格式输入，0为全部下载）')
            if k=='0':
                week=list(range(1,len(w)+1))
                break
            elif re.search(r'\d+-\d+',k):
                se=re.search(r'\d+-\d+',k).group(0).split('-')
                if 0<eval(se[0])<=len(w) and 0<eval(se[1])<=len(w):
                    week=list(range(eval(se[0]),eval(se[1])+1))
                    break
                else:
                    print('请输入课程范围内的数字')
            elif re.match(r'\d+$',k):
                if 0<eval(k)<=len(w):
                    week=[eval(k)]
                    break
                else:
                    print('请输入课程范围内的数字')
            else:
                print('输入错误！')
        while True:
            k=input('请选择需要下载的课件("video","pdf","all")')
            if k in ["video","pdf","all"]:
                tp=k
                break
            else:
                print('输入错误！')
        sharpness='sd'
        if tp in ["video","all"]:
            while True:
                k=input('请选择视频清晰度(标清"sd",高清"hd",超高清"shd")')
                if k in ['sd','hd','shd']:
                    sharpness=k
                    break
                else:
                    print('输入错误！')
        urls=load_urls(week,tp,sharpness)
        
        #import mul_process_package         #for_多进程打包
        #multiprocessing.freeze_support()  #for_多进程打包
        pool=Pool(5)                     #同时启动的进程数
        for url in urls:
            glo=[lid,m,path0]
            pool.apply_async(download, args=(url,glo))
        #pool.map(download,urls)
        pool.close()
        pool.join()
        '''for url in urls:
            download(url)'''
        print('已全部下载完成！')
        ct=input('是否继续下载？[y/n]')
        if ct and ct[0] in 'Nn':
            break
    input('Press <Enter>')





