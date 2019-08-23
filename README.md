# mooc-dl

![python 3.6.7](https://img.shields.io/badge/python-3.6.7-green?style=flat-square&logo=python)

本程序提供一键下载中国大学MOOC全课件功能，仅供学习使用，版权归中国大学 MOOC 所有，不用于任何商业用途

迫于强迫症，时隔近一年，我最终还是抽出几个小时重写了下，但是原来的各种复杂功能就不实现了，只保留其中主要的 API ，实现基本功能，旧版本见 `branch/v1`

基于 [pynotex](https://github.com/SigureMo/notev/tree/master/Codes/pynotex) 快速开发，主要作为 `course-clawer/icourse163` 备用接口（也许哪天电脑端的接口不那么好爬了）

# Usage

在运行之前请确保安装 Python3.5 及以上版本，并安装依赖

``` bash
pip install -r requirements.txt
```

之后在 `config.json` 中对一些参数进行配置就可以使用啦（登录只支持爱课程账号，因为其他的做起来太复杂，如果嫌注册太麻烦，直接使用这里放的共享账号就好）

``` json
{
  "username": "<icourse_user_name>",
  "password": "<icourse_password>",
  "resolution": <resolution_level>,
  "root": <root_dir>,
  "num_thread": <num_thread>,
  "segment_size": <segment_size>
}
```

下载时，只需要以网址作为参数传入即可

``` bash
python mooc-dl.py https://www.icourse163.org/course/ZJU-93001?tid=1003997005
```

# Recommendation

[Course Crawler(Forked from Foair/course-crawler)](https://github.com/SigureMo/course-crawler) 支持更多的课程与资源类型~
