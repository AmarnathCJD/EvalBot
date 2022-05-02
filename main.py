import telethon
from config import AUTH, auTH, command, Master
import sys, io, traceback, asyncio


@command(pattern="ping")
async def ping(event):
    await event.reply("pong")


@command(pattern="eval")
@auTH
async def eval(e):
    cmd = e.text.split(" ", 1)
    if len(cmd) == 1:
        await e.reply("No code provided")
        return
    cmd = cmd[1]
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    ros = sys.stdout = io.StringIO()
    red = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, e)
    except Exception:
        exc = traceback.format_exc()
    stdout = ros.getvalue()
    stderr = red.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = (
        "__►__ **EVALPy**\n```{}``` \n\n __►__ **OUTPUT**: \n```{}``` \n".format(
            cmd,
            evaluation,
        )
    )
    if len(evaluation) > 4095:
        with io.BytesIO(evaluation.encode()) as finale:
            finale.name = "eval.txt"
            return await e.reply(f"```{cmd}```", file=finale)
    await e.reply(final_output)


async def aexec(code, event):
    exec(
        f"async def __aexec(e, client): "
        + "\n message = event = e"
        + "\n reply = await event.get_reply_message()"
        + "\n p = print"
        + "".join(f"\n {l}" for l in code.split("\n")),
    )

    return await locals()["__aexec"](event, event.client)


@command(pattern="exec")
@auTH
async def exec(e):
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
    AUTH.append(user.id)


@command(pattern="deauth")
@Master
async def deauth(e):
    user = await get_user(e)
    if not user:
        return
    await e.reply("user Removed from Auth\n")
    AUTH.remove(user.id)

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
    await e.reply("\n".join(str(x) for x in AUTH))