import base64
import io

from requests import post
from telethon import types
from config import command
from webcolors import hex_to_name, name_to_hex


@command(pattern="(q|quote)")
async def _quotly_api_(e):
    if not e.reply_to:
        return await e.reply("This has to be send while replying to a message.")
    r = await e.get_reply_message()
    try:
        d = e.text.split(maxsplit=1)[1]
    except IndexError:
        d = ""
    color = None
    for y in d.split():
        try:
            color, g = name_to_hex(y), "hex"
        except ValueError:
            try:
                color, g = hex_to_name(y), "name"
            except ValueError:
                continue
    if color:
        d = d.replace(hex_to_name(color) if g == "hex" else color, "")
    else:
        color = "#1b1429"
    photo = True if "p" in d else False
    messages = []
    num = [int(x) for x in d.split() if x.isdigit()]
    num = num[0] if num else None
    msgs = (
        [
            i
            async for i in e.client.iter_messages(
                e.chat_id,
                ids=list(range(e.reply_to_msg_id, e.reply_to_msg_id + num)),
            )
            if i
        ]
        if num
        else [r]
    )
    c = [1]
    for _x in msgs:
        if _x:
            if _x.sender and isinstance(_x.sender, types.Channel):
                _name = _x.chat.title
                _first_name = _last_name = _username = ""
                _id = _x.chat_id
                _title = "Admin"
            elif _x.sender and isinstance(_x.sender, types.User):
                _name = _x.sender.first_name
                _name = _name + _x.sender.last_name if _x.sender.last_name else _name
                if _x.fwd_from and _x.fwd_from.from_name:
                    _name = _x.fwd_from.from_name
                _first_name = _x.sender.first_name
                _last_name = _x.sender.last_name
                _username = _x.sender.username
                _id = _x.sender_id
                _title = "Admin"
            elif not _x.sender:
                _name = _x.chat.title
                _first_name = _last_name = _x.chat.title
                _username = ""
                _id = _x.chat_id
                _title = "Anon"
            _text = _x.raw_text or ""
            _from = {
                "id": _id,
                "first_name": _first_name,
                "last_name": _last_name,
                "username": _username,
                "language_code": "en",
                "title": _title,
                "type": "group",
                "name": _name if c[-1] != _id else "",
            }
            if len(msgs) == 1:
                if _x.reply_to and "r" in d:
                    reply = await _x.get_reply_message()
                    if isinstance(reply.sender, types.Channel):
                        _r = {
                            "chatId": e.chat_id,
                            "first_name": reply.chat.title,
                            "last_name": "",
                            "username": reply.chat.username,
                            "text": reply.text,
                            "name": reply.chat.title,
                        }
                    elif reply.sender:
                        name = reply.sender.first_name
                        name = (
                            name + " " + reply.sender.last_name
                            if reply.sender.last_name
                            else name
                        )
                        if reply.fwd_from and reply.fwd_from.from_name:
                            _name = reply.fwd_from.from_name
                        _r = {
                            "chatId": e.chat_id,
                            "first_name": reply.sender.first_name,
                            "last_name": "reply.sender.last_name",
                            "username": reply.sender.username,
                            "text": reply.text,
                            "name": name,
                        }
                    else:
                        _r = {}
                else:
                    _r = {}
            else:
                _r = {}
            if _x.sticker:
                mediaType = "sticker"
                media = [
                    {
                        "file_id": _x.file.id,
                        "file_size": _x.file.size,
                        "height": _x.file.height,
                        "width": _x.file.width,
                    }
                ]
            elif _x.photo:
                mediaType = "photo"
                media = [
                    {
                        "file_id": _x.file.id,
                        "file_size": _x.file.size,
                        "height": _x.file.height,
                        "width": _x.file.width,
                    }
                ]
            else:
                media = None
            avatar = True
            if c[-1] == _id:
                avatar = False
            c.append(_id)
            if not media:
                messages.append(
                    {
                        "entities": get_entites(_x),
                        "chatId": e.chat_id,
                        "avatar": avatar,
                        "from": _from,
                        "text": _text,
                        "replyMessage": _r,
                    }
                )
            elif media:
                messages.append(
                    {
                        "chatId": e.chat_id,
                        "avatar": avatar,
                        "media": media,
                        "mediaType": mediaType,
                        "from": _from,
                        "replyMessage": {},
                    }
                )
    post_data = {
        "type": "quote",
        "backgroundColor": color,
        "width": 512,
        "height": 768,
        "scale": 2,
        "messages": messages,
    }
    req = post(
        "https://bot.lyo.su/quote/generate",
        headers={"Content-type": "application/json"},
        json=post_data,
    )
    try:
        fq = req.json()["result"]["image"]
        with io.BytesIO(base64.b64decode((bytes(fq, "utf-8")))) as f:
            f.name = "sticker.png" if photo else "sticker.webp"
            qs = await e.respond(file=f, buttons=None, force_document=photo)
    except Exception as ep:
        await e.reply("error: " + str(ep))


def get_entites(x):
    q = []
    for y in x.entities or []:
        if isinstance(y, types.MessageEntityCode):
            type = "code"
        elif isinstance(y, types.MessageEntityBold):
            type = "bold"
        elif isinstance(y, types.MessageEntityItalic):
            type = "italic"
        elif isinstance(y, types.MessageEntityBotCommand):
            type = "bot_command"
        elif isinstance(y, types.MessageEntityUrl):
            type = "url"
        elif isinstance(y, types.MessageEntityEmail):
            type = "email"
        elif isinstance(y, types.MessageEntityPhone):
            type = "phone_number"
        elif isinstance(y, types.MessageEntityUnderline):
            type = "underline"
        elif isinstance(y, types.MessageEntityMention):
            type = "mention"
        else:
            continue
        q.append({"type": type, "offset": y.offset, "length": y.length})
    return q

# qtop, qrate, qrand removed
