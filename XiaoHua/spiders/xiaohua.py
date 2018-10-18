# --coding:utf-8--
import scrapy
from XiaoHua.items import XiaohuaItem
from scrapy.http import Request
import requests
import re
import os
from bs4 import BeautifulSoup
import sys
reload(sys)

sys.setdefaultencoding('utf-8')

class Myspider(scrapy.Spider):
    name='XiaoHua'
    allowed_domains=['mmonly.cc']
    base=r'/Users/Jason/Desktop/picture/'
    def start_requests(self):
        #一共有6页
        url = 'http://www.mmonly.cc/tag/'

        yield Request(url,callback=self.parse_one)

    def parse_one(self,response):
        #创建一个大的list存储所有的item
        base_url="http://www.mmonly.cc"
        items=[]
        websoup=BeautifulSoup(response.text)
        a_dicts=websoup.find_all('div', "TagList")[0].find_all('a')
        for a_text in a_dicts:
            #创建实例,并转化为字典
            main=(a_text['href'], a_text['title'])
            item=XiaohuaItem()
            item['siteURL']=base_url+main[0]
            item['title']=main[1]
            item['fileName']=self.base+item['title']
            items.append(item)

        for i in range(1):
            #创建文件夹
            item = items[0]
            fileName=item['fileName']
            if not os.path.exists(fileName):
                os.makedirs(fileName)
            #用meta传入下一层
            yield Request(url=item['siteURL'],meta={'item1':item},callback=self.parse_two)

    def parse_two(self,response):
        #传入上面的item1
        item2=response.meta['item1']
        items=[]
        html=response.text
        webSoup=BeautifulSoup(html)
        div_soups=webSoup.find_all('div', 'item masonry_brick masonry-brick')
        for div_soup in div_soups:
            imageURL=div_soup.find_all('div', 'img')[0].find_all('img')[0]['src']
            title=div_soup.find_all('div', 'title')[0].text
            pageURL=div_soup.find_all('div', 'img')[0].find_all('a')[0]['href']
            item = XiaohuaItem()
            item['meizhiURL']=pageURL
            item['fileName']=item2['fileName']+'/'+title
            item['title']=title
            items.append(item)
        for i in range(1):
            item=items[0]
            fileName=item['fileName']
            if not os.path.exists(fileName):
                os.makedirs(fileName)
            yield Request(url=item['meizhiURL'], meta={'item2': item}, callback=self.parse_three)

    def parse_three(self, response):
        item3 = response.meta['item2']
        html = response.text.encode('utf-8')
        # 用正则提取页数
        pattern = re.compile(r'共(.*?)页', re.S)
        Num = re.search(pattern, html).group(1)
        for i in range(1, int(Num)+1):
            item=XiaohuaItem()
            item['fileName']=item3['fileName']
            item['path']=item['fileName']+'/'+str(i)+'.jpg'

        '''
        websoup = BeautifulSoup(html)
        Num=websoup.find_all('div', "wrappic")
        print(Num)
        items=[]
        for i in range(1,int(Num)+1):
            item=XiaohuaItem()
            item['fileName']=item2['fileName']
            #构造每一个图片的存储路径
            item['path']=item['fileName']+'/'+str(i)+'.jpg'
            #构造每一个图片入口链接，以获取源码中的原图链接
            item['pageURL']=response.url[:-5]+'_'+str(i)+'.html'
            items.append(item)
        for item in items:
            #yield Request(url=item['pageURL'],meta={'item2':item},callback=self.parse_three)
        '''

    def parse_four(self,response):
        item=XiaohuaItem()
        #传入上面的item2
        item3=response.meta['item2']
        pattern=re.compile(r'<li class="pic-down h-pic-down"><a target="_blank" class="down-btn" href=\'(.*?)\'>.*?</a>',re.S)
        URL=re.search(pattern,response.text).group(1)
        item['detailURL']=URL
        item['path']=item3['path']
        item['fileName']=item3['fileName']
        yield item










