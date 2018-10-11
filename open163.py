<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""网易公开课"""

import time
import xml.dom.minidom
import requests

from bs4 import BeautifulSoup

try:
    from Crypto.Cipher import AES # 把site-package下的crypto改为Crypto就好
except:
    from crypto.Cipher import AES # pip install pycryptodome

def open_decrypt(hex_string, t):
    """
    Input：
        hex_string：String：xml中获得的未解析的十六进制字符串
        t：Integer：xml中获得的'encrypt'
    Output：
        String：使用aes解密后得到的url
    方法来源：src/com/netease/openplayer/util/CryptoUtil.as
    """
    CRYKey = {1: b"4fxGZqoGmesXqg2o", 2: b"3fxVNqoPmesAqg2o"}
    aes = AES.new(CRYKey[t], AES.MODE_ECB)
    return str(aes.decrypt(bytes.fromhex(hex_string)),encoding='gbk',errors="ignore").replace('\x08','').replace('\x06', '')

def get_courses(url):
    """
    Input：
        url ：String：课程主网页url
    Output：
        List：[(视频网页url, 视频名), ...]
    """
    
    res = requests.get(url)
    soup=BeautifulSoup(res.text,'html.parser')
    listrow = soup.find('div', class_='listrow')
    links = []

    names = soup.find('p', class_='bread')
    organization = names.find_all('a', class_='f-c9')[0].string.strip()
    course = names.find_all('a', class_='f-c9')[1].string.strip()
    print(organization,course)
    for item in listrow.find_all('div',class_='item'):
        p = item.find('p', class_='f-thide')
        if p.find('a'):
            a = p.find('a')
            links.append((a.get('href'), a.string))
        else:
            links.append((url, p.string.split(']')[-1]))
    return links

def get_courses(url):
    """
    Input：
        url ：String：课程主网页url
    Output：
        List：[(视频网页url, 视频名), ...]
    """
    res = requests.get(url)
    soup=BeautifulSoup(res.text,'html.parser')
    list1 = soup.find('table', id='list1')
    tds = list1.find_all('td', class_="u-ctitle")
    links = []
    for td in tds:
        a = td.find('a')
        links.append((a.get('href'), a.string))
    return links

def get_xml(url):
    """
    Input：
        url ：String：视频网页url
    Output：
        String：xml文本
    Tips：在浏览器抓到的js里找了半天也没找到那个2_到底怎么来的，看了下基本都是2_就直接用了，也许是像v1、v2这样的等级接口？
    """
    video_info = url.replace('.html', '').split('/')[-1]
    xml_url = 'http://live.ws.126.net/movie/' + video_info[-2] + '/' + video_info[-1] + '/2_' + video_info + '.xml'
    res = requests.get(xml_url)
    res.encoding = 'gbk'
    return res.text

def xml2dict(text):
    """
    Input：
        url ：String：xml文本
    Output：
        Dict：将xml文本解析成dict
    """
    def xmlnode2string(xml_node):
        tag_name = xml_node.tagName
        return xml_node.toxml('utf8').decode().replace('<{}>'.format(tag_name),'').replace('</{}>'.format(tag_name),'')
    
    def get_hex_urls(xml_node):
        hex_urls_dict = {}
        for node in xml_node.childNodes:
            hex_urls_list = []
            for url_hex_node in node.childNodes:
                hex_urls_list.append(xmlnode2string(url_hex_node))# 这个地方不太严谨，好几个url，不知道拿哪个好了，姑且用了最后一个
            hex_urls_dict[node.tagName] = hex_urls_list
        return hex_urls_dict
    
    data = {
        'name': '',
        'encrypt': 1,
        'flvurl': {'hd': [],},
        'flvurl_origin': {'hd': [],},
        'mp4url': {'HD': [],},
        'mp4url_origin': {'HD': [],},
        'protoVersion': 1,
        'useMp4': 1,
        'subs': {},
        }
    sub_dict = {'中文': 'zh-cn', '英文': 'en'}
    DOMTree = xml.dom.minidom.parseString(text)
    data['name'] = xmlnode2string(DOMTree.getElementsByTagName('title')[0])
    data['encrypt'] = int(xmlnode2string(DOMTree.getElementsByTagName('encrypt')[0]))
    data['flvurl'] = get_hex_urls(DOMTree.getElementsByTagName('flvUrl')[0])
    data['flvurl_origin'] = get_hex_urls(DOMTree.getElementsByTagName('flvUrlOrigin')[0])
    data['mp4url'] = get_hex_urls(DOMTree.getElementsByTagName('playurl')[0])
    data['mp4url_origin'] = get_hex_urls(DOMTree.getElementsByTagName('playurl_origin')[0])
    data['protoVersion'] = int(xmlnode2string(DOMTree.getElementsByTagName('protoVersion')[0]))
    data['useMp4'] = int(xmlnode2string(DOMTree.getElementsByTagName('useMp4')[0]))
    for srt_node in DOMTree.getElementsByTagName('subs')[0].getElementsByTagName('sub'):
        data['subs'][sub_dict[xmlnode2string(srt_node.getElementsByTagName('name')[0])]] = xmlnode2string(srt_node.getElementsByTagName('url')[0])
    return data

def parse_url(data):
    """
    Input：
        data ：Dict：xml解析所得dict
    Output：
        Tuple：(解析所得视频url, 字幕信息, 视频扩展名)
    方法来源：src/com/netease/openplayer/model/OpenMovieData.as
    Tips：不知道为啥，按照as里面写的解析，格式明明应该是对的，但是测试cs50（测试用例的第一个url）下的所有的url最后解析都是flv，所以最后ext用url校正了下
    """
    k = ''
    if data['useMp4'] == 1:
        ext = 'mp4'
    else:
        ext = 'flv'
    k += ext + 'url'
    if data['protoVersion'] == 2:
        k += '_origin'
    for hex_strings in data[k].values():
        hex_string = hex_strings[0]
    video_url = open_decrypt(hex_string, data['encrypt'])
    ext = video_url.split('.')[-1]
    return video_url, data['subs'], ext



def download(url):
    """
    Input：
        url：String：课程主网页url
    """
    for video_url, video_name in get_courses(url):
        print(video_name)
        video_url, subs, ext = parse_url(xml2dict(get_xml(video_url)))
        with open(video_name + '.' +ext, 'wb') as f:
            f.write(requests.get(video_url).content)
        for lan, srt_url in subs.items():
            with open(video_name + '[' + lan + ']' + '.srt', 'wb') as f:
                f.write(requests.get(srt_url).content)
# 测试用例   
url = 'http://open.163.com/special/opencourse/cs50.html'
url = 'http://open.163.com/special/lectureroncomputerscience/'
url = 'http://open.163.com/special/opencourse/closereadingcooperative.html'
url = 'http://open.163.com/special/cuvocw/chuantongzhengzhi.html'
url = 'http://open.163.com/special/Khan/trigonometry.html'
#url = 'http://open.163.com/movie/2016/1/3/3/MBBL91A3O_MBBL9CG33.html'
download(url)
#videourl = 'http://live.ws.126.net/movie/U/R/2_M6U6LS8CV_M6U6MHDUR.xml'
#url = 'http://open.163.com/movie/2010/3/U/R/M6U6LS8CV_M6U6MHDUR.html'
#print(parse_url(xml2dict(get_xml(url))))
#print(open_decrypt('0A574162ED90BC133D30DEC31AB9EF3EFD96E84FCC48F2902B9CEED9E67AC6AF79502F487FB273967EB29928B018BB06803C88F005284D6154EE156601238A852694C636267E063B6724235AA9426147', 2))
=======
# -*- coding: utf-8 -*-
"""网易公开课"""

import time
import xml.dom.minidom
import requests

from bs4 import BeautifulSoup

try:
    from Crypto.Cipher import AES # 把site-package下的crypto改为Crypto就好
except:
    from crypto.Cipher import AES # pip install pycryptodome

def open_decrypt(hex_string, t):
    """
    Input：
        hex_string：String：xml中获得的未解析的十六进制字符串
        t：Integer：xml中获得的'encrypt'
    Output：
        String：使用aes解密后得到的url
    方法来源：src/com/netease/openplayer/util/CryptoUtil.as
    """
    CRYKey = {1: b"4fxGZqoGmesXqg2o", 2: b"3fxVNqoPmesAqg2o"}
    aes = AES.new(CRYKey[t], AES.MODE_ECB)
    return str(aes.decrypt(bytes.fromhex(hex_string)),encoding='gbk',errors="ignore").replace('\x08','').replace('\x06', '')

def get_courses(url):
    """
    Input：
        url ：String：课程主网页url
    Output：
        List：[(视频网页url, 视频名), ...]
    """
    
    res = requests.get(url)
    soup=BeautifulSoup(res.text,'html.parser')
    listrow = soup.find('div', class_='listrow')
    links = []

    names = soup.find('p', class_='bread')
    organization = names.find_all('a', class_='f-c9')[0].string.strip()
    course = names.find_all('a', class_='f-c9')[1].string.strip()
    print(organization,course)
    for item in listrow.find_all('div',class_='item'):
        p = item.find('p', class_='f-thide')
        if p.find('a'):
            a = p.find('a')
            links.append((a.get('href'), a.string))
        else:
            links.append((url, p.string.split(']')[-1]))
    return links

def get_courses(url):
    """
    Input：
        url ：String：课程主网页url
    Output：
        List：[(视频网页url, 视频名), ...]
    """
    res = requests.get(url)
    soup=BeautifulSoup(res.text,'html.parser')
    list1 = soup.find('table', id='list1')
    tds = list1.find_all('td', class_="u-ctitle")
    links = []
    for td in tds:
        a = td.find('a')
        links.append((a.get('href'), a.string))
    return links

def get_xml(url):
    """
    Input：
        url ：String：视频网页url
    Output：
        String：xml文本
    Tips：在浏览器抓到的js里找了半天也没找到那个2_到底怎么来的，看了下基本都是2_就直接用了，也许是像v1、v2这样的等级接口？
    """
    video_info = url.replace('.html', '').split('/')[-1]
    xml_url = 'http://live.ws.126.net/movie/' + video_info[-2] + '/' + video_info[-1] + '/2_' + video_info + '.xml'
    res = requests.get(xml_url)
    res.encoding = 'gbk'
    return res.text

def xml2dict(text):
    """
    Input：
        url ：String：xml文本
    Output：
        Dict：将xml文本解析成dict
    """
    def xmlnode2string(xml_node):
        tag_name = xml_node.tagName
        return xml_node.toxml('utf8').decode().replace('<{}>'.format(tag_name),'').replace('</{}>'.format(tag_name),'')
    
    def get_hex_urls(xml_node):
        hex_urls_dict = {}
        for node in xml_node.childNodes:
            hex_urls_list = []
            for url_hex_node in node.childNodes:
                hex_urls_list.append(xmlnode2string(url_hex_node))# 这个地方不太严谨，好几个url，不知道拿哪个好了，姑且用了最后一个
            hex_urls_dict[node.tagName] = hex_urls_list
        return hex_urls_dict
    
    data = {
        'name': '',
        'encrypt': 1,
        'flvurl': {'hd': [],},
        'flvurl_origin': {'hd': [],},
        'mp4url': {'HD': [],},
        'mp4url_origin': {'HD': [],},
        'protoVersion': 1,
        'useMp4': 1,
        'subs': {},
        }
    sub_dict = {'中文': 'zh-cn', '英文': 'en'}
    DOMTree = xml.dom.minidom.parseString(text)
    data['name'] = xmlnode2string(DOMTree.getElementsByTagName('title')[0])
    data['encrypt'] = int(xmlnode2string(DOMTree.getElementsByTagName('encrypt')[0]))
    data['flvurl'] = get_hex_urls(DOMTree.getElementsByTagName('flvUrl')[0])
    data['flvurl_origin'] = get_hex_urls(DOMTree.getElementsByTagName('flvUrlOrigin')[0])
    data['mp4url'] = get_hex_urls(DOMTree.getElementsByTagName('playurl')[0])
    data['mp4url_origin'] = get_hex_urls(DOMTree.getElementsByTagName('playurl_origin')[0])
    data['protoVersion'] = int(xmlnode2string(DOMTree.getElementsByTagName('protoVersion')[0]))
    data['useMp4'] = int(xmlnode2string(DOMTree.getElementsByTagName('useMp4')[0]))
    for srt_node in DOMTree.getElementsByTagName('subs')[0].getElementsByTagName('sub'):
        data['subs'][sub_dict[xmlnode2string(srt_node.getElementsByTagName('name')[0])]] = xmlnode2string(srt_node.getElementsByTagName('url')[0])
    return data

def parse_url(data):
    """
    Input：
        data ：Dict：xml解析所得dict
    Output：
        Tuple：(解析所得视频url, 字幕信息, 视频扩展名)
    方法来源：src/com/netease/openplayer/model/OpenMovieData.as
    Tips：不知道为啥，按照as里面写的解析，格式明明应该是对的，但是测试cs50（测试用例的第一个url）下的所有的url最后解析都是flv，所以最后ext用url校正了下
    """
    k = ''
    if data['useMp4'] == 1:
        ext = 'mp4'
    else:
        ext = 'flv'
    k += ext + 'url'
    if data['protoVersion'] == 2:
        k += '_origin'
    for hex_strings in data[k].values():
        hex_string = hex_strings[0]
    video_url = open_decrypt(hex_string, data['encrypt'])
    ext = video_url.split('.')[-1]
    return video_url, data['subs'], ext



def download(url):
    """
    Input：
        url：String：课程主网页url
    """
    for video_url, video_name in get_courses(url):
        print(video_name)
        video_url, subs, ext = parse_url(xml2dict(get_xml(video_url)))
        with open(video_name + '.' +ext, 'wb') as f:
            f.write(requests.get(video_url).content)
        for lan, srt_url in subs.items():
            with open(video_name + '[' + lan + ']' + '.srt', 'wb') as f:
                f.write(requests.get(srt_url).content)
# 测试用例   
url = 'http://open.163.com/special/opencourse/cs50.html'
url = 'http://open.163.com/special/lectureroncomputerscience/'
url = 'http://open.163.com/special/opencourse/closereadingcooperative.html'
url = 'http://open.163.com/special/cuvocw/chuantongzhengzhi.html'
url = 'http://open.163.com/special/Khan/trigonometry.html'
#url = 'http://open.163.com/movie/2016/1/3/3/MBBL91A3O_MBBL9CG33.html'
download(url)
#videourl = 'http://live.ws.126.net/movie/U/R/2_M6U6LS8CV_M6U6MHDUR.xml'
#url = 'http://open.163.com/movie/2010/3/U/R/M6U6LS8CV_M6U6MHDUR.html'
#print(parse_url(xml2dict(get_xml(url))))
#print(open_decrypt('0A574162ED90BC133D30DEC31AB9EF3EFD96E84FCC48F2902B9CEED9E67AC6AF79502F487FB273967EB29928B018BB06803C88F005284D6154EE156601238A852694C636267E063B6724235AA9426147', 2))
>>>>>>> history
