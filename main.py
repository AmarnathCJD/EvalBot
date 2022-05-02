import telethon
from config import AUTH, auTH, command, Master, bot
import sys, io, traceback, asyncio, logging 


@command(pattern="ping")
async def ping(event):
    await event.reply("pong")


@command(pattern="eval")
@auTH
async def _eval(e):
        cmd = e.text.split(" ", maxsplit=1)[1]
        if e.reply_to:
            await e.get_reply_message()
        old_stderr = sys.stderr
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        redirected_error = sys.stderr = io.StringIO()
        stdout, stderr, exc = None, None, None
        try:
            await aexec(cmd, e)
        except Exception:
            exc = traceback.format_exc()
        stdout = redirected_output.getvalue()
        stderr = redirected_error.getvalue()
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        evaluation = ""
        if exc:
            evaluation = exc
        elif stderr:
            evaluation = stderr
        elif stdout:
            evaluation = stdout
        else:
            evaluation = "Success"
        final_output = "`{}`".format(evaluation)
        MAX_MESSAGE_SIZE_LIMIT = 4095
        if len(final_output) > MAX_MESSAGE_SIZE_LIMIT:
            with io.BytesIO(str.encode(final_output)) as out_file:
                out_file.name = "eval.text"
                await e.client.send_file(
                    e.chat_id,
                    out_file,
                    force_document=True,
                    allow_cache=False,
                    caption=cmd,
                )
        else:
            await e.respond(final_output)

async def aexec(code, event):

    def p(_x):
        return print(slitu.yaml_format(_x))

    reply = await event.get_reply_message()
    r = exec(
        "async def __aexec(event, reply, client, p): "
        + "\n e = event"
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    await event.reply(str(await r))
    return await locals()["__aexec"](event, reply, event.client, p)


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

bot.run_until_disconnected()    
