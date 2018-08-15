# -*- encoding: utf-8 -*-

from selenium import webdriver
from lxml import etree
import requests
import re
import time
import json
import pymysql

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,und;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
}        
conn = pymysql.connect(host="127.0.0.1", user="root", password="12345678", database="invoice2", port=3306)
curs = conn.cursor()


def get_cookies(url):
    cookie_list = {}
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)
    cookies = driver.get_cookies()
    for co in cookies:
        if co in cookies:
            if co['name'] == '__jsl_clearance' or co['name'] == '__jsluid':
                cookie_list[co['name']] = co['value']
    driver.quit()
    cookies = requests.utils.add_dict_to_cookiejar(cj=None, cookie_dict=cookie_list)
    return cookies


def make_session(url):
    global headers
    cookies = get_cookies(url)
    s = requests.Session()
    s.cookies = cookies
    s.headers = headers
    return s


def fetch(ids):
    for province_id in ids:
        # target_url 对应每个省
        target_light_url = "http://www.gsxt.gov.cn/affiche-query-area-info-paperall.html?" \
                     "noticeType=11&areaid=100000&noticeTitle=&regOrg=" + province_id
        target_serious_url = "http://www.gsxt.gov.cn/affiche-query-area-info-paperall.html?" \
                     "noticeType=21&areaid=100000&noticeTitle=&regOrg=" + province_id
        time.sleep(2)
        print target_serious_url
        # 每省5页
        for i in range(1, 6):
            data = {'draw': i, 'start': (i-1)*10, 'length': 10}
            try:
                response = s.post(target_light_url, data=data, verify=False)
                res_obj = json.loads(response.content)
            except Exception as e:
                pass
            else:
                res_dict = res_obj.get('data', None)
                info_list = []
                if res_dict:
                    # 每页10条
                    for info in res_dict:
                        info_dict = {}
                        info_title = info.get('noticeTitle')
                        info_content = info.get('noticeContent')
                        info_dict['info_id'] = province_id
                        info_dict['info_title'] = info_title
                        info_dict['info_content'] = info_content
                        info_list.append(info_dict)
                parse(info_list, flag=0)

            try:
                response = s.post(target_serious_url, data=data, verify=False)
                res_obj = json.loads(response.content)
            except Exception as e:
                pass
            else:
                res_dict = res_obj.get('data', None)
                info_list = []
                if res_dict:
                    for info in res_dict:
                        info_dict = {}
                        info_title = info.get('noticeTitle')
                        info_content = info.get('noticeContent')
                        info_dict['info_id'] = province_id
                        info_dict['info_title'] = info_title
                        info_dict['info_content'] = info_content
                        info_list.append(info_dict)
                parse(info_list, flag=1)


def parse(info_list, flag):
    no_num_list = []
    num_list = []
    for info_dict in info_list:
        info_id = info_dict.get('info_id')
        info_title = info_dict.get('info_title').encode('utf-8')
        info_content = info_dict.get('info_content')
        try:
            pattern = re.compile(r'\w{14,19}')
            num = pattern.findall(info_content)
            if num[0]:
                num = num[0].encode('utf-8')
            else:
                num = None
        except Exception as e:
            pass
        if flag == 0:
            try:
                pattern = re.compile(r"^关于将(.+)的列入经营|^关于将(.+)列入经营|^关于(.+)的列入经营|^关于(.+)列入|.+列入(.+)经营异常|^(.+)列入经营异常名录|个体工商户(.+)\(经营者")
                company = pattern.findall(info_title)
                print('11', company)
                for com in company[0]:
                    if com:
                        com = com.decode('utf-8')
                        print com
                        if num:
                            light = (com, num, 1)
                            num_list.append(light)    
                        else:
                            light = (com, 1)
                            no_num_list.append(light)
            except Exception as e:
                pass 
                                           
        else:
            try:
                pattern = re.compile(r"^关于(.+)列入严重违法|(.+)列入严重违法企业名单|.+列入(.+)严重违法")
                company = pattern.findall(info_title)
            except Exception as e:
                pass 
            finally:   
                if not company:
                    com = info_content.encode('utf-8').split('统一')[0].decode('utf-8')[:-1]
                    print com
                    if num:
                        serious = (com, num, 2)
                        num_list.append(serious)
                    else:
                        serious = (com, 2)
                        no_num_list.append(serious)

                else:
                    try:
                        print('22', company)
                        for com in company[0]:
                            if com:
                                com = com.decode('utf-8')
                                print com
                                if num:
                                    serious = (com, num, 2)
                                    num_list.append(serious)             
                                else:
                                    serious = (com, 2)
                                    no_num_list.append(serious)
                    except Exception as e:
                        pass
            
    try:
        if num_list:
            execute_sql(num_list, 0)
        elif no_num_list:
            execute_sql(no_num_list, 1)  
    except Exception as e:
        print e


def execute_sql(list, f):
    if f == 0:
        sql = "INSERT INTO company_black_list (company, number, degree) VALUES (%s, %s, %s)"
        curs.executemany(sql, list)
        conn.commit()
    else:
        sql = "INSERT INTO company_black_list (company, degree) VALUES (%s, %s)"
        curs.executemany(sql, list)
        conn.commit()


if __name__ == '__main__':
    url = "http://www.gsxt.gov.cn/corp-query-entprise-info-xxgg-100000.html"
    s = make_session(url)
    r = s.get(url, verify=False)
    print r
    con = r.content.replace('\n', '').replace('\t', '').replace('\r', '')
    content = etree.HTML(con)
    id_list = content.xpath('//div[@class="label-list"]/div/@id')
    fetch(id_list)
    curs.close()
    conn.close()
    


