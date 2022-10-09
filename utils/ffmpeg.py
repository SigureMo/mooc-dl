import os
import random
import subprocess
import shutil
import platform

"""
ref : https://github.com/soimort/you-get
"""


class FFmpegNotFoundError(Exception):
    def __init__(self):
        super().__init__("请配置正确的 FFmpeg 路径")


class FFmpeg:
    def __init__(self, ffmpeg_path="ffmpeg"):
        try:
            if subprocess.run([ffmpeg_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 1:
                raise FFmpegNotFoundError()
        except FileNotFoundError:
            raise FFmpegNotFoundError()
        self.path = os.path.normpath(ffmpeg_path)
        tmp_dir = os.path.join(os.path.dirname(ffmpeg_path), "tmp")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        self.tmp_dir = os.path.normpath(tmp_dir)

    def __del__(self):
        if hasattr(self, "tmp_dir") and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def exec(self, params):
        """ 调用 ffmpeg """
        cmd = [self.path]
        cmd.extend(params)
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def convert(self, input_path, output_path):
        """ 视频格式转换 """

        # fmt: off
        params = [
            "-i", input_path,
            "-c", "copy",
            "-map", "0",
            "-y",
            output_path
        ]
        self.exec(params)

    def join_videos(self, video_path_list, output_path):
        """ 将视频拼接起来 """

        concat_list_path = os.path.join(self.tmp_dir, "concat_list_{:04}.tmp".format(random.randint(0, 9999))).replace(
            "\\", "/"
        )
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for video_path in video_path_list:
                if os.path.isfile(video_path):
                    video_relpath = os.path.relpath(video_path, start=self.tmp_dir)
                    video_abspath = os.path.abspath(video_path)
                    write_path = video_relpath if platform.system() == 'Windows' else video_abspath
                    f.write("file '{}'\n".format(write_path))
        # fmt: off
        params = [
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_path,
            "-c", "copy",
            "-y",
            output_path
        ]
        self.exec(params)
        os.remove(concat_list_path)

    def join_video_audio(self, video_path, audio_path, output_path):
        """ 将视频和音频合并 """

        # fmt: off
        params = [
            "-i", video_path,
            "-i", audio_path,
            "-codec", "copy",
            "-y",
            output_path
        ]

        self.exec(params)
