#edit by eggnice
# *_* coding: utf-8 *_*

import sys
import os
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
import datetime
import time
import random

class Rush_buy(object):
    def __init__(self, buy_time, login_retry, driver_path='', submit_times=10):
        self.buy_time = buy_time
        self.max_login_retry = login_retry
        self.curry_login_times = 0
        self.login_success = False
        self.submit_times = int(submit_times)
        self.driver_path = driver_path
        self.browser = ''

    def open_browser(self):
        #初始化浏览器
        option = webdriver.ChromeOptions()
        option.add_argument('disable-infobars')
        try:
            webdriver.Chrome(chrome_options=option)
        except WebDriverException, e:
            self.browser = webdriver.Chrome(executable_path=self.driver_path, chrome_options=option)
        except Exception, e:
            print '打开浏览器遇到错误: %s' %e
            sys.exit(1)
        #driver.maximize_window(),最大化浏览器

    def login(self):
        #登录淘宝
        self.browser.get('https://www.taobao.com') 
        try:
            if self.curry_login_times > self.max_login_retry:
                print "登录次数已经超过最大尝试登录次数"
                sys.exit(1)
            self.browser.find_element_by_link_text("亲，请登录")
            self.browser.find_element_by_link_text("亲，请登录").click()
            print '请用手机扫描二维码进行登录'
            time.sleep(10)
            if self.browser.find_element_by_link_text("亲，请登录"):
            #如果等待10ｓ还没登录则继续重新登录
                self.curry_login_times += 1
                self.login()
        except NoSuchElementException, e:
            print "登录成功"
            self.login_success = True
        except Exception, e:
            print '重新尝试第%d次登录，点击登录出错: %s' %(self.curry_login_times, e)
            self.curry_login_times += 1
            self.login()

    def _refresh_keep_alive(self):
        #通过不断刷新购物车界面达到session保持
        if self.login_success:
            while (self.buy_time - datetime.datetime.now()).seconds > 150:
                self.browser.get('https://cart.taobao.com/cart.htm')
                time.sleep(60)
            return True

    def buy_action(self):
        #提交购物篮物品
        self.browser.get('https://cart.taobao.com/cart.htm')
        time.sleep(1)
        #尝试选择购物车所有物品
        try:
            self.browser.find_element_by_id("J_SelectAll1")
            self.browser.find_element_by_id("J_SelectAll1").click()
        except Exception, e:
            print "选择物品出错:%s" %e 
            sys.exit(1)
        #等待时间到抢购时间
        while datetime.datetime.now() < self.buy_time:
            time.sleep(0.1)
        #开始结算
        try:
            self.browser.find_element_by_id('J_Go')
            self.browser.find_element_by_id('J_Go').click()
        except Exception, e:
            print '开始结算出错:%s' %e
            sys.exit(1)
        #开始提交订单
        for t in range(self.submit_times):
            try:
                self.browser.set_page_load_timeout(10)
                self.browser.find_element_by_link_text('提交订单').click()
                print '提交应该成功了,请在24小时内付款' 
                sys.exit(0)
            except TimeoutException, e:
                continue
            except Exception, e:
                print "未知错误:%s" %e
                continue
        print '经过%d次尝试都无法提交订单' %self.submit_times 
                

    def start_buy(self):
        #开始
        if self.buy_time - datetime.timedelta(seconds=20) < datetime.datetime.now():
            print '输入的抢购时间已过: %s' %str(self.buy_time); sys.exit(1)
        else:
            self.open_browser()
        if self.browser:
            print '打开浏览器完成'
            self.login()
        if self.login_success:
            print '登录淘宝成功,开始刷新session'
            if self._refresh_keep_alive():
                print '开始提交购物车订单'
                self.buy_action()

if __name__ == '__main__':
    try:
        buy_t = '2018-12-07 09:11:00'
        driver_path = os.path.abspath(os.path.curdir) + '/chromedriver'
        buy_time = datetime.datetime.strptime(buy_t, '%Y-%m-%d %H:%M:%S')
    except Exception, e:
        print '输入的时间格式有误,请输入时间:年-月-日 时:分:秒'
        sys.exit(1)
    obj = Rush_buy(buy_time, 3, driver_path=driver_path)
    obj.start_buy()
