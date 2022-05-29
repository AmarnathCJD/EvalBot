import asyncio
import io
import sys
import traceback

import requests

from .helpers import auth, command, get_user


@command(pattern="eval")
@auth
async def _eval(e):
    try:
        c = e.text.split(" ", 1)[1]
    except IndexError:
        return await e.reply("No code provided")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        value = await aexec(c, e)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = exc or stderr or stdout or value or "No output"
    if len(str(evaluation)) > 4094:
        with io.BytesIO(str(evaluation).encode()) as file:
            file.name = "eval.txt"
            return await e.respond(file=file)
    final_output = (
        "__►__ **EVALPy**\n```{}``` \n\n __►__ **OUTPUT**: \n```{}``` \n".format(
            c,
            evaluation,
        )
    )
    await e.reply(final_output)


async def aexec(code, event):
    exec(
        (
            "async def __aexec(e, client): "
            + "\n p = print"
            + "\n message = event = e"
            + "\n r = reply = await event.get_reply_message()"
            + "\n chat = event.chat_id"
            + "\n from pprint import pprint"
            + "\n pp = pprint"
        )
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](event, event.client)


@command(pattern="(bash|exec)")
@auth
async def _exec(e):
    try:
        cmd = e.text.split(maxsplit=1)[1]
    except IndexError:
        return await e.reply("No cmd provided.")
    p = await e.reply("Processing...")
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    out = str(stdout.decode().strip()) + str(stderr.decode().strip())
    if len(out) > 4095:
        with io.BytesIO(out.encode()) as file:
            file.name = "exec.txt"
            await e.reply(file=file)
            await p.delete()
    else:
        f = "`BASH` \n`Output:`\n\n```{}```".format(out)
        await p.edit(f)


@command(pattern="request")
async def _request(e):
    METHODS = ("get", "post", "put", "delete", "patch", "head")
    args = e.text.split()
    if len(args) == 1:
        return await e.reply("No arguments provided.")
    elif len(args) == 2:
        url = args[1]
    elif len(args) > 2:
        url = args[1]
        args = args[2:]
    if not url.startswith("http"):
        url = "http://{}".format(url)
    method = "GET"
    for m in METHODS:
        if m.lower() in args:
            method = m.upper()
            break
    if "-d" in args:
        data = args[args.index("-d") + 1]
    else:
        data = None
    if "-h" in args:
        headers = args[args.index("-h") + 1]
    else:
        headers = None
    if "-t" in args:
        timeout = int(args[args.index("-t") + 1])
    else:
        timeout = 10
    try:
        r = requests.request(method, url, data=data, headers=headers, timeout=timeout)
    except requests.exceptions.ConnectionError:
        return await e.reply("No internet connection.")
    except requests.exceptions.Timeout:
        return await e.reply("Request timed out.")
    except requests.exceptions.RequestException:
        return await e.reply("Invalid request.")
    except Exception as ex:
        return await e.reply("Unknown error." + str(ex))
    if r.status_code == 200:
        resp = "**SUCCESS**\n\n{}".format(
            r.text.replace("`", "") if r.text else r.content
        )
    else:
        resp = "**FAILURE**\n\n`{}`".format(
            r.text.replace("`", "") if r.text else r.content
        )
    if len(resp) > 4096:
        with io.BytesIO(resp.encode()) as file:
            file.name = "req.txt"
            await e.reply(file=file)
    else:
        await e.reply(resp)


@command(pattern="ext")
async def _ext(e):
    try:
        ext = e.text.split(" ", 1)[1]
    except IndexError:
        return await e.reply("No extension provided.")
    if ext.startswith("."):
        ext = ext[1:]
    URL = "https://api.roseloverx.tk/fileinfo/{}".format(ext)
    r = requests.get(URL)
    if r.status_code == 200:
        response = f"""
        **Extension:** `{ext}`
        **Description:** `{r.json()['description']}`
        """
        image = r.json().get("icon")
        await e.reply(response, image=image)
    else:
        await e.reply("No extension found.")


@command(pattern="info")
async def _info(e):
    if not e.is_reply and len(e.text.split()) == 1:
        user = e.sender
    else:
        user, _ = await get_user(e)
    if not user:
        return await e.reply("No user found.")
    USER_INFO = (
        "**USER INFO**\n"
        "`Name:` **{}**\n"
        "`ID:` **{}**\n"
        "`Username:` **{}**\n"
        "`Bot:` **{}**\n"
    ).format(
        user.first_name,
        user.id,
        user.username,
        user.bot,
    )
    await e.reply(USER_INFO)
