import os
from .helpers import command, sizeof_fmt, bash
import telethon
import time
import yt_dlp
from urllib.parse import quote
import requests
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo
from youtubesearchpython import VideosSearch as vs

aud_ops = {
    "format": "bestaudio",
    "addmetadata": True,
    "key": "FFmpegMetadata",
    "prefer_ffmpeg": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }
    ],
    "outtmpl": "%(id)s.mp3",
    "quiet": True,
    "logtostderr": False,
}
vid_ops = {
    "format": "best[height>=720]",
    "addmetadata": True,
    "key": "FFmpegMetadata",
    "prefer_ffmpeg": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
    "outtmpl": "%(id)s.mp4",
    "logtostderr": False,
    "quiet": True,
}


@command(pattern="song")
async def download_song(e):
    try:
        q = e.text.split(None, 1)[1]
    except IndexError:
        return await e.reply("The song query was not provided!")
    try:
        v = vs(q, limit=1).result()["result"][0]
    except (IndexError, KeyError, TypeError):
        return await e.reply("No song result found for your query!")
    axe = await e.reply(
        "Preparing to upload **{}** by {}".format(
            v.get("title"), v.get("channel").get("name") or "Channel"
        )
    )
    duration = int(v["duration"].split(":")[0]) * 60 + \
        int(v["duration"].split(":")[1])
    if duration > 3600:
        await axe.edit("Upload failed song duration is more than 1 hour(s)!")
    with yt_dlp.YoutubeDL(aud_ops) as yt:
        try:
            yt.extract_info(v["link"])
        except Exception as bx:
            return await axe.edit(str(bx))
    async with e.client.action(e.chat_id, "audio"):
        await e.client.send_file(
            e.chat_id,
            v["id"] + ".mp3",
            supports_streaming=False,
            force_document=False,
            allow_cache=False,
            attributes=[
                DocumentAttributeAudio(
                    duration=duration,
                    title=v["title"],
                    performer=v["channel"]["name"],
                    waveform=b"320",
                )
            ],
        )
    await axe.delete()
    os.remove(v["id"] + ".mp3")


@command(pattern="video")
async def download_video(e):
    try:
        q = e.text.split(None, 1)[1]
    except IndexError:
        return await e.reply("The video query was not provided!")
    try:
        v = vs(q, limit=1).result()["result"][0]
    except (IndexError, KeyError, TypeError):
        return await e.reply("No video result found for your query!")
    axe = await e.reply(
        "Preparing to upload Video **{}** by {}".format(
            v.get("title"), v.get("channel").get("name") or "Channel"
        )
    )
    duration = int(v["duration"].split(":")[0]) * 60 + \
        int(v["duration"].split(":")[1])
    if duration > 3600:
        await axe.edit("Upload failed video duration is more than 1 hour(s)!")
    with yt_dlp.YoutubeDL(vid_ops) as yt:
        try:
            yt.extract_info(v["link"])
        except Exception as bx:
            return await axe.edit(str(bx))
    async with e.client.action(e.chat_id, "video"):
        await e.client.send_file(
            e.chat_id,
            v["id"] + ".mp4",
            supports_streaming=True,
            caption=v["title"],
            attributes=[DocumentAttributeVideo(
                duration=duration, w=854, h=480)],
        )
    await axe.delete()
    os.remove(v["id"] + ".mp4")


@command(pattern="stream")
async def _stream_platforma(e):
    try:
        q = e.text.split(None, maxsplit=1)[1]
    except IndexError:
        return await e.reply("No query given!")
    r = requests.get("https://api.roseloverx.tk/stream?q={}".format(quote(q)))
    try:
        r = r.json()
    except:
        return await e.reply("ErrorJsonDecoder.")
    src = "Streaming sites for **{}**:".format(q)
    buttons = []
    s = 0
    if not r["data"]:
        return await e.reply(src+"\nNot available on any OTT.")
    for x in r["data"]:
        s += 1
        p = (f'({x.get("price")})' if "stream" not in x.get(
            "price") else "") if x.get("price") else ""
        buttons.append([telethon.Button.url(x.get("name") + p, x.get("url"))])
    await e.reply(src, buttons=buttons)


@command(pattern='compress')
async def _compress_vid(e):
    v = await e.get_reply_message()
    if not v or v.video == None:
        await e.reply('`No video found to compress!`\nConverts video To h265 codec')
        return
    vd = await v.download_media()
    t = time.time()
    cmd = f'ffmpeg -i {vd} -c:v libx265 -vtag hvc1 compressed-{vd}'
    await bash(cmd)
    size = os.stat(f'compressed-{vd}').st_size
    comp_size = sizeof_fmt(size)
    await e.respond('Time: ' + str(time.time() - t) + f's\nFileName: `compressed-{vd}`' + f'\n**{sizeof_fmt(v.file.size)}** --> **{comp_size}**', file='compressed-' + vd)
    
