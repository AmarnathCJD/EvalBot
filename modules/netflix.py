import asyncio
import base64
import io
import os
import random
import string

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from modules.helpers import command


def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    b = webdriver.Chrome(options=chrome_options)
    b.delete_all_cookies()
    return b


def fb(b):
    s = b.page_source
    s = BeautifulSoup(s, "html.parser")
    b = s.findAll("button")
    for x in b:
        print(xpath(x))


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


def progress_bar(percentage) -> str:
    return "|" * int(percentage) + " " * (100 - int(percentage))


def gen_email():
    CHAR = string.ascii_letters
    return "".join(random.choice(CHAR) for a in range(10)) + "@gmail.com"


async def enter_details(payload: dict, browser: webdriver.Chrome):
    email = payload["email"]
    password = payload["password"]
    msg = payload["msg"]
    EMAIL_TAG = browser.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div/div/div/div/div[2]/div[1]/div[2]/form/div/ul/li/div/div/label/input",
    )
    EMAIL_TAG.clear()
    EMAIL_TAG.send_keys(email)
    EMAIL_TAG.send_keys(Keys.ENTER)
    await asyncio.sleep(1)
    msg = await msg.edit("Entering Details" + progress_bar(10))
    try:
        browser.find_element(
            by=By.XPATH, value="/html/body/div[1]/div/div/div[2]/div/div[2]/button"
        ).click()
    except:
        pass
    await asyncio.sleep(1)
    try:
        pwd = browser.find_element(By.NAME, "password")
        pwd.clear()
        pwd.send_keys(password)
        pwd.send_keys(Keys.ENTER)
    except:
        pass
    await asyncio.sleep(1.27)
    msg = await msg.edit("Entering Details" + progress_bar(30))
    try:
        browser.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[2]/button"
        ).click()
    except:
        pass
    await asyncio.sleep(1)

    wait = WebDriverWait(browser, 10)
    try:
        browser.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[2]/button"
        ).click()
    except:
        pass
    await asyncio.sleep(1)
    msg = await msg.edit("Entering Details" + progress_bar(60))
    try:
        browser.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/div[3]/div[2]/div[1]/a"
        ).click()
    except:
        pass
    wait.until(EC.element_to_be_clickable((By.ID, "id_firstName")))
    browser.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div/div[2]/div/form/div[1]/div[2]/ul[1]/li[1]/div/div[1]/label/input",
    ).send_keys("Jenna Smith")
    browser.find_element(By.ID, "id_lastName").send_keys("Smith")
    browser.find_element(By.ID, "id_creditCardNumber").send_keys(payload["cc_number"])
    browser.find_element(By.ID, "id_creditExpirationMonth").send_keys(
        payload["cc_exp_date"]
    )
    browser.find_element(By.ID, "id_creditCardSecurityCode").send_keys(
        payload["cc_cvv"]
    )
    TERMS = browser.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div/div[2]/div/form/div[1]/div[2]/div/div/div/input",
    )
    browser.execute_script("arguments[0].click();", TERMS)
    msg = await msg.edit("Entering Details" + progress_bar(80))
    browser.find_element(
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/form/div[2]/button"
    ).click()
    msg = await msg.edit("Entering Details" + progress_bar(100))
    try:
        wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "messageContainer"))
        )
    except TimeoutException:
        return True
    element = browser.find_element(By.CLASS_NAME, "messageContainer")
    with open("screenshot.png", "wb") as f:
        f.write(base64.b64decode(element.screenshot_as_base64.encode()))
    return False


async def send_photo(browser, e):
    with io.BytesIO(base64.b64decode(browser.get_screenshot_as_base64())) as f:
        f.name = "screenshot.png"
        await e.respond(file=f)


def show_screenshot(browser):
    image = browser.get_screenshot_as_base64()
    with open("screenshot.png", "wb") as f:
        f.write(base64.b64decode(image))


async def setup_netflix(payload: dict):
    browser = setup_browser()
    browser.get("https://netflix.com")
    return write_response(
        payload["email"],
        payload["password"],
        await enter_details(payload, browser),
        browser,
    )


def write_response(email, password, resp: bool, browser: webdriver.Chrome):
    if resp:
        RESULT = "Netflix account created successfully"
        RESULT += "\nEmail: " + email
        RESULT += "\nPassword: " + password
    else:
        RESULT = "Netflix account creation failed"
        RESULT += (
            '\nError: "'
            + browser.find_element(By.CLASS_NAME, "messageContainer").text
            + '"'
        )
    return RESULT, resp


@command(pattern="netflix")
async def _nfgen(e):
    msg = await e.respond("🔄 Generating Netflix account...")
    args = e.text.split(" ")
    if len(args) == 1:
        return await msg.edit("Enter CC Details in the format: `!netflix <email>|<password>|<cc_number>|<cc_exp_date>|<cc_cvc>`")
    args = ''.join(args[1:]).split("|")
    if len(args) == 4:
        cc_number, cc_exp_month, cc_exp_year, cc_cvc = args
        cc_exp_date = cc_exp_month + "/" + cc_exp_year
        payload = {
            "email": gen_email(),
            "password": "qwerty123@",
            "cc_number": cc_number,
            "cc_exp_date": cc_exp_date,
            "cc_cvc": cc_cvc,
            "msg": msg,
        }
        txt, _ = await setup_netflix(payload)
    elif len(args) == 6:
        email, password, cc_number, cc_exp_month, cc_exp_year, cc_cvc = args
        cc_exp_date = cc_exp_month + "/" + cc_exp_year
        payload = {
            "email": email,
            "password": password,
            "cc_number": cc_number,
            "cc_exp_date": cc_exp_date,
            "cc_cvc": cc_cvc,
            "msg": msg,
        }
        txt, _ = await setup_netflix(payload)
    if os.path.exists("screenshot.png"):
        await msg.delete()
        await e.respond(txt, file="screenshot.png")
    else:
        await msg.delete()
        await e.respond(txt)
