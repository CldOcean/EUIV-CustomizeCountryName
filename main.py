# -*- coding: utf-8 -*-
r"""组词自定义国名工具 —— 入口。

只有一套界面：网页引擎，开一个独立原生窗口（pywebview + Edge WebView2）。

    <python> main.py                  # 原生窗口（默认，推荐）
    <python> main.py --browser        # 退回系统默认浏览器（调试前端时方便 F12）

pywebview 或 WebView2 不可用时会自动降级到浏览器，不会白屏。
以前那个 tkinter「经典界面」已经不再维护了（app.py / theme.py / widgets.py
都没复制过来），所以也不再有「切换引擎」这件事。

平时直接双击 exe：
    组词自定义国名工具.exe

源码模式用系统 Python 3.14：
    C:\Users\CldOcean\AppData\Local\Programs\Python\Python314\python.exe
（托管版 Python 3.13 编译时没带 tkinter —— 命令行脚本够用，界面请用 3.14）
依赖：pywebview（原生窗口）、pypinyin（排序）。
"""

import json
import os
import sys
import traceback

import paths

HERE = paths.APP_HOME
if HERE not in sys.path:
    sys.path.insert(0, HERE)

ERR_LOG = os.path.join(HERE, 'error.log')
SETTINGS_PATH = os.path.join(HERE, 'settings.json')


def _fatal(title, detail):
    """出事就往 error.log 里写一份。

    没有控制台也不会弹 tkinter 窗口了，所以这里是唯一的线索来源。
    打包版还会把 stdout/stderr 接到同一个文件（见 build_exe.py 的入口脚本）。
    """
    try:
        with open(ERR_LOG, 'w', encoding='utf-8') as f:
            f.write(detail)
    except Exception:
        pass
    sys.stderr.write(detail + '\n')
    return title


def _settings():
    try:
        with open(SETTINGS_PATH, encoding='utf-8') as f:
            d = json.load(f)
        if isinstance(d, dict):
            return d
    except Exception:
        pass
    return {}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    try:
        from web import server, window
    except ImportError as e:
        _fatal('缺少依赖', '导入失败：%s\n\n%s' % (e, traceback.format_exc()))
        return 1

    if '--browser' in argv:
        try:
            server.serve()
        except Exception:
            _fatal('服务异常退出', traceback.format_exc())
            return 1
        return 0

    try:
        window.launch()
    except Exception:
        _fatal('界面异常退出', traceback.format_exc())
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
