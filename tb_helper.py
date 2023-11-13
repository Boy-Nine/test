import re
import time
from loguru import logger
from typing import *
from net import httpclient as hlp
from seleniumwire.request import Request
from urllib.parse import urlparse


# 获取链接域名
def cutDomain(url: str) -> str:
    """
    获取链接域名
    :param url: 链接
    :return: 域名
    """
    res = urlparse(url)
    domain = res.netloc
    arr = domain.split(".")
    if len(arr[0]) < 2:
        return domain[len(arr[0]):]
    return domain


# 解析滑块数据 返回x5sec数据
def decodeX5secResponse(xhrResponseDoc: Request, isFruitType: bool, sgcookie: Dict[str, object], ur: str = ""
                        ) -> Tuple[bool, str]:
    """
    解析滑块数据 返回x5sec数据
    :param xhrResponseDoc: 滑块接口拦截数据  ->html页面源代码
    :param isFruitType: 是否是水果滑块 True 水果滑块  False 普通滑块
    :param sgcookie: sgcookie ->cookie
    :param ur: 当前页面链接 ->url
    :return: x5sec数据 ->Tuple[bool, str]     bool:True成功 or False失败    str: x5sec数据
    """
    respTmpBody = ''
    if not xhrResponseDoc:
        return False, ""
    if not sgcookie:
        logger.error(f'TB sgcookie is None :{sgcookie}')
        return False, ""

    sgcookie = sgcookie.get('value', '')
    if xhrResponseDoc is not None:
        if type(xhrResponseDoc) is str:
            respTmpBody = xhrResponseDoc
    pattern = r'SECDATA": "(.*?)"'
    res = re.search(pattern, respTmpBody, re.M | re.I)
    if res is None:
        return False, ""
    x5secDataStr = res.group(1)
    # xb7d00fa96d1a2479ec473cc00a68345251655274947a-213664603a-756711472aaazc2aj889120098a__bx__fito.tmall.hk%3A443%2Fsearch.htm
    uuidPattern = r'NCTOKENSTR": "(.*?)"'
    res = re.search(uuidPattern, respTmpBody, re.M | re.I)
    if res is None:
        return False, ""
    uuid = res.group(1)
    # "NCAPPKEY": "X82Y__01b039119eeb8cdaeea0efe4c183b847"
    res = re.search('NCAPPKEY": "(.*?)"', respTmpBody, re.M | re.I)
    if res is None:
        return False, ""
    key = res.group(1)
    fromUrlPattern = r'FORMACTIOIN": "(.*?)"'
    res = re.search(fromUrlPattern, respTmpBody, re.M | re.I)
    if res is None:
        return False, ""
    parsed_url = urlparse(ur)
    fromUrl = parsed_url.scheme + '://' + parsed_url.netloc + res.group(1)
    fromUrl = fromUrl.replace('verify/', '')
    # 获取x5sec数据
    x5sec = makex5sec(uuid, x5secDataStr, key, fromUrl, isFruitType, sgcookie)
    #  ; Max-Age
    if not x5sec:
        return False, ""
    x5sec = x5sec.replace('; Max-Age', '')
    return True, x5sec


# 爬虫接口获取x5sec数据
def makex5sec(uuid: str, x5secdata: str, key: str, fromUrl: str, isFruitType: bool, sgcookie: dict) -> None or str:
    """
    爬虫接口获取x5sec数据
    :param uuid: uuid
    :param x5secdata: x5secdata
    :param key: key
    :param fromUrl: fromUrl
    :param isFruitType: 是否是水果滑块 True 水果滑块  False 普通滑块
    :param sgcookie: sgcookie
    :return: x5sec数据   None-> 验证失败   str-> x5sec数据
    """
    if len(uuid) == 0 or len(x5secdata) == 0:
        return None
    sgcookie = 'sgcookie=' + sgcookie
    for retry in range(3):
        try:
            if retry > 0:
                logger.warning(f'淘宝风控爬虫接口 retry: {retry}')
            url = "http://gateway.jiazhi.online/v4/services/jiazhi-box/box/component/makex5sec"
            headers = {
                'token': 'MTUwMjE5NzY4NjY5ODg5NzQwOA==',
                'host': 'gateway.jiazhi.online',
                'User-Agent': 'shihuoRPA',
            }
            typ = 'app_rpa'
            if isFruitType is True:
                typ = 'fruit'
            payload = {
                'key': key,  # 'X82Y__57fdd2994bdc8cd94e04774785d7f71a',
                'url': fromUrl,
                'bxuuid': uuid,
                'x5secdata': x5secdata,
                'type': typ,
                'vendor': 'shihuo',
                'cookie': sgcookie,
            }
            logger.info(
                f'淘宝滑块数据->uuid:{uuid}  x5secdata:{x5secdata}   key:{key}  '
                f'  url:{fromUrl}    type:{type}    cookie:{sgcookie}')
            resp = hlp.get(url=url, headers=headers, payload=payload, shihuo_key='code', shihuo_status=0)
            if not resp:
                logger.error(f'淘宝风控接口调用失败: {resp}')
            logger.info(resp)
            if "data" in resp:
                if 'error' in resp['data']:
                    raise ValueError(resp["data"]['error'])
                if resp['data']['body'] is not None:
                    logger.success("淘宝风控处理成功")
                    return resp["data"]["body"]
            time.sleep(15)
        except Exception as err:
            logger.error(f'淘宝风控接口调用异常-{err}')
            time.sleep(2)
    return None




"""
1. 命名改变
2. tb_helper的方法迁移到 同一个文件
"""