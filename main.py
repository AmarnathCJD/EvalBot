import importlib
import requests
import telethon
from config import AUTH, auTH, command, Master, bot
import sys
import io
import traceback
import asyncio
from pprint import pprint

from database import auth_user, unauth_user


@command(pattern="ping")
async def ping(event):
    await event.reply("pong")
    pprint("pong")


@command(pattern="eval")
@auTH
async def deval(e):
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
    final_output = (
        "__►__ **EVALPy**\n```{}``` \n\n __►__ **OUTPUT**: \n```{}``` \n".format(
            c,
            evaluation,
        )
    )
    if len(final_output) > 4090:
        final_output = evaluation
        with io.BytesIO(final_output.encode()) as out_file:
            out_file.name = "eval.txt"
            await e.respond(file=out_file, caption=c)
    await e.reply(final_output)


async def aexec(code, event):
    exec(
        (
            "async def __aexec(e, client): "
            + "\n p = print"
            + "\n message = event = e"
            + "\n reply = await event.get_reply_message()"
            + "\n chat = event.chat_id"
            + "\n pp = pprint"
        )
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](event, event.client)


@command(pattern="goval")
@auTH
async def goval(e):
    try:
        cmd = e.text.split(maxsplit=1)[1]
    except IndexError:
        await e.reply("No cmd provided.")
        return
    endpoint = "https://go.dev/_/compile"
    params = {"version": 2, "body": cmd, "withVet": True}
    r = requests.post(endpoint, params=params)
    resp = r.json()
    result = {"out": "nil", "err": "nil"}
    if resp.get("Events"):
        result["out"] = resp["Events"][0]["Message"]
    if resp.get("Errors"):
        result["err"] = resp["Errors"]
    if result["out"] != "nil":
        evaluation = result["out"]
    elif result["err"] != "nil":
        evaluation = result["err"]
    else:
        evaluation = "nil"
    final_output = (
        "__►__ **EVALGo**\n```{}``` \n\n __►__ **OUTPUT**: \n```{}``` \n".format(
            cmd,
            evaluation,
        )
    )
    await e.reply(final_output)


@command(pattern="exec")
@auTH
async def _exec(e):
    try:
        cmd = e.text.split(maxsplit=1)[1]
    except IndexError:
        return
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) + str(stderr.decode().strip())
    cresult = f"<code>Bash:~$</code> <code>{cmd}</code>\n<code>{result}</code>"
    if len(cresult) > 4095:
        with io.BytesIO(cresult.encode()) as finale:
            finale.name = "bash.txt"
            return await e.respond(f"`{cmd}`", file=finale)
    await e.respond(cresult, parse_mode="html")


@command(pattern="auth")
@Master
async def auth(e):
    user = await get_user(e)
    if not user:
        return
    await e.reply("user Added to Auth\n")
    auth_user(user.id)


@command(pattern="deauth")
@Master
async def deauth(e):
    user = await get_user(e)
    if not user:
        return
    await e.reply("user Removed from Auth\n")
    unauth_user(user.id)


async def get_user(e: telethon.events.NewMessage.Event):
    user: telethon.tl.types.User
    if e.is_reply:
        user = (await e.get_reply_message()).sender
    else:
        args = e.text.split(maxsplit=1)
        if len(args) == 1:
            await e.reply("No user specified")
            return
        try:
            user = await e.client.get_entity(args[1])
        except telethon.errors.UserNotFoundError:
            await e.reply("No user found")
            return
    if user.bot:
        await e.reply("Bots can't be authed")
        return
    return user


@command(pattern="authlist")
@auTH
async def authlist(e):
    await e.reply("**Auth List:**\n" + '\n'.join(str(x) for x in AUTH))

importlib.import_module("quotly", "quotly.py")
importlib.import_module("dev", "dev.py")
importlib.import_module("song", "song.py")
importlib.import_module("torr", "torr.py")
bot.run_until_disconnected()
