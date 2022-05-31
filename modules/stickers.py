import os

from PIL import Image

from .helpers import command, get_reply_gif, get_reply_image, bash


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

GIF_TO_WEBM = "ffmpeg -i {} -c vp9 -b:v 0 -crf 40 -vf scale=512:512 -t 00:00:03 {}"


@command(pattern="webm")
async def _gif_to_webm(e):
    i = await get_reply_gif(e)
    if not i:
        return await e.reply("Reply to any GIF")
    gif = await i.download_media()
    filename = "".join(gif.split(".")[:1]) + ".webm"
    r = await bash(GIF_TO_WEBM.format(gif, filename))
    await e.reply(file=filename)
    os.remove(filename)
    os.remove(gif)
