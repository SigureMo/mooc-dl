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
        open(path, 'w').close()
    return os.path.normpath(path)


def repair_filename(filename):
    """ 修复不合法的文件名 """
    def to_full_width_chr(matchobj):
        char = matchobj.group(0)
        full_width_char = chr(ord(char) + + ord('？') - ord('?'))
        return full_width_char
    # 路径非法字符，转全角
    regex_path = re.compile(r'[\\/:*?"<>|]')
    # 空格类字符，转空格
    regex_spaces = re.compile(r'\s+')
    # 不可打印字符，移除
    regex_non_printable = re.compile(
        r'[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        r'\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]')
    # 原有标号，移除
    regex_sort = re.compile(r'^[第一二三四五六七八九十\d]+[\s\d._\-章课节讲]*[.\s、\-]\s*\d*')

    filename = regex_path.sub(to_full_width_chr, filename)
    filename = regex_spaces.sub(' ', filename)
    filename = regex_non_printable.sub('', filename)
    filename = regex_sort.sub('', filename)
    filename = filename.strip()
    return filename


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


def size_format(size, ndigits=2):
    """ 输入数据字节数，与保留小数位数，返回数据量字符串 """
    flag = '-' if size < 0 else ''
    size = abs(size)
    units = ["Bytes", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "BB"]
    idx = len(units) - 1
    unit = ""
    unit_size = 0
    while idx >= 0:
        unit_size = 2 ** (idx * 10)
        if size >= unit_size:
            unit = units[idx]
            break
        idx -= 1
    return "{}{:.{}f} {}".format(flag, size/unit_size, ndigits, unit)
