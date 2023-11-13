from selenium_web import *
from unittest import TestCase

class TestsWeb(TestCase):

    driver = web_init(show=True)
    tb_tools = TbWebTool(driver=driver,user_email='v_cuitianliang@shihuo.cn')


    def tests_tb_login(self):
        self.tb_tools.tb_login()


    def text_tb_get_item_url(self):
        self.tb_tools.tb_login()
        item_url = 'https://uland.taobao.com/item/edetail?id=DN578RuZh5baAdAxWHRMWujtn-7QqmnqCw6NkyZort04'
        res_url = self.tb_tools.tb_get_url(item_url=item_url)
        print(res_url)






