import os
import sys

from .helpers import bash, command

REPO = "https://github.com/amarnathcjd/evalbot"


async def update():
    await bash("git pull")
    await update_deps()


async def update_deps():
    await bash("pip3 install -r requirements.txt -U")


def execl():
    os.execl(sys.executable, sys.executable, *sys.argv)


async def generate_github_change_log():
    return str(await bash("git log -1 --stat --pretty=format:'%s'"))


@command(pattern="update")
async def _update(e):
    await e.reply("Updating...")
    await update()
    await e.reply((await generate_github_change_log()))
    execl()
