# -*- coding:utf-8 -*-
import re
from pyv8 import PyV8
import requests

TARGET_URL = "http://www.gsxt.gov.cn/corp-query-entprise-info-xxgg-100000.html"


def getHtml(url, cookie=None):
    header = {
        "Host": "www.gsxt.gov.cn",
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
    }
    print '====='
    html = requests.get(url=url, headers=header, timeout=30, cookies=cookie)
    print html.cookies


getHtml(TARGET_URL)