from abc import ABC, abstractmethod
import sys
import re
import os
from typing import List
from queue import Queue
from urllib.parse import quote_plus, unquote_plus, quote
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

class Chrome(ABC):
    def __init__(
        self,
        options=False,
        auto_open_devtools_for_tab=False
    ):
        self.options = options
        if options:
            if auto_open_devtools_for_tab:
                self.chrome_add_options()
                
    chrome_options = webdriver.ChromeOptions()
    
    @abstractmethod
    def run(self):
        raise NotImplementedError("Should be implemented in subclass")
    
    def chrome_add_options(self):
        self.chrome_options.add_argument("--auto-open-devtools-for-tabs")
    
    def set_up(self):
        if self.options:
            self.chrome_driver = webdriver.Chrome(options=self.chrome_options)
        else:
            self.chrome_driver = webdriver.Chrome()
    
    def __call__(self):
        return self.run()
    
    def teardown(self):
        self.chrome_driver.quit()


class Scraper(Chrome):
    def __init__(self, quote=False):
        super().__init__(
            # options=True, auto_open_devtools_for_tab=True
        )
        
        self.queue = Queue()
        _url = FlipPath.base
        if quote:
            _url = quote_plus(_url)
        self.queue.put(_url)
    
    branch = re.compile(SearchMobile.branch)
    phone = re.compile(SearchMobile.phone)
    
    def hover_electronics_category(self):
        self.chrome_driver.get(self.queue.get())
        hovers = self.chrome_driver.find_elements(By.CLASS_NAME, "_1ch8e_")
        for h in hovers:
            electronics = h.get_attribute("aria-label")
            if electronics == "Electronics":
                webdriver.ActionChains(self.chrome_driver)\
                    .move_to_element(h)\
                        .perform()
                sleep(100)
                
    def insert_raw(self, data, /, *, db = db.get_session()):
        d = models.RawModel(data=data)
        db.add(d)
        db.commit()
    
    def find_blocks(self, class_id: str = None):
        
        try:
            # self.chrome_driver.refresh()
            blocks: list[WebElement] = WebDriverWait(
                self.chrome_driver, 5
            ).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "KzDlHZ"))
                # EC.presence_of_element_located((By.TAG_NAME, "html"))
            )
            for block in blocks:
                # img = block.find_element(By.TAG_NAME, "img")
                # title = block.find_element(By.CLASS_NAME, "KzDlHZ")
                # print(f"Img: {img.get_attribute("href")}\nTitle: {title.text}")
                # print("inserting", block.text)
                self.insert_raw(block.text)
                # print('-'*50)
        except Exception as e:
            print(e)
        

    def parse_page(self, page: str):
        bs = BeautifulSoup(page, "html.parser")
        div_blocks = bs.find_all("div")
        for div in div_blocks:
            print(div)
            
    def search_input(self, search: str = None):
        if not search:
            raise RuntimeError("Search keyword cannot be None")
        
        # element = WebDriverWait(
        #     self.chrome_driver, 10
        # ).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, "Pke_EE"))
        # )
        element = self.chrome_driver.find_element(By.CLASS_NAME, 'Pke_EE')
        
        element.send_keys(search)
        element.send_keys(Keys.ENTER)
        self.find_blocks()
    
    def run(self):
        
        self.chrome_driver.get(
            self.queue.get()
        )
        try:
            self.search_input("Laptops")
        except Exception as e:
            raise RuntimeError(str(e))
        # while not self.queue.empty():
        #     body_element = self.get_content()
        #     self.find_all_links(body_element)

    def filter_url(self, url: str):
        if self.branch.search(url) and self.phone.search(url):
            return url
        return 

    def find_all_links(self, element: WebElement, db = db.get_session()):
        a_tags = element.find_elements(By.TAG_NAME, 'a')
        for a in a_tags:
            with open("file1.txt", 'a+') as f:
                url = a.get_attribute('href')
                if isinstance(url, str):
                    url = self.filter_url(url)
                    if not url: continue
                    print(url)
                    if self._quote_url:
                        url = quote_plus(url)
                    if url:    
                        self.queue.put(url)
                        # save url in database
                    instance = models.URLModel(url=url)
                    db.add(instance)
                    db.commit()
                
    def get_content(self) -> WebElement:
        url = self.queue.get()
        # print(url, type(url))
        if self._quote_url:
            url = unquote_plus(url) 
        self.chrome_driver.get(url)
        return self.chrome_driver.find_element(By.TAG_NAME, 'body')

     
def main():
    scraper = Scraper()
    scraper.set_up()
    scraper()
    scraper.teardown()
    # electronic_hover = chrome_driver.find_element(
    #     By.XPATH, 
    #     '//*[@id="container"]/div/div[1]/div/div/div/div/div[1]/div/div/div/div[2]/div[1]/div/div[1]/div/div/div/div/div[1]/div[2]/div/div'
    # )
    # webdriver.ActionChains(chrome_driver)\
    #     .move_to_element(electronic_hover)\
    #         .perform()

    
if __name__ == "__main__":
    main()