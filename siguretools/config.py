import os

class Config():
    def __init__(self,path,sep=" 's value is "):
        self._path=path
        self._sep=sep
        if not os.path.exists(path):
            with open(self._path,'w',encoding='utf-8',newline='\r\n') as f:
                f.write('')
        with open(self._path,'r',encoding='utf-8',newline='\r\n') as f:
            for line in f:
                kv=line.replace('\n','').replace('\r','').split(self._sep)
                if len(kv)==2 and kv[0]:
                    vars(self)[kv[0]]=kv[1]#将cfg的str变成属性
    def save(self):
        with open(self._path,'w',encoding='utf-8',newline='\r\n') as f:
            cfg=[]
            for k in vars(self):
                if k=='_path' or k=='_sep':
                    continue
                if isinstance(vars(self)[k],str):
                    cfg.append([k,vars(self)[k]])
                else:
                    try:
                        cfg.append([k,str(vars(self)[k])])
                    except:
                        print('属性{}无法保存'.format(k))
            for item in cfg:#保存所有属性，包括新添加的
                f.write(self._sep.join(item)+'\n')

    def get(self,attr,default=None):
        if hasattr(self,attr):
            return vars(self)[attr]
        else:
            return default

    def set(self,attr,value):
        vars(self)[attr]=value

if __name__=='__main__':
    config=Config('config.txt')#初始化配置文件
    config.path=os.path.expanduser("~")+os.sep+'Desktop'\
                 +os.sep+'test'#设置属性
    print(config.get('path','Please setting a path!'))#获取属性值
    config.save()#保存
    config=Config('config.txt')#再次读取配置文件
    del config.path#删除属性值
    config.save()#重新保存

'''
获取属性时请尽量使用get方法，不然如果没有该属性容易报错
尽量保存为str格式，就算是数字也尽量如此
可通过Config('config','mysep')自定义分隔符
可使用del将属性值删除
'''
