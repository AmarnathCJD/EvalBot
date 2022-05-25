from .helpers import command, bash
import os
import sys

REPO = "https://github.com/amarnathcjd/evalbot"


def update():
    bash("git pull")
    update_deps()
    execl()


def update_deps():
    bash("pip3 install -r requirements.txt -U")


def execl():
    os.execl(sys.executable, sys.executable, *sys.argv)


@command(pattern="update")
async def _update(e):
    await e.reply("Updating...")
    update()
