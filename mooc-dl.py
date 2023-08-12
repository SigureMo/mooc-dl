import hashlib
import re
import os
import sys
import time
import argparse

from urllib.parse import urlencode

from utils.crawler import Crawler
from utils.config import Config
from utils.common import repair_filename, touch_dir
from utils.playlist import Dpl
from utils.downloader import FileManager
from utils.ffmpeg import FFmpeg

spider = Crawler()
spider.trust_env = False
VIDEO, PDF, RICH_TEXT = 1, 3, 4
COURSEWARE = {VIDEO: "Video", PDF: "PDF", RICH_TEXT: "Rich_text"}

headers = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; PCT-AL10 Build/HUAWEIPCT-AL10)",
    "edu-app-channel": "ucmooc_offical",
    "edu-app-type": "android",
    "edu-app-version": "4.19.0",
}
spider.headers.update(headers)
CONFIG = Config()


def handle_args(config):
    parser = argparse.ArgumentParser(description="中国大学 MOOC 下载器")
    parser.add_argument("-u", "--username", type=str, default=None)
    parser.add_argument("-p", "--password", type=str, default=None)
    parser.add_argument("-q", "--resolution", type=int, choices=[0, 1, 2], default=None)
    parser.add_argument("-d", "--root", type=str, default=None)
    parser.add_argument("-n", "--num_thread", type=int, default=None)
    parser.add_argument("-w", "--overwrite", action="store_true")
    parser.add_argument("-tp", "--file-path-template", type=str, default=None)
    parser.add_argument("--range", type=str, default=None)
    parser.add_argument("--file-types", type=str, default=None)
    parser.add_argument("--use-ffmpeg", action="store_true")
    parser.add_argument("url", type=str)

    def _parse_range(range_str):
        INF = 999
        if "~" not in range_str:
            range_str = f"{range_str}~{range_str}"
        start, end = range_str.split("~")
        # 允许 a.b.c~ 或者 ~a.b.c 甚至 ~
        start = start if start else "0.0.0"
        end = end if end else f"{INF}.{INF}.{INF}"
        # 允许 a.b~c，自动补零为 a.b.0~c.INF.INF
        start = start.split(".")
        start = list(map(lambda x: int(x), start))
        start = start + (3 - len(start)) * [0]
        end = end.split(".")
        end = list(map(lambda x: int(x), end))
        end = end + (3 - len(end)) * [INF]
        return {
            "start": start,
            "end": end,
        }

    def _parse_file_types(file_types_str):
        file_types = file_types_str.split(",").strip()
        file_types = list(map(lambda x: int(x), file_types))
        return file_types

    args = parser.parse_args()
    if args.username is not None:
        config["username"] = args.username
    if args.password is not None:
        config["password"] = args.password
    if args.root is not None:
        config["root"] = args.root
    if args.resolution is not None:
        config["resolution"] = args.resolution
    if args.num_thread is not None:
        config["num_thread"] = args.num_thread
    if args.overwrite:
        config["overwrite"] = True
    if args.file_path_template is not None:
        config["file_path_template"] = args.file_path_template
    if args.range is not None:
        config["range"] = _parse_range(args.range)
    if args.file_types is not None:
        config["file_types"] = _parse_file_types(args.file_types)
    if args.use_ffmpeg:
        config["use_ffmpeg"] = True

    return args.url


def login(username, password):
    """登录获取 token"""
    pd = hashlib.md5()
    pd.update(password.encode("utf-8"))
    passwd = pd.hexdigest()
    data = {
        "username": username,
        "passwd": passwd,
        "mob-token": "",
    }
    res = spider.post("http://www.icourse163.org/mob/logonByIcourse", headers=headers, data=data)
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
    """获取完整课程信息"""
    data = {
        "tid": tid,
        "mob-token": token,
    }
    url = "https://www.icourse163.org/mob/course/courseLearn/v1"
    res = spider.post(url, data=data)
    return res.json()


def get_summary(url):
    """从课程主页面获取信息"""

    url = url.replace("learn/", "course/")
    res = spider.get(url).text

    term_match = re.search(r'termId : "(\d+)"', res)
    if not term_match:
        print("无法获取课程信息！")
        sys.exit(1)
    term_id = term_match.group(1)
    names = re.findall(r'name:"(.+)"', res)
    course_name = " - ".join(names)
    # term_ids = re.findall(r'id : "(\d+)",\ncourse', res)

    return term_id, repair_filename(course_name)


