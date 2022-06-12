import base64
import io

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def setup_browser(new=False):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
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


def enter_email(email: str, browser):
    EMAIL_TAG = browser.find_element_by_xpath(
        "/html/body/div[1]/div/div/div/div/div/div[2]/div[1]/div[2]/form/div/ul/li/div/div/label/input"
    )
    EMAIL_TAG.clear()
    EMAIL_TAG.send_keys(email)
    if EMAIL_TAG.get_attribute("value") != "":
        return True
    return False


def get_started(browser):
    BTN = browser.find_element_by_xpath(
        "/html/body/div[1]/div/div/div/div/div/div[2]/div[1]/div[2]/form/div/div/button"
    )
    if BTN:
        BTN.click()


async def send_photo(browser, e):
    with io.BytesIO(base64.b64decode(browser.get_screenshot_as_base64())) as f:
        f.name = "screenshot.png"
        await e.respond(file=f)


def setup_netflix(email=""):
    browser = setup_browser()
    browser.get("https://netflix.com")
    if email != "":
        enter_email(email, browser)
        get_started(browser)
    return browser
