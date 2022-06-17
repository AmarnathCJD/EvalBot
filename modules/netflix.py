import asyncio
import base64
import io
import math
import os
import random
import string

from bs4 import BeautifulSoup
from requests import post
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from modules.helpers import command

safety_check = []


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


def progress_bar(percentage: int) -> str:
    progress_str = "[{0}{1}] {2}%\n".format(
        "".join(["▰" for i in range(math.floor(percentage / 10))]),
        "".join(["▱" for i in range(10 - math.floor(percentage / 10))]),
        round(percentage, 2),
    )
    return "\n" + progress_str


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
    msg = await msg.edit("Generating Account...\nPlease wait..." + progress_bar(10))
    try:
        browser.find_element(
            by=By.XPATH, value="/html/body/div[1]/div/div/div[2]/div/div[2]/button"
        ).click()
    except:
        return await send_photo(
            browser, msg, "Error: __**Could not find the button**__"
        )
    await asyncio.sleep(1)
    try:
        pwd = browser.find_element(By.NAME, "password")
        pwd.clear()
        pwd.send_keys(password)
        pwd.send_keys(Keys.ENTER)
    except:
        return await send_photo(
            browser, msg, "Error: __**Could not find the button**__"
        )
    await asyncio.sleep(1.27)
    msg = await msg.edit("Generating Account...\nPlease wait..." + progress_bar(30))
    try:
        browser.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[2]/button"
        ).click()
    except:
        return await send_photo(
            browser, msg, "Error: __**Could not find the button**__"
        )
    await asyncio.sleep(1)
    wait = WebDriverWait(browser, 10)
    try:
        browser.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[2]/button"
        ).click()
    except:
        return await send_photo(
            browser, msg, "Error: __**Could not find the button**__"
        )
    await asyncio.sleep(1)
    msg = await msg.edit("Generating Account...\nPlease wait..." + progress_bar(50))
    try:
        browser.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/div[3]/div[2]/div[1]/a"
        ).click()
    except:
        return await send_photo(
            browser, msg, "Error: __**Could not find the button**__"
        )
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
        payload["cc_cvc"]
    )
    TERMS = browser.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div/div[2]/div/form/div[1]/div[2]/div/div/div/input",
    )
    browser.execute_script("arguments[0].click();", TERMS)
    msg = await msg.edit("Generating Account...\nPlease wait..." + progress_bar(80))
    browser.find_element(
        By.XPATH, "/html/body/div[1]/div/div/div[2]/div/form/div[2]/button"
    ).click()
    msg = await msg.edit("Generating Account...\nPlease wait..." + progress_bar(100))
    try:
        wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "messageContainer"))
        )
    except TimeoutException:
        with open("screenshot.png", "wb") as f:
            f.write(base64.b64decode(browser.get_screenshot_as_base64()))
        verify = browser.find_element(By.CLASS_NAME, "stepTitle")
        if verify.text == "Verify your card.":
            return False, "3D Secure Verification Failed"
        return True, "Success"
    element = browser.find_element(By.CLASS_NAME, "messageContainer")
    with open("screenshot.png", "wb") as f:
        browser.set_window_size(1920, 1080)
        f.write(base64.b64decode(element.screenshot_as_base64.encode()))
    return False, browser.find_element(By.CLASS_NAME, "messageContainer").text


async def send_photo(browser, e, txt):
    with io.BytesIO(base64.b64decode(browser.get_screenshot_as_base64())) as f:
        f.name = "screenshot.png"
        await e.respond(txt, file=f)


async def setup_netflix(payload: dict):
    browser = setup_browser()
    browser.get("https://netflix.com")
    resp, err = await enter_details(payload, browser)
    browser.quit()
    return write_response(
        payload["email"],
        payload["password"],
        resp,
        err,
    )


def write_response(email, password, resp: bool, err):
    if resp:
        RESULT = "**Netflix**\n\n**Email:** `{}`\n**Password:** `{}`\n**Status:** `Success`".format(
            email, password
        )
    else:
        RESULT = "**Netflix account creation failed**"
        RESULT += "\nError: __**" + err + "**__"
    return RESULT, resp


@command(pattern="netflix")
async def _nfgen(e):
    if e.sender_id in safety_check:
        return await e.reply("Please wait for the current operation to finish.")
    safety_check.append(e.sender_id)
    msg = await e.respond("🔄 Generating Netflix account...")
    args = e.text.split(" ")
    if len(args) == 1:
        return await msg.edit(
            "Enter CC Details in the format: `!netflix <email>|<password>|<cc_number>|<cc_exp_date>|<cc_cvc>`"
        )
    args = "".join(args[1:]).split("|")
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
    safety_check.remove(e.sender_id)


SPOTIFY_API = "https://spclient.wg.spotify.com:443/signup/public/v1/account/"


@command(pattern="spotify")
async def _spotify_gen(e):
    try:
        email = e.text.split(None, maxsplit=1)[1]
    except IndexError:
        email = gen_email()
    data = {
        "iagree": True,
        "birth_day": "17",
        "platform": "Android-ARM",
        "creation_point": "client_mobile",
        "password": "Qwerty123#",
        "key": "142b583129b2df829de3656f9eb484e6",
        "birth_year": "2000",
        "email": email,
        "gender": "male",
        "app_version": "849800892",
        "birth_month": "12",
        "password_repeat": "Qwerty123#",
    }
    r = post(SPOTIFY_API, data=data).json()
    if len(str(r)) > 4095:
        with io.BytesIO(str(r).encode()) as f:
            f.name = "resp.txt"
            await e.respond(file=f)
    await e.reply(str(r))
