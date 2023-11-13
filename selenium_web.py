import random
from rpaweb.util import *

from weboptions import get_webdriver_options
from rpaweb.webbase import *
from my_web_util import MyWebUtil
from shihuorpa.metrics import sendMsg

from shopexpand.api import *
from shihuorpa.roi_trace import ROITrace
from tb_web_base import TbRiskTool


# web初始化
def web_init(show: bool = False) -> ShiHuoWebdriver:
    opts = get_webdriver_options(show=show)
    driver = NewShiHuoWebdriver(opts=opts)
    return driver


# 淘宝自动化网页工具
class TbWebTool:
    def __init__(self, driver: ShiHuoWebdriver, user_email: str = 'v_cuitianliang@shihuo,cn'):
        self.driver = driver
        self.wu = MyWebUtil(driver=self.driver)
        self.tb_wu = TbRiskTool(self.driver)
        self.user_email = user_email

    @staticmethod
    # 飞书发送消息
    def send_feishu(state, user_email='v_cuitianliang@shihuo.cn'):
        if state == 200:
            sendMsg(userId=user_email, msg='淘宝扫码登录-登陆成功~')
        elif state == 300:
            sendMsg(userId=user_email, msg='淘宝扫码没成功，请重新启动程序并登陆~')
        elif state == 400:
            sendMsg(userId=user_email, msg='淘宝扫码登陆~等待30秒~', imgPath='./login_screenshot.png')
        elif state == 0:
            sendMsg(userId=user_email, msg='淘宝已是登陆状态，无需登录~')
        return

    def tb_login(self) -> bool:
        """
        淘宝扫码登录
        :return:  True 登陆成功  False 登录失败
        """
        # 访问个人订单页面 判断是否已登录
        self.wu.get_url_v2(url='https://i.taobao.com/my_taobao.htm', timeout=150, new_tab=True)
        self.wu.load_storages(path='.', storage_names=['cookie', 'local_storage', 'session_storage'])
        self.wu.get_url_v2(url='https://i.taobao.com/my_taobao.htm', timeout=150)
        time.sleep(5)
        # self.tb_wu.tb_slider_drag()
        # 右上角二维码登录
        mini_qcode_xpath = '//*[@id="login"]//*[@class="iconfont icon-qrcode"]'
        # 二维码过期刷新
        refresh_xpath = '//*[@id="login"]//button[@class="refresh"]'
        # 点击 扫码登录
        mini_qcode_ele = self.wu.get_element(By.XPATH, mini_qcode_xpath, timeout=3)
        if not mini_qcode_ele:
            if 'login' not in self.driver.current_url:
                logger.info('无登录页，已登录成功')
                self.send_feishu(0, self.user_email)
                time.sleep(3)
                # 保存cookie
                self.wu.save_storages(path='.', storage_names=['cookie', 'local_storage', 'session_storage'])
                time.sleep(5)
                # TODO 登陆遇到验证码滑块
                if '验证码拦截' in self.driver.title:
                    logger.info('登陆遇到验证码滑块')
                    self.tb_wu.tb_slider_drag()
                return True

            btn_run = self.wu.wait_element_v2(By.XPATH, '//button[@class="fm-button fm-submit "]', timeout=10,
                                              from_exists=True)
            if btn_run:
                self.wu.get_element(By.XPATH, '//button[@class="fm-button fm-submit "]', timeout=2).click()
                logger.info('点击-快速进入 完成，已登录成功')
                self.send_feishu(0, self.user_email)
                time.sleep(3)
                # 保存cookie
                self.wu.save_storages(path='.', storage_names=['cookie', 'local_storage', 'session_storage'])
            logger.error('登录页元素未找到 异常退出')
            return False

        mini_qcode_ele.click()
        # 扫码登录逻辑
        for i in range(5):
            # 判断二维码是否过期
            refresh_ele = self.wu.get_element(By.XPATH, refresh_xpath, timeout=3)
            if refresh_ele:
                refresh_ele.click()
                time.sleep(3)

            self.driver.get_screenshot_as_file('./login_screenshot.png')
            self.send_feishu(state=400, user_email=self.user_email)
            t = 0
            while t < 30:
                t += 1
                if 'login' not in self.driver.current_url:
                    time.sleep(3)
                    logger.info('扫码登录成功')
                    self.send_feishu(200, self.user_email)
                    try:
                        WebDriverWait(self.driver, 120)  # 等待页面加载完成
                    except:
                        pass
                    # TODO 登陆遇到验证码滑块
                    if '验证码拦截' in self.driver.title:
                        logger.info('登陆遇到验证码滑块')
                        self.tb_wu.tb_slider_drag()
                    # 保存cookie
                    self.wu.save_storages(path='.', storage_names=['cookie', 'local_storage', 'session_storage'])
                    return True
                time.sleep(1)

        self.send_feishu(300, self.user_email)
        raise Exception('淘宝扫码没成功，请重新启动程序并登陆~')

    # 淘宝访问商品详情页 获取转链后的url
    def tb_get_url(self, item_url: str) -> None or str:
        with ROITrace(process_name='访问商品详情页'):
            self.wu.get_url_v2(url=item_url, timeout=150)
        tb_item_url = self.driver.current_url
        if 'item.taobao.com/item.htm?id=' in self.driver.current_url:
            time.sleep(random.uniform(15, 30))
            return tb_item_url
        tb_risk = self.tb_wu.tb_slider_drag()
        if not tb_risk:
            logger.error(f'滑块验证失败-->{item_url}')
            return None
        time.sleep(random.uniform(15, 30))
        tb_item_url = self.driver.current_url
        if 'item.taobao.com/item.htm?id=' in self.driver.current_url:
            return tb_item_url
        logger.error(f'当前转链异常：当前链接：{tb_item_url}')
        return None
