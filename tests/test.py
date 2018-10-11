from Easyload import *
from siguretools import config
config=Config('data/config.txt','$')
mob_token=gettoken(config.username,config.passwd)[0]
root=config.get(platform.system()+'Root')
courseinfo=get_courseinfo(1002777001,mob_token)
print(courseinfo)
input()
