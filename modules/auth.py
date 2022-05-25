from ._config import OWNER_ID
from ._db import AUTH, auth_user, unauth_user
from .helpers import command, get_user


@command(pattern="auth|deauth|authlist")
async def _auth(e):
    user, arg = await get_user(e)
    if not user:
        return
    if user.bot:
        await e.reply("Bots can't be authed")
        return
    if user.id == OWNER_ID:
        await e.reply("You can't auth the owner")
        return
    elif user.id == e.sender_id:
        await e.reply("You can't auth yourself")
        return
    if e.text.split()[0][1:] == "authlist":
        await e.reply("**Auth List:**\n" + "\n".join(str(x) for x in AUTH))
        return
    if user.id in AUTH:
        unauth_user(user.id)
        await e.reply("user Removed from Auth\n")
    else:
        await e.reply("user Added to Auth\n")
        auth_user(user.id)
