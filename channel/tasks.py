from celery import shared_task
from . import models
import subprocess
import shutil

@shared_task(name='Test')
def add(x, y):
    return x + y

@shared_task(name='Optimize_video')
def optimize_video(file, channelId, objectID):
    print(objectID)
    video = models.VideoFile.objects.get(id = objectID)
    content = models.Content.objects.get(id = video.content.id)
    content.status = 'Processing'
    ffprobe_command = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        f'uploads/{file}'
    ]
    try:
        result = subprocess.run(ffprobe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        duration = float(result.stdout.strip())
        content.duration = duration
    except subprocess.CalledProcessError as e:
        print(f"Error getting video duration: {e}")

    content.save()

    outputFile = f'uploads/videos/{channelId}/{objectID}'
    cmd = f'ffmpeg -i uploads/{file} -filter_complex "[0:v]split=3[v1][v2][v3]; [v1]scale=640:480[v480p]; [v2]scale=1280:720[v720p]; [v3]scale=1920:1080[v1080p]" -map "[v480p]" -map 0:a -c:v:0 libx264 -b:v:0 1000k -preset fast -g 48 -sc_threshold 0 -c:a aac -b:a 128k -f hls -hls_time 6 -hls_playlist_type vod -hls_segment_filename "{outputFile}/480p_%03d.ts" {outputFile}/480p.m3u8 -map "[v720p]" -map 0:a -c:v:1 libx264 -b:v:1 2500k -preset fast -g 48 -sc_threshold 0 -c:a aac -b:a 128k -f hls -hls_time 6 -hls_playlist_type vod -hls_segment_filename "{outputFile}/720p_%03d.ts" {outputFile}/720p.m3u8 -map "[v1080p]" -map 0:a -c:v:2 libx264 -b:v:2 5000k -preset fast -g 48 -sc_threshold 0 -c:a aac -b:a 128k -f hls -hls_time 6 -hls_playlist_type vod -hls_segment_filename "{outputFile}/1080p_%03d.ts" {outputFile}/1080p.m3u8 -ss 00:00:00 -frames:v 1 -q:v 2 {outputFile}/thumbnail.jpg'
    copyFile = 'master.m3u8'
    p = subprocess.call(cmd, shell=True)
    shutil.copy(copyFile, f'{outputFile}/master.m3u8')
    content.status = 'Process Completed'
    content.save()
    video.hsl_file = f'{outputFile}/master.m3u8'
    video.save()
    return 'Successfully the Video is optimized'