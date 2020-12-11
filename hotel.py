# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 19:25:58 2020

@author: Tang_Huanqiang
"""
from selenium import webdriver
import time
from lxml import etree
import requests
class Hotel():
    '''
    输入城市的拼音为city，景点名字为name
    '''
    def __init__(self,city,name):
        self.city = city
        self.name = name
        self.hotels = []
        self.prices = []
        self.urls = []
        self.descriptions = []
        self.get_html()
        self.get_data()
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
        driver = webdriver.Chrome(chrome_options = chrome_options)
        print()
        driver.get('http://www.elong.com/'+self.city)
        
        return driver
    def get_pic(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'}
        for i in range(len(self.urls)):
            response = requests.get(self.urls[i],headers=headers)
            pic_url = 'image/'+self.urls[i].split('/')[-1] 
            self.urls[i] = 'image/'+self.urls[i].split('/')[-1] 
            with open(pic_url,'wb') as f:
               f.write(response.content)
    def get_html(self):
        driver = self.open_brower()
        time.sleep(1)
        element = driver.find_element_by_xpath('//*[@id="m_searchBox"]/div[3]/label/input')
        element.send_keys(self.name)
        element = driver.find_element_by_xpath('//*[@id="m_searchBox"]/div[4]')
        element.click()
        # 下拉
        js = "document.documentElement.scrollTop=1000"  
        time.sleep(1)
        driver.execute_script(js)
        # 解析html
        self.html = driver.page_source
        driver.close()
        
    def get_data(self):
        flag = 0
        HTML = etree.HTML(self.html)
        # 获取景点
        hotels = HTML.xpath('//*[@id="hotelContainer"]/div/div')
        if hotels != []:
            for i in range(len(hotels)):
                hotel = hotels[i]
                if hotel.xpath('./div/div[2]/div[3]/p[1]/a/span[2]/text()') != [] and flag <10:
                    self.hotels.append(hotel.xpath('./div/div[2]/div[3]/p[1]/a/span[2]/text()')[0])
                    self.prices.append(hotel.xpath('./div/div[2]/div[1]/div[1]/a/span[2]/text()')[0])
                    place = hotel.xpath('./div/div[2]/div[3]/p[2]/text()')[1][1:-1] 
                    distance = hotel.xpath('./div/div[2]/div[3]/p[2]/span[3]/text()')
                    if len(distance) != 0 :
                        self.descriptions.append(str(place+',距'+self.name+distance[0]+'公里'))
                    else:
                        self.descriptions.append(str(place) )
                    img = hotel.xpath('./div/div[1]/a/img')[0]
                    self.urls.append(img.xpath('./@big-src')[0])
                    flag = flag +1
        
        if len(hotels) < 10:
            hotels = HTML.xpath('//*[@id="hotelContainer"]/div[3]/div')
            for i in range(len(hotels)):
                hotel = hotels[i]
                if hotel.xpath('./div/div[2]/div[3]/p[1]/a/span[2]/text()') != [] and flag <10:
                    self.hotels.append(hotel.xpath('./div/div[2]/div[3]/p[1]/a/span[2]/text()')[0])
                    self.prices.append(hotel.xpath('./div/div[2]/div[1]/div[1]/a/span[2]/text()')[0])
                    place = hotel.xpath('./div/div[2]/div[3]/p[2]/text()')[1][1:-1] 
                    distance = hotel.xpath('./div/div[2]/div[3]/p[2]/span[3]/text()')
                    if len(distance) != 0 :
                        self.descriptions.append(str(place+',距'+self.name+distance[0]+'公里'))
                    else:
                        self.descriptions.append(str(place) )
                    img = hotel.xpath('./div/div[1]/a/img')[0]
                    self.urls.append(img.xpath('./@big-src')[0])
                    flag = flag +1    
             
                    

    
    
    


if __name__ == '__main__':
    h = Hotel('xian','大唐芙蓉园')
    print(h.hotels,h.prices,h.descriptions,h.urls)