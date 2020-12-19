# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 14:00:49 2020

@author: Tang_Huanqiang
"""
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
import threading
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from fangan import Fangan
from xpinyin import Pinyin
import pandas as pd
import os
class myThread (threading.Thread):
    '''
    输入方案的url，多线程执行类Fangan，存储数据
    '''
    def __init__(self,fangan_url):
        threading.Thread.__init__(self)
        self.fangan_url = fangan_url
    def run(self):
        print ("开始线程：" + self.name)
        Fangan(self.fangan_url)
        print ("退出线程：" + self.name)
        
class ChengShi():
    '''
    id 2020
    name为城市名字 西安
    '''
    def __init__(self,city_id,name):
        self.FangAns = []
        self.city_id = city_id
        # 初始化city_id
        self.name = name
        p = Pinyin()
        self.city_string = p.get_pinyin(self.name,'')
        if self.city_string == 'zhongqing':
            self.city_string = 'chongqing'
        self.init_city_id()
        self.get_city_url()
        self.get_article_url()
    def init_city_id(self):
        path = 'city_model.csv'
        if os.path.exists(path):
            city_id_model = pd.read_csv(path,index_col=0)
        else:
            city_id_model = pd.DataFrame(columns=('city_id','city_name'))
        if city_id_model[(city_id_model.city_id==self.city_id)].empty:
            temp = {'city_id':[self.city_id],'city_name':[self.city_string]}
            temp = pd.DataFrame(temp)
            city_id_model = pd.concat([city_id_model,temp],ignore_index=True,axis=0)
            city_id_model.to_csv(path)
        
    def save_spotlist_id(self):
            path = 'city_model_spotlist.csv'
            if os.path.exists(path):
                city_id_spotlist = pd.read_csv(path,index_col=0)
            else:
                city_id_spotlist = pd.DataFrame(columns=('citymodel_id','spotlist_id'))
            if self.all_number%1000 == 1:
                city_id_spotlist = city_id_spotlist[(city_id_spotlist.citymodel_id != self.city_id)]
            if city_id_spotlist[(city_id_spotlist.spotlist_id==self.all_number)].empty:
                temp = {'citymodel_id':[self.city_id],'spotlist_id':[self.all_number]}
                temp = pd.DataFrame(temp)
                city_id_spotlist = pd.concat([city_id_spotlist,temp],ignore_index=True,axis=0)
            city_id_spotlist.to_csv(path)
        
    def open_brower(self):
        # 设置不打开浏览器
        chrome_options = webdriver.ChromeOptions()
        # linux的
        #chrome_options.add_argument('blink-settings=imagesEnabled=false')
        #chrome_options.add_argument('--no-sandbox')      # root
        #chrome_options.add_argument('--disable-dev-shm-usage')
        # 不知道
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        # 设置中文
        chrome_options.add_argument('lang=zh_CN.UTF-8')
        # 更换头部
        chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69"')
        #  打开浏览器
        driver = webdriver.Chrome(chrome_options = chrome_options)
        return driver
    
    def get_city_url(self):
        driver = self.open_brower()
        # 进入自由行页面
        driver.get('https://vacations.ctrip.com/freetravel')
        driver.find_element_by_class_name('search_txt').send_keys(self.name)
        driver.find_element_by_class_name('main_search_btn').click()
        # 等待出现
        WebDriverWait(driver=driver, timeout=300, poll_frequency=0.5,  ignored_exceptions=None).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="root"]/div/div[1]/div[8]/div[1]')))
        self.city_url = driver.current_url + str('&p=')
        driver.close()
        
    def  all_number_init_(self):
        for i in range(1,41):
            number = self.city_id*1000 + i
            path = 'city_model_spotlist.csv'
            if os.path.exists(path):
                city_id_spotlist = pd.read_csv(path,index_col=0)
            else:
                city_id_spotlist = pd.DataFrame(columns=('citymodel_id','spotlist_id'))
            if city_id_spotlist[(city_id_spotlist.spotlist_id==number)].empty:
                if i ==1:
                    self.all_number = number
                else:
                    self.all_number = number-1
                break
        
        
        
    def get_article_url(self):
        start = time.time()
        max_number = self.city_id*1000 + 40   #最多方案
        self.all_number_init_()
        for i in range(15,18):#页数 一页三十个方案
            if self.all_number <= max_number:     
                page_url = self.city_url + str(i)
                driver = self.open_brower()
                driver.get(page_url)
                html = driver.page_source
                soup = BeautifulSoup(html,'html.parser')
                driver.close()
                whole_plans = soup.find_all('div',class_='list_product_box js_product_item')
                # threads = []
                for plan in whole_plans: #每页的方案
                    # 创建城市-方案关联表
                    if plan.parent['class'][0] != 'list_ad_box':
                        title = plan.find('p',class_='list_product_title')['title']  
                        pattern = re.compile(r'\+.{0,}日')
                        if pattern.search(title) == None and self.all_number <= max_number :    
                            article_id = plan['data-track-product-id']
                            fangan_url = 'https://vacations.ctrip.com/travel/detail/p' + article_id
                            f = Fangan(self.city_id,self.all_number,fangan_url,self.city_string)
                            if len(f.data_list) > 11:
                                print(self.all_number,f.data_list)
                                path = 'spotlist.csv'
                                if os.path.exists(path):
                                    spotlist = pd.read_csv(path,index_col=0)
                                    spotlist = spotlist[(spotlist.spotlist_id != self.all_number)]
                                else:
                                    spotlist = pd.DataFrame(columns=('spotlist_id','max_day','spotlist_image'))
                                path = 'spotlist_houselist.csv'
                                if os.path.exists(path):
                                    spotlist_houselist = pd.read_csv(path,index_col=0)
                                    spotlist_houselist = spotlist_houselist[(spotlist_houselist.spotlist_id != self.all_number)]
                                else:
                                    spotlist_houselist = pd.DataFrame(columns=('spotlist_id','housemodel_id'))
                                path = 'spotlist_spot.csv'
                                if os.path.exists(path):
                                    spotlist_spot = pd.read_csv(path,index_col=0)
                                    spotlist_spot = spotlist_spot[(spotlist_spot.spotlist_id != self.all_number)]
                                else:
                                    spotlist_spot = pd.DataFrame(columns=('spotlist_id','spotmodel_id'))
                                
                                
                                if spotlist[(spotlist.spotlist_image==f.data_list[1])].empty:
                                    self.save_spotlist_id()
                                    temp = {'spotlist_id':[f.data_list[0]],'max_day':[f.data_list[-1][0]],'spotlist_image':[f.data_list[1]]}
                                    temp = pd.DataFrame(temp)
                                    spotlist = pd.concat([spotlist,temp],ignore_index=True,axis=0)
                                    for j in range(2,12):
                                        if type(f.data_list[j])!= list:
                                            temp = {'spotlist_id':[self.all_number],'housemodel_id':[f.data_list[j]]}
                                            temp = pd.DataFrame(temp)
                                            spotlist_houselist = pd.concat([spotlist_houselist,temp],ignore_index=True,axis=0)
                                        
                                    for j in range(2,len(f.data_list)):
                                        if type(f.data_list[j])!= list :
                                            pass
                                        else:
                                            temp = {'spotlist_id':[self.all_number],'model_day':[int(f.data_list[j][0])],'spotmodel_id':[f.data_list[j][1]]}
                                            temp = pd.DataFrame(temp)
                                            spotlist_spot = pd.concat([spotlist_spot,temp],ignore_index=True,axis=0)
                                else:
                                    self.all_number = self.all_number -1
                                
                                self.all_number = self.all_number+1
                                spotlist_houselist.to_csv('spotlist_houselist.csv')
                                spotlist_spot.to_csv('spotlist_spot.csv')
                                spotlist.to_csv('spotlist.csv')
                                    
                            
                                
                                
                            
                            
                            
                            
                            
                    #T = myThread(fangan_url)
                    #T.start()
                    #threads.append(T)
                #for t in threads:
                #   t.join()
        end = time.time()
        print('总花费时间为',end-start)
citys = [[2020,'西安'],[2021,'重庆'],[2022,'广州'],[2023,'北京']]
c = citys[2]
ChengShi(c[0],c[1])     

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    




