from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME = []


def browser(new=False):
    if not new and len(CHROME) != 0:
        return CHROME[0]
    CHROME.empty()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    b = webdriver.Chrome(chrome_options=chrome_options)
    CHROME.append(b)
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
    return EMAIL_TAG.text or "Failed to enter email."
