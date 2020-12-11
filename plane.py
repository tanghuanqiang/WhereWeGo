# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 08:51:13 2020
for plane price
@author: Tang_Huanqiang
"""
import time
from lxml import etree
from selenium import webdriver
class Plane():
    def __init__(self,from_place,to_place,date):
        self.from_place = from_place
        self.to_place = to_place
        self.date = date
        self.get_url()
        self.get_price()

    def get_url(self):
        base_dic = {
            '西安':'sia',
            '北京':'bjs',
            '广州':'can',
            '重庆':'ckg'
            }
        string = base_dic[self.from_place]+'-'+base_dic[self.to_place]
        self.url = 'https://flights.ctrip.com/itinerary/oneway/'+string+'?date='+self.date+'&hasChild=false&hasBaby=false&classType=ALL'
    
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
    def get_price(self):
        driver = self.open_brower()
        driver.get(self.url)
        time.sleep(1)
        element = driver.find_element_by_xpath('//*[@id="base_bd"]/div[3]/div[1]/div[1]/div/div/div[1]/div[2]/a')
        element.click()
        
        self.html = driver.page_source
        self.tree = etree.HTML(self.html)
        self.price = self.tree.xpath('//*[@id="base_bd"]/div[3]/div[1]/div[2]/div/div[2]/div[1]/div[1]/div/div/div[8]/div/span/text()')
        print(self.price)
p = Plane(from_place='重庆', to_place='北京',date='2020-12-29')


