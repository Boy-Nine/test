from rpaweb.util import WebUtil
from loguru import logger


# 增加 刷新等待方法
class MyWebUtil(WebUtil):
    def get_refresh(self, timeout: int = 20) -> bool:
        """
        刷新当前页面，超时自动停止加载
        :params timeout  超时时间
        """
        try:
            self.driver.refresh()
            self.driver.set_page_load_timeout(timeout)
            return True
        except:
            logger.error('刷新当前网页加载超时异常')
            return False
