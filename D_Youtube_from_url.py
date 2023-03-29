from pytube import YouTube,Playlist
import pyperclip
import os
import subprocess
import socket
import socks
import sys
import datetime
import time
import requests
from tqdm import tqdm
import random

def file_size_display(size):
    power = 2 ** 10
    n = 0
    units = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}"

def merge_to_mp4(audio,video):
    outfile_name = video.rsplit('.')[0] + '-new.mp4'
    cmd = "F:/owner/temp/douyin/youtube/ffmpeg-5.1-full_build/bin/ffmpeg -i " +'\"' + f'{audio}' +'\"'  + " -i "  +'\"' + f'{video}' +'\"'  + " -acodec copy -vcodec copy "  +'\"'  + f'{outfile_name}'  +'\"'

    # 使用FFmpeg命令获取视频的时长
    result = subprocess.Popen(
        ["F:/owner/temp/douyin/youtube/ffmpeg-5.1-full_build/bin/ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", video],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    video_duration = float(result.stdout.readline())

    # 使用tqdm创建进度条
    with tqdm(total=video_duration) as pbar:
        # 启动FFmpeg进程
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, universal_newlines=True, encoding="utf-8")
        pbar.set_description(f"合并进度")
        for line in process.stdout:
            # 检查输出是否包含 "time="，如果是则更新进度条
            if "time=" in line:
                time_str = line[line.index("time=") + 5:line.index("time=") + 13]
                time_sec = sum(float(x) * 60 ** i for i, x in enumerate(reversed(time_str.split(":"))))
                pbar.update(time_sec - pbar.n)

    # 等待FFmpeg进程完成
    process.wait()
    pbar.close()

    # 检查合并结果是否成功
    if process.returncode == 0:
        print("合并成功！")
    else:
        print("合并失败！")

    os.remove(audio)
    os.remove(video)

def progress_func(stream, chunk, bytes_remaining):
    curr = stream.filesize - bytes_remaining
    done = int(50 * curr / stream.filesize)
    sys.stdout.write("\r[{}{}] ".format('=' * done, ' ' * (50-done)) )
    sys.stdout.flush()

def on_progress(vid, chunk, bytes_remaining):
    total_size = vid.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    totalsz = file_size_display(total_size)
    remain = file_size_display(bytes_remaining)
    dwnd = file_size_display(bytes_downloaded)
    percentage_of_completion = round(percentage_of_completion, 2)
    curr = vid.filesize - bytes_remaining
    done = int(20 * curr / vid.filesize)
    if done - 20 != 0:
        sys.stdout.write(
            "\r[{}{}] 下载进度: {}% 文件大小:{}  已经下载: {}  剩余大小:{}  ".format('▉' * done,
                                                                                       ' ' * (
                                                                                                   20 - done),
                                                                                       percentage_of_completion,
                                                                                       totalsz, dwnd,
                                                                                       remain))

        sys.stdout.flush()
    else:
        print(
            "\r[{}{}] 下载进度: {}% 文件大小:{}  已经下载: {}  剩余大小:{}  ".format('▉' * done,
                                                                                       ' ' * (
                                                                                                   20 - done),
                                                                                       percentage_of_completion,
                                                                                       totalsz, dwnd,
                                                                                       remain))


