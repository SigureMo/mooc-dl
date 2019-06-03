# mooc-dl

本程序提供一键下载中国大学MOOC全课件功能，仅供学习使用，版权归中国大学 MOOC 所有，不用于任何商业用途

# Usage

``` bash
python mooc-dl.py https://www.icourse163.org/course/ZJU-93001?tid=1003997005
```

# Change Logs

迫于强迫症，时隔近一年，我最终还是抽出几个小时重写了下，但是原来的各种复杂功能就不实现了，只保留其中主要的 API ，实现基本功能，旧版本见 `v1.0`

基于 [pynotex](https://github.com/SigureMo/notev/tree/master/Codes/pynotex) 快速开发，作为 `course-clawer/icourse163` 备用接口

# Extend

[Course Crawler(Forked from Foair/course-crawler)](https://github.com/SigureMo/course-crawler)
