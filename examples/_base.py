# -*- coding: utf-8 -*-
# Time       : 2021/12/16 16:27
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 用于运行实例的调度框架
import random
import time
from string import printable

import requests
from requests.exceptions import (
    ConnectionError,
    SSLError,
    HTTPError,
    Timeout,
    ProxyError
)
from selenium.common.exceptions import (
    WebDriverException,
    ElementNotInteractableException,
    NoSuchElementException
)
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located,
    element_to_be_clickable
)
from selenium.webdriver.support.wait import WebDriverWait

from src.config import logger


class CatWalk:
    def __init__(
            self, register_url: str, silence: bool = False, anti_email: bool = False,
            usr_email: bool = None, chromedriver_path: str = None, action_name: str = None
    ):
        self.register_url = register_url
        self.silence = silence
        self.anti_email = anti_email
        self.usr_email = usr_email
        self.email_object_context = {}
        self.chromedriver_path = "chromedriver" if chromedriver_path is None else chromedriver_path
        self.action_name = "CatWalk" if action_name is None else action_name

        self.username, self.password, self.email = "", "", ""
        self.beat_dance = 0
        self.timeout_retry_time = 3

    def set_spider_option(self):
        options = ChromeOptions()

        # 静默启动
        if self.silence is True:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")

        try:
            return Chrome(options=options)
        except WebDriverException as e:
            if "chromedriver" in str(e):
                print(f">>> CHROMEDRIVER_PATH 路径下指定目录下缺少（对应浏览器版本的）chromedriver。")
                print(f">>> 默认情况下，您需要将（对应浏览器版本的）chromedriver 放置于 main.py 同级目录下。")
                print(f">>> 请参考 ./src/config.py 的相关注释配置CHROMEDRIVER_PATH，"
                      f"此外，您还可以访问本项目技术文档寻找答案：\n"
                      f"https://github.com/QIN2DIM/sspanel-email")
                print(f">>> 若以上方式无法帮助到您，请于本项目 issue 提交您的报错信息：\n"
                      f"https://github.com/QIN2DIM/armour-email/issues")
                exit()

    def check_heartbeat(self):
        url = self.register_url
        session = requests.session()
        try:
            response = session.get(url, timeout=5)
            if response.status_code > 400:
                logger.error(f"站点异常 - url={url} status_code={response.status_code} ")
                return False
            return True
        # 站点被动行为，流量无法过墙
        except ConnectionError:
            logger.error(f"流量阻断 - url={url}")
            return False
        # 站点主动行为，拒绝国内IP访问
        except (SSLError, HTTPError, ProxyError):
            logger.warning(f"代理异常 - url={url}")
            return False
        # 站点负载紊乱或主要服务器已瘫痪
        except Timeout:
            logger.error(f"响应超时 - url={url}")
            return False

    @staticmethod
    def get_html_handle(api: Chrome, url, wait_seconds: int = 15):
        api.set_page_load_timeout(time_to_wait=wait_seconds)
        api.get(url)

    def generate_account(self, email_class: str = "@qq.com"):
        # 账号信息
        username = "".join(
            [random.choice(printable[: printable.index("!")]) for _ in range(9)]
        )
        password = "".join(
            [random.choice(printable[: printable.index(" ")]) for _ in range(15)]
        )

        # 根据实例特性生成 faker email object
        # 若不要求验证邮箱，使用随机字节码，否则使用备用方案生成可接受验证码的邮箱对象
        if not self.anti_email:
            if not self.usr_email:
                email = username
            else:
                email = username + email_class
        else:
            self.utils_email(method="email")
            email = self.email_object_context.get("email")
        return username, password, email

    def utils_email(self, method="email"):
        if method == "email":
            from src.armour import get_email_context
            self.email_object_context = get_email_context(self.chromedriver_path, silence=True)
        elif method == "code":
            from src.armour import get_verification_code
            link = self.email_object_context.get("link", "")
            if link.startswith("https://"):
                driver = self.email_object_context.get("driver")
                email_code = get_verification_code(
                    link=link,
                    chromedriver_path=self.chromedriver_path,
                    driver=driver,
                    silence=True
                )
                self.email_object_context["code"] = email_code

    def sign_up(self, api: Chrome):
        self.username, self.password, self.email = self.generate_account()

        while True:
            # ======================================
            # 填充注册数据
            # ======================================
            time.sleep(0.5 + self.beat_dance)
            try:
                WebDriverWait(api, 20).until(
                    presence_of_element_located((By.ID, "name"))
                ).send_keys(self.username)

                email_ = api.find_element(By.ID, "email")
                passwd_ = api.find_element(By.ID, "passwd")
                repasswd_ = api.find_element(By.ID, "repasswd")
                email_.clear()
                email_.send_keys(self.email)
                passwd_.clear()
                passwd_.send_keys(self.password)
                repasswd_.clear()
                repasswd_.send_keys(self.password)
            except (ElementNotInteractableException, WebDriverException):
                time.sleep(0.5 + self.beat_dance)
                continue

            # ======================================
            # 依据实体抽象特征，选择相应的解决方案
            # ======================================
            if self.anti_email:
                # 发送邮箱验证码
                api.find_element(By.ID, "email_verify").click()
                # 确认发送邮箱验证码
                time.sleep(0.5 + self.beat_dance)
                WebDriverWait(api, 10).until(element_to_be_clickable((
                    By.XPATH, "//button[@class='swal2-confirm swal2-styled']"
                ))).click()
                # 监听并接受邮箱验证码
                self.utils_email(method="code")
                verification_code = self.email_object_context.get("code")
                # 填写邮箱验证码
                email_code = api.find_element(By.ID, "email_code")
                email_code.clear()
                email_code.send_keys(verification_code)
            # ======================================
            # 提交注册数据，完成注册任务
            # ======================================
            # 点击注册按键
            time.sleep(0.5)
            for _ in range(3):
                try:
                    api.find_element(By.ID, "register-confirm").click()
                except (ElementNotInteractableException, WebDriverException):
                    print(f"正在同步集群节拍 | "
                          f"action={self.action_name} "
                          f"hold={1.5 + self.beat_dance}s "
                          f"session_id={api.session_id} "
                          f"event=`register-pending`")
                    time.sleep(self.timeout_retry_time + self.beat_dance)
                    continue

            time.sleep(0.5)
            for _ in range(3):
                try:
                    api.find_element(By.XPATH, "//button[contains(@class,'confirm')]").click()
                    return True
                except NoSuchElementException:
                    time.sleep(self.timeout_retry_time + self.beat_dance)
                    continue
            else:
                api.refresh()
                self.sign_up(api)

    def go(self):
        """

        :return:
        """
        raise ImportError
