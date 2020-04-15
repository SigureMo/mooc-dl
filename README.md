# mooc-dl

![python 3.6.7](https://img.shields.io/badge/python-3.6.7-green?style=flat-square&logo=python)

本程序提供中国大学 MOOC 课件的下载，方便离线观看与复习，但本程序及其所得内容不可用于商业用途

## Usage

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
  "num_thread": <num_thread>,             // 下载线程数
  "overwrite": false                      // 强制覆盖已有文件
  "file_path_template": "{base_dir}{sep}{cnt_1} {chapter_name}{sep}{cnt_2} {lesson_name}{sep}{cnt_3} {unit_name}"
                                          // 文件存储路径模板，可据此自定义文件存储路径
}
```

下载时，只需要以网址作为参数传入即可

``` bash
python mooc-dl.py https://www.icourse163.org/course/ZJU-93001?tid=1003997005
```

## Tips

### 关于文件路径

默认的文件路径是分级的，如果你不喜欢这样的效果，完全可以修改模板进行自定义，比如类似 course-crawler 那种分类式，你只需要将模版设置成这样即可

```
{
   "file_path_template": "{base_dir}{sep}{type}{sep}{cnt_3} {unit_name}"
}
```

### 进度条的问题

暂时进度条体验非常不佳，但不影响下载功能

## License

<!-- 鉴于某“开源”项目明显借鉴了 [Course-Crawler](https://github.com/Foair/course-crawler) 的代码却用于商业化，所以-->本 Repo 转用 GPL-3.0 协议开源

请遵守该开源协议使用本项目，本项目源程序及所得内容均不可用于商业用途
