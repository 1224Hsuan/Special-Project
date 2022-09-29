from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from PIL import Image
import time
import os
import pandas as pd

# choose the csv file to read
urls = pd.read_csv("TP.csv",header=None, names=['url'])
url = urls.url
s = Service(r"D:\insert\chromedriver.exe")


for i in range (0, len(url)):
    browser = webdriver.Chrome(service = s)
    
    # set the window size
    browser.set_window_size(1200,3000)
    browser.get(url[i])

    # get the screenshot of the element
    photo = browser.find_element(By.CLASS_NAME, 'image-container')
    action = ActionChains(browser)
    action.move_to_element(photo).perform()

    # save the screenshot
    file_name = str(i + 1) + '.png'
    browser.get_screenshot_as_file(file_name)

    # crop the image
    photo = browser.find_element(By.CLASS_NAME, 'image-container')
    left = 311.6
    top = 269.5
    right = left + 1120
    bottom = top + 635
    photo = Image.open(file_name)
    photo = photo.crop((left, top, right, bottom))
    photo.save(file_name)
    browser.close()

    time.sleep(5.49751502)

