from config import command
from dev import bash
import re

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
