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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException
)
from bs4 import BeautifulSoup
from time import sleep

BASE_DIR = Path(__file__).resolve().parent   

try:
    import db, models
except Exception as e:
    raise RuntimeError(str(e))

from utils.chrome import Chrome
from utils import FlipPath, SearchMobile


class Scraper(Chrome):
    def __init__(self, quote=False):
        super().__init__(
            # options=True, auto_open_devtools_for_tab=True
        )
        
        self.category = None
        
        self.queue = Queue()
        _url = FlipPath.base
        if quote:
            _url = quote_plus(_url)
        self.queue.put(_url)
    
    branch = re.compile(SearchMobile.branch)
    phone = re.compile(SearchMobile.phone)
    
                
    def insert_raw(
        self, 
        title,
        img,
        detail,
        cur_price,
        /,
        db = db.get_session()
    ):
        d = models.RawModel(title=title, img=img, detail=detail, cur_price=cur_price)
        db.add(d)
        db.commit()

    
    def search_input(self, search: str = None):
        if not search:
            raise RuntimeError("Search keyword cannot be None")
        element = self.chrome_driver.find_element(By.CLASS_NAME, 'Pke_EE')        
        element.send_keys(search)
        element.send_keys(Keys.ENTER)
        
    
    data_blocks_locator1 = (By.CSS_SELECTOR, "div.tUxRFH")
    data_blocks_locator2 = (By.CSS_SELECTOR,"div.slAVV4")
    # True -> locator1
    # False -> locator2
    locator = True
    
    def get_detault_locator(self):
        if self.locator:
            return self.data_blocks_locator1
        return self.data_blocks_locator2
    
    def find_blocks(self, class_id: str = None):
        # waiting for visiblity of all data blocks
        self.chrome_driver.refresh()
        
        
        blocks: list[WebElement]
        if self.locator:
            try:
                print("Trying locator 1")
                blocks = WebDriverWait(
                    self.chrome_driver, 5
                ).until(
                    EC.any_of(
                        EC.presence_of_all_elements_located(self.get_detault_locator()),
                        EC.visibility_of_all_elements_located(self.get_detault_locator()),
                    )
                )
            except TimeoutException as e:
                print("\nSwitching to locator 2")
                self.locator = False
                
        if not self.locator:
            try:
                print("Trying locator 2")
                blocks = WebDriverWait(
                    self.chrome_driver, 5
                ).until(
                    EC.any_of(
                        EC.presence_of_all_elements_located(self.get_detault_locator()),
                        EC.visibility_of_all_elements_located(self.get_detault_locator()),
                    )
                )
            except TimeoutException as e:
                raise RuntimeError("Unable to using the locatore, please check of the page source and your program")
        
        if blocks is None:
            raise RuntimeError("Invalid data blocks and locators")
        
        # 
        for block in blocks:
            # go to the block
            action = ActionChains(self.chrome_driver)
            action.move_to_element(block)
            action.perform()
            
            img = block.find_element(By.CSS_SELECTOR, "img.DByuf4")
            title = block.find_element(By.CSS_SELECTOR, 'div.KzDlHZ') if self.locator else block.find_element(By.CSS_SELECTOR, "a.wjcEIp")
            detail_list = block.find_elements(By.TAG_NAME, "li") if self.locator else block.find_elements(By.CSS_SELECTOR, "div.NqpwHC")
            details_join = ";".join([x.text for x in detail_list])
            try:
                cur_price = block.find_element(By.CSS_SELECTOR, "div.Nx9bqj")
                self.insert_raw(rf"{title.text}", rf"{img.get_attribute("src")}", rf"{details_join}", float(cur_price.text[1:]))
            except Exception as e:
                print(e)
                self.insert_raw(rf"{title.text}", rf"{img.get_attribute("src")}", rf"{details_join}", 0.)
            

    def next_page(self):
        # scroll to page navbar
        nav_pages = self.chrome_driver.find_element(By.CSS_SELECTOR, "nav.WSL9JP")
        print("moving to paging nav")
        action = ActionChains(self.chrome_driver)
        action.move_to_element(nav_pages)
        action.perform()
        #
        # Waiting for element to be visible
        pre_nav_btns: list[WebElement] = WebDriverWait(self.chrome_driver, 5).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a._9QVEpD"))
        )
        # 
        # check the btn button
        if self.previous_url == self.current_url:
            raise IndexError("Last page")
        # 
        # waiting for element to be clickable
        next_btn = pre_nav_btns[-1]
        WebDriverWait(self.chrome_driver, 5).until(
            EC.element_to_be_clickable(next_btn)
        )
        counter = 10
        while (counter > 0):
            try:
                next_btn.click()
                break
            except Exception as e:
                pass
            counter-=1
        self.previous_url = self.current_url
        self.current_url = self.chrome_driver.current_url
        print(f"\n{self.previous_url}\n{self.current_url}\n")
        # self.chrome_driver.execute_script("document.querySelector('nav.WSL9JP').lastChild.click()")
    
    def run(self):
        self.chrome_driver.maximize_window()
        self.current_url = self.queue.get()
        self.previous_url = None
        self.chrome_driver.get(self.current_url)
        
        if isinstance(self.category, str):
            self.search_input(self.category)
        else:
            self.search_input("Laptops")
        while True:
            self.find_blocks()
            self.next_page()
        
    def filter_url(self, url: str):
        if self.branch.search(url) and self.phone.search(url):
            return url
        return 

    
    def get_content(self) -> WebElement:
        url = self.queue.get()
        # print(url, type(url))
        if self._quote_url:
            url = unquote_plus(url) 
        self.chrome_driver.get(url)
        return self.chrome_driver.find_element(By.TAG_NAME, 'body')

    def user_input(self):
        self.category  = input("Enter your fav category: ").strip()
        if (
            not self.category or 
            self.category == " " or 
            self.category == ''
        ):
            self.category = None 
        
     
def main():
    scraper = Scraper()
    scraper.user_input()
    scraper.set_up()
    scraper()
    scraper.teardown()

    
if __name__ == "__main__":
    main()