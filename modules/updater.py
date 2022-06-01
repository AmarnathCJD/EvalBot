import os
import sys

from .helpers import bash, command

REPO = "https://github.com/amarnathcjd/evalbot"


async def update_deps():
    await bash("pip3 install -r requirements.txt -U")


def execl():
    os.execl(sys.executable, sys.executable, *sys.argv)


async def generate_github_change_log():
    c = await bash("git log -1 --stat --pretty=format:'%s'")
    changelog = f"`{c}`\n\n[Full Change Log]("
    changelog += f"{REPO}/commits/master) | [GitHub]({REPO})"
    return changelog + "\nupdating..."


@command(pattern="update")
async def _update(e):
    await bash("git pull")
    await e.reply((await generate_github_change_log()), link_preview=False)
    await update_deps()
    execl()
