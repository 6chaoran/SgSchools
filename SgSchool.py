from shutil import rmtree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tqdm import tqdm
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import re


class Crawler:

    def __init__(self, url_school_list):
        self.driver = webdriver.Chrome('./chromedriver')
        self.url_school_list = url_school_list

    def get_school_list(self):
        self.driver.get(self.url_school_list)
        schools = self.driver.find_elements(
            By.XPATH, "/html/body/div[*]/div/section[@class='single']/div/ul[*]/li")
        data = []
        for school in tqdm(schools):
            row = {
                'name': school.text,
                'link': school.find_element(By.TAG_NAME, 'a').get_attribute('href')
            }
            data += [row]
        data = pd.DataFrame(data)

    def get_tbl_headers(self, dom_tbl):
        headers = dom_tbl.find_elements(By.XPATH, './thead/tr/th')
        headers = [i.text.strip() for i in headers]
        return headers

    def get_tbl_row(self, dom_row):
        row = dom_row.find_elements(By.TAG_NAME, 'td')
        values = [i.text.strip() for i in row]
        return values

    def get_tbl_rows(self, dom_tbl):
        rows = dom_tbl.find_elements(By.XPATH, './tbody/tr')
        values = [self.get_tbl_row(r) for r in rows]
        return values

    def parse_tbl(self, dom_tbl):
        header = self.get_tbl_headers(dom_tbl)
        values = self.get_tbl_rows(dom_tbl)
        data = pd.DataFrame(values, columns = header)
        return data
    
    def save_tbls(self, dom_tbls, name):
        for i, tbl in enumerate(dom_tbls):
            data = self.parse_tbl(tbl)
            outdir = Path(f"./table_{i}/{name}.csv")
            #outdir.parent.mkdir(parents=True, exist_ok=True)
            data.to_csv(outdir, index=False)
        return None

    def crawl_school(self, name, link):
        self.driver.get(link)
        dom_tbls = self.driver.find_elements(By.XPATH, '/html/body/div[*]/div/section[@class="single"]/div/table')
        self.save_tbls(dom_tbls, name)

