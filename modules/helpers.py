import asyncio
from functools import wraps

import telethon

from ._config import OWNER_ID, bot
from ._db import AUTH

ERRORS = []


def command(**args):
    args["pattern"] = "^(?i)[?/!]" + args["pattern"] + "(?: |$|@ValerinaRobot)(.*)"

    def decorator(func):
        async def wrapper(ev):
            try:
                await func(ev)
            except Exception as e:
                ERRORS.append(e)
                await ev.reply(str(e))

        bot.add_event_handler(wrapper, telethon.events.NewMessage(**args))
        return func

    return decorator


def InlineQuery(**args):
    def decorator(func):
        async def wrapper(ev):
            try:
                await func(ev)
            except Exception as e:
                ERRORS.append(e)

        bot.add_event_handler(wrapper, telethon.events.InlineQuery(**args))
        return func

    return decorator


def Callback(**args):
    def decorator(func):
        async def wrapper(ev):
            try:
                await func(ev)
            except Exception as e:
                ERRORS.append(e)
                await ev.answer(str(e), alert=True)

        bot.add_event_handler(func, telethon.events.CallbackQuery(**args))
        return func

    return decorator


def auth(func):
    @wraps(func)
    async def sed(e):
        if e.sender_id and (e.sender_id in AUTH or e.sender_id == OWNER_ID):
            await func(e)
        else:
            await e.reply("You are not authorized to use this command")

    return sed


def master(func):
    @wraps(func)
    async def sed(e):
        if e.sender_id == OWNER_ID:
            await func(e)
        else:
            await e.reply("You are not authorized to use this command :SED")

    return sed


async def get_user(e: telethon.events.NewMessage.Event):
    user: telethon.tl.types.User
    arg = ""
    Args = e.text.split(maxsplit=2)
    if e.is_reply:
        user = (await e.get_reply_message()).sender
        arg = (Args[1] + (Args[2] if len(Args) > 2 else "")) if len(Args) > 1 else ""
    else:
        if len(Args) == 1:
            await e.reply("No user specified")
            return None, ""
        try:
            user = await e.client.get_entity(Args[1])
        except BaseException as ex:
            await e.reply(str(ex))
            return
        arg = Args[2] if len(Args) > 2 else ""
    return user, arg


async def HasRight(chat_id, user_id, right):
    if user_id == OWNER_ID:
        return True
    if user_id in AUTH:
        return True
    p = await bot(
        telethon.tl.functions.channels.GetParticipantRequest(chat_id, user_id)
    )
    p: telethon.tl.types.ChannelParticipant.to_dict
    if p.participant.admin_rights.to_dict()[right] == True:
        return True
    return False


async def getSender(e: telethon.events.NewMessage.Event):
    if e.sender != None:
        return e.sender
    else:
        if e.sender_chat != None:
            return e.sender_chat
        else:
            return None


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


async def bash(code):
    cmd = code.split(" ")
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) + str(stderr.decode().strip())
    return result


async def get_reply_image(v):
    if not v.reply_to:
        return None
    r = await v.get_reply_message()
    if not r.media:
        return None
    if isinstance(r.media, telethon.tl.types.MessageMediaDocument):
        if r.media.document.mime_type.split("/")[0] == "image":
            return r
        else:
            return None
    elif isinstance(r.media, telethon.tl.types.MessageMediaPhoto):
        return r
    else:
        return None


async def get_reply_gif(e):
    r = await e.get_reply_message()
    if not r.gif:
        return None
    return r


async def get_reply_video(e):
    r = await e.get_reply_message()
    if not r.video:
        return None
    return r
