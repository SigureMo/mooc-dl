from Easyload import *
if __name__=='__main__':
    #################login###################
    from config import Config
    config=Config('config.txt','$')
    mob_token=gettogen(config.username,config.passwd)[0]
    ##################root#################
    root=config.root
    #####################################
    cids=[
        '1001944005',#材科基
        '1001734003',#物化2
        '1001734002',#物化1
        '268001',#python
        '1001542001',#java1
        '1001527001',#组原下
        '1001871001',#python数据可视化
        '93001',#数据结构
        '1002536002',#tensorflow
        '1001870001',#python spider
        '1002253024',#web
        '154005',#computer network
        '309001',#组原上
        '1001571004',#computer OS
        '1001541001',#java0
        ]
    for cid in cids:
        flag=0
        while not flag:
            try:
                courseinfo=get_courseinfo(cid,mob_token)
                results=courseinfo.get('results')
                courseDto=results.get('courseDto')#课程信息
                cid=courseDto.get('id')#1001542001
                coursename=courseDto.get('name')#"面向对象程序设计——Java语言"
                schoolName=courseDto.get('schoolName')#"浙江大学"
                tid=courseDto.get('currentTermId')#1002776001
                print('开始下载订阅课程 {} '.format(coursename))
                flag=1

            except:
                flag=0
                print('噫，我没找到这个课程！')
            
        chapters=courseinfo.get('results').get('termDto').get('chapters')

        weeknum=list(range(len(chapters)))

        loadtype=[1,3,4]

        sharpness='shd'

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
                        	+unit.get('name'))
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
        print('{}的更新内容已下载完成'.format(coursename))
    print('已全部下载完成……')
    input('Press <Enter>')
