from os import getenv

import requests
from bs4 import BeautifulSoup

from modules.helpers import command


def upload_img(filePath):
    searchUrl = "http://www.google.hr/searchbyimage/upload"
    multipart = {"encoded_image": (filePath, open(filePath, "rb")), "image_content": ""}
    response = requests.post(searchUrl, files=multipart, allow_redirects=False)
    fetchUrl = response.headers["Location"]
    return fetchUrl


def fetch_img(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
    }
    response = requests.get(
        url,
        headers=headers,
        verify=False,
    )
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def collect_results(soup):
    results = []
    for result in soup.find_all(class_="jtfYYd"):
        title = (
            result.find(class_="LC20lb").text if result.find(class_="LC20lb") else ""
        )
        if not title:
            continue
        url = result.find("a")["href"] if result.find("a") else ""
        description = (
            result.find_all("span")[-1].text if result.find_all("span") else ""
        )
        results.append({"title": title, "url": url, "description": description})

    title = soup.find(class_="fKDtNb").text if soup.find(class_="fKDtNb") else ""
    return results, title


@command(pattern="reverse")
async def _reverse(e):
    r = await e.get_reply_message()
    if not r or not r.media:
        await e.edit("`Reply to a photo or sticker to reverse it.`")
        return
    rp = await e.reply("`Processing...`")
    p = await e.client.download_media(r.media)
    results, title = collect_results(fetch_img(upload_img(p)))
    if not results:
        await rp.edit("`Couldn't find anything in reverse search.`")
        return
    RESULT = f"**Search Query:**\n`{title}`\n\n**Results:**\n"
    q = 0
    for result in results:
        q += 1
        RESULT += f"`{q}.` [{result['title']}]({result['url']})\n"
        if q == 5:
            break
    await rp.edit(RESULT)


# INSTAGRAM DL
IG_SESSION_ID = getenv("IG_SESSION_ID")


@command(pattern="igdl")
async def _igdl(e):
    try:
        url = e.text.split(" ")[1]
    except IndexError:
        await e.reply("`Usage: .igdl <url>`")
        return
    url = url + "&__a=1"
    cookies = {
        "sessionid": IG_SESSION_ID,
    }
    data = requests.get(url, cookies=cookies).json()
    try:
        caption = data["items"][0]["caption"]["text"]
    except KeyError:
        caption = ""
    VID = False
    if data["items"][0].get("video_versions"):
        if len(data["items"][0]["video_versions"]) > 0:
            IMAGE = data["items"][0]["video_versions"][0]["url"]
            VID = True
    else:
        try:
            images = data["items"][0]["carousel_media"][0]["image_versions2"][
                "candidates"
            ]
            HEIGHT = 0
            IMAGE = ""
            for i in images:
                if i["width"] > HEIGHT:
                    HEIGHT = i["width"]
                    IMAGE = i["url"]
            if not IMAGE:
                return await e.reply("`Couldn't find any images in this post.`")
        except KeyError:
            return await e.reply("`Couldn't find any images in this post.`")
    async with e.client.action(e.chat_id, ("photo" if not VID else "video")):
        await e.client.send_file(e.chat_id, IMAGE, caption=caption)
