import telethon
from requests import exceptions, get
from telethon import Button

from .helpers import InlineQuery

REDIRECT_THUMB = "https://img.icons8.com/external-flaticons-lineal-color-flat-icons/64/undefined/external-redirect-internet-marketing-flaticons-lineal-color-flat-icons-2.png"


async def answer_query(
    e: telethon.events.InlineQuery.Event, title, text, desc, thumb, buttons
):
    builder = e.builder
    result = builder.article(title=title, text=text, description=desc, buttons=buttons)
    await e.answer([result])


@InlineQuery(pattern="url")
async def _url(e):
    try:
        q = e.text.split(" ")[1]
    except IndexError:
        return await answer_query(
            e,
            "Error",
            "No URL provided",
            "Provide Any url to get its Redirect Link",
            REDIRECT_THUMB,
            [Button.switch_inline("Try Again", "url", True)],
        )
    try:
        r = get(q, allow_redirects=True, timeout=10)
    except exceptions.ConnectionError:
        return await answer_query(
            e,
            "Error",
            "Connection Error",
            "Provide Any url to get its Redirect Link",
            REDIRECT_THUMB,
            [Button.switch_inline("Try Again", "url", True)],
        )
    except exceptions.Timeout:
        return await answer_query(
            e,
            "Error",
            "Timeout Error",
            "Provide Any url to get its Redirect Link",
            REDIRECT_THUMB,
            [Button.switch_inline("Try Again", "url", True)],
        )
    except exceptions.TooManyRedirects:
        return await answer_query(
            e,
            "Error",
            "Too Many Redirects",
            "Provide Any url to get its Redirect Link",
            REDIRECT_THUMB,
            [Button.switch_inline("Try Again", "url", True)],
        )
    except exceptions.HTTPError:
        return await answer_query(
            e,
            "Error",
            "HTTP Error",
            "Provide Any url to get its Redirect Link",
            REDIRECT_THUMB,
            [Button.switch_inline("Try Again", "url", True)],
        )
    URL_STAT = "`URL Status:` **" + str(r.status_code) + "**"
    URL_STAT += "\n`URL Content Type:` **" + str(r.headers["Content-Type"]) + "**"
    URL_STAT += "\n`URL Content Length:` **" + str(r.headers["Content-Length"]) + "**"
    URL_STAT += "\n`Response Time:` **" + str(r.elapsed.total_seconds()) + "**"
    URL_STAT += "\n`Redirect URL:` **" + str(r.url) + "**"
    URL_STAT += "\n`IP Address:` **" + str(r.headers["X-Client-IP"]) + "**"
    await answer_query(
        e,
        "Redirect Link (" + str(r.status_code) + ")",
        "Redirect Link: " + r.url,
        "",
        REDIRECT_THUMB,
        [Button.url("OPEN URL", r.url)],
    )
