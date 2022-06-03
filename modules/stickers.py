import io
import os

from PIL import Image

from .helpers import bash, command, get_reply_gif, get_reply_image, get_reply_video


def resize_image(image, size):
    return image.resize(size, Image.ANTIALIAS)


@command(pattern="(stoi|itos)")
async def _stoi(e):
    cmd = e.text.split(" ")[0][1:]
    i = await get_reply_image(e)
    if not i:
        return await e.reply("Reply to an image/sticker")
    image = await i.download_media()
    IMAGE = Image.open(image)
    if cmd == "stoi":
        filename = "".join(image.split(".")[:1]) + ".png"
    elif cmd == "itos":
        IMAGE = resize_image(IMAGE, (512, 512))
        filename = "".join(image.split(".")[:1]) + ".webp"
    IMAGE.save(filename)
    await e.reply(file=filename)
    os.remove(filename)
    os.remove(image)


@command(pattern="resize")
async def _resize(e):
    try:
        size = e.text.split(" ")[1]
        size = size.split("x")
        size = (int(size[0]), int(size[1]))
    except (TypeError, IndexError):
        return await e.reply("Usage: `resize <width>x<height>`")
    i = await get_reply_image(e)
    if (size[0] * size[1]) > 8294400:
        return await e.reply("Max resolution supported is 3840x2160.")
    if not i:
        return await e.reply("Reply to an image/sticker")
    image = await i.download_media()
    IMAGE = Image.open(image)
    IMAGE = resize_image(IMAGE, size)
    filename = "resized_" + image
    IMAGE.save(filename)
    await e.reply(file=filename)
    os.remove(filename)
    os.remove(image)


GIF_TO_WEBM = "ffmpeg -i {} -c vp9 -b:v 0 -crf 40 -vf scale=512:-1 -t 00:00:03 {}"
VID_DIMENTIONS = "ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x {}"


@command(pattern="webm")
async def _gif_to_webm(e):
    i = await get_reply_gif(e)
    if not i:
        return await e.reply("Reply to any GIF")
    gif = await i.download_media()
    filename = "".join(gif.split(".")[:1]) + ".webm"
    v = await bash(VID_DIMENTIONS.format(gif))
    msg = await e.reply("Converting...")
    v = v.split("x")
    v = (int(v[0]), int(v[1]))
    ratio = v[0] / v[1]
    if ratio > 1:
        v = (int(512 * ratio), 512)
    else:
        v = (512, int(512 / ratio))
    await bash(GIF_TO_WEBM.format(gif, filename))
    await e.reply(file=filename)
    await msg.delete()
    os.remove(filename)
    os.remove(gif)


WATERMARK = """ffmpeg -i {}
 -vf "drawtext=text='{}':x=10:y=H-th-10:
               fontcolor=white:
               shadowcolor=black:shadowx=5:shadowy=5"
{}"""


@command(pattern="watermark")
async def _watermark(e):
    try:
        text = e.text.split(" ")[1]
    except:
        return await e.reply("Usage: `watermark <text>`")
    i = await get_reply_video(e)
    if not i:
        return await e.reply("Reply to any video")
    video = await i.download_media()
    filename = "watermarked_" + video
    out = await bash(WATERMARK.format(video, text, filename))
    with io.BytesIO(out.encode()) as f:
        f.name = "out.txt"
        await e.reply(file=f)
    await e.reply(file=filename)
    os.remove(filename)
    os.remove(video)
