# -*- coding: utf-8 -*-
r"""全局路径基准 —— 所有模块都从这里取，别再各算各的 __file__。

为什么要有这个文件：打包成 exe 之后 ``__file__`` 指向 PyInstaller 的
临时解压目录（``_MEIxxxxx``），**每次启动还不一样**。拿它当基准的话
``settings.json`` / ``工程文件/`` / ``生成的mod/`` 会跟着跑到临时目录里，
关掉程序就被清掉了 —— 表现是「每次开都像第一次开」。

所以：frozen 时用 **exe 所在目录**，没打包时用 ``__file__``。
exe 就放在 ``tools/自定义国名生成器/`` 里，跟源码目录是同一个位置，
于是 HERE / TOOLS / ROOT 三条推导跟源码模式完全一致。
"""

import os
import sys


def _home():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


APP_HOME = _home()                        # .../tools/自定义国名生成器
SELF = os.path.basename(APP_HOME)         # '自定义国名生成器'


def _find_tools():
    """往上找 tools/ 目录。

    正常情况下 tools 就是 APP_HOME 的上一级，一步到位。
    万一 exe 被人挪了窝，往上翻几层找「有个叫 tools 的父目录、
    且里面还有同名子目录」的位置兜一下；找不到就退回上一级。
    """
    p = APP_HOME
    for _ in range(5):
        up = os.path.dirname(p)
        if not up or up == p:
            break
        if os.path.basename(up) == 'tools' and os.path.isdir(os.path.join(up, SELF)):
            return up
        p = up
    return os.path.dirname(APP_HOME)


TOOLS = _find_tools()                     # .../tools
ROOT = os.path.dirname(TOOLS)             # 工作区根


def frozen():
    """现在是打包后的 exe 在跑吗？"""
    return bool(getattr(sys, 'frozen', False))
