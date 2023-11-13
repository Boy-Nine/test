from unittest import TestCase
from run import *


class TestRun(TestCase):

    def test_read_excel(self):
        excel_path = '/Users/admin/Downloads/双11品类日超级U选-识货-报名商品.xlsx'
        df_list = my_read_excel(read_excel_path=excel_path)
        print(df_list)


    def test_excel_save(self):
        excel_path = '/Users/admin/Downloads/双11品类日超级U选-识货-报名商品.xlsx'
        df_list = my_read_excel(read_excel_path=excel_path)[:10]
        for dic in df_list:
            dic['转链链接'] = 'xxxxxxxxx'

        my_save_excel(data_lis=df_list,save_excel_path='/Users/admin/Downloads/双11品类日超级U选-识货-报名商品-1.xlsx')