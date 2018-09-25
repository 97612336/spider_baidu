import datetime
import time

import pymysql

import util

baidu_url = "http://www.baidu.com/baidu?wd="
baidu_fengyun_url = "http://top.baidu.com/"


# 得到热搜的关键词
def get_fengyun_words():
    words_list = []
    fengyun_res = util.get_html_text(baidu_fengyun_url)
    # 得到实时热点关键词
    now_hot_words = util.html_parser(fengyun_res, '//*[@id="hot-list"]/li/a[@class="list-title"]/text()')
    words_list = words_list + now_hot_words
    # 得到七日关注热词
    seven_day_words = util.html_parser(fengyun_res,
                                       '//*[@id="main"]/div[1]/div[1]/div[3]/div[2]/ul/li/a[@class="list-title"]/text()')
    words_list = words_list + seven_day_words
    # 得到今日上榜热词
    new_hot_words_tmp = util.html_parser(fengyun_res, '//*[@id="flip-list"]/div[1]/div/div/a/text()')
    new_hot_words = []
    for one_word in new_hot_words_tmp:
        new_one_word = str(one_word).strip()
        new_hot_words.append(new_one_word)
    words_list = words_list + new_hot_words
    #     得到民生热点词
    man_life_words = util.html_parser(fengyun_res,
                                      '//*[@id="box-cont"]/div[4]/div[2]/div/div[2]/div[1]/ul/li/div[1]/a[@class="list-title"]/text()')
    words_list = words_list + man_life_words
    #     得到热门搜索
    hot_search_words = util.html_parser(fengyun_res,
                                        '//*[@id="box-cont"]/div[8]/div[2]/div/div[2]/div[1]/ul/li/div[1]/a[@class="list-title"]/text()')
    words_list = words_list + hot_search_words
    words_set = set(words_list)
    return words_set


# 搜索热词，得到热词网页
def search_hot_words(one_hot_word):
    new_url = baidu_url + one_hot_word
    html_text = util.get_html_text(new_url)
    # 获取百度快照url
    href_list = util.html_parser(html_text, '//div[@class="result c-container "]/div[@class="f13"]/a[@class="m"]/@href')
    return href_list


# 根据一个快照链接，得到具体的网页内容
def get_content_by_one_href(one_href):
    html_text = util.get_html_text(one_href)
    head_str = '<div style="position:relative">'
    body_str_tmp = html_text.split('<div style="position:relative">')[-1]
    body_str = body_str_tmp.split('</body>')[0]
    new_html = head_str + body_str
    return new_html


# 执行存入数据库的操作
def save_to_db(one_word, html_str):
    db = util.get_mysql_db()
    cursor = db.cursor()
    new_html = pymysql.escape_string(html_str)
    sql_str = "insert into articles (html,hot_word) VALUES(\'%s\',\'%s\');" % (new_html, one_word)
    cursor.execute(sql_str)
    db.commit()
    print("成功存入一条数据：%s" % datetime.datetime.now())
    cursor.close()
    db.close()


# 删除一周前的内容
def del_week_age_articles():
    db = util.get_mysql_db()
    cursor = db.cursor()
    # 获取当前时间
    now_time = datetime.datetime.now() - datetime.timedelta(days=7)
    now_time_str = str(now_time)
    sql_str = "delete from articles where save_time<'%s';" % (now_time_str)
    res = cursor.execute(sql_str)
    print("删除了%s行数据" % res)
    db.commit()
    cursor.close()
    db.close()


if __name__ == '__main__':
    while 1:
        # 得到所有搜索的热词
        hot_set = get_fengyun_words()
        # 遍历每个热词，然后搜索每个热词，得到html网页里所有百度快照的链接
        print("共得到%s个关键词" % len(hot_set))
        for one_word in hot_set:
            # 根据一个搜索的关键词查询所有的百度快照url
            href_list = search_hot_words(one_word)
            for one_href in href_list:
                # 得到百度快照ＵＲＬ的内容
                new_html = get_content_by_one_href(one_href)
                # 执行存入数据库的操作
                save_to_db(one_word, new_html)
        del_week_age_articles()
        # 休息十个小时
        print("运行完一次，休息10个小时")
        time.sleep(60 * 60 * 10)
