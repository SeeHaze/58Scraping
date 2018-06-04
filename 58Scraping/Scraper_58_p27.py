# -*- coding:utf8 -*-
#encoding = utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import time
import lxml.html
import cookielib
import httplib
import requests

from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

import pymysql

# user_Agent
user_Agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
host_url=''
# 初始化配置
def initWork():
    # 初始化配置根据自己chromedriver位置做相应的修改
    chromedriver = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    return driver

# 执行登录
def handleLogin(username,password):
    # 执行操作的页面地址
    url = 'https://passport.58.com/login'
    # driver.set_window_size(480, 760)
    driver.get(url)
    # 获得cookie信息
    cookie1 = driver.get_cookies()
    # 将获得cookie的信息打印
    print "[cookie1]: "+str(cookie1)

    elem = driver.find_element_by_xpath("//*[@id='pwdLogin']/i")
    item = elem.text
    # print str(item)
    if item == "密码登录":
        sleep(2)
        elem = driver.find_element_by_xpath("//*[@id='pwdLogin']/i");
        elem.click()
        # 休眠两秒钟后执行填写用户名和密码操作
        sleep(2)
        elem = driver.find_element_by_xpath("//*[@id='usernameUser']");
        elem.send_keys(username)
        sleep(2)
        # 58同城输入密码这里具有迷惑性，id='passwordUserText'这个input不是输入密码的地方，
        # 点击这个input之后会隐藏，然后id='passwordUser'显示出来，这个才是输入密码的地方。
        elem = driver.find_element_by_xpath("//*[@id='passwordUserText']");
        elem.click()
        elem = driver.find_element_by_xpath("//*[@id='passwordUser']");
        elem.send_keys(password)
        elem = driver.find_element_by_xpath("//*[@id='btnSubmitUser']");
        elem.send_keys(Keys.ENTER)
        cookie2 = driver.get_cookies()
        # 将获得cookie的信息打印
        print  "[cookie2]: "+str(cookie2)
    else:
        # 休眠两秒钟后执行填写用户名和密码操作
        sleep(2)
        elem = driver.find_element_by_xpath("//*[@id='usernameUser']");
        elem.send_keys(username)
        sleep(2)
        elem = driver.find_element_by_xpath("//*[@id='passwordUserText']");
        elem.click()
        elem = driver.find_element_by_xpath("//*[@id='passwordUser']");
        elem.send_keys(password)
        elem = driver.find_element_by_xpath("//*[@id='btnSubmitUser']");
        elem.send_keys(Keys.ENTER)
        cookie2 = driver.get_cookies()
        # 将获得cookie的信息打印
        print  "[cookie2]: "+str(cookie2)

#获取网页源码
def getPage(url,cookies):
    try:
        # 将获取的cookies带入请求中
        s = requests.Session()
        requests.utils.add_dict_to_cookiejar(s.cookies, cookies)
        s.headers.update({'User-Agent': user_Agent})
        response = s.get(url)
        response.encoding="utf-8"
        # print response.text
        return response.text
    except requests.RequestException as e:
        if hasattr(e,"reason"):
            print u"连接失败，错误原因",e.reason
            return None

# #获取网页源码
# def getPageBySelenium(url):

#获取各类别的链接
def getCategoryUrl(Url,cookies):
    Page = getPage(Url,cookies)
    tree = lxml.html.fromstring(Page)#将网页源码转成lxml格式
    urls = []
    items = tree.cssselect('div.sidebar-right > ul > li > a')#div.sidebar-right > ul > li > a
    for item in items: #按照分类
        # url=item.text_content()
        url=item.get('href')
        types=item.text.encode('utf-8').strip()
        urls.append(types+'|'+host_url+url.encode('utf-8')[1:])
        print types+'|'+host_url+url.encode('utf-8')[1:]
    # print urls
    # page=getPage('http://jn.58.com/zpgangjin/',cookies)
    # itemPage=getCategoryPageNum(page)
    return urls

