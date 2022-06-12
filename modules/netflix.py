import asyncio
import base64
import io
import random
import string

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


def setup_browser(new=False):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    b = webdriver.Chrome(chrome_options=chrome_options)
    return b


def xpath(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:  # type: bs4.element.Tag
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name
            if 1 == len(siblings)
            else "%s[%d]"
            % (child.name, next(i for i, s in enumerate(siblings, 1) if s is child))
        )
        child = parent
    components.reverse()
    return "/%s" % "/".join(components)


def gen_email():
    CHAR = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(CHAR) for a in range(10)) + "@gmail.com"


async def enter_details(email: str, password: str, browser):
    EMAIL_TAG = browser.find_element_by_xpath(
        "/html/body/div[1]/div/div/div/div/div/div[2]/div[1]/div[2]/form/div/ul/li/div/div/label/input"
    )
    EMAIL_TAG.clear()
    EMAIL_TAG.send_keys(email)
    browser.find_element_by_xpath(
        "/html/body/div[1]/div/div/div/div/div/div[2]/div[1]/div[2]/form/div/div/button"
    ).click()
    await asyncio.sleep(0.27)
    browser.find_element_by_xpath(
        "/html/body/div[1]/div/div/div[2]/div/div[2]/button"
    ).click()
    await asyncio.sleep(0.27)
    PASSWORD_TAG = browser.find_element_by_xpath(
        "/html/body/div[1]/div/div/div[2]/div/form/div/div[1]/div[2]/ul/li[2]/div/div/label/input"
    )
    PASSWORD_TAG.clear()
    PASSWORD_TAG.send_keys(password)
    PASSWORD_TAG.send_keys(Keys.ENTER)
    await asyncio.sleep(0.27)


async def send_photo(browser, e):
    with io.BytesIO(base64.b64decode(browser.get_screenshot_as_base64())) as f:
        f.name = "screenshot.png"
        await e.respond(file=f)


async def setup_netflix(email=""):
    _email = gen_email() if email == "" else email
    browser = setup_browser()
    browser.get("https://netflix.com")
    await enter_details(_email, "qwerty123#", browser)
    return browser
