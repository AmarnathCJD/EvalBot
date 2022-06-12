from selenium import webdriver


def browser():
    options = webdriver.ChromeOptions()
    options.headless = True
    browser = webdriver.Chrome(options=options)
    return browser
    
