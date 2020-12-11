# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 14:50:29 2020

@author: Tang_Huanqiang
"""
import os
from selenium import webdriver
from bs4 import BeautifulSoup
import re
from jingdian import Jingdian
import requests
import pandas as pd
from comment import Comment
from hotel import Hotel
class Fangan():
    '''
    id 为城市的id
    city为城市的拼音
    传入url，输出在二维数组self.data_list
    默认保存为csv文件，命名为url中的文章id
    存方案第一张图在image文件夹中，命名为文章id，格式为jpg
    '''
    def __init__(self,fangan_id,url,city_string=None):
        if type(fangan_id) == int:
            # self.fangan_id = '%03d'%fangan_id    补充为三位
            self.fangan_id = fangan_id
        elif type(fangan_id) == str:
            #self.fangan_id = fangan_id.zfill(3)           补充为三位
            self.fangan_id = int(fangan_id)
        self.flag = 1
        self.city_string = city_string
        self.url = url
        self.id = self.url.split('/')[-1]
        self.data_list = [self.fangan_id]
        self.get_html()
        self.get_data()
        self.save_pic()
        self.end_line()

        
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
        driver.get(self.url)
        self.html = driver.page_source
        driver.close()
    
    def get_data(self):
        soup = BeautifulSoup(self.html,'html.parser') 
        # 获取景点
        days = soup.find_all('div',class_ = 'daily_itinerary_item')
        for i in range(len(days)):
            days[i] = str(days[i])
            soup = BeautifulSoup(days[i],'html.parser')
            tables = soup.find_all('div',class_="daily_itinerary_sub_info")
            if tables != []:
                for tag in tables:
                    if tag.find(text = '景点') != None or tag.find(text = '自由活动') != None:
                        pattern = re.compile(r'<a class="itinerary_sce_name">(.*?)</a>')
                        name = pattern.findall(str(tag))
                        for n in range(len(name)):
                            name[n] = re.sub('\（.*\）','',name[n])
                            name[n] = re.sub('\(.*\)','',name[n])
                            if self.flag:
                                print('开始爬取：',name[n],'的酒店')
                                self.jiudian = Hotel(self.city_string,name[n])
                                path = 'hotel\\'+self.city_string+'.csv'
                                for j in range(len(self.jiudian.hotels)):
                                    if os.path.exists(path):
                                        hotels = pd.read_csv(path,index_col=0)
                                    else:
                                        hotels = pd.DataFrame(columns=('name','price','description','url'))
                                    if hotels[(hotels.name==self.jiudian.hotels[j])].empty:
                                        index = len(hotels)
                                        self.data_list.append(int(index))
                                        hotel = pd.DataFrame({'name':[self.jiudian.hotels[j]],'price':[self.jiudian.prices[j]],'description':[self.jiudian.descriptions[j]],'url':[self.jiudian.urls[j]]})
                                        hotels = pd.concat([hotels,hotel],ignore_index=True,axis=0)
                                    else:
                                        self.data_list.append(int(hotels[(hotels.name==self.jiudian.hotels[j])].index[0]))                               
                                    hotels.to_csv(path,encoding = 'UTF-8')
                                self.flag = 0
                      
                            
                            # 查看是否存在
                            path = 'place\\'+self.city_string+'.csv'
                            if os.path.exists(path):
                                places = pd.read_csv(path,index_col=0)
                            else:
                                places = pd.DataFrame(columns=('name','price','description','picurl'))
                            if places[(places.name==name[n])].empty:
                                # 获取价格
                                print('开始获取：',name[n],'的价格')
                                price = Jingdian(name[n]).price
                                print('开始获取：',name[n],'的介绍和图片')
                                # 获取评论
                                c = Comment(name[n])
                                comment = c.comment
                                pic = c.pic_url
                                index = '%03d'% len(places)
                                self.data_list.append(int(str(i+1)+index))
                                place = pd.DataFrame({'name':[name[n]],'price':[price],'description':[comment],'picurl':[pic]})
                                places = pd.concat([places,place],ignore_index=True,axis=0)
                                places.to_csv(path,encoding = 'UTF-8')
                            else:
                                index = places[places.name==name[n]].index[0]
                                index = '%03d'% index
                                self.data_list.append(int(str(i+1)+index))
                                places.to_csv(path)


                            
    def save_pic(self):
        if self.data_list != []:
            # 图片
            soup = BeautifulSoup(self.html,'html.parser') 
            img = soup.find('img',class_='pil-figure-image')
            imgsrc = 'https:' + img['src']
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.57'}
            response = requests.get(imgsrc,headers=headers)
            pic_url = 'image/' + imgsrc.split('/')[-1]
            
            print('方案图片存储为：',pic_url,'成功')
            with open(pic_url,'wb') as f:
               f.write(response.content)
            self.data_list.insert(1,pic_url)

    def end_line(self):
        print('方案：',self.url,'已经爬取完毕')



    


a = Fangan(1,'https://vacations.ctrip.com/travel/detail/p26417599','xian')












