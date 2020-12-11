# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 21:27:35 2020

@author: Tang_Huanqiang
"""
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
class Jingdian():
    '''
    传入name，输出为整数self.price
    '''
    def __init__(self,name):
        self.base_url = 'https://baike.baidu.com/'
        self.name = name
        self.price = 0
        self.content = ''
        self.get_html()                
        self.run()
    def open_brower(self):
        # 设置不打开浏览器
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        # 设置中文
        chrome_options.add_argument('lang=zh_CN.UTF-8')
        # 更换头部
        chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69"')
        driver = webdriver.Chrome(chrome_options = chrome_options)
        return driver
    def get_html(self):
        driver = self.open_brower()
        driver.get(self.base_url)
        WebDriverWait(driver=driver, timeout=300, poll_frequency=0.5,  ignored_exceptions=None).until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/form[1]/input')))
        # 输入景点
        driver.find_element_by_id('query').send_keys(self.name)
        #点击搜索
        driver.find_element_by_id('search').click()
        #等待跳转
        time.sleep(0.5)
        # 获取当前页面源码并解析
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        # 查看标签创建词条是否存在
        cant_find = soup.find('div',class_="create-entrance")
        # 不存在证明已经打开了目的景点百科文库
        if cant_find == None:
            self.html = html
        # 存在证明名字无法进入百科，点击第一条链接
        else:
            driver.find_element_by_xpath('/html/body/div[2]/div[1]/dl/dd[1]/a').click()
            time.sleep(0.5)
            #修改句柄进去新的网页
            n = driver.window_handles
            driver.switch_to_window(n[-1])
            # 重新解析网页
            html = driver.page_source
            self.html = html
        self.url = driver.current_url
        driver.close()
    def run(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        table = soup.find('div',class_="basic-info cmn-clearfix")
        if table == None:
            self.price = 0
            return 
        key = table.find_all('dt')
        value = table.find_all('dd')
        self.price = 0
        for t in range(len(key)):
            if '门票价格' in key[t].get_text():
                # 存在价格
                self.content = value[t].get_text()
                if '免费' in self.content:
                    self.price =0
                else:
                    pattern = re.compile(r'[\d\.]+元')
                    self.price = pattern.findall(self.content)
                    if len(self.price) == 0:
                        self.price = 0
                    elif len(self.price) == 1 :
                        self.price = self.price[0]
                        self.price = self.price[:-1]
                        if '.' in self.price:
                            index = self.price.index('.')
                            self.price = self.price[:index]
                    else:
                        self.price = min(self.price)
                        self.price = self.price[:-1]
                        if '.' in self.price:
                            index = self.price.index('.')
                            self.price = self.price[:index]





