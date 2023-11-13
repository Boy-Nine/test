# -*- coding: utf-8 -*-
import gzip
import random
import time
from datetime import datetime, timedelta

from loguru import logger
from selenium.webdriver.common.by import By
from typing import *
from rpaweb.webbase import NewShiHuoWebdriver
from rpaweb.webbase import ShiHuoWebdriver
import tb_helper
from shihuorpa.metrics import sendMsg
from my_web_util import MyWebUtil
from selenium.webdriver.remote.webelement import WebElement


# 淘宝风控工具
class TbRiskTool:
    def __init__(self, driver: NewShiHuoWebdriver):
        """
        :param driver:  必须是 接口拦截的NewShiHuoWebdriver  否则用不了
        """
        self.driver: ShiHuoWebdriver = driver
        self.wu = MyWebUtil(self.driver)

    # 拖动滑块主流程
    def tb_slider_drag(self, is_get_url: bool = True) -> bool:
        """
        拖动滑块
        :param is_get_url: 滑块通过后需要刷新下页面 是否需要重新get一下url 默认True 需要
                            全屏滑块 通过refresh刷新页面 可能存在不会通过滑块
                            需要重新get页面才能通过滑块 但是会丢失当前的筛选项
        :return:  True 滑块验证成功  False 滑块验证失败    None 无滑块/滑块验证异常
        """
        msg_err = ''
        for retry in range(3):
            try:
                if retry > 1:
                    logger.warning(f'淘宝风控整体 retry: {retry}')
                # 获取滑块类型
                type_dic = self.get_track_type()
                if type_dic is None:
                    # logger.info('未捕捉到滑块type_dic  返回True')
                    return True
                isFruitType = type_dic.get('isFruitType', False)
                isIframe = type_dic.get('isIframe', False)
                # 接口拦截获取滑块信息 并通过滑块
                is_track_ok = self.skip_slide(isIframe=isIframe, isFruitType=isFruitType, is_get_url=is_get_url)
                if is_track_ok:
                    logger.success('淘宝滑块成功！')
                    # return True
            except Exception as err:
                msg_err += err
                logger.exception(f'淘宝滑块异常：{err}')
            time.sleep(random.uniform(5, 8))
        # 3次失败 发送通知到群里
        sendMsg(userId='', chatId='oc_630846dbcfb991fc4a6564bc223258e2', msg=f'rpakit淘宝滑块验证失败!{msg_err}')
        return False

    # 根据接口拦截滑块获取滑块信息并通过滑块
    def skip_slide(self, isIframe: bool, isFruitType: bool, is_get_url: bool = True) -> bool:
        """
        根据接口拦截滑块获取滑块信息并通过滑块
        :param isIframe: 是否需要进入到iframe
        :param isFruitType: 是否是水果滑块
        :param is_get_url: 是否需要根据referer 重新get一下url 确保滑块通过
        :return: True 滑块验证成功  False 滑块验证失败 None 无滑块/滑块验证异常
        """
        # 获取域名
        domain = tb_helper.cutDomain(url=self.driver.current_url)

        # 获取接口拦截数据
        xhrResponse = self.get_response(domain=domain, isIframe=isIframe, is_get_url=is_get_url)
        if xhrResponse is None:
            logger.info('未捕捉到滑块xhrResponse  返回 True')
            return True
        xhrResponseDoc, ur, referer_url = xhrResponse
        if isIframe:
            domain = tb_helper.cutDomain(url=ur)
            # domain_s = tb_helper.cutDomain(url=ur)
            # domain_lis = domain_s.split('.')
            # domain = domain_lis[len(domain_s[0]):]

        if not ur or not xhrResponseDoc:
            logger.info('未捕捉到滑块xhrResponse  返回 True')
            return True
        # 获取sg_cookie数据
        sgcookie = self.driver.get_cookie(name='sgcookie')
        _, x5 = tb_helper.decodeX5secResponse(xhrResponseDoc=xhrResponseDoc, isFruitType=isFruitType,
                                              sgcookie=sgcookie, ur=ur)
        if _:
            # logger.success('滑块验证成功：{rpaName}')
            session_cookie = {
                'name': 'x5sec',  # Cookie的名字
                'value': x5,  # Cookie的值
                # 'domain': domain,  # 域名
                'path': '/',  # 路径
                'secure': True,  # 设置为True，表示只在HTTPS安全连接下传输
                # 'httpOnly': True,  # 设置为True，禁止通过JavaScript访问该Cookie
                'expiry': int((datetime.now() + timedelta(minutes=30)).timestamp()),  # 设置为0，表示会话Cookie
                'sameSite': "None"
            }

            if domain[0] == '.' or isIframe:
                session_cookie['domain'] = domain  # 添加全局domain  如：.taobao.com   不添加则只支持当前的页面域名
            # 带有iframe的需要进入到iframe后在添加cookie
            if isIframe:
                detail_iframe_ele = self.get_iframe_ele()
                # 切入到 iframe视图
                if detail_iframe_ele:
                    self.driver.switch_to.frame(detail_iframe_ele)
                    self.driver.add_cookie(cookie_dict=session_cookie)
                    self.driver.switch_to.default_content()
                else:
                    domain2 = domain.split('.')
                    session_cookie['domain'] = domain[len(domain2[0]):]  # 添加全局domain 如：.taobao.com 不添加则只支持当前的页面域名
                    self.driver.add_cookie(cookie_dict=session_cookie)
            # 无iframe 使用全局的domain
            else:
                self.driver.add_cookie(cookie_dict=session_cookie)
            if is_get_url and referer_url:
                self.wu.get_url_v2(referer_url, timeout=120)
            else:
                self.wu.get_refresh(timeout=120)
            return True
        else:
            logger.error('滑块验证失败')
        return False

    # 获取iframe元素
    def get_iframe_ele(self) -> None or WebElement:
        """
        获取iframe元素
        :return:
        """
        # 商详页的  xpath iframe  水果 和 普通滑块 都有可能出现
        detail_iframe = self.wu.wait_element_v2(By.XPATH, '//*[@class="J_MIDDLEWARE_FRAME_WIDGET"]//iframe', timeout=2,
                                                from_exists=True)
        detail_iframe_2 = self.wu.wait_element_v2(By.XPATH, '//iframe[@id="sufei-dialog-content"]', from_exists=True,
                                                  timeout=2)

        detail_iframe_3 = self.wu.wait_element_v2(By.XPATH, '//iframe[@id="baxia-dialog-content"]', from_exists=True,
                                                  timeout=2)

        # 商详页的  滑块 水果+普通 xpath iframe 元素
        if detail_iframe or detail_iframe_2 or detail_iframe_3:
            if detail_iframe:
                detail_iframe_ele = self.wu.get_element(By.XPATH, '//*[@class="J_MIDDLEWARE_FRAME_WIDGET"]//iframe',
                                                        timeout=3)
            elif detail_iframe_2:
                detail_iframe_ele = self.wu.get_element(By.XPATH, '//iframe[@id="sufei-dialog-content"]',
                                                        timeout=3)
            elif detail_iframe_3:
                detail_iframe_ele = self.wu.get_element(By.XPATH, '//iframe[@id="baxia-dialog-content"]', timeout=3)
            else:
                detail_iframe_ele = self.wu.get_element(By.XPATH, '//*[@class="J_MIDDLEWARE_FRAME_WIDGET"]//iframe',
                                                        timeout=3)

            return detail_iframe_ele
        return None

    # 获取滑块类型
    def get_track_type(self) -> Dict[str, bool] or None:
        """
        获取滑块类型
        """
        res = {"isFruitType": False, "isIframe": False}
        # 获取iframe元素
        detail_iframe_ele = self.get_iframe_ele()
        # 进入iframe滑块
        if detail_iframe_ele:
            # 进入到 detail_iframe
            self.driver.switch_to.frame(detail_iframe_ele)
            # 判断滑块类型  普通 or 水果
            isFruitType = self.track_is_fruit()
            self.driver.switch_to.default_content()
            if isFruitType is None:
                return None
            res['isIframe'] = True
            res['isFruitType'] = isFruitType
            return res
        # 全屏滑块
        else:
            # 全屏模式 不进入iframe 拿滑块类型
            isFruitType = self.track_is_fruit()
            if isFruitType is None:
                return None
            logger.success('遇到 全屏滑块 不需要进入到iframe')
            res['isIframe'] = False
            res['isFruitType'] = isFruitType
            return res

    # 判断 滑块是 水果  类型 还是 普通类型
    def track_is_fruit(self) -> bool:
        """
        判断滑块是 水果类型 还是 普通类型
        :return : True 水果滑块类型    False 普通滑块类型  None 未匹配到滑块
        """
        isFruitType = False
        # 拖动滑块  普通滑块
        is_ordinary = self.wu.wait_element_v2(By.ID, 'nc_1__scale_text', timeout=2, from_exists=True)
        # 水果滑块  水果滑块
        is_fruit = self.wu.wait_element_v2(By.XPATH, '//*[@id="nocaptcha"]//*[@class="scratch-captcha-container"]',
                                           timeout=2, from_exists=True)
        # 拖动滑块  普通滑块
        if is_ordinary:
            logger.info('淘宝遇到 普通滑块')
            return isFruitType
            # 全屏 水果滑块  水果滑块
        elif is_fruit:
            isFruitType = True
            logger.info('淘宝遇到 水果滑块')
            return isFruitType
        else:
            # logger.info('未遇到滑块~')
            return None
        # return None

    # 获取接口拦截数据
    def get_response(self, domain: str, isIframe: bool, is_get_url: bool = True) -> None or List[str]:
        """
        获取接口拦截数据
        :param domain:  域名   .taobao.com
        :param isIframe: 是否需要进入到iframe
        :param is_get_url: 是否需要根据referer 重新get一下url 确保滑块通过 全屏滑块refresh 通过不了 需要重新get 但是会丢失当前的筛选项
        :return: xhrResponse1  ur  referer_url
        """
        # 开启接口拦截
        self.driver.start_network_intercept([])
        self.wu.get_refresh(timeout=80)
        # 拦截滑块接口数据
        time.sleep(3)
        rep_lis = self.driver.stop_network_intercept([domain, 'punish'])
        xhrResponse1 = ''
        ur = ''
        referer_url = ''
        if len(rep_lis) <= 0:
            logger.info('未捕捉到滑块')
            return None
        for rep in rep_lis:
            if isIframe:
                if rep.response.status_code == 200 and 'punish' in rep.url:
                    try:
                        xhrResponse1 = gzip.decompress(rep.response.body).decode()
                    except:
                        xhrResponse1 = gzip.decompress(rep.response.body).decode('gbk', errors='ignore')
                    ur = rep.url
                    break
            else:
                if rep.response.status_code == 200 and 'html' in rep.response.headers.get_content_type():
                    try:
                        if is_get_url:
                            referer_url = rep.headers.get('Referer', '')
                        xhrResponse1 = gzip.decompress(rep.response.body).decode()
                    except:
                        xhrResponse1 = gzip.decompress(rep.response.body).decode('gbk', errors='ignore')
                    ur = rep.url
                    break
        return [xhrResponse1, ur, referer_url]
