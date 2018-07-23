import codecs
import json
from urllib.request import urlopen
import re
import requests
import time
from bs4 import BeautifulSoup
import pymysql


class JDSelfSpider:
    def init(self):
        return 0

    def html_spider(self, url):
        html = urlopen(url)
        bsObj = BeautifulSoup(html.read())
        s = str(bsObj)
        return s

    def s2file(self, content, filepath):
        fh = open(filepath, 'w', encoding='utf-8')
        fh.write(content)
        fh.close()

    def match_title(self, _text):
        nnum = re.search(r'<div class="sku-name">[\s\S]+</div>[\s\S]+<div class="news">', _text)
        title = str(nnum.group())
        title = title.replace('<div class="sku-name">', "")
        title = title.replace('</div>', "")
        title = title.replace('<div class="news">', "")
        title = title.replace('\n', "")
        title = title.replace("  ", "")
        title = re.sub(r'<img alt=".*>', '', title)
        return title

    def match_price_stock(self, skuNum):
        url = "https://c0.3.cn/stock?skuId=" + skuNum + "&area=1_72_4137_0&cat=9987,653,655&buyNum=1&choseSuitSkuIds=&extraParam={%22originid%22:%221%22}&ch=1&fqsp=0&pduid=1517411915024356082147&pdpin=&detailedAdd=null&callback=jQuery6632357"
        _text = self.html_spider(url)
        _text = str(_text)
        # price = re.search(r'("m":"[\s\S]+","id":"\d+)|("p":"[\s\S]+","id":"\d+)', _text)
        price = re.search(r'"p":"[\s\S]+","id":"\d+', _text)
        if not price:
            price = re.search(r'"m":"[\s\S]+","id":"\d+', _text)
        stock = re.search(r'<strong>[\S]+</strong>', _text)
        price = str(price.group())
        price = price.replace('"', '')
        price = price.replace(':', '')
        price = price.replace('p', '')
        price = price.replace('m', '')
        price = re.sub(r',id[\d]+', '', price, count=0)
        stock = str(stock.group())
        stock = stock.replace("<strong>", "")
        stock = stock.replace("</strong>", "")
        return price, stock

    # 获取评论
    def get_comment(self, num, score=0, filename='0'):  # 分析json其中score的值与差评好评相关
        session = requests.Session()
        session.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
                                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        with codecs.open(filename, 'w', 'utf-8') as file:
            for page in range(20):  # 每个page有一定数目的评论
                try:
                    url = self.get_URL(str(num), score, page)
                    data = session.get(url)
                    data = re.sub(r'fetchJSON_comment98vv37157\(', '', data.text)
                    data = data[:-2]
                    data = json.loads(data)
                    for each in data['comments']:
                        file.write(each['content'].strip('\n') + '\n')
                    print(url)
                    print('Finished!')
                except:
                    print('error')
                    pass

    def get_URL(self, num, score=0, page=0):
        url = 'https://club.jd.com/comment/productPageComments.action?callback=' \
              'fetchJSON_comment98vv37157&productId=' + num + '&score=' + str(score) + \
              '&sortType=6&page=' + str(page) + '&pageSize=10&isShadowSku=0&fold=1'
        return url

    def get_Detail_Keys(self, _text):
        nnums = re.findall(r'<dt>.*</dt><dd>.*</dd>', _text)
        dict_keys = {}
        for nnum in nnums:
            key = re.search(r'<dt>.*</dt>', nnum)
            value = re.search(r'<dd>.*</dd>', nnum)
            key_s = str(key.group())
            key_s = key_s.replace("<dt>", "")
            key_s = key_s.replace("</dt>", "")
            value_s = str(value.group())
            value_s = value_s.replace("<dd>", "")
            value_s = value_s.replace("</dd>", "")
            dict_keys[key_s] = value_s
        return dict_keys

    def get_ImgUrls(self, _text):
        nnums = re.findall(r'data-url.*width', _text)
        smallImgUrl = []
        for nnum in nnums:
            imgUrl = re.search(r"src=.*width", nnum)
            imgUrl = str(imgUrl.group())
            imgUrl = imgUrl.replace('src="//', '')
            imgUrl = imgUrl.replace("width", "")
            imgUrl = imgUrl.replace('"', '')
            smallImgUrl.append(imgUrl)
        return smallImgUrl

    def Integrate(self, num):
        url = "https://item.jd.com/" + str(num) + ".html"
        # 爬取html源码信息并返回字符串
        try:
            _text = self.html_spider(url)
            #time.sleep(3)
            print(num)
        except:
            pass
        if '<div class="itemover-tip">' in _text or "sku-name" not in _text:
            return -1
        # 匹配标题
        try:
            title = self.match_title(_text)
        except:
            pass
        # 匹配价格和库存
        try:
            price, stock = self.match_price_stock(skuNum=str(num))
        except:
            pass
        # 抓取评论
        try:
            commentFilePath = "comment/jd/jd_comment_" + str(num) + ".txt"
            self.get_comment(num, filename=commentFilePath)
        except:
            pass
        # 匹配商品规格属性键值对
        try:
            detail_keys = self.get_Detail_Keys(_text)
        except:
            pass
        # 匹配商品小图信息
        try:
            smallImgUrls = self.get_ImgUrls(_text)
        except:
            pass
        # 返回标题、价格、库存、评论文本路径、属性键值字典、小图列表
        return 0, num, str(title), str(price), str(stock), str(commentFilePath), str(detail_keys), str(smallImgUrls)

    # 写入数据库
    def write2database(self):
        con=pymysql.connect(host="127.0.0.1",user="root",passwd="zhaolei",db="goodsinfo",charset='utf8')
        cur = con.cursor()

        for num in range(1489166, 4000000, 1):
            data=self.Integrate(num)
            if data == -1:
                continue

            try:
                r = cur.execute('insert into tmp_1 values(%s,%s,%s,%s,%s,%s,%s,%s)', data)
                if r > 0:
                    print("success")
            except:
                pass
        con.commit()
        con.close()


