import random
import time

from loguru import logger
from net import httpclient as cli


def get_item_int_id(item_str_id: str) -> None or str:
    """
    根据淘宝联盟的字符串id  转换成 数字id  一次1分钱
    :param item_str_id:  字符串id 如：Do95jysZh5baAddOVuRMwijtn-oM9VK9SBWKw7y0zI4X
    :return: 转链后的url 如： https://item.taobao.com/item.htm?id=698939760184   /  None
    """
    url = 'https://tkapi.apptimes.cn/tbk/get-numid'
    params = {
        'appkey': 'qfdf8q5k',
        'string_id': item_str_id
    }
    headers = {'User-Agent': ''}
    time.sleep(random.uniform(1,3))
    res = cli.get(url=url, payload=params, headers=headers, shihuo_cookie=False, enable_status_check=False,
                  retain_user_agent=True, retry=1, shihuo_key='errcode', shihuo_status=0)
    if not res:
        logger.error(f'id=[{item_str_id}]get_item_int_id error')
        return None
    item_id = res.get('data', {}).get('item_id', '')
    if not item_id:
        logger.error(f'id=[{item_str_id}] get_item_int_id error2 :{res}')
        return None
    item_url = 'https://item.taobao.com/item.htm?id=' + item_id
    return item_url
