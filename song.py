from config import command
from dev import bash
from urllib.parse import quote
import requests 
import re
from telethon import Button

pattern = r'"([^"]*)"'


async def download_song(query: str):
    out = await bash("spotdl '{}'".format(query))
    match = re.findall(pattern, out) if out != "" else []
    if len(match) == 0:
        return "", "No results found!"
    return match[-1] + ".mp3", ""


@command(pattern="song")
async def dl_song(e):
    try:
        q = e.text.split(None, maxsplit=1)[1]
    except IndexError:
        return await e.reply("No query given!")
    resp, err = await download_song(q)
    if err != "":
        return await e.reply(err)
    async with e.client.action(e.chat_id, "audio"):
        try:
            await e.respond(file=resp)
        except BaseException as errr:
            await e.reply(str(errr))

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
   p = (f'({x.get("price")})' if "stream" not in x.get("price") else "") if x.get("price") else ""
   buttons.append([Button.url(x.get("name") + p, x.get("url"))])
 await e.reply(src, buttons=buttons)

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

@command(pattern='mdisk')
async def _mdisk(e):
 try:
   _url = e.text.split(None, maxsplit=1)[1]
 except IndexError:
   return await e.reply("Please provide mdisk url.")
 url = _url.split("/")
 if len(url) == 0:
   return await e.reply("Failed to find MediaID.")
 url = url[-1]
 base_url = "https://diskuploader.entertainvideo.com/v1/file/cdnurl?param=" + url
 r = get(base_url)
 try:
     try:
         r = r.json()
     except:
         return await e.reply('Resource not found, 404.')  
     filename = r['filename'] if r.get("filename") else 'file0'
     src = r['download'] if r.get("download") else (r.get("source") or "")
     duration = int(r['duration']) if r.get("duration") else 0
     size = int(r['size']) if r.get('size') else 0
 except:
     return await e.reply("Error: extractMetadata failed.")
 strf_du = str(datetime.timedelta(seconds = duration))
 size = sizeof_fmt(size)
 _data = f'**FileName:** {filename}'
 _data += f'\n**Size:** {size}' if size != '0B' else ""
 _data += f'\n**Duration:** {strf_du}' if duration != 0 else ""
 _data += f'\n**Mdisk URL:** {_url}'
 buttons = [Button.url('Direct URL', src)]
 await e.reply(_data, buttons=buttons)
     
     
