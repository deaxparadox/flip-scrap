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
from selenium.common.exceptions import StaleElementReferenceException
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
        
        self.queue = Queue()
        _url = FlipPath.base
        if quote:
            _url = quote_plus(_url)
        self.queue.put(_url)
    
    branch = re.compile(SearchMobile.branch)
    phone = re.compile(SearchMobile.phone)
    
                
    def insert_raw(self, data, /, *, db = db.get_session()):
        d = models.RawModel(data=data)
        db.add(d)
        db.commit()

    
    def search_input(self, search: str = None):
        if not search:
            raise RuntimeError("Search keyword cannot be None")
        element = self.chrome_driver.find_element(By.CLASS_NAME, 'Pke_EE')        
        element.send_keys(search)
        element.send_keys(Keys.ENTER)
        
    
    def find_blocks(self, class_id: str = None):
        # waiting for visiblity of all data blocks
        self.chrome_driver.refresh()
        data_blocks_locator = (By.CLASS_NAME, "KzDlHZ")
        blocks = WebDriverWait(
            self.chrome_driver, 5
        ).until(
            EC.any_of(
                EC.presence_of_all_elements_located(data_blocks_locator),
                EC.visibility_of_all_elements_located(data_blocks_locator),
            )
        )
        # 
        for block in blocks:
            # go to the block
            action = ActionChains(self.chrome_driver)
            action.move_to_element(block)
            action.perform()
            self.insert_raw(block.text)

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
        
        self.current_url = self.queue.get()
        self.previous_url = None
        self.chrome_driver.get(self.current_url)
        self.search_input("Smartphone")
        while True:
            self.find_blocks()
            self.next_page()
        

 

     
def main():
    scraper = Scraper()
    scraper.set_up()
    scraper()
    scraper.teardown()

    
if __name__ == "__main__":
    main()