from Easyload import *
from tools.config import Config

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

    mob_token=gettoken(config.username,config.passwd)[0]
    root=config.get(platform.system()+'Root')
    #####################################
    tids=[
        '1002700003',#人工智能实践：Tensorflow笔记
        '1002788142',#Web信息系统应用开发

        '1002644012',#计算机网络
        '1002784135',#计算机操作系统
        '1002654021',#数据结构
        '1002791028',#计算机组成原理（上）
        '1002790026',#计算机组成原理（下）

        '1002774001',#程序设计入门——C语言
        '1002775002',#C语言程序设计进阶

        '1002777001',#零基础学Java语言
        '1002776001',#面向对象程序设计——Java语言

        '1002788003',#Python语言程序设计
        '1002781006',#Python网络爬虫与信息提取
        '1002856007',#Python科学计算三维可视化
        '1001963002',#Python云端系统开发入门(old)
        '1001965001',#Python机器学习应用(old)
        '1001966001',#Python游戏开发入门(old)
        '1002239009',#Python数据分析与展示(old)
        ]
    tids = ['1002339003']
    for tid in tids:
        flag=0
        while not flag:
            try:
                courseinfo=get_courseinfo(tid,mob_token)
                results=courseinfo.get('results')
                courseDto=results.get('courseDto')#课程信息
                print(courseinfo)
                cid=courseDto.get('id')#1001542001
                coursename=courseDto.get('name')#"面向对象程序设计——Java语言"
                print('开始下载订阅课程 {} '.format(coursename))
                flag=1

            except:
                flag=0
                print('噫，我没找到这个课程！')
            
        chapters=courseinfo.get('results').get('termDto').get('chapters')

        weeknum=list(range(len(chapters)))###全部课程###

        loadtype=[1,3,4]###全部类型###

        sharpness='shd'###超清画质###

        print('获取链接中，很快就好哒！')
        coursewares=getcoursewares(courseinfo,root,mob_token,sharpness)
        print('下载进程召唤术...')
        general_view(courseinfo,root)        #课程概览
        playlist(coursename,coursewares,root)#播放列表
        ##########################单进程#################################
        for courseware in coursewares:
            courseware.download(weeknum,loadtype)
        ##########################check#################################
        #for courseware in coursewares:
        #    if  courseware.path and not os.path.exists(courseware.path):
        #        print('噫，{}刚才下载失败啦，我再试试，稍等下哈'.format(courseware.name))
        #        courseware.download(weeknum,loadtype)
        #print('{}的更新内容已下载完成'.format(coursename))
    print('已全部下载完成……')
    input('Press <Enter>')
