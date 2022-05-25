from bs4 import BeautifulSoup
from requests import get

from .helpers import command

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