#获取招聘信息页面页数
def getCategoryPageNum(page):
    tree = lxml.html.fromstring(page)
    itemPage=''
    itemPage = tree.cssselect('body > div.con > div.main.clearfix > div.leftCon > div.pagesout > span.num_operate > i')[-1].text_content()
    # print itemPage
    return itemPage

# 获取各类别下的各条招聘信息
def getRecruitUrl(url,cookies):
    Page = getPage(url,cookies)
    # print Page
    itemPageNum=getCategoryPageNum(Page)
    if not itemPageNum.strip():
        itemPageNum='1'
    print itemPageNum
    urlLists = []
    for i in range(1,int(itemPageNum)+1):
        if i > 1:
            Page = getPage(url+'pn'+str(i)+'/',cookies)
        if i%10==0:
            sleep(10)
        tree = lxml.html.fromstring(Page)
        items = tree.cssselect('ul#list_con > li > div.item_con.job_title > div.job_name.clearfix > a')
        for item in items:
            proUrl = item.get('href')
            print proUrl
            urlLists.append(proUrl.encode('utf-8'))
            info_list=getRecrInfo(proUrl,cookies)
            for info in info_list:
                print info
                # print info.decode('utf-8')
                # print bytes.decode(info)
                # print info
            writeDate(info_list)
            sleep(2)
    return urlLists

# 获取招聘的信息：
def getRecrInfo(url,cookies):
    recrPage = getPage(url,cookies)
    try:
        tree = lxml.html.fromstring(recrPage)
        jobtitle_ele = tree.cssselect('body > div.con > div.leftCon > div.item_con.pos_info > div.pos_base_info > span.pos_title')
        jobtitle=''
        if len(jobtitle_ele)>0:
            jobtitle=bytes.decode(jobtitle_ele[0].text_content().encode('utf-8').strip()).encode('utf-8')#职位标题
        print jobtitle
        jobname_ele = tree.cssselect('body > div.con > div.leftCon > div.item_con.pos_info > span')
        jobname=''
        if len(jobname_ele)>0:
            jobname=bytes.decode(jobname_ele[0].text_content().encode('utf-8').strip()).encode('utf-8')#职位名称
        print jobname
        jobdescription_ele = tree.cssselect('body > div.con > div.leftCon > div:nth-child(2) > div.subitem_con.pos_description > div.posDes > div.des')
        jobdescription=''
        if len(jobdescription_ele)>0:
            jobdescription=bytes.decode(jobdescription_ele[0].text_content().encode('utf-8').strip().replace('<br>','')).encode('utf-8')#职位描述
        print jobdescription
        wages_ele = tree.cssselect('body > div.con > div.leftCon > div.item_con.pos_info > div.pos_base_info > span.pos_salary')
        wages=''
        if len(wages_ele)>0:
            wages=bytes.decode(wages_ele[0].text_content().encode('utf-8').strip().replace('<span class="font18">元/月</span>','')).encode('utf-8')#薪资
        print wages
        companyname_ele = tree.cssselect('body > div.con > div.rightCon > div:nth-child(1) > div > div.comp_baseInfo_title > div.baseInfo_link > a')
        companyname=''
        if len(companyname_ele)>0:
            companyname=bytes.decode(companyname_ele[0].text_content().encode('utf-8').strip()).encode('utf-8')#公司名称
        print 'companyname: ',companyname
        companyinfo_ele = tree.cssselect('body > div.con > div.leftCon > div:nth-child(2) > div.subitem_con.comp_intro > div.txt > div > div > div > p')
        companyinfo=''
        if len(companyinfo_ele)>0:
            companyinfo=bytes.decode(companyinfo_ele[0].text_content().encode('utf-8').strip().replace('<br>','')).encode('utf-8')#公司简介
        print 'companyinfo: ',companyinfo
        education_ele = tree.cssselect('body > div.con > div.leftCon > div.item_con.pos_info > div.pos_base_condition > span:nth-child(2)')
        education=''
        if len(education_ele)>0:
            education=bytes.decode(education_ele[0].text_content().encode('utf-8').strip()).encode('utf-8')#学历
        print 'education: ',education
        educationremark_ele = tree.cssselect('body > div.con > div.leftCon > div.item_con.pos_info > div.pos_base_condition > span.item_condition.border_right_None')
        educationremark=''
        if len(educationremark_ele)>0:
            educationremark=bytes.decode(educationremark_ele[0].text_content().encode('utf-8').strip()).encode('utf-8')#学历经验备注
        print 'educationremark: ',educationremark
        number_people_ele = tree.cssselect('body > div.con > div.leftCon > div.item_con.pos_info > div.pos_base_condition > span.item_condition.pad_left_none')
        number_people=''
        if len(number_people_ele)>0:
            number_people=bytes.decode(number_people_ele[0].text_content().encode('utf-8').strip()).encode('utf-8')#人数
        print 'number_people: ',number_people
        address_ele = tree.cssselect('body > div.con > div.leftCon > div.item_con.pos_info > div.pos-area > span:nth-child(2)')
        address=''
        if len(address_ele)>0:
            address=bytes.decode(address_ele[0].text_content().encode('utf-8').strip()).encode('utf-8')#地址
        print 'address: ',address
        # print jobtitle,jobname,jobdescription,wages,companyname,companyinfo,education,educationremark,number_people,address
        return [jobtitle,jobname,jobdescription,wages,companyname,companyinfo,education,educationremark,number_people,address]
    except Exception,e:
        print e

