import datetime
import json
import os
from lxml import etree

import chardet
import pymysql
import requests


def get_mysql_db():
    home_path = os.getenv("HOME")
    conf_file_path = home_path + "/conf/sqlconf"
    with open(conf_file_path, "r") as f:
        conf_str = f.read()
    conf_dict = json.loads(conf_str)
    conn = pymysql.connect(host=conf_dict.get("SqlHost"), port=int(conf_dict.get("SqlPort")),
                           user=conf_dict.get("SqlUser"), password=conf_dict.get("SqlPassword"),
                           db="bigbiy_web", charset='utf8mb4')
    return conn


# 获取URL的网页HTML
def get_html_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
    }
    res = requests.get(url, headers=headers)
    html_bytes = res.content
    code_style = chardet.detect(html_bytes).get("encoding")
    try:
        html_text = html_bytes.decode(code_style, "ignore")
    except:
        print(datetime.datetime.now())
        print("encoding is error")
        return ''
    return html_text


def html_parser(html_text, compl_str):
    # 解析HTML文件
    # try:
    tree = etree.HTML(html_text)
    res = tree.xpath(compl_str)
    # except:
    #     print(datetime.datetime.now())
    #     print("can't parse html")
    #     return
    return res
