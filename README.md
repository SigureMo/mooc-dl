# mooc-dl

![python 3.6.7](https://img.shields.io/badge/python-3.6.7-green?style=flat-square&logo=python)

本程序提供一键下载中国大学MOOC全课件功能，仅供学习使用，版权归中国大学 MOOC 所有，不用于任何商业用途

主要作为 `course-clawer/icourse163` 备用接口

近期中 M 视频接口全面变更为 m3u8 了，所以可以说必须要下载、合并了，所以 `course-crawler` 暂时不支持中 M 视频下载，要下载视频先用这个备用的吧，但是这里并不会做像 `course-crawler` 那么结构化的下载方式

- [ ] 暂未支持字幕
- [ ] 进度条体验不佳

但上面的这些……暂时都不想做了……再说吧……

# Usage

在运行之前请确保安装 Python3.5 及以上版本，并安装依赖

``` bash
pip install -r requirements.txt
```

之后在 `config.json` 中对一些参数进行配置就可以使用啦（登录只支持爱课程账号，因为其他的做起来太复杂，如果嫌注册太麻烦，直接使用这里放的共享账号就好）

```
{
  "username": <icourse_user_name>,        // 你的爱课程账号
  "password": <icourse_password>,         // 你的爱课程账号密码
  "resolution": <resolution_level>,       // 清晰度等级，可选 0,1,2 清晰度递减
  "root": <root_dir>,                     // 下载目标根目录
  "num_thread": <num_thread>              // 下载线程数
}
```

下载时，只需要以网址作为参数传入即可

``` bash
python mooc-dl.py https://www.icourse163.org/course/ZJU-93001?tid=1003997005
```

# More

[Course Crawler(Forked from Foair/course-crawler)](https://github.com/SigureMo/course-crawler) 支持更多的课程与资源类型~