def parse_resource(resource, token):
    """解析课件链接、参数"""
    if resource[0] == VIDEO:
        _, file_path, unit_id, content_id = resource

        # get signature
        data = {"bizType": 1, "mob-token": token, "bizId": unit_id, "contentType": 1}

        while True:
            res = spider.post(
                "https://www.icourse163.org/mob/j/v1/mobileResourceRpcBean.getResourceToken.rpc", data=data
            )
            if res.json()["results"] is not None:
                break
            time.sleep(0.5)
        signature = res.json()["results"]["videoSignDto"]["signature"]

        # get urls
        data = {"enVersion": 1, "clientType": 2, "mob-token": token, "signature": signature, "videoId": content_id}
        res = spider.post("https://vod.study.163.com/mob/api/v1/vod/videoByNative", data=data)
        videos = res.json()["results"]["videoInfo"]["videos"]

        # select quality
        resolutions = [3, 2, 1]
        resolution = resolutions[CONFIG["resolution"] :] + list(reversed(resolutions[: CONFIG["resolution"]]))
        for reso in resolution:
            for video in videos:
                if video["quality"] == reso:
                    video_url = video["videoUrl"]
                    break
            else:
                continue
            break

        # download subtitle
        srt_info = res.json()["results"]["videoInfo"]["srtCaptions"]
        if srt_info:
            for srt_item in srt_info:
                srt_path = os.path.splitext(file_path)[0] + "_" + srt_item["languageCode"] + ".srt"
                srt_url = srt_item["url"]
                spider.download_bin(srt_url, srt_path)

        return video_url, file_path, None

    elif resource[0] == PDF:
        _, file_path, unit_id, content_id = resource

        api_url = "http://www.icourse163.org/mob/course/learn/v1"
        data = {"t": 3, "cid": content_id, "unitId": unit_id, "mob-token": token}
        res = spider.post(api_url, data=data)
        pdf_url = res.json()["results"]["learnInfo"]["textOrigUrl"]
        return pdf_url, file_path, None

    elif resource[0] == RICH_TEXT:
        _, file_path, json_content = resource

        api_url = "http://www.icourse163.org/mob/course/attachment.htm"
        data = json_content
        return api_url, file_path, data


def get_resource(term_id, token, file_types=[VIDEO, PDF, RICH_TEXT]):
    """获取课件信息"""
    resource_list = []

    course_info = get_courseinfo(term_id, token)
    for chapter_num, chapter in enumerate(course_info.get("results").get("termDto").get("chapters")):
        for lesson_num, lesson in enumerate(chapter.get("lessons") if chapter.get("lessons") is not None else []):
            for unit_num, unit in enumerate(lesson.get("units")):
                if unit["contentType"] not in file_types:
                    continue
                courseware_num = (chapter_num + 1, lesson_num + 1, unit_num + 1)
                if courseware_num < tuple(CONFIG["range"]["start"]) or courseware_num > tuple(CONFIG["range"]["end"]):
                    continue
                file_path = CONFIG["file_path_template"].format(
                    base_dir=base_dir,
                    sep=os.path.sep,
                    type=COURSEWARE.get(unit["contentType"], "Unknown"),
                    cnt_1=get_section_num(courseware_num, level=1),
                    cnt_2=get_section_num(courseware_num, level=2),
                    cnt_3=get_section_num(courseware_num, level=3),
                    chapter_name=repair_filename(chapter["name"]),
                    lesson_name=repair_filename(lesson["name"]),
                    unit_name=repair_filename(unit["name"]),
                )
                touch_dir(os.path.dirname(file_path))

                if unit["contentType"] == VIDEO:
                    ext = ".mp4"
                    file_path += ext
                    playlist.write_path(file_path)
                    resource_list.append((VIDEO, file_path, unit["id"], unit["contentId"]))
                elif unit["contentType"] == PDF:
                    file_path += ".pdf"
                    resource_list.append((PDF, file_path, unit["id"], unit["contentId"]))
                elif unit["contentType"] == RICH_TEXT:
                    if unit.get("jsonContent"):
                        json_content = eval(unit["jsonContent"])
                        file_path = CONFIG["file_path_template"].format(
                            base_dir=base_dir,
                            sep=os.path.sep,
                            type="File",
                            cnt_1=get_section_num(courseware_num, level=1),
                            cnt_2=get_section_num(courseware_num, level=2),
                            cnt_3=get_section_num(courseware_num, level=3),
                            chapter_name=repair_filename(chapter["name"]),
                            lesson_name=repair_filename(lesson["name"]),
                            unit_name=repair_filename(os.path.splitext(json_content["fileName"])[0])
                            + os.path.splitext(json_content["fileName"])[1],
                        )
                        touch_dir(os.path.dirname(file_path))

                        resource_list.append((RICH_TEXT, file_path, json_content))

    return resource_list


