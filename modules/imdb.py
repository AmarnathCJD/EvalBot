import os

from bs4 import BeautifulSoup
from requests import get
from telethon import Button

from ._db import DB
from .helpers import Callback, command

BASE_URL = "http://www.imdb.com"


def get_mov(url):
    s = get_page_soup(url)
    title = (
        s.find(class_="sc-b73cd867-0 eKrKux").text
        if s.find(class_="sc-b73cd867-0 eKrKux")
        else ""
    )
    year = (
        s.find(class_="sc-8c396aa2-2 itZqyK").text
        if s.find(class_="sc-8c396aa2-2 itZqyK")
        else ""
    )
    rating = (
        s.find(class_="sc-7ab21ed2-1 jGRxWM").text
        if s.find(class_="sc-7ab21ed2-1 jGRxWM")
        else ""
    )
    genres = get_genres(s)
    return {"title": title, "year": year, "rating": rating, "genres": genres}


def get_movie_url(title):
    url = BASE_URL + "/find?ref_=nv_sr_fn&q=" + title.replace(" ", "+")
    soup = get_page_soup(url)
    links = soup.find_all("a", href=True)
    for link in links:
        if link["href"].startswith("/title/"):
            return BASE_URL + link["href"]
    return None


def get_page_soup(url):
    response = get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def get_movie_info(url):
    soup = get_page_soup(url)
    movie = {
        "title": soup.find(class_="sc-b73cd867-0 eKrKux").text
        if soup.find(class_="sc-b73cd867-0 eKrKux")
        else "",
        "year": soup.find(class_="sc-8c396aa2-2 itZqyK").text
        if soup.find(class_="sc-8c396aa2-2 itZqyK")
        else "",
        "rating": soup.find(class_="sc-7ab21ed2-1 jGRxWM").text
        if soup.find(class_="sc-7ab21ed2-1 jGRxWM")
        else "",
        "genres": get_genres(soup),
        "videos": get_videos(soup),
        "images": get_images(soup),
        "details": get_crew_cast_info(soup),
    }
    print(movie)


def get_genres(soup):
    genres_ = soup.find(class_="ipc-chip-list sc-16ede01-4 bMBIRz")
    genr = []
    if genres_:
        for genre in genres_.find_all(class_="ipc-inline-list__item ipc-chip__text"):
            genr.append(genre.text)
    return genr


def get_videos(soup):
    soup = soup.find(
        class_="ipc-sub-grid ipc-sub-grid--page-span-2 ipc-sub-grid--nowrap ipc-shoveler__grid"
    )
    videos = []
    if videos:
        for video in soup.find_all(class_="ipc-lockup-overlay ipc-focusable"):
            url = BASE_URL + video["href"]
            aria_label = video["aria-label"]
            videos.append({"url": url, "name": aria_label})
    return videos


def get_images(soup):
    soup = soup.find(
        class_="ipc-sub-grid ipc-sub-grid--page-span-2 ipc-sub-grid--nowrap ipc-shoveler__grid"
    )
    images = []
    if images:
        for image in soup.find_all(class_="ipc-lockup-overlay ipc-focusable"):
            url = BASE_URL + image["href"]
            aria_label = image["aria-label"]
            images.append({"url": url, "name": aria_label})
    return images


def get_crew_cast_info(soup):
    cast = []
    for actor in soup.find_all(class_="sc-18baf029-7 eVsQmt"):
        name_ = actor.find(class_="sc-18baf029-1 gJhRzH")
        name = name_.text
        profile_url = BASE_URL + name_["href"]
        charector = actor.find(class_="sc-18baf029-5 hMdVSb").text
        episodes = (
            actor.find(class_="title-cast-item__episodes").text
            if actor.find(class_="title-cast-item__episodes")
            else None
        )
        cast.append(
            {
                "name": name,
                "profile_url": profile_url,
                "charector": charector,
                "episodes": episodes,
            }
        )
    creators = []
    for li in soup.find_all(class_="ipc-metadata-list__item"):
        if li.text.startswith("Creators"):
            for c in li.find_all("a"):
                if c.text not in creators:
                    creators.append(c.text)
    user_review = ""
    rev = soup.find(
        class_="ipc-list-card--border-speech ipc-list-card sc-1201338c-1 SmVod ipc-list-card--base"
    )
    if rev:
        user_review = rev.find(class_="ipc-html-content-inner-div").text
    story = ""
    story_line = soup.find(class_="ipc-page-section ipc-page-section--base celwidget")
    if story_line:
        story = story_line.find(class_="ipc-html-content-inner-div")
        if story:
            story = story.text
    language = soup.find({"testid": "title-details-languages"})
    if language:
        language = language.find(
            "a",
            class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link",
        )
        if language:
            language = language.text
    else:
        language = ""
    release_date = soup.find({"data-testid": "title-details-release-date"})
    if release_date:
        release_date = release_date.find(
            "a",
            class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link",
        ).text
    else:
        release_date = ""
    aka = ""
    aka_ = soup.find({"data-testid": "title-details-akas"})
    if aka_:
        aka = aka_.find("a", class_="ipc-metadata-list-item__list-content-item").text
    return {
        "cast": cast,
        "creators": creators,
        "user_review": user_review,
        "story": story,
        "language": language,
        "release_date": release_date,
        "aka": aka,
    }


