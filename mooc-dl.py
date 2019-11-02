import json
import hashlib
import re
import os
import sys

from urllib.parse import urlencode
from bs4 import BeautifulSoup

from utils.crawler import Crawler
from utils.config import Config
from utils.thread import ThreadPool
from utils.common import Task, repair_filename, touch_dir, size_format
from utils.playlist import Dpl
from utils.segment_dl import FileManager

spider = Crawler()
VIDEO, PDF, RICH_TEXT = 1, 3, 4

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
    # 'edu-app-version': '3.17.1',
}
srt_types = ["zh-cn", "en"]
spider.headers.update(headers)
CONFIG = Config()


def login(username, password):
    """ 登录获取 token """
    pd = hashlib.md5()
    pd.update(password.encode('utf-8'))
    passwd = pd.hexdigest()
    headers = {
        'edu-app-type': 'android',
        'edu-app-version': '2.6.1'
        }
    data={
        'username': username,
        'passwd': passwd,
        'mob-token': ''
        }
    res = spider.post('http://www.icourse163.org/mob/logonByIcourse',
                    headers = headers,
                    data = data)
    result = res.json()
    code = result.get("status").get("code")
    if code == 0:
        return result.get("results").get("mob-token")
    elif code == 100:
        print("密码错误！")
        return None
    else:
        print("登录失败！")
        return None


def get_courseinfo(tid, token):
    """ 获取完整课程信息 """
    data = {
        'tid': tid,
        'mob-token': token
        }
    url = 'https://www.icourse163.org/mob/course/courseLearn/v1'
    res = spider.post(url, data=data)
    return res.json()


def get_summary(url):
    """从课程主页面获取信息"""

    url = url.replace('learn/', 'course/')
    res = spider.get(url).text

    term_id = re.search(r'termId : "(\d+)"', res).group(1)
    names = re.findall(r'name:"(.+)"', res)
    course_name = " - ".join(names)
    # term_ids = re.findall(r'id : "(\d+)",\ncourse', res)

    return term_id, course_name

def parse_resource(resource, token):
    """ 解析课件链接、参数 """
    if resource[0] == VIDEO:
        _, file_path, unit_id, content_id = resource

        # get signature
        data = {
            'bizType': 1,
            'mob-token': token,
            'bizId': unit_id,
            'contentType': 1
        }

        res = spider.post("https://www.icourse163.org/mob/j/v1/mobileResourceRpcBean.getResourceToken.rpc", data=data)
        signature = res.json()['results']['videoSignDto']['signature']

        # get urls
        data = {
            "enVersion": 1,
            "clientType": 2,
            "mob-token": token,
            "signature": signature,
            "videoId": content_id
        }
        res = spider.post('https://vod.study.163.com/mob/api/v1/vod/videoByNative', data=data)
        videos = res.json()['results']['videoInfo']['videos']

        # select quality
        resolutions = [3, 2, 1]
        resolution = resolutions[CONFIG['resolution']:] + list(reversed(resolutions[:CONFIG['resolution']]))
        for reso in resolution:
            for video in videos:
                if video['quality'] == reso:
                    video_url = video['videoUrl']
                    break
            else:
                continue
            break

        # SRT，暂未探索，先不解析
        # if srt_keys:
        #     data = {
        #         't': 1,
        #         'mob-token': token,
        #         'unitId': unit_id,
        #         'cid': content_id,
        #         }
        #     res = spider.post('https://www.icourse163.org/mob/course/learn/v1', data = data)
        #     for srt_key in res.json()['results']['learnInfo']['srtKeys']:
        #         srt_path = file_path[:-4] + "_" + srt_types[srt_key["lang"]] + ".srt"
        #         srt_url = srt_key['nosUrl']
        #         spider.download_bin(srt_url, srt_path)

        return video_url, file_path, data

    elif resource[0] == PDF:
        _, file_path, unit_id, content_id = resource

        api_url = 'http://www.icourse163.org/mob/course/learn/v1'
        data = {
            't': 3,
            'cid': content_id,
            'unitId': unit_id,
            'mob-token': token
        }
        res = spider.post(api_url, data = data)
        pdf_url = res.json()["results"]["learnInfo"]["textOrigUrl"]
        return pdf_url, file_path, None

    elif resource[0] == RICH_TEXT:
        _, file_path, json_content = resource

        api_url = 'http://www.icourse163.org/mob/course/attachment.htm'
        data = json_content
        return api_url, file_path, data


