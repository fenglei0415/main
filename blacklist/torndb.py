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


def execute_sql(xfmc, xfsbh):
    sql = "SELECT degree from company_black_list where company='%s' OR number='%s' LIMIT 1" % (xfmc, xfsbh)
    print sql
    curs.execute(sql)
    row = curs.fetchall()
    conn.commit()
    print('row=', row)
    if row:
        num = row.get('degree')
        if num == 1:
            error_list.append({'id': RECOGNITION_COMPANY_BLACK_LIGHT,
                                'msg': RECOGNITION_CHOICE.get(RECOGNITION_COMPANY_BLACK_LIGHT)})
        else:
            error_list.append({'id': RECOGNITION_COMPANY_BLACK_SERIOUS,
                                'msg': RECOGNITION_CHOICE.get(RECOGNITION_COMPANY_BLACK_SERIOUS)})



if __name__ == '__main__':
    xfmc = '贵阳市白云区明道装饰工程有限公司企业'
    xfsbh = '915201133088860981'
    execute_sql(xfmc, xfsbh)
    curs.close()
    conn.close()
    