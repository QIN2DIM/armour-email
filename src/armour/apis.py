# -*- coding: utf-8 -*-
# Time       : 2021/12/16 16:10
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:

from .core import EmailRelay, Chrome


def get_verification_code(
        link: str,
        chromedriver_path: str = None,
        driver: Chrome = None,
        silence: bool = True
) -> str:
    """
    监听来件并识别验证码，返回邮箱验证码。

    需要先调用 apis_get_email_context() 获得邮箱账号

    :param driver:
    :param chromedriver_path:
    :param silence:
    :param link: 邮箱指纹链接，被封装在 apis_get_email_context() 的返回值中
    :return:
    """
    chromedriver_path = "chromedriver" if chromedriver_path is None else chromedriver_path

    er = EmailRelay(
        url=link,
        chromedriver_path=chromedriver_path,
        silence=silence
    )
    api = er.set_spider_option() if driver is None else driver

    try:
        # 站点映射转移
        er.get_html_handle(api, er.register_url)

        # 监听新邮件
        er.check_receive(api)

        # 切换到邮件正文页面
        er.switch_to_mail(api)

        # 清洗出验证码
        verification_code = er.get_number(api)

        return verification_code
    finally:
        api.quit()


def get_email_context(
        chromedriver_path: str = None,
        silence: bool = True
) -> dict:
    """
    生产具备指纹特性的邮箱

    :param chromedriver_path:
    :param silence:
    :return: 返回 context 上下文对象，包含 `email` `id` `link` 键值对
    """
    chromedriver_path = "chromedriver" if chromedriver_path is None else chromedriver_path

    er = EmailRelay(
        chromedriver_path=chromedriver_path,
        silence=silence
    )
    api = er.set_spider_option()

    try:
        # 站点映射转移
        er.get_html_handle(api, er.register_url)

        # 获取随机指纹邮箱
        er.get_temp_email(api)

        # 使用 context 封装上下文运行环境
        context = {
            "email": er.email_driver,
            "id": er.email_id,
            "link": er.mailbox_link.format(er.email_id),
        }

        return context
    finally:
        api.quit()
