from .helpers import command, get_reply_image
from PIL import Image
import os


def resize_image(image, size):
    return image.resize(size, Image.ANTIALIAS)
    


@command(pattern="(stoi|itos)")
async def _stoi(e):
    cmd = e.text.split(" ")[0][1:]
    i = await get_reply_image(e)
    if not i:
        return await e.reply("Reply to an image/sticker")
    image = await i.download_media()
    if cmd == "stoi":
        IMAGE = Image.open(image)
        IMAGE = resize_image(IMAGE, (512, 512))
        filename = ''.join(image.split('.')[:1]) + '.png'
        IMAGE.save(filename)
        await e.reply(file=filename)
        os.remove(filename)
    elif cmd == "itos":
        IMAGE = Image.open(image)
        IMAGE = resize_image(IMAGE, (512, 512))
        filename = ''.join(image.split('.')[:1]) + '.webp'
        IMAGE.save(filename)
        await e.reply(file=filename)
        os.remove(filename)
