<<<<<<< HEAD
# MOOC_Downloading
## Menu
1. [Instructions](#使用说明)
2. [Announcements](#注意事项)
3. [References](#参考链接)
4. [Develop](#开发相关)
5. [Latest version](#最新版本)
6. [Acknowledgements](#特别鸣谢)
7. [Recommend](#推荐)
8. [About](#关于)

## 使用说明：
### 免责声明：
本程序提供一键下载中国大学MOOC全课件功能，仅供学习使用，版权归中国大学MOOC所有，不用于任何商业用途。

### 文件说明：
1. `Easyload.py` 封装下载方法和命令行交互方法（主程序）
2. `Myloads.py` 通过简单的配置批量下载课程
3. `GUI.py` GUI，暂时Bug多且功能不完善，不建议使用
4. `data` 存放命令行版和GUI版各自的用户数据
5. `tools` 存放程序依赖的一些class
6. `logs` 存放日志文件

### 程序流程：
1. 版本检测
2. 账号密码
3. 下载路径
4. 课程号（在需要学习的MOOC课程网址中找到'XXX-ddddddd'格式中后面的数字部分 将其复制过来即可，其中XXX指大写字母，为学校名英文缩写，其后为一串数字，就是课程号。例：`https://www.icourse163.org/course/BIT-268001`中的`268001`）
5. 学期号（选择下载第几次开课内容）
6. 周次（按照章节次序选择课程，与课程名中的周次无关，支持单个数字、数字-数字的输入，其中单个整数0和all为下载全部）
7. 课件类型（1对应视频、3对应文档、4对应附件、all对应所有都下，支持多个数字组合）
8. 视频清晰度（选择下视频时会询问，sd对应标清、hd对应高清、shd对应超高清，请根据自己流量情况进行选择）
9. 等待几秒开始下载，下载提示增加信息提示头，错误[Error]，成功[Success]，下载[Loading]，信息[Info]


## 注意事项：
1. 当前输入容错功能较低，请尽量按照输入提示进行输入
2. 如果有下载完成的提示信息仅代表已将所有下载任务尝试下载过一遍，并不代表每个都下载成功，请仔细观察是否有下载失败的提示，并根据提示进行操作
3. 进程数看需求选择，内置限制3-10
4. 可通过任务管理器查看下载情况，如果程序对应硬盘无活动，请用鼠标点击程序后按回车便可重新唤醒程序
5. 请不要在主进程运行时候读写`data/`
6. Playlistの食用方法：将该文件直接拖到支持m3u播放列表的播放器(Windows推荐使用Potplayer,Linux推荐SMPlayer)内就好啦，因为其中保存的是相对位置文件位置，请不要更改该课件的文件结构哦，否则该列表会失效的哦（若想启用绝对路径请自行修改配置文件中的`playListMode`为`AP`后重新启动下载器）
7. 请修改IgnoreOptions.txt（仅支持True和False），True则为自动使用上次配置，否则每次都会询问
8. 近期版本更迭较大，测试并不全面，如有bug产生，请尽快联系我

## 参考链接：
1. [python编写断点续传下载软件](https://www.leavesongs.com/PYTHON/resume-download-from-break-point-tool-by-python.html)
2. [Python实现下载界面(带进度条，断点续传，多线程多任务下载等)](http://blog.51cto.com/eddy72/2106091)
3. [Python GUI之tkinter 实战（二）tkinter+多线程](https://blog.csdn.net/yingshukun/article/details/78838395)
4. [用PyQt5写的第一个程序](https://www.cnblogs.com/archisama/p/5444032.html)

## 开发相关：
### 状态：
Bug修补，暂停新内容开发，GUI暂时搁置

### 测试环境：
1. Windows10 Python3.6
2. Deepin15.6 Python3.5

### 安装依赖：
1. requests
> `pip install requests`
2. bs4
> `pip install BeautifulSoup4`
3. pyqt5 <- 仅`GUI.py`
> `pip install pyqt5`
* 若linux下直接安装失败，请使用 `sudo python3 -m pip install <moduleName>`
* 若因为安装速度过慢而安装失败，请加参数`-i https://pypi.tuna.tsinghua.edu.cn/simple/`

### 实现过程
1. 使用fiddler对手机抓包
  * 点击课程可抓到courseInfo及其获取方法
  * 中国大学MOOC APP 下载视频以获取videoUrl与对应解析方法
  * 中国大学MOOC APP 下载文档以获取pdfUrl与对应解析方法
2. 使用fiddler对Chrome抓包
  * 点击富文本下的下载附件以获取附件url
3. 确实没啥，取了点巧，手机抓包，导致后来的扩展难以摆脱最初的思路，扩展部分暂时不考虑，可以使用[推荐](#推荐)内容下的项目下载其他来源的视频

### 许可协议
`MIT`

## 最新版本：
### 版本号：1.7
#### 内容：
1. 修正GUI中由于未对`isLoad`进行检测而造成的下载错乱问题
2. 增加下载意外中断后重检机制
3. 增加日志文件
4. 由于已经查明原m3u文件兼容性问题来源为相对路径的引用，故取消对dpl格式播放列表的支持，m3u中增加绝对路径引用模式，请自行修改`data/config.txt`中`playListMode`值为`AP`（绝对路径）或`RP`（相对路径），由于相对路径的可移植性更强，故默认使用相对路径
5. 扩展：`tools`中增加 `playList.py`文件，可以方便地对当前目录下所有视频文件进行扫描，并生成`playlist.m3u`，参数可自行修改（简单小工具，不难实现，可以方便地生成其他来源课程播放列表）
6. 修改`Easyload.py`与`Myloads.py`中原多进程下载为多线程下载，依赖于`tools/multithreading.py`，具体性能暂未测试
7. 增加`__init__.py`，封装为package，并将`MOOC_Downloading.py`更名为`GUI.py`
8. 增加版本自动检测机制，通过GitHub仓库对版本进行检测，并询问是否下载
9. 增加`HISTORY.md`,`.gitignore`
> +更多参见[HISTORY.md](HISTORY.md)

## 特别鸣谢
1. 微信群`Python爱生活`各位小伙伴的支持
2. 热心网友H发现新‘类型’：字幕，并对播放列表格式提出建议

## 推荐
[Course Crawler(Forked from Foair/course-crawler)](https://github.com/SigureMo/course-crawler)

## 关于
`Sigure_Mo` Python新手

=======
# MOOC_Downloading
## Menu
1. [Instructions](#使用说明)
2. [Announcements](#注意事项)
3. [References](#参考链接)
4. [Develop](#开发相关)
5. [Latest version](#最新版本)
6. [Acknowledgements](#特别鸣谢)
7. [Recommend](#推荐)
8. [About](#关于)

## 使用说明：
### 免责声明：
本程序提供一键下载中国大学MOOC全课件功能，仅供学习使用，版权归中国大学MOOC所有，不用于任何商业用途。

### 文件说明：
1. `Easyload.py` 封装下载方法和命令行交互方法（主程序）
2. `Myloads.py` 通过简单的配置批量下载课程
3. `GUI.py` GUI，暂时Bug多且功能不完善，不建议使用
4. `data` 存放命令行版和GUI版各自的用户数据
5. `tools` 存放程序依赖的一些class
6. `logs` 存放日志文件

### 程序流程：
1. 版本检测
2. 账号密码
3. 下载路径
4. 课程号（在需要学习的MOOC课程网址中找到'XXX-ddddddd'格式中后面的数字部分 将其复制过来即可，其中XXX指大写字母，为学校名英文缩写，其后为一串数字，就是课程号。例：`https://www.icourse163.org/course/BIT-268001`中的`268001`）
5. 学期号（选择下载第几次开课内容）
6. 周次（按照章节次序选择课程，与课程名中的周次无关，支持单个数字、数字-数字的输入，其中单个整数0和all为下载全部）
7. 课件类型（1对应视频、3对应文档、4对应附件、all对应所有都下，支持多个数字组合）
8. 视频清晰度（选择下视频时会询问，sd对应标清、hd对应高清、shd对应超高清，请根据自己流量情况进行选择）
9. 等待几秒开始下载，下载提示增加信息提示头，错误[Error]，成功[Success]，下载[Loading]，信息[Info]


## 注意事项：
1. 当前输入容错功能较低，请尽量按照输入提示进行输入
2. 如果有下载完成的提示信息仅代表已将所有下载任务尝试下载过一遍，并不代表每个都下载成功，请仔细观察是否有下载失败的提示，并根据提示进行操作
3. 进程数看需求选择，内置限制3-10
4. 可通过任务管理器查看下载情况，如果程序对应硬盘无活动，请用鼠标点击程序后按回车便可重新唤醒程序
5. 请不要在主进程运行时候读写`data/`
6. Playlistの食用方法：将该文件直接拖到支持m3u播放列表的播放器(Windows推荐使用Potplayer,Linux推荐SMPlayer)内就好啦，因为其中保存的是相对位置文件位置，请不要更改该课件的文件结构哦，否则该列表会失效的哦（若想启用绝对路径请自行修改配置文件中的`playListMode`为`AP`后重新启动下载器）
7. 请修改IgnoreOptions.txt（仅支持True和False），True则为自动使用上次配置，否则每次都会询问
8. 近期版本更迭较大，测试并不全面，如有bug产生，请尽快联系我

## 参考链接：
1. [python编写断点续传下载软件](https://www.leavesongs.com/PYTHON/resume-download-from-break-point-tool-by-python.html)
2. [Python实现下载界面(带进度条，断点续传，多线程多任务下载等)](http://blog.51cto.com/eddy72/2106091)
3. [Python GUI之tkinter 实战（二）tkinter+多线程](https://blog.csdn.net/yingshukun/article/details/78838395)
4. [用PyQt5写的第一个程序](https://www.cnblogs.com/archisama/p/5444032.html)

## 开发相关：
### 状态：
Bug修补，暂停新内容开发，GUI暂时搁置

### 测试环境：
1. Windows10 Python3.6
2. Deepin15.6 Python3.5

### 安装依赖：
1. requests
> `pip install requests`
2. bs4
> `pip install BeautifulSoup4`
3. pyqt5 <- 仅`GUI.py`
> `pip install pyqt5`
* 若linux下直接安装失败，请使用 `sudo python3 -m pip install <moduleName>`
* 若因为安装速度过慢而安装失败，请加参数`-i https://pypi.tuna.tsinghua.edu.cn/simple/`

### 实现过程
1. 使用fiddler对手机抓包
  * 点击课程可抓到courseInfo及其获取方法
  * 中国大学MOOC APP 下载视频以获取videoUrl与对应解析方法
  * 中国大学MOOC APP 下载文档以获取pdfUrl与对应解析方法
2. 使用fiddler对Chrome抓包
  * 点击富文本下的下载附件以获取附件url
3. 确实没啥，取了点巧，手机抓包，导致后来的扩展难以摆脱最初的思路，扩展部分暂时不考虑，可以使用[推荐](#推荐)内容下的项目下载其他来源的视频

### 许可协议
`MIT`

## 最新版本：
### 版本号：1.7
#### 内容：
1. 修正GUI中由于未对`isLoad`进行检测而造成的下载错乱问题
2. 增加下载意外中断后重检机制
3. 增加日志文件
4. 由于已经查明原m3u文件兼容性问题来源为相对路径的引用，故取消对dpl格式播放列表的支持，m3u中增加绝对路径引用模式，请自行修改`data/config.txt`中`playListMode`值为`AP`（绝对路径）或`RP`（相对路径），由于相对路径的可移植性更强，故默认使用相对路径
5. 扩展：`tools`中增加 `playList.py`文件，可以方便地对当前目录下所有视频文件进行扫描，并生成`playlist.m3u`，参数可自行修改（简单小工具，不难实现，可以方便地生成其他来源课程播放列表）
6. 修改`Easyload.py`与`Myloads.py`中原多进程下载为多线程下载，依赖于`tools/multithreading.py`，具体性能暂未测试
7. 增加`__init__.py`，封装为package，并将`MOOC_Downloading.py`更名为`GUI.py`
8. 增加版本自动检测机制，通过GitHub仓库对版本进行检测，并询问是否下载
9. 增加`HISTORY.md`,`.gitignore`
> +更多参见[HISTORY.md](HISTORY.md)

## 特别鸣谢
1. 微信群`Python爱生活`各位小伙伴的支持
2. 热心网友H发现新‘类型’：字幕，并对播放列表格式提出建议

## 推荐
[Course Crawler(Forked from Foair/course-crawler)](https://github.com/SigureMo/course-crawler)

## 关于
`Sigure_Mo` Python新手

>>>>>>> history
[return 0](#mooc_downloading)