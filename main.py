from modules._config import TOKEN, bot, __load_modules

bot.start(bot_token=TOKEN)

__load_modules()

bot.run_until_disconnected()
