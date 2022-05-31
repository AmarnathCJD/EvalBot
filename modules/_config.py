import logging
from importlib import import_module
from os import environ, getenv, listdir, path

from dotenv import load_dotenv
from pymongo import MongoClient, errors
from telethon import TelegramClient

load_dotenv()

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

TOKEN = getenv("TOKEN")
API_KEY = getenv("API_KEY")
API_HASH = getenv("API_HASH")
OWNER_ID = int(getenv("OWNER_ID", 0))
MONGO_URI = getenv("MONGO_URI")

for key in ["API_KEY", "API_HASH", "TOKEN", "OWNER_ID", "MONGO_URI"]:
    if not getenv(key):
        print(f"Please setup {str(key)}")
        try:
            value = input(f"{str(key)}: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            exit(1)
        environ[str(key)] = value
    if not path.exists(".env"):
        with open(".env", "w") as f:
            for key in ["API_KEY", "API_HASH", "TOKEN", "OWNER_ID", "MONGO_URI"]:
                if key in environ:
                    f.write(f"{str(key)}={environ[str(key)]}\n")

bot = TelegramClient(None, api_id=API_KEY, api_hash=API_HASH)
db = MongoClient(MONGO_URI)

try:
    db.list_database_names()
except errors.ServerSelectionTimeoutError:
    print("Failure to connect to MongoDB")

DB = db.get_database("bot")


def __load_modules():
    for module in listdir("./modules"):
        if module.endswith(".py") and not module.startswith("_"):
            import_name = f"modules.{module[:-3]}"
            import_module(import_name, module)
            print(f"Loaded {import_name}")
