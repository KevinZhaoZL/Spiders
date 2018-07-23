# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#定义需要爬取的数据
class SuningItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    #商品价格
    price = scrapy.Field()
    #商品链接地址
    link = scrapy.Field()
    #商品标题
    title = scrapy.Field()
    #商品所在店铺名
    shopname = scrapy.Field()
    #商品参数
    canshu = scrapy.Field()
    #快递费用
    kuaidi = scrapy.Field()
    #评论人名称
    nickName = scrapy.Field()
    #评论内容
    content = scrapy.Field()
    #评论对象
    commodityName = scrapy.Field()
    #评论时间
    publishTime = scrapy.Field()
    #评论总数
    totalCount = scrapy.Field()
    pass
