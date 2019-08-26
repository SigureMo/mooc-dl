import os
import re


class Task():
    """任务对象"""

    def __init__(self, func, args=(), kw={}):
        """接受函数与参数以初始化对象"""

        self.func = func
        self.args = args
        self.kw = kw

    def run(self):
        """执行函数
        同步函数直接执行并返回结果，异步函数返回该函数
        """

        result = self.func(*self.args, **self.kw)
        return result


class ClassicFile(object):
    """典型文件（UTF-8 编码的文件）类

    属性
        _f：文件指针；
        file：文件名或文件路径。
    """

    def __init__(self, path):
        """传入一个文件名或路径，然后打开文件"""

        self._f = open(path, 'w', encoding='utf_8')
        self.path = path

    def __del__(self):
        """关闭文件，并将文件号和文件名都清空"""

        self._f.close()
        del self._f
        del self.path

    def flush(self):
        """刷新缓存，写入文件"""
        self._f.flush()

    def write_string(self, string):
        """向对象中打开的文件写入字符串，会自动加入换行"""

        self._f.write(string + '\n')


def touch_dir(path):
    """ 若文件夹不存在则新建，并返回标准路径 """
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.normpath(path)


def touch_file(path):
    """ 若文件不存在则新建，并返回标准路径 """
    if not os.path.exists(path):
        os.open(path, 'w').close()
    return os.path.normpath(path)


def repair_filename(filename):
    """ 修复不合法的文件名 """
    regex_path = re.compile(r'[\\/:*?"<>|]')
    return regex_path.sub('', filename)


def get_size(path):
    """ 获取文件夹或文件的字节数 """
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        size = 0
        for subpath in os.listdir(path):
            size += get_size(os.path.join(path, subpath))
        return size
    else:
        return 0


def size_format(size):
    """ 输入数据字节数，返回数据字符串 """
    flag = '-' if size < 0 else ''
    size = abs(size)
    if size >= 2 ** 90:
        return '{}{:.2f} BB'.format(flag, size / 2**90)
    elif size >= 2 ** 80:
        return '{}{:.2f} YB'.format(flag, size / 2**80)
    elif size >= 2 ** 70:
        return '{}{:.2f} ZB'.format(flag, size / 2**70)
    elif size >= 2 ** 60:
        return '{}{:.2f} EB'.format(flag, size / 2**60)
    elif size >= 2 ** 50:
        return '{}{:.2f} PB'.format(flag, size / 2**50)
    elif size >= 2 ** 40:
        return '{}{:.2f} TB'.format(flag, size / 2**40)
    elif size >= 2 ** 30:
        return '{}{:.2f} GB'.format(flag, size / 2**30)
    elif size >= 2 ** 20:
        return '{}{:.2f} MB'.format(flag, size / 2**20)
    elif size >= 2 ** 10:
        return '{}{:.2f} kB'.format(flag, size / 2**10)
    else:
        return '{}{:.2f} Bytes'.format(flag, size)
