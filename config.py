import os


class Config():
    def __init__(self,path):
        self._path=path
        if not os.path.exists(path):
            with open(self._path,'w',encoding='utf-8',newline='\r\n') as f:
                f.write('')
        with open(self._path,'r',encoding='utf-8',newline='\r\n') as f:
            for line in f:
                kv=line.replace('\n','').replace('\r','').split(sep)
                if len(kv)==2 and kv[0]:
                    vars(self)[kv[0]]=kv[1]#将cfg的str变成属性
    def save(self):
        with open(self._path,'w',encoding='utf-8',newline='\r\n') as f:
            cfg=[]
            for k in vars(self):
                if k=='_path':
                    continue
                if isinstance(vars(self)[k],str):
                    cfg.append([k,vars(self)[k]])
                else:
                    try:
                        cfg.append([k,str(vars(self)[k])])
                    except:
                        print('属性{}无法保存'.format(k))
            for item in cfg:#保存所有属性，包括新添加的
                f.write(sep.join(item)+'\n')

    def get(self,attr):
        if hasattr(self,attr):
            return vars(self)[attr]
        else:
            return None
sep='$'
'''
config=Config('config.txt')
config.path=1234
print(config.get('sdfas'))
config.save()
'''
'''
获取属性时请尽量使用get方法，不然如果没有该属性容易报错
'''
