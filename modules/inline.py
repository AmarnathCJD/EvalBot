from requests import get
from telethon import events
from .helpers import InlineQuery

@InlineQuery(pattern="url")
async def _url(e):
    try:
        url = e.text.split(None, maxsplit=2)[1].split(None, maxsplit=2)[1]
    except IndexError:
        return await e.answer(
            [
                e.builder.article(
                    title="No URL Given.",
                    description="please provide a url to get its redirect output.",
                    text="No url was given, provide it get redirect url.",
                )
            ]
        )
    try:
        r = get(url, allow_redirects=True)
    except Exception as a:
        return await e.answer(
            [
                e.builder.article(
                    title="Error", description="URL unreachable.", text=str(a)
                )
            ]
        )
    if r.status_code == 302:
       return await e.answer(
            [
                e.builder.article(
                    title="Redirected (302)", description=str(r.url), text="Redirected, New URL: " + str(r.url)
                )
            ]
        )
    else:
        return await e.answer(
            [
                e.builder.article(
                    title="Sucess (" + str(r.status_code) + ")", description=str(r.url), text="Not Redirected, URL: " + str(r.url)
                )
            ]
        )