#写入数据库
def writeDate(info):
    try:
        conn = pymysql.connect(host = '127.0.0.1',  # 远程主机的ip地址， 
                                user = 'root',   # MySQL用户名
                                db = 'scraper58',   # database名
                                passwd = '123456',   # 数据库密码
                                port = 3306,  #数据库监听端口，默认3306
                                charset = "utf8")  #指定utf8编码的连接
        cursor = conn.cursor()  # 创建一个光标，然后通过光标执行sql语句
        if info:
            # print "INSERT INTO Scraper_recruitinfo (fjobtitle, fjobname, fjobdescription, fwages, fcompanyname, fcompanyinfo, feducation, feducationremark, fNumberofpeople, faddress) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",[info[0],info[1],info[2][0:254],info[3],info[4],info[5],info[6],info[7],info[8],info[9]]

            cursor.execute(
                    "INSERT INTO `Scraper_recruitinfo` (`fjobtitle`, `fjobname`, `fjobdescription`, `fwages`, `fcompanyname`, `fcompanyinfo`, `feducation`, `feducationremark`, `fNumberofpeople`, `faddress`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    [info[0].encode('utf-8'),info[1].encode('utf-8'),info[2].encode('utf-8')[0:254],info[3].encode('utf-8'),info[4].encode('utf-8'),info[5].encode('utf-8'),info[6].encode('utf-8'),info[7].encode('utf-8'),info[8].encode('utf-8'),info[9].encode('utf-8')])
        cursor.close()  #关闭光标
        conn.commit()  #保存
        conn.close()  #关闭连接
    except Exception,e:
        print e

if __name__ == '__main__':

    # 定义登录的用户名密码
    username = "17865150518"
    password = "yzw199567"

    driver = initWork()
    try:
        driver.set_window_size(480, 760)
        driver.get('http://www.58.com')
        host_url = driver.current_url
        print "host_url:",str(host_url)
        elems = handleLogin(username,password)
        cookie3 = driver.get_cookies()
        # for cookie in cookie3:
        #     print "driver.add_cookie({\'name\':\'%s\', \'value\':\'%s\'})" % (cookie['name'], cookie['value'])
        cookies = {}
        for item in cookie3:
            cookies[item['name']] = item['value'] 
        print "【开始采集】"
        urls=getCategoryUrl(str(host_url)+"/job.shtml",cookies)
        for url in urls:
            recruitUrls=getRecruitUrl(url.split("|")[1],cookies)
            # print recruitUrls
            sleep(7)
        print '结束'
    finally:
        driver.close()
        driver.quit()
    pass