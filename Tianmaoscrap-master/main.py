# coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
import uuid
import re
from bs4 import BeautifulSoup
import urllib2
import requests
import json
import codecs


class TmallScrap:
    url = 'https://list.tmall.com/search_product.htm?q=%B1%CA%BC%C7%B1%BE&type=p&vmarket=&spm=875.7931836%2FB.a2227oh.d100&from=mallfp..pc_1_searchbutton'
    cookie = ''
    img_pth = 'img'

    def __init__(self):
        driver = webdriver.PhantomJS()
        driver.get("https://login.taobao.com/member/login.jhtml")
        time.sleep(5)
        # 用户名 密码
        elem_user = driver.find_element_by_name("TPL_username")
        elem_user.send_keys("your user name")
        elem_pwd = driver.find_element_by_name("TPL_password")
        elem_pwd.send_keys("your pass word")
        submit_btn = driver.find_element_by_id("J_SubmitStatic")

        time.sleep(3)
        submit_btn.send_keys(Keys.ENTER)

        cookies = driver.get_cookies()
        self.cookie = "; ".join([item["name"] + "=" + item["value"] for item in cookies])

    def get_soup(self, _url, _cookie, _refer=None):
        url = _url
        headers = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
            "cookie": self.cookie,
            "referer": _refer}

        response = requests.get(url, headers=headers)
        contents = response.content

        soup = BeautifulSoup(contents, 'html.parser')
        return soup

    def generate_ip(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'}
        url = 'http://www.xicidaili.com/nn/1'
        s = requests.get(url, headers=headers)
        soup = BeautifulSoup(s.text, 'lxml')
        ips = soup.select('#ip_list tr')
        ip_list = []
        for i in ips:
            try:
                ipp = i.select('td')
                ip = ipp[1].text
                host = ipp[2].text
                ip_list.append(ip + ':' + host)
            except Exception as e:
                print ' '
        return ip_list

    def save_image(self, _url, save_path, _filename):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        img_data = requests.get(_url).content
        path = save_path + "/" + _filename + '.jpg'
        with open(path, 'wb') as handler:
            handler.write(img_data)

    def get_dic(self, sku_id, header_url, endco):
        headers2 = {'Referer': header_url}
        url3 = "https://mdskip.taobao.com/core/initItemDetail.htm?itemId=" + sku_id
        sess_j = requests.Session()
        sess_d = sess_j.get(url3, headers=headers2)
        sess_d.encoding = endco
        recall_info = json.loads(sess_d.text)
        return recall_info

    def get_basicinfo(self, soup):
        product_list = []
        product_title = soup.find("div", {"id": "J_ItemList"})
        # print product_title

        # take care 广告
        # product_title = [x for x in product_title if x.get('class', []) == ['product', 'item-1111', '']]
        product_item = product_title.find_all("div", {"class": "product "})
        for index, item in enumerate(product_item):
            product_img = []
            sku_id =item['data-id']
            seller_name = item.find("div", class_='productShop').find("a", class_='productShop-name').text
            shop_price = item.find("p", class_='productPrice').find("em").text
            shop_title = item.find("div", class_='productTitle').find_all("a")
            product_name = ''
            for item_title in shop_title:
                product_name += item_title.text.strip()
            sales_count_a = item.find("p", class_='productStatus') and item.find("p", class_='productStatus').text
            sales_count = sales_count_a and sales_count_a.strip() or "No Shop Status"
            item_url = 'http:' + item.find("div", class_='productImg-wrap').find("a")['href']
            try:
                url_img = 'http:' + item.find("div", class_='productImg-wrap').find("a").find("img")['src']
            except:
                url_img = 'http:' + item.find("div", class_='productImg-wrap').find("a").find("img")['data-ks-lazyload']
            save_path = self.img_pth
            file_name = str(uuid.uuid4())
            product_img.append(file_name)
            self.save_image(url_img, save_path, file_name)
            prosoup = self.get_soup(item_url, self.cookie, item_url)

            proxy_ip_list  = self.generate_ip()

            # get price info
            headers2 = {'Referer': item_url,'cookie':self.cookie}
            url3 = "https://mdskip.taobao.com/core/initItemDetail.htm?itemId=" + sku_id
            proxy = urllib2.ProxyHandler({'http': '121.232.144.76:9000'})
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)
            ws3 = urllib2.urlopen(urllib2.Request(url3, headers=headers2)).read()
            ws2 = ws3.decode('unicode_escape').encode('utf-8')
            # print ws2
            recall_info = json.loads(ws2)
            price_info = recall_info['defaultModel']['itemPriceResultDO']['priceInfo']
            suit_finnal_price_list = []
            for i in price_info:
                try:
                    suit_final_price ={'skuid': i, 'final price': price_info[i]['promotionList'][0]['price']}
                    suit_finnal_price_list.append(suit_final_price)
                except:
                    suit_final_price = {'skuid': i, 'final price': 'No Discount'}
                    suit_finnal_price_list.append(suit_final_price)

            ulimgs = prosoup.find('ul', {"id": "J_UlThumb"})
            imglist = ulimgs.find_all('li')
            for index2, img in enumerate(imglist):
                detailsrc = 'http:' + img.find('a').find('img')['src']
                detail_file_path = self.img_pth
                detail_file_name = str(uuid.uuid4())
                self.save_image(detailsrc, detail_file_path, detail_file_name)
                product_img.append(detail_file_name)
            sss = prosoup.find("div", {"id": "J_DetailMeta"})
            map_list = []
            m = re.search(r"\"(skuList)\":\[(.*?)\]", str(sss))
            pro_json = json.loads('{' + (m.group(0)) + '}')
            pro_list = pro_json['skuList']
            y = re.findall(r"\"(priceCent)\":(\d+),\"(skuId)\":\"(\d+)\",\"(stock)\":(\d+)", str(sss))
            for item_y in y:
                map_json = {item_y[0]: item_y[1],
                            item_y[2]: item_y[3],
                            item_y[4]: item_y[5]
                            }
                map_list.append(map_json)
            list_n = []
            for i in map_list:
                for y in pro_list:
                    if i['skuId'] == y[u'skuId']:
                        map_json = {
                            'default_price': i['priceCent'],
                            'skuId': i['skuId'],
                            'product name': y[u'names'],
                            'stock': i['stock']
                        }
                        list_n.append(map_json)
            finnal_price_list = []
            for i in list_n :
                for y in suit_finnal_price_list:
                    if i['skuId'] == y['skuid']:
                        finnal_price_dic ={
                            'default_price': round(int(i['default_price'])/100, 2),
                            'skuId': i['skuId'],
                            'product name': i['product name'],
                            'stock': i['stock'],
                            'final_price': y['final price']
                        }
                        finnal_price_list.append(finnal_price_dic)


            detail = {
                "sku_id":sku_id,
                "seller_name": seller_name.strip(),
                "Product Price": shop_price.strip(),
                "Product Name": product_name,
                "product Image List": product_img,
                "sales_count": sales_count,
                "item_url": item_url,
                "Product List": finnal_price_list
            }
            product_list.append(detail)

        return product_list

    def out(self, _list):
        for item in _list:
            print "Sku id:", item['sku_id']
            print "Shop Name:", item['seller_name']
            print "Product Price:", item['Product Price']
            print "Product Name:", item['Product Name']
            for p in item['product Image List']:
                print p + '.img'
            print "sales_count:", item['sales_count']
            print "item_url:", item['item_url']
            for i in item['Product List']:
                print 'Product Name:', i['product name'], '  SkuId:', i['skuId'], '  Stock Value:', i['stock'], 'Default price:', i['default_price'], 'Final price:', i['final_price']+'\n',
            print '\n'

    def write(self, _list):
        f = codecs.open('file.txt', 'w', encoding='utf-8')
        for item in _list:
            f.write("Product Name: " + item['Product Name'] + '\n')
            f.write("Sku ID: " + item['sku_id'] + '\n')
            f.write("Product Price: " + item['Product Price'] + '\n')
            f.write("Shop Name: " + item['seller_name'] + '\n')
            f.write("sales_count: " + item['sales_count'] + '\n')
            f.write("item_url: " + item['item_url'] + '\n')
            for p in item['product Image List']:
                f.write(p + '.img' + '\n')
            for i in item['Product List']:
                f.write("Product Name: " + i['product name'] + '  SkuId:  ' + i['skuId'] + '  Stock Value:  ' + i['stock'] +'  Default price:  ' + str(i['default_price'])+ '  Final price:  ' + i['final_price']+'\n',)
            f.write('------ ' + '\n')


if __name__ == '__main__':
    p = TmallScrap()
    soup = p.get_soup(p.url, p.cookie)
    t_list = p.get_basicinfo(soup)
    p.out(t_list)
    p.write(t_list)
