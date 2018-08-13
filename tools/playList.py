import os

root = '.'
mode = 'RP'
s = ''
for dirpath, dirnames, filenames in os.walk(root):
    for filename in filenames:
        if os.path.splitext(filename)[-1] in ['.mp4', '.flv', '.rm', '.rmvb', '.3gp', '.avi', '.mpeg', '.mpg', '.mkv', '.dat', ',asf', '.wmv', '.mov', '.ogg', '.ogm',]:
            path = dirpath + os.sep + filename + '\n'
            if mode == 'RP':
                path = path.replace(root + os.sep, '')
            s += path
with open(root+os.sep+'Playlist.m3u','w',encoding='utf-8') as f:
    f.write(s)
input('已成功生成播放列表')
        
