import re,os
import urllib.request
import ssl
import scrapy
from scrapy.http import Request
from sys import path
path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
from suning.items import SuningItem
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.spiders import CrawlSpider, Rule

class SnSpider(RedisCrawlSpider):
    name = "sn"
    redis_key = 'mycrawler:start_urls'
    start_urls = ['http://www.suning.com/']

    def __init__(self, key=None,page=0, *args, **kwargs):
        super(SnSpider, self).__init__(*args, **kwargs)
        self.key=key
        self.page=int(page)
        
    def parse(self, response):
    	for i in range(0,self.page): #此处可以控制爬取该商品的页数，每页大约60件商品
    	    url = "http://search.suning.com/"+str(self.key)+"/&cp="+str(i)
    	    yield Request(url=url,callback=self.pages)

    def pages(self,response):
        body = response.body.decode("utf8","igrone")
        #item = SuningItem()
        links = re.compile(r'www.suning.com/sellers/[0-9]*.html').findall(body)
        for i in links:
            a='http://'
            yield Request(url=a+i,callback=self.next)

    def next(self,response):
        item = SuningItem()
        body = response.body.decode("utf8","igrone")
        item["title"] = response.xpath("//title/text()").extract()[0]
        item["kuaidi"] = response.xpath("//strong/text()").extract()[1]
        item["price"] = response.xpath("//strong/text()").extract()[2]
        item["shopname"] = response.xpath("//p[@class='talk']/a[@class='shopName talk-name']/text()").extract()[0]
        item["canshu"] = response.xpath("//ul[@class=' clearfix']/li/text()").extract()
        item["link"] = response.xpath("//a[@class='bnt-action']/@href").extract()[1]
        id = re.compile(r'[0-9]+').findall(item['link'])
        commentcounturl = "http://review.suning.com/ajax/review_satisfy/general-000000000"+str(id[1])+"-"+str(id[0])+"-----allShop.proccessReview.htm"
        body=urllib.request.urlopen(commentcounturl).read().decode("utf8","igrone")
        item["totalCount"] = re.compile('"totalCount":(.*?),').findall(body)[0]

        allcontent=[]
        allnickName=[]
        allpublishTime=[]
        allcommodityName=[]
        for i in range(1,5):
            commenturl="http://review.suning.com/ajax/review_lists/general-"+str(id[1])+"-"+str(id[0])+"-total-1-default-"+str(i)+"-----reviewList.htm"
            body=urllib.request.urlopen(commenturl).read().decode("utf8","igrone")
            nickName = re.compile('"nickName":"(.*?)"').findall(body)
            content = re.compile('"content":"(.*?)"').findall(body)
            commodityName = re.compile('"commodityName":"(.*?)"').findall(body)
            publishTime = re.compile('"publishTime":"(.*?)"').findall(body)
            allnickName.extend(nickName)
            allcontent.extend(content)
            allcommodityName.extend(commodityName)
            allpublishTime.extend(publishTime)

        item["content"]=allcontent
        item["nickName"]=allnickName
        item["publishTime"]=allpublishTime
        item["commodityName"]=allcommodityName

        yield item


