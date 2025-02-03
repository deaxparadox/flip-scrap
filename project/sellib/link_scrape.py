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
    base: str = "https://www.flipkart.com/"
    
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
    
    current_url: str = None
    search_box_classes = [
        'Pke_EE',"zDPmFV"
    ]
    
    def insert_raw(self, url, /, *, db = db.get_session()):
        d = models.URLModel(url=url)
        db.add(d)
        db.commit()
    
    def find_data_blocks(self, class_id: str = None):
        try:
            # self.chrome_driver.refresh()
            blocks: list[WebElement] = WebDriverWait(
                self.chrome_driver, 10
            ).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "KzDlHZ"))
            )
            for block in blocks:
                print(block)
                # img = block.find_element(By.TAG_NAME, "img")
                # title = block.find_element(By.CLASS_NAME, "KzDlHZ")
                # print(f"Img: {img.get_attribute("href")}\nTitle: {title.text}")
                # print("inserting", block.text)
            
        except Exception as e:
            # print(str(e))
            print(self.chrome_driver.current_url)
            print("\nData blocks error page error.\n")
        return
        
    def search_input(self, search: str = None):
        if not search:
            raise RuntimeError("Search keyword cannot be None")
        
        element: WebElement | None = None
        # print(f"\n\n{self.chrome_driver.current_url}, {self.current_url}\n\n")
        if self.chrome_driver.current_url != FlipPath.base:
            element = self.chrome_driver.find_element(By.CLASS_NAME, self.search_box_classes[1])
        else:
            element = self.chrome_driver.find_element(By.CLASS_NAME, self.search_box_classes[0])
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(search)
        # sleep(2)
        element.send_keys(Keys.ENTER)
        
    def run(self):
        categories = [
            "Laptops",
            "Mobile",
            "Washing machine",
            "TV"
        ]
        self.current_url = self.queue.get()
        self.chrome_driver.get(self.current_url)
        # try:
        #     # for c in categories:
        #         self.search_input("Laptops")
        #         self.find_data_blocks()
        #         self.next_page()
        #         if self.next_page_status:
        #             self.find_data_blocks()
        #             self.next_page()        
        # except Exception as e:
        #     raise RuntimeError(str(e))
        while not self.queue.empty():
            body_element = self.get_content()
            self.find_all_links(body_element)

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
        if self._quote_url:
            url = unquote_plus(url) 
        self.chrome_driver.get(url)
        return self.chrome_driver.find_element(By.TAG_NAME, 'body')

     
def main():
    scraper = Scraper()
    scraper.set_up()
    scraper()
    scraper.teardown()

    
if __name__ == "__main__":
    main()