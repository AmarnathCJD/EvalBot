from functools import wraps
import os
from dotenv import load_dotenv
import telethon

AUTH = []

import logging

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.WARNING,
)

def init_vars():
    load_dotenv()
    if not all(
        key in os.environ for key in ["API_KEY", "API_HASH", "TOKEN", "OWNER_ID"]
    ):
        print("Please setup API_KEY, API_HASH, TOKEN and OWNER_ID")
        for key in ["API_KEY", "API_HASH", "TOKEN", "OWNER_ID"]:
            if key not in os.environ:
                try:
                    value = input(f"{key}: ")
                except (KeyboardInterrupt, EOFError):
                    print("\nExiting...")
                    exit(1)
                os.environ[key] = value
        with open(".env", "w") as f:
            for key in ["API_KEY", "API_HASH", "TOKEN", "OWNER_ID"]:
                f.write(f"{key}={os.environ[key]}\n")
    return {
        "API_KEY": os.environ["API_KEY"],
        "API_HASH": os.environ["API_HASH"],
        "TOKEN": os.environ["TOKEN"],
        "OWNER_ID": os.environ["OWNER_ID"],
    }


env = init_vars()


def init_bot():
    bot = telethon.TelegramClient(
        "bot", api_id=env["API_KEY"], api_hash=env["API_HASH"]
    )
    bot.start(bot_token=env["TOKEN"])
    return bot


bot = init_bot()


def command(**args):
    args["pattern"] = "^(?i)[?/!]" + args["pattern"]

    def decorator(func):
        bot.add_event_handler(func, telethon.events.NewMessage(**args))
        return func

    return decorator


def auTH(func):
    @wraps(func)
    async def sed(e):
        if e.sender_id and e.sender_id in AUTH:
            await func(e)
        else:
            await e.reply("You are not authorized to use this command")

    return sed


def Master(func):
    @wraps(func)
    async def sed(e):
        if e.sender_id == int(env["OWNER_ID"]):
            await func(e)
        else:
            await e.reply("You are not authorized to use this command")

    return sed
