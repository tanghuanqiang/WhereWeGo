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
    name为城市名字
    '''
    def __init__(self,name):
        self.FangAns = []
        self.name = name
        p = Pinyin()
        self.city_string = p.get_pinyin(self.name,'')
        self.get_city_url()
        self.get_article_url()
        #self.save_to_csv()
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
        
    def get_article_url(self):
        start = time.time()
        all_number = 1
        self.all_fangan = []
        for i in range(1,4):#页数 一页三十个方案
            page_url = self.city_url + str(i)
            driver = self.open_brower()
            driver.get(page_url)
            html = driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            driver.close()
            whole_plans = soup.find_all('div',class_='list_product_box js_product_item')
            # threads = []
            for plan in whole_plans: #每页的方案
                if plan.parent['class'][0] != 'list_ad_box':
                    title = plan.find('p',class_='list_product_title')['title']  # 上海4日自由行·【高铁往返|3晚连住】车次全覆盖·舒适型酒店任选·高性价比·住得舒心就好
                    pattern = re.compile(r'\+.{0,}日')
                    if pattern.search(title) == None and all_number <= 6 :
                        article_id = plan['data-track-product-id']
                        fangan_url = 'https://vacations.ctrip.com/travel/detail/p' + article_id
                        f = Fangan(all_number,fangan_url,self.city_string)
                        if len(f.data_list) > 11:
                            print(f.data_list)
                            key = f.data_list[0]
                            value = f.data_list[1:]
                            path = 'plan/' + self.city_string + '.csv'
                            if os.path.exists(path):
                                old = pd.read_csv(path,index_col=0)
                                print('读取')
                            else:
                                old = pd.DataFrame()
                                print('创建')
                            # 查看方案重复 和 数字存在
                            repeat = 0
                            for k in old:
                                if old[k][0] == value[0]:
                                    repeat = 1
                            
                            while str(key) in old:
                                print(key,'数字存在')
                                all_number = all_number + 1
                                key = key + 1
                            each = dict([(key,value)]) 
                            new = pd.DataFrame(each)
                            if not repeat :
                                print('存')
                                old = pd.concat([old,new],axis=1)
                                old.to_csv(path)
                                self.all_fangan.append(f.data_list)
                                all_number = all_number +1
                            else:
                                print('重复了')
                            
                            
                            
                            
                            
                            
                            
                    #T = myThread(fangan_url)
                    #T.start()
                    #threads.append(T)
                #for t in threads:
                #   t.join()
        end = time.time()
        print('总花费时间为',end-start)
    def save_to_csv(self):
        self.all_dict = {}
        for i in self.all_fangan:
            key = i[0]
            value = i[1:]
            each = dict([(key,value)]) 
            for k,v in each.items():
                self.all_dict[k] = v
        self.plans = pd.DataFrame(dict([(k,pd.Series(v))for k,v in self.all_dict.items()]))
        self.plans.to_csv('plan/'+self.city_string+'.csv',encoding='UTF-8')
citys = ['西安','重庆','广州','北京']
#for c in citys:
 #   ChengShi(c)       
a = ChengShi('西安')  
    
    
    
    
    
    
    
    
     
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    




