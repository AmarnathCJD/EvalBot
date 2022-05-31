import os

from PIL import Image

from .helpers import bash, command, get_reply_gif, get_reply_image


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


GIF_TO_WEBM = "ffmpeg -i {} -c vp9 -b:v 0 -crf 40 -vf scale={}:{} -t 00:00:03 {}"
VID_DIMENTIONS = "ffprobe -v error -show_entries stream=width,height -of default=noprint_wrappers=1 {}"


@command(pattern="webm")
async def _gif_to_webm(e):
    i = await get_reply_gif(e)
    if not i:
        return await e.reply("Reply to any GIF")
    gif = await i.download_media()
    filename = "".join(gif.split(".")[:1]) + ".webm"
    v = await bash(VID_DIMENTIONS.format(gif))
    await e.reply(v)
    v = v.split("\n")[0].split(" ")
    v = (int(v[0]), int(v[1]))
    ratio = v[0] / v[1]
    if ratio > 1:
        v = (int(512 * ratio), 512)
    else:
        v = (512, int(512 / ratio))
    await bash(GIF_TO_WEBM.format(gif, v[0], v[1], filename))
    await e.reply(file=filename)
    os.remove(filename)
    os.remove(gif)