if __name__ == '__main__':
    test = JDSelfSpider()
    num_six = 100000
    num_seven = 1000000
    num = 941677
    ##爬取不到完整界面的问题
    # title,price,stock,commentFilePath,detail_keys,smallImgUrls=test.Integrate(num)
    # print(test.Integrate(num))
    test.write2database()
    # con=pymysql.connect(host="127.0.0.1",user="root",passwd="root",db="goodsinfo",charset='utf8')
    # cur=con.cursor()
    # data=0,1234569978,'test',"test",'test','test','test','2'
    # data=(0, 941676, '佳洁士（Crest）闪耀炫白 牙贴14件装（祛牙渍 茶渍 咖啡渍 美国原装进口）（新老包装 随机发货）', '239.00', '有货', 'comment/jd/jd_comment_941676.txt', '{}', "['img11.360buyimg.com/n5/jfs/t5662/23/8710780693/202295/ddc64a15/597eb019N0410cacb.jpg ', 'img11.360buyimg.com/n5/jfs/t2953/243/1291523551/82701/a6a63240/577b26f6N0c884aa6.jpg ', 'img11.360buyimg.com/n5/jfs/t2755/38/2972900608/68976/4fbc2f20/577b26faN1011da87.jpg ', 'img11.360buyimg.com/n5/jfs/t2632/333/2997901139/88753/6a01db8b/577b26fdNcd4b7843.jpg ', 'img11.360buyimg.com/n5/jfs/t2737/285/2958236121/58095/a9123dde/577b2700N9dc00fc0.jpg ']")
    # r=cur.execute('insert into jd values(%s,%s,%s,%s,%s,%s,%s,%s)',data)
    # # r=cur.execute('insert into jd values(0,1234569978,"test","test","test","test","test","2")')
    # print(r)
    # str和dict
    # l={1:2,2:3}
    # l=str(l)
    # l=eval(l)
    # print(l[1])