@command(pattern="imdb")
async def imdb(e):
    try:
        movie_name = e.text.split(" ")[1]
    except IndexError:
        await e.edit("`Enter movie name`")
        return
    url = get_movie_url(movie_name)
    if not url:
        await e.edit("`Couldn't find the movie.`")
        return
    x = await e.reply("`Getting info...`")
    movie_info = get_mov(url)
    MOVIE = f"""
    🎬 **{movie_info['title']}**
    **Rating**: {movie_info['rating']}
    **Year**: {movie_info['year']}
    **Genres**: {movie_info['genres']}
    """
    await x.edit(MOVIE)


series = DB.series

IMDB_API = os.getenv("IMDB_KEY")


def add_series(user_id, series_id, name, watchtime):
    series_ = get_all_series(user_id)
    for i in series_:
        if i["series_id"] == series_id:
            return True
    series.update_one(
        {"user_id": user_id},
        {
            "$push": {
                "series": {"series_id": series_id, "name": name, "watchtime": watchtime}
            }
        },
        upsert=True,
    )
    return False


def get_all_series(user_id):
    q = series.find_one({"user_id": user_id})
    if q:
        return q.get("series")
    return []


def get_series_by_id(user_id, id):
    s = get_all_series(user_id)
    try:
        ser = s[id - 1]
    except IndexError:
        return None
    return ser


def rm_series(user_id, id):
    series.update_one(
        {"user_id": user_id},
        {"$pull": {"series": {"series_id": id}}},
        upsert=True,
    )


@command(pattern="watched")
async def _watched(e):
    try:
        query = e.text.split(None, maxsplit=1)[1]
    except IndexError:
        return await display_watched(e)
    params = {
        "api_key": IMDB_API,
        "language": "en-US",
        "query": query,
        "include_adult": "true",
        "page": "1",
    }
    r = get("https://api.themoviedb.org/3/search/multi", params=params)
    if r.status_code != 200:
        return await e.reply("`Something went wrong.`")
    data = r.json()
    if len(data["results"]) == 0:
        return await e.reply("`Couldn't find it.`")
    result = data["results"][0]
    if result["media_type"] == "tv":
        return await display_tv_series(e, result["id"])
    else:
        return await display_movie(e, result["id"])


async def display_tv_series(e, result_id):
    params = {"api_key": IMDB_API}
    r = get(f"https://api.themoviedb.org/3/tv/{result_id}", params=params)
    if r.status_code != 200:
        return await e.reply(f"`Error: {r.status_code}`")
    res = r.json()
    if res["number_of_seasons"] == 0:
        return await e.reply("`No seasons found!`")
    seasons = res["number_of_seasons"]
    runtime = res["episode_run_time"][0]
    episodes = res["number_of_episodes"]
    tagline = res["tagline"]
    if tagline:
        tagline = f"       -`{tagline}`"
    else:
        tagline = ""
    s = add_series(
        e.sender_id, result_id, res["name"], get_watchtime(runtime, episodes, True)
    )
    watchtime = f"**Watchtime**: +{get_watchtime(runtime, episodes)}"
    if s:
        return await e.reply("Already in watched list!\n" f"**Title**: {res['name']}\n")
    status = f"**Status**: {res['status']}" if res["status"] else ""
    seasons = f"**S**: {seasons} | **E**: {episodes}"
    POSTER = f"https://image.tmdb.org/t/p/original{res['poster_path']}"
    try:
        await e.reply(
            f"**Added __{res['name']}__  to watched List**\n{tagline}\n{status}\n{seasons}\n{watchtime}",
            file=POSTER,
        )
    except:
        await e.reply(
            f"**Added __{res['name']}__  to watched List**\n{tagline}\n{status}\n{seasons}\n{watchtime}",
        )


