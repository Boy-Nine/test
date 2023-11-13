import pandas as pd
from typing import *

import selenium_web
from api import *
from selenium_web import *


# 读取excel数据 转list【dict】
def my_read_excel(read_excel_path: str) -> List[Dict[object, object]]:
    """
    读取excel数据 转list【dict】
    :param read_excel_path:  读取的excel路径
    :return:  list【dict】
    """
    df_lis = pd.read_excel(read_excel_path).to_dict(orient='records')
    return df_lis


# 保存excel数据
def my_save_excel(data_lis: list, save_excel_path: str) -> bool:
    """
    保存excel数据
    :param data_lis:  list【dict】 需要保存的数据
    :param save_excel_path:  保存的excel路径
    :return: True 保存完成
    """
    df = pd.DataFrame(data_lis)
    # 将列"转链链接"移动到列"商品链接"的后面
    cols = df.columns.tolist()
    cols.remove("转链链接")
    cols.insert(cols.index("商品链接") + 1, "转链链接")  # 将"d"插入到"cc"的后面
    df = df[cols]

    df.to_excel(save_excel_path, index=False)
    return True


# 整体流程运行
def run(read_excel_path: str, save_excel_path: str, project_type: int = 1):
    """
    整体流程运行
    :param read_excel_path:  读取的excel路径
    :param save_excel_path:  保存的excel路径
    :param project_type:  项目类型 0 api接口(花钱)  1 selenium
    :return:
    """
    df_list = my_read_excel(read_excel_path=read_excel_path)
    tb_run = None
    if project_type == 1:
        # selenium形式
        driver = selenium_web.web_init(show=True)
        tb_run = selenium_web.TbWebTool(driver=driver, user_email='v_cuitianliang@shihuo.cn')
        tb_login_bool = tb_run.tb_login()
        if not tb_login_bool:
            logger.exception('登录失败 程序退出')
            raise Exception('登录失败 程序退出')

    len_count = len(df_list)
    for index, dic in enumerate(df_list):
        logger.info(f'当前运行：{index + 1}/{len_count}')
        item_int_url = ''
        dic['转链链接'] = item_int_url
        goods_url = dic.get('商品链接', '')
        if 'https://uland.taobao.com/item/edetail?id=' not in goods_url:
            logger.warning(f'链接不符合提取要求：{goods_url}')
            continue

        # 提取商品id
        item_str_id = goods_url.split('?id=')[-1]
        if project_type == 0:  # 0 是接口形式
            # 字符串id转 数字id  接口形式
            item_int_url = get_item_int_id(item_str_id=item_str_id)
        # selenium形式 提取转链后的链接
        elif project_type == 1:  # 1是selenium形式
            item_int_url = tb_run.tb_get_url(item_url=goods_url)
        else:  # 默认
            item_int_url = tb_run.tb_get_url(item_url=goods_url)

        if not item_int_url:
            logger.warning(f'获取商品id失败：{goods_url}')
            continue
        with ROITrace('商品id链接复制保存'):
            dic['转链链接'] = item_int_url
        logger.success(f'{goods_url} 获取成功：{item_int_url}')

    my_save_excel(data_lis=df_list, save_excel_path=save_excel_path)
    logger.success('全部获取完成-保存成功')
    return True


# if __name__ == '__main__':
#     read_path = '/Users/admin/Downloads/双11品类日超级U选-识货-报名商品.xlsx'
#     save_path = '淘宝id转链结果.xlsx'
#     run(read_excel_path=read_path, save_excel_path=save_path, project_type=1)