def get_resource(term_id, token):
    """ 获取课件信息 """
    resource_list = []

    course_info = get_courseinfo(term_id, token)
    for chapter_num, chapter in enumerate(course_info.get('results').get('termDto').get('chapters')):
        for lesson_num, lesson in enumerate(chapter.get('lessons')):
            for unit_num, unit in enumerate(lesson.get('units')):
                courseware_num = (chapter_num+1, lesson_num+1, unit_num+1)
                file_path = os.path.join(
                    base_dir,
                    get_section_num(courseware_num, level=1) + " " + repair_filename(chapter["name"]),
                    get_section_num(courseware_num, level=2) + " " + repair_filename(lesson["name"]),
                    get_section_num(courseware_num, level=3) + " " + repair_filename(unit["name"])
                )
                touch_dir(os.path.dirname(file_path))

                if unit['contentType'] == VIDEO:
                    ext = '.mp4'
                    file_path += ext
                    playlist.write_path(file_path)
                    resource_list.append((
                        VIDEO,
                        file_path,
                        unit['id'],
                        unit['contentId']
                    ))
                elif unit['contentType'] == PDF:
                    file_path += ".pdf"
                    resource_list.append((
                        PDF,
                        file_path,
                        unit['id'],
                        unit['contentId']
                    ))
                elif unit['contentType'] == RICH_TEXT:
                    if unit.get('jsonContent'):
                        json_content = eval(unit['jsonContent'])
                        file_path = os.path.join(
                            base_dir,
                            get_section_num(courseware_num, level=1) + " " + repair_filename(chapter["name"]),
                            get_section_num(courseware_num, level=2) + " " + repair_filename(lesson["name"]),
                            get_section_num(courseware_num, level=3) + " " + repair_filename(json_content["fileName"])
                        )
                        resource_list.append((
                            RICH_TEXT,
                            file_path,
                            json_content
                        ))

    return resource_list

def get_section_num(courseware_num, level=3):
    """ 根据等级获取课件的标号 """
    return ".".join(list((map(lambda x: str(x), courseware_num[: level]))))


if __name__ == "__main__":
    root = CONFIG["root"]
    num_thread = CONFIG["num_thread"]
    segment_size = CONFIG["segment_size"]
    url = sys.argv[1]

    # 登录并获取信息
    token = login(CONFIG["username"], CONFIG["password"])
    term_id, course_name = get_summary(url)
    course_id = re.match(r"https://www.icourse163.org/(course|learn)/\w+-(\d+)", url).group(2)
    print(course_name)
    print(course_id)

    # 创建必要环境
    base_dir = touch_dir(os.path.join(root, course_name))
    playlist = Dpl(os.path.join(base_dir, 'Playlist.dpl'))

    # 获取资源列表
    resource_list = get_resource(term_id, token)

    # 解析资源
    resources = []
    for i, resource in enumerate(resource_list):
        print("parse_resource {}/{}".format(i, len(resource_list)), end="\r")
        url, file_path, params = parse_resource(resource, token)
        if params is not None:
            url += "?" + urlencode(params)
        resources.append((url, file_path))

    # 将资源（片段）分发至线程池，并开始下载
    manager = FileManager(num_thread, segment_size, spider=spider)
    manager.dispense_resources(resources)
    manager.run()

    # 启动（主线程）监控器，等待下载完成
    manager.monitoring()
    print("\nDone!")