async def display_movie(e, result_id):
    params = {"api_key": IMDB_API}
    r = get(f"https://api.themoviedb.org/3/movie/{result_id}", params=params)
    if r.status_code != 200:
        return await e.reply(f"`Error: {r.status_code}`")
    res = r.json()
    runtime = res["runtime"]
    tagline = res["tagline"]
    imdb_id = res["imdb_id"]
    release_date = res["release_date"]
    status = res["status"]
    if tagline:
        tagline = f"       -`{tagline}`"
    else:
        tagline = ""
    s = add_series(
        e.sender_id, result_id, res["title"], get_watchtime(runtime, 1, True)
    )
    if s:
        return await e.reply(
            "Already in watched list!\n" f"**Title**: {res['title']}\n"
        )
    watchtime = f"**Watchtime**: +{get_watchtime(runtime, 1)}"
    status = f"**Status**: {res['status']}" if res["status"] else ""
    release_date = f"**Release Date**: {release_date}" if release_date else ""
    imdb_id = f"**IMDB ID**: `{imdb_id}`" if imdb_id else ""
    POSTER = f"https://image.tmdb.org/t/p/original{res['poster_path']}"
    try:
        await e.reply(
            f"**Added __{res['title']}__  to watched List**\n{tagline}\n{status}\n{release_date}\n{imdb_id}\n{watchtime}",
            file=POSTER,
        )
    except:
        await e.reply(
            f"**Added __{res['title']}__  to watched List**\n{tagline}\n{status}\n{release_date}\n{imdb_id}\n{watchtime}"
        )


def get_watchtime(runtime, episodes=1, isint=False):
    w = int(runtime) * int(episodes)
    if isint:
        return int(w)
    if w > 60:
        return f"{int(w / 60)} hours"
    else:
        return f"{w} mins"


def format_time(time):
    hours = time // 60
    minutes = time % 60  # %
    return "{}h {}mins".format(hours, minutes)


async def display_watched(e):
    user_id = e.sender_id
    series = get_all_series(user_id=user_id)
    if len(series) == 0:
        return await e.reply("`You haven't watched any series yet!`")
    t = get_series_text(series)
    buttons = None
    if len(t.split("\n")) > 15:
        buttons = [Button.inline("➡️ Next", data="nxt_{}_{}".format(user_id, 2))]
    await e.respond(
        t, parse_mode="html", reply_to=e.reply_to_msg_id or e.id, buttons=buttons
    )


@Callback(pattern="nxt_(.*?)_(.*?)")
async def _next_page(e):
    user_id = int(e.match.group(1))
    page = int(e.match.group(2))
    series = get_all_series(user_id=user_id)
    t = get_series_text(series)
    buttons = [
        Button.inline("➡️ Next", data="nxt_{}_{}".format(user_id, page + 1)),
        Button.inline("⬅️ Previous", data="prev_{}_{}".format(user_id, page - 1)),
    ]
    await e.edit(t, buttons=buttons, parse_mode="html")


@Callback(pattern="prev_(.*)_(.*)")
async def _prev_page(e):
    user_id = int(e.match.group(1))
    page = int(e.match.group(2))
    series = get_all_series(user_id=user_id)
    t = get_series_text(series)
    buttons = (
        [
            Button.inline("➡️ Next", data="nxt_{}_{}".format(user_id, page + 1)),
            Button.inline("⬅️ Previous", data="prev_{}_{}".format(user_id, page - 1)),
        ]
        if page > 1
        else [Button.inline("➡️ Next", data="nxt_{}_{}".format(user_id, page + 1))]
    )
    await e.edit(t, buttons=buttons, parse_mode="html")


def paginate(s, page_number):
    lines = s.split("\n")
    chunks = [lines[i : i + 15] for i in range(0, len(lines), 15)]
    return "\n".join(chunks[page_number - 1])


def get_series_text(series, page_no=1):
    text = "<u><b>Watched Series</b></u>\n"
    q = 0
    wt = 0
    y = ""
    for i in series:
        q += 1
        y += f"{q}. -><b>{i['name']}</b> ({format_time(i['watchtime'])})\n"
        wt += int(i["watchtime"])
    text += paginate(y, page_no)
    text += f"\n<b>Total Watchtime</b>: {format_time(wt)} \n"
    return text


# soon


@command(pattern="rmwatched")
async def _rmwatched(e):
    try:
        query = e.text.split(None, maxsplit=1)[1]
    except IndexError:
        return await e.reply("`What should i remove?`")
    if not query.isdigit():
        return await e.reply("`Usage: /rmwatched <series number>`")
    s = get_series_by_id(e.sender_id, int(query))
    if not s:
        return await e.reply("`Series not found!`")
    text = "Are you sure you want to remove {} from your watched list?".format(
        s["name"]
    )
    await e.reply(
        text,
        buttons=[
            Button.inline("Yes", data="rmwatched_yes_{}".format(s["series_id"])),
            Button.inline("No", data="rmwatched_no_{}".format(s["series_id"])),
        ],
    )


@Callback(pattern="rmwatched_(.*)_(.*)")
async def rmwatched_yes(e):
    data = e.data.decode("utf-8").split("_")
    series_id = data[2]
    rm_series(e.sender_id, series_id)
    await e.edit("`Removed from watched list!`")


@Callback(pattern="cancelrmwatched")
async def rmwatched_no(e):
    await e.edit("`Cancelled!`")
