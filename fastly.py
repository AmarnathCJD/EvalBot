from telethon import TelegramClient, events
from telethon.sessions import StringSession 
from requests import post
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

load_dotenv()
STRING = os.getenv('STRING')
API_KEY = os.getenv('API_KEY')
API_HASH = os.getenv('API_HASH')
OCR_API_KEY = os.getenv('OCR_KEY')

OCR_URL = 'https://api.api-ninjas.com/v1/imagetotext'
HEADERS = {'X-Api-Key': OCR_API_KEY}

c = TelegramClient(StringSession(STRING), API_KEY, API_HASH)
c.start()

@c.on(events.NewMessage(from_users=[1877720720]))
async def _fastly(e):
 if not e.photo:
    return
 p = await e.download_media('ocr.jpg')
 _req = post(OCR_URL, headers=HEADERS, files={'image': open(p, 'rb')})
 data = _req.json()
 logging.info(data)
 _text = data[0]['text']
 await e.respond(str(_text))
 os.remove('ocr.jpg')

@c.on(events.NewMessage(pattern='ocr'))
async def _f(e):
 r = await e.get_reply_message()
 if not r or not r.photo:
    return
 p = await r.download_media('ocr.jpg')
 _req = post(OCR_URL, headers=HEADERS, files={'image': open(p, 'rb')})
 data = _req.json()
 logging.info(data)
 _text = data[0]['text']
 await e.respond(str(_text))
 os.remove('ocr.jpg')
 
c.run_until_disconnected()
