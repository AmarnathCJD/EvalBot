from config import command
import sys
import os
import asyncio


@command(pattern="(update|upd|uchange|u)")
async def update(e):
    cmd = e.text.split(" ", 1)[0][:-1]
    if cmd == "uchange":
        return await e.reply("`"+(await bash("git log --stat"))[:400]+"`")
    dd = await e.reply("`Fetching updates ...`")
    os.system("git pull")
    await dd.edit("`Updates fetched, restarting ...`")
    os.system("python3 -m pip install -r requirements.txt")
    
    os.execl(sys.executable, sys.executable, *sys.argv)


@command(pattern="(restart|re|r)")
async def restart(e):
    await e.reply("`Restarting ...`")
    os.execl(sys.executable, sys.executable, *sys.argv)


async def bash(code):
    cmd = code.split(" ")
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) \
        + str(stderr.decode().strip())
    return result
