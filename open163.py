import requests
import time
import xml.dom.minidom

from bs4 import BeautifulSoup
from xml.dom.minidom import parse

try:
    from Crypto.Cipher import AES # 把site-package下的crypto改为Crypto就好
except:
    from crypto.Cipher import AES # pip install pycryptodome

def open_decrypt(hex_string, t):
    """
    方法来源：src/com/netease/openplayer/util/CryptoUtil.as
    """
    CRYKey = {1: b"4fxGZqoGmesXqg2o", 2: b"3fxVNqoPmesAqg2o"}
    aes = AES.new(CRYKey[t], AES.MODE_ECB)
    return str(aes.decrypt(bytes.fromhex(hex_string)),encoding='gbk',errors="ignore").replace('\x08','').replace('\x06', '')

def get_courses(url):
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
    video_info = url.replace('.html', '').split('/')[-1]
    xml_url = 'http://live.ws.126.net/movie/' + video_info[-2] + '/' + video_info[-1] + '/2_' + video_info + '.xml'
    res = requests.get(xml_url)
    res.encoding = 'gbk'
    return res.text

def xml2dict(text):
    def xmlnode2string(xml_node):
        tag_name = xml_node.tagName
        return xml_node.toxml('utf8').decode().replace('<{}>'.format(tag_name),'').replace('</{}>'.format(tag_name),'')
    
    def get_hex_urls(xml_node):
        hex_urls_dict = {}
        for node in xml_node.childNodes:
            hex_urls_list = []
            for url_hex_node in node.childNodes:
                hex_urls_list.append(xmlnode2string(url_hex_node))
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
    方法来源：src/com/netease/openplayer/model/OpenMovieData.as
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
    for video_url, video_name in get_courses(url):
        print(video_name)
        video_url, subs, ext = parse_url(xml2dict(get_xml(video_url)))
        with open(video_name + '.' +ext, 'wb') as f:
            f.write(requests.get(video_url).content)
        for lan, srt_url in subs.items():
            with open(video_name + '[' + lan + ']' + '.srt', 'wb') as f:
                f.write(requests.get(srt_url).content)
                
url = 'http://open.163.com/special/opencourse/cs50.html'
url = 'http://open.163.com/special/lectureroncomputerscience/'
url = 'http://open.163.com/special/opencourse/closereadingcooperative.html'
download(url)
videourl = 'http://live.ws.126.net/movie/U/R/2_M6U6LS8CV_M6U6MHDUR.xml'
#url = 'http://open.163.com/movie/2010/3/U/R/M6U6LS8CV_M6U6MHDUR.html'
#print(parse_url(xml2dict(get_xml(url))))
#print(open_decrypt('0A574162ED90BC133D30DEC31AB9EF3EFD96E84FCC48F2902B9CEED9E67AC6AF79502F487FB273967EB29928B018BB06803C88F005284D6154EE156601238A852694C636267E063B6724235AA9426147', 2))
