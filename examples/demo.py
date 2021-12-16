# -*- coding: utf-8 -*-
# Time       : 2021/12/16 16:29
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import time

from src.config import logger
from ._base import CatWalk


class Email2Walk(CatWalk):
    def __init__(self, register_url: str, silence: bool = False,
                 anti_email: bool = False):
        super(Email2Walk, self).__init__(register_url, silence=silence, anti_email=anti_email)

    def go(self):
        # 检测实例状态
        if not self.check_heartbeat():
            return

        # 获取任务设置
        api = self.set_spider_option()
        try:
            # 弹性访问
            self.get_html_handle(api, url=self.register_url)
            # 注册账号
            self.sign_up(api)
        finally:
            logger.success("实例运行完毕，3s后退出程序。")
            time.sleep(3)
            api.quit()


@logger.catch()
def demo_email2walk(atomic: dict, silence=False):
    logger.info("加载运行实例 - atomic={}".format(atomic))

    e2w = Email2Walk(
        register_url=atomic["register_url"],
        silence=silence,
        anti_email=atomic.get("anti_email")
    )

    e2w.go()
