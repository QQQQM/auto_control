#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/11/24 9:35
# @Author : Qi Meng
# @File : auto.py

import time
import pyautogui
from selenium import webdriver
from configparser import ConfigParser

# 保护措施，避免失控
pyautogui.FAILSAFE = True
# 为所有的PyAutoGUI函数增加延迟。默认延迟时间是0.1秒。
pyautogui.PAUSE = 0.5
screenWidth, screenHeight = pyautogui.size()

config_parser = ConfigParser()
config_parser.read('config.cfg', encoding='utf-8')
config = config_parser['default']
print(config['driver_path'])

opt = webdriver.ChromeOptions()  # 创建浏览器
opt.headless = False

driver = webdriver.Chrome(executable_path=config['driver_path'], options=opt)  # 创建浏览器对象
driver.maximize_window()  # 最大化窗口

# driver.get('https://scholar.google.com/')  # 打开网页
driver.get("https://f.glgoo.top/scholar?hl=zh-CN&q=" + config['key_word'])  # 打开网页
time.sleep(1)
home_handle = driver.current_window_handle  # home handle 记录原来的句柄
print("成功打开网页！")

'''
# 输入要查找的关键词
driver.find_element_by_id('gs_hdr_tsi').send_keys(config['key_word'])  # 输入窗口
driver.find_element_by_id('gs_hdr_tsb').click()  # 点击确定
time.sleep(2)
'''

num = 0        # num用来记录条目数，即html源码中的编号
cnt = 0        # cnt用来记录已经下载的的pdf数目
while cnt < int(config['num']):
    if num != 0 and num % 10 == 0:                # google学术每页有10项，自动换页
        driver.find_element_by_xpath("//span[@class='gs_ico gs_ico_nav_next']").click()
        time.sleep(2)
        home_handle = driver.current_window_handle  # home handle 记录原来的句柄

    path = "//div[@id='gs_res_ccl_mid']/div[@class='gs_r gs_or gs_scl'][@data-rp = '" + str(num) + \
           "']//span[@class='gs_ctg2']"
    url_path = "//div[@id='gs_res_ccl_mid']/div[@class='gs_r gs_or gs_scl'][@data-rp = '" + str(num) + \
               "']/div/div/div/a"
    num += 1                                      # 对编号数进行累加

    try:
        print("成功定位！编号：", num)
        item = driver.find_element_by_xpath(path)
        url_item = driver.find_element_by_xpath(url_path)
    except:
        print("编号：", num, "定位失败")
        continue

    if item.text != "[PDF]":                               # 如果非pdf内容则跳过
        print("编号：", num, "非pdf文件！")
        continue

    cnt += 1
    url = url_item.get_attribute("href")               # 获得下一个页面的url
    driver.execute_script("window.open('"+url+"')")    # 新窗口模式打开下一个界面
    # item.click()                                     # 普通模式打开
    time.sleep(2)
    print("成功打开PDF文件！")

    handles = driver.window_handles  # 获取所有handles
    if len(handles) == 1:
        continue

    pyautogui.moveTo(screenWidth / 2, screenHeight / 2)  # 鼠标移至中央
    pyautogui.click()                                    # 单击中页面唤醒
    pyautogui.hotkey('ctrl', 's')                        # 快捷键保存pdf
    time.sleep(2)
    pyautogui.press('enter')                             # 确认保存至默认位置
    time.sleep(2)
    print("正在保存！")
    # driver.back()

    pdf_handle = None                                    # 初始化pdf句柄
    for handle in handles:                               # 找出当前句柄
        if handle != home_handle:
            pdf_handle = handle
    driver.switch_to.window(pdf_handle)                  # 切换到pdf句柄
    driver.close()                                       # 关闭当前窗口
    driver.switch_to.window(home_handle)                 # 切换回原来的句柄
