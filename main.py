import os
from importlib import import_module

from modules._config import TOKEN, bot

bot.start(bot_token=TOKEN)


def __load_modules():
    for module in os.listdir("./modules"):
        if module.endswith(".py") and not module.startswith("_"):
            import_name = f"modules.{module[:-3]}"
            import_module(import_name, module)
            print(f"Loaded {import_name}")


__load_modules()

bot.run_until_disconnected()
