# -*- coding: utf-8 -*-
# Time       : 2021/12/16 16:28
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: SSPanel-Uim 邮箱验证案例

# ==============================================
# TODO [√]用于项目演示的运行实例，（也许）需要使用代理
# ==============================================
# - `anti_email` 表示需要邮箱验证
# - 无标记实例为对照组
ActionNiuBiCloud = {
    "register_url": "https://niubi.cyou/auth/register",
}

ActionFreeDogCloud = {
    "register_url": "https://www.freedog.pw/auth/register",
    "anti_email": True
}
ActionSavierCloud = {
    "register_url": "https://savier.xyz/auth/register",
    "anti_email": True
}
# ==============================================
# TODO [√]运行前请检查 chromedriver 配置
# ==============================================
from examples import demo_email2walk

if __name__ == '__main__':
    demo_email2walk(
        # 无验证对照组
        # atomic=ActionNiuBiCloud,

        # 邮箱验证实验组
        atomic=ActionSavierCloud,
    )
