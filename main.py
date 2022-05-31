from modules._config import TOKEN, __load_modules, bot

bot.start(bot_token=TOKEN)

__load_modules()

bot.run_until_disconnected()
