# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 09:18:47 2020

@author: Tang_Huanqiang
"""

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from lxml import etree
import re
import requests
class Comment():
    '''
    输入name，输出为self.comment,字符串类型
    '''
    def __init__(self,name):
        self.name = name
        self.get_html()
        self.get_comment()
        self.get_pic()
    def open_brower(self):
        # 设置不打开浏览器
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        # 设置中文
        chrome_options.add_argument('lang=zh_CN.UTF-8')
        # 更换头部
        chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69"')
        #  打开浏览器
        driver = webdriver.Chrome(chrome_options = chrome_options)
        return driver
    def get_html(self):
        driver = self.open_brower()
        driver.get('https://www.ctrip.com/')
        WebDriverWait(driver=driver, timeout=300, poll_frequency=0.5,  ignored_exceptions=None).until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/div[3]/div/div[2]/input')))
        driver.find_element_by_xpath('/html/body/div[3]/div/div[2]/input').send_keys(self.name)
        time.sleep(0.5)
        driver.find_element_by_id('search_button_global').click()
        # 切换页面   
        n = driver.window_handles
        driver.switch_to_window(n[-1])
        time.sleep(0.5)
        self.html = driver.page_source
        driver.close()
    def get_comment(self):
        soup = BeautifulSoup(self.html,'html.parser')
        comments = soup.find('div',class_ = 'LimitHeightText')
        if comments != None:
            ps = comments.find_all('p')
            self.comment = ''
            for p in ps:
                self.comment = self.comment + str(p.text)
        else:
            self.comment = ''
    def get_pic(self):
        HTML = etree.HTML(self.html)
        url = HTML.xpath('//*[@id="__next"]/div[4]/div/div[3]/div[1]/div[2]/div/div[1]/@style')
        if len(url) != 0 :
            url = url[0]
            pic_url = re.search('"(.*?)"',url)
            start = pic_url.span()[0] + 1
            end = pic_url.span()[1] -1
            url = url[start:end]
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.57'}
            response = requests.get(url,headers=headers)
            self.pic_url = 'image/' + url.split('/')[-1]
            print('景点图片存储为：',self.pic_url,'成功')
            with open(self.pic_url,'wb') as f:
                f.write(response.content)
        else:
            self.pic_url=''


        
        
        