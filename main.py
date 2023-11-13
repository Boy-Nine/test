import json

import run
import argparse
import os
import platform
import sys
import time
from loguru import logger
from shihuorpa.metrics import ShiHuoRPA

parser = argparse.ArgumentParser(description='淘宝字符串id转链')

parser.add_argument('--debug', type=bool, default=False, help='测试模式')
parser.add_argument('--read_excel_path', type=str, default="", help='读取的excel文件')

args = parser.parse_args()
read_excel_path = args.read_excel_path

# project_type=1 selenium形式 接口只在本地跑
project_type = 1

# 根据电脑系统 选择不同的路径
sysName = platform.system()
modName = '淘宝id转链'
timeStr = time.strftime("%Y年%m月%d日%H点%M", time.localtime())
if sysName == 'Darwin':
    savePath = sys.path[0] + '/' + modName + timeStr + '.xlsx'
elif sysName == 'Windows':
    savePath = r'C:\Users\Public\Downloads\\' + modName + timeStr + ".xlsx"
else:
    savePath = r'/tmp/rpa/' + modName + timeStr + '.xlsx'

if args.debug is True:
    os.environ['RPAUSER'] = 'v_cuitianliang'
    read_excel_path = '/Users/admin/Downloads/双11品类日超级U选-识货-报名商品.xlsx'
    project_type = 1  # 0 api   1 selenium

if __name__ == '__main__':
    shiHuoRPA = ShiHuoRPA(apollo_namespace='finance.json')
    if shiHuoRPA.UserInfo() is None:
        raise Exception('用户登录异常')
    try:
        # 运行整体程序
        ee = run.run(read_excel_path=read_excel_path, save_excel_path=savePath, project_type=project_type)
        js = {
            'ok': 'true'
        }
        js = json.dumps(js)
        if not os.path.exists(savePath):
            savePath = ''
        shiHuoRPA.Report(details=js, msg=f'{modName}完成', filePath=savePath)
        logger.info('整体OK！已结束')
    except Exception as e:
        logger.exception(e)
        js = {
            'err': str(e)
        }
        js = json.dumps(js)
        if not os.path.exists(savePath):
            savePath = ''
        shiHuoRPA.Report(details=js, msg=f'{modName}数据错误:{e}', filePath=savePath)
