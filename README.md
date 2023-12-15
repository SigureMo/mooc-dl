# mooc-dl

本程序提供中国大学 MOOC 课件的下载，方便离线观看与复习，但本程序及其所得内容不可用于商业用途

> [!IMPORTANT]
>
> 本程序已停止维护，如果你想要继续使用，请自行 fork 本项目并修改相关代码

## Usage

在运行之前请确保安装 Python3.6 及以上版本，并安装依赖

```bash
pip install -r requirements.txt
```

之后在 `config.json` 中对一些参数进行配置就可以使用啦（登录只支持爱课程账号，因为其他的做起来太复杂，如果嫌注册太麻烦，直接使用这里放的共享账号就好）

> [!NOTE]
>
> 目前中国大学 MOOC 已经会验证账号是否参加课程，因此请一定确保替换共享账号为自己的账号，并且确保自己的账号已经参加了课程

<!-- prettier-ignore -->
```jsonc
{
  "username": "<icourse_user_name>",      // 你的爱课程账号
  "password": "<icourse_password>",       // 你的爱课程账号密码
  "resolution": 0,                        // 清晰度等级，可选 0,1,2 清晰度递减
  "root": "",                             // 下载目标根目录
  "num_thread": 16,                       // 下载线程数
  "overwrite": false,                     // 是否强制覆盖已有文件
  "file_path_template": "{base_dir}{sep}{cnt_1} {chapter_name}{sep}{cnt_2} {lesson_name}{sep}{cnt_3} {unit_name}",
                                          // 文件存储路径模板，可据此自定义文件存储路径
  "range": {                              // 设置开始章节和结束章节
    "start": [0, 0, 0],
    "end": [999, 999, 999]
  },
  "file_types": [1, 3, 4],                // 下载文件类型，可选 1,3,4，分别代表视频、PDF、附件，默认全部下载
  "use_ffmpeg": false                     // 是否使用 FFmpeg 进行合并，需自行安装 FFmpeg
}
```

下载时，只需要以网址作为参数传入即可

```bash
python mooc-dl.py "https://www.icourse163.org/course/ZJU-93001?tid=1003997005"
```

此外还支持通过参数来覆盖配置，如

```bash
python mooc-dl.py "https://www.icourse163.org/course/ZJU-93001?tid=1003997005" --range="1.2~5.4" --file-types="1, 3" --use-ffmpeg --overwrite
```

## Tips

### 关于文件路径

默认的文件路径是分级的，如果你不喜欢这样的效果，完全可以修改模板进行自定义，比如类似 course-crawler 那种分类式，你只需要将模版设置成这样即可

```jsonc
{
   "file_path_template": "{base_dir}{sep}{type}{sep}{cnt_3} {unit_name}"
}
```

### 进度条的问题

暂时进度条体验非常不佳，但不影响下载功能

### 关于维护

~~由于 Nyakku 已经很少使用中国大学 MOOC 了，因此本程序不会积极维护，如果只是遇到小错误的话会尝试修复，但如果中国大学 MOOC 发生大的 API 变动，本项目会停止维护……（应该快了）~~ 已停止维护

## License

本 Repo 采用 GPL-3.0 协议开源，请遵守该开源协议使用本项目，本项目源程序及所得内容均不可用于商业用途
