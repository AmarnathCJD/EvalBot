import os

from PIL import Image

from .helpers import command, get_reply_image


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
