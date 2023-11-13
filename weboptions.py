# -*- coding: utf-8 -*-
import os
from selenium import webdriver
from core.env import ENV
from database.redis import getChromePathKey
from loguru import logger


# 页面初始化的options
def get_webdriver_options(show: bool, userDir: str = '') -> webdriver.ChromeOptions:
    opts = webdriver.ChromeOptions()
    # linux或者show 为False 都开启headless模式
    if show is False or ENV.is_linux():
        opts.add_argument('--headless=new')
    if ENV.is_windows():
        chromePath = ''
        paths = getChromePathKey()
        for pathTmp in paths:
            if os.path.exists(pathTmp):
                chromePath = pathTmp
                break
        if chromePath == '':
            raise Exception('windows环境未检索到chrome.exe文件')
        opts.binary_location = chromePath
    # opts.add_experimental_option("detach", True)  # 不自动关闭浏览器
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])  # 以开发者模式启动调试chrome，可以去掉提示受到自动软件控制
    opts.add_experimental_option('useAutomationExtension', False)  # 去掉提示以开发者模式调用
    opts.add_argument("--window-size=1920,1050")  # 指定浏览器分辨率
    opts.add_argument("--disable-blink-features")
    opts.add_argument("--disable-blink-features=AutomationControlled")  # 隐藏selenium的自动自动控制的功能的显示防止被检测
    opts.add_argument('--disable-gpu')  # 谷歌禁用GPU加速
    opts.add_argument('--force-device-scale-factor=1')
    opts.add_argument('--no-sandbox')  # 禁止沙箱模式，否则肯能会报错遇到chrome异常
    if userDir == '':
        userDir = ENV.join_file_path(ENV.homePath, 'userdatadir')
    opts.add_argument('--user-data-dir={}'.format(userDir))  # 加载前面获取的 个人资料路径
    opts.add_argument(
        '--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"')
    logger.info('user-data-dir: {}'.format(userDir))
    return opts