def download_4k(link,file_path):
    yt = YouTube(link, on_progress_callback=on_progress)

    file_video = file_path + 'video'
    file_audio = file_path + 'audio'
    # Showing details
    print("Title: ", yt.title)
    print("Number of views: ", yt.views)
    print("Length of video: ", yt.length)
    print("Rating of video: ", yt.rating)

    # # 最高分辨率视频
    ys_high_video = yt.streams.filter(adaptive=True, only_video=True).first()

    # 4K分辨率视频
    # ys_high_video = yt.streams.filter(res="2160p").first()

    # 1080P分辨率视频
    # ys_high_video = yt.streams.filter(res="1080p").first()

    # 最高音频
    ys_high_audio = yt.streams.filter(adaptive=True, only_audio=True).last()
    print(ys_high_video, '\n', ys_high_audio)

    # 文件名称和路径
    audio = file_audio + '/' + ys_high_audio.default_filename.rsplit('.')[0] + '.' + ys_high_audio.subtype
    video = file_video + '/' + ys_high_video.default_filename.rsplit('.')[0] + '.' + ys_high_video.subtype
    print('视频文件保存路径： ',video,'\n音频文件保存路径： ', audio)
    # print(ys_high_video.default_filename)

    #检查文件是否已经下载
    outfile = video.rsplit('.')[0] + '-new.mp4'
    if not os.path.exists(outfile):
        print('视频文件下载开始......')
        # while True:
        #     try:
        video_wf_filesize = ys_high_video.filesize
        # 检查视频文件是否完整下载
        if os.path.exists(video):
            video_file_size = os.path.getsize(video)
            print('\n无音频的视频文件总的大小为：' + str(file_size_display(video_wf_filesize)), '  已经下载文件大小为：' + str(file_size_display(video_file_size)),
                  '  待下载的文件大小为：' + str(file_size_display(video_wf_filesize - video_file_size)))
        else:
            print('\n无音频的视频文件总的大小为：' + str(file_size_display(video_wf_filesize)), '  已经下载文件大小为：0KB' ,
                  '  待下载的文件大小为：' + str(file_size_display(video_wf_filesize)))
            # ys_high_video.download(file_video)
            video_file_size = 0
        if video_file_size != video_wf_filesize:
            # 检查是否有未完成的下载，如果有，就获取已下载的字节数
            if os.path.exists(video):
                headers = {"Range": f"bytes={os.path.getsize(video)}-"}
                initial = video_file_size
            else:
                headers = {}
                initial = 0

            # 发送 HTTP 请求并保存文件  https://www.youtube.com/watch?v=Lc3CxLEjAxI
            with open(video, "ab") as f:
                r = requests.get(ys_high_video.url, headers=headers, stream=True)
                # total_size = int(r.headers.get("Content-Length", 0))
                total_size = video_wf_filesize - video_file_size
                block_size = 1024  # 1 KB
                t = tqdm(total=total_size, initial=initial, unit="iB", unit_scale=True)
                t.set_description(f"\n下载进度")

                # 写入下载的数据
                for chunk in r.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        t.update(len(chunk))
                t.close()
            print('\r无音频的视频文件下载完成')
        else:
            print('\r无音频的视频文件已经下载')


        print('\r音频频文件下载开始......')
        audio_wfile_size = ys_high_audio.filesize

        # # # 检查音频文件是否完整下载
        if os.path.exists(audio):
            audio_file_size = os.path.getsize(audio)
            print('\n音频文件总的大小为：' + str(file_size_display(audio_wfile_size)), '  已经下载文件大小为：' + str(file_size_display(audio_file_size)),
                  '  待下载的文件大小为：' + str(file_size_display(audio_wfile_size - audio_file_size)))
        else:
            print('\n音频文件总的大小为：' + str(file_size_display(audio_wfile_size)), '  已经下载文件大小为：0KB',
                  '  待下载的文件大小为：' + str(file_size_display(audio_wfile_size)))
            ys_high_audio.download(file_audio)
            audio_file_size = os.path.getsize(audio)
        if audio_file_size != audio_wfile_size:
            # 检查是否有未完成的下载，如果有，就获取已下载的字节数
            if os.path.exists(audio):
                headers = {"Range": f"bytes={os.path.getsize(audio)}-"}
                initial = audio_file_size
            else:
                headers = {}
                initial = 0
            # 发送 HTTP 请求并保存文件  https://www.youtube.com/watch?v=Oo04RTZSGOg
            with open(audio, "ab") as f:
                # headers = {"Range": f"bytes={file_size}-"}
                r = requests.get(ys_high_audio.url, headers=headers, stream=True)
                # total_size = int(r.headers.get("Content-Length", 0))
                total_size = audio_wfile_size - audio_file_size
                block_size = 1024  # 1 KB
                t = tqdm(total=total_size, initial=initial, unit="iB", unit_scale=True)
                t.set_description(f"\n下载进度")

                # 写入下载的数据
                for chunk in r.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        t.update(len(chunk))
                t.close()
            print('\r音频频文件下载完成')
        else:
             print('\r音频频文件已经下载')
        # 合并视频音频为MP4
        merge_to_mp4(audio, video)
            #     break
            # except:
            #       time.sleep(random.randint(0, 1))

    else:
         print('\r此文件已经下载')

start_time = datetime.datetime.now()

# # 设置全局代理
socks.set_default_proxy(socks.SOCKS5, "localhost", 20555)
# no_proxy_temp = socket.socket   # 记录设置全局不代理
socket.socket = socks.socksocket

file_path = r'H:/youtube/temp/4K Nature/'

# 获取当前目录中名为temp.txt的文件路径
# current_dir = os.getcwd()

txt_file_path = os.path.join(file_path, 'temp.txt')
#
# # 如果temp.txt不存在，则创建一个新的文件
if not os.path.exists(txt_file_path):
    open(txt_file_path, 'w').close()

# 从temp.txt中获取链接地址
with open(txt_file_path, 'r') as f:
    link = f.read().strip()

# 如果链接地址为空，则从剪贴板中获取链接，并写入temp.txt
if not link:
    link = pyperclip.paste().strip()
    with open(txt_file_path, 'w') as f:
        f.write(link)
    playlist = pyperclip.paste()
else:
    playlist = str(link)
    print(playlist)

while True:
    try:
        if 'https://www.youtube.com/' in playlist and 'list=' not in playlist:
            download_4k(playlist, file_path)
            with open(txt_file_path, 'w') as f:
                # 清空文件
                f.truncate(0)
            os.startfile(file_path + 'video')
        elif 'https://www.youtube.com/' in playlist and 'list=' in playlist:
            all_playlist_urls = Playlist(playlist)  #.playlist_id
            print(all_playlist_urls)
            playlist_name = all_playlist_urls.title
            print(playlist_name)
            save_file_path = file_path + playlist_name + '/'
            if not os.path.exists(save_file_path):
                os.makedirs(save_file_path)
                print('创建文件夹：', save_file_path)
            if len(all_playlist_urls) > 0:
                total = len(all_playlist_urls)
                num_i = 0
                for link in all_playlist_urls:
                    download_4k(link,save_file_path)
                    num_i += 1
                    print('共' + str(total) + '个，第' + str(num_i) + '个   ' + str(link))
                with open(txt_file_path, 'w') as f:
                    # 清空文件
                    f.truncate(0)
                os.startfile(save_file_path + 'video/')
        else:
            print('没有正确视频地址')
            pass
        break
    except:
        time.sleep(random.randint(0, 1))

after_today = datetime.date.today()
after_hour = int(time.strftime("%Y,%m,%d,%H,%M,%S").split(',')[3])
end_time = datetime.datetime.now()
elapsed_time = end_time - start_time

# 将总耗时格式化为"小时:分钟:秒"的字符串
hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
minutes, seconds = divmod(remainder, 60)
elapsed_time_str = f"{hours:02}:{minutes:02}:{seconds:02}"

print('处理完毕 开始时间：',start_time,'结束时间：',end_time,"总耗时:", elapsed_time_str)
