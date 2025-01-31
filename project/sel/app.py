import sys
import re
import os
from typing import List
from queue import Queue
from urllib.parse import quote_plus, unquote_plus, quote
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from bs4 import BeautifulSoup
from time import sleep

BASE_DIR = Path(__file__).resolve().parent   

try:
    import db, models
except Exception as e:
    raise RuntimeError(str(e))

class FlipPath:
    base: str = "https://www.flipkart.com"
    
class SearchMobile:
    phone = r"(phone|phones)"
    branch = r"(apple-iphone|apple|mi|lg|samsung|htc|honor|motorola|apple|oppo|realme|nothing)"


queue = Queue()
queue.put(FlipPath.base)


branch = re.compile(SearchMobile.branch)
phone = re.compile(SearchMobile.phone)

def filter_url(url: str):
    if branch.search(url) and phone.search(url):
        return url

def find_all_links(element: WebElement, db = db.get_session()):
    a_tags = element.find_elements(By.TAG_NAME, 'a')
    for a in a_tags:
        with open("file1.txt", 'a+') as f:
            url = a.get_attribute('href')
            if isinstance(url, str):
                filtered_url = filter_url(url)
                if filtered_url:    
                    queue.put(
                        filtered_url   
                    )
            # instance = models.URLModel(url=quote_plus(filter_url(url)))
            # db.add(instance)
            # db.commit()
            
def get_content(driver: webdriver.Chrome) -> WebElement:
    url = queue.get()
    print(url, type(url))
    driver.get(url)
    return driver.find_element(By.TAG_NAME, 'body')

     
def main():
    chrome_driver = webdriver.Chrome()
    
    # electronic_hover = chrome_driver.find_element(
    #     By.XPATH, 
    #     '//*[@id="container"]/div/div[1]/div/div/div/div/div[1]/div/div/div/div[2]/div[1]/div/div[1]/div/div/div/div/div[1]/div[2]/div/div'
    # )
    # webdriver.ActionChains(chrome_driver)\
    #     .move_to_element(electronic_hover)\
    #         .perform()
    
    while not queue.empty():
        body_element = get_content(chrome_driver)
        find_all_links(body_element)
    chrome_driver.quit()
    
if __name__ == "__main__":
    main()