def get_section_num(courseware_num, level=3, sep=".", template="{:d}"):
    """根据等级获取课件的标号"""
    return sep.join(list((map(lambda x: template.format(x), courseware_num[:level]))))


def merge(merge_list, ffmpeg=None):
    """合并待合并列表"""
    for i, merge_file in enumerate(merge_list):
        print("merging {}/{}".format(i, len(merge_list)), end="\r")
        file_path = merge_file["target"]
        if ffmpeg is not None:
            ffmpeg.join_videos(merge_file["segments"], file_path)
        else:
            with open(file_path, "wb") as fw:
                for ts_path in merge_file["segments"]:
                    with open(ts_path, "rb") as fr:
                        fw.write(fr.read())
        for ts_path in merge_file["segments"]:
            os.remove(ts_path)


if __name__ == "__main__":
    url = handle_args(CONFIG)
    root = CONFIG["root"]
    num_thread = CONFIG["num_thread"]

    # 登录并获取信息
    token = login(CONFIG["username"], CONFIG["password"])
    match_obj = re.match(r"https?://www.icourse163.org(/spoc)?/(course|learn)/\w+-(\d+)", url)
    if match_obj is None:
        print("无法解析的链接：{}，请检查链接是否错误……".format(url))
        sys.exit(1)

    term_id, course_name = get_summary(url)
    course_id = match_obj.group(3)
    print(course_name)
    print(course_id)

    # 创建必要环境
    base_dir = touch_dir(os.path.join(root, course_name))
    playlist = Dpl(os.path.join(base_dir, "Playlist.dpl"))

    # 获取资源列表
    resource_list = get_resource(term_id, token, file_types=CONFIG["file_types"])

    # 解析资源
    resources = []
    merge_list = []
    for i, resource in enumerate(resource_list):
        print("parse_resource {}/{}".format(i, len(resource_list)), end="\r")
        url, file_path, params = parse_resource(resource, token)
        # 过滤掉已经下载的资源
        if os.path.exists(file_path) and not CONFIG["overwrite"]:
            print("[info] {} already exists!".format(file_path))
            continue
        if ".m3u8" in url:
            merge_file = {"target": file_path, "segments": []}
            id = 0
            m3u8_text = spider.get(url).text
            for line in m3u8_text.split("\n"):
                if line.endswith(".ts"):
                    ts_url = "/".join(url.split("/")[:-1]) + "/" + line
                    ts_path = "{}{:03d}.ts".format(file_path.rstrip(".mp4"), id)
                    resources.append((ts_url, ts_path))
                    id += 1
                    merge_file["segments"].append(ts_path)
            merge_list.append(merge_file)

        else:
            if params is not None:
                url += "?" + urlencode(params)
            resources.append((url, file_path))

    # 将资源（片段）分发至线程池，并开始下载
    manager = FileManager(num_thread, spider=spider, overwrite=CONFIG["overwrite"])
    manager.dispense_resources(resources)
    manager.run()

    # 启动（主线程）监控器，等待下载完成
    manager.monitoring()

    # 合并所有 ts 片段
    os.chdir(base_dir)    # 工作目录和目标可能不在一个盘符
    ffmpeg = None
    if CONFIG["use_ffmpeg"]:
        ffmpeg = FFmpeg()
    merge(merge_list, ffmpeg=ffmpeg)

    print("\nDone!")
