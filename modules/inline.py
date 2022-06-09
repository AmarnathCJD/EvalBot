from requests import get

from .helpers import InlineQuery


@InlineQuery(pattern="url")
async def _url(e):
    try:
        url = e.text.split(" ", maxsplit=3)[2]
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
