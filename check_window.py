# -*- coding: utf-8 -*-
r"""原生窗口自检：真的开一个桌面窗口出来，看完再关掉。

    <python> check_window.py

HTTP 那层和前端逻辑由 check_web.py 管，这里只盯「容器」——
也就是「双击出来到底是不是个正经窗口」这件事：

- 窗口真的创建出来了（拿得到 HWND，且按标题也能找到同一个）
- 页面真的渲染了（在窗口里跑 JS 数表格行数）
- JS 桥在（window.pywebview.api.set_theme 存在 → 主题能同步到标题栏）
- 关窗之后本地服务真的退干净了

**pywebview 必须在主线程跑**，所以这个脚本自己就是主流程，
关窗靠后台线程调 QUIT_HOOK —— 不能反过来。
"""

import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from web import server as S          # noqa: E402
from web import window as W          # noqa: E402
import winapi                        # noqa: E402

OK, FAIL = [], []


def check(name, cond, extra=''):
    (OK if cond else FAIL).append(name)
    print('  %s %s%s' % ('[OK]' if cond else '[!!]', name,
                         ('  <- ' + str(extra)) if (extra and not cond) else ''))
    sys.stdout.flush()


def main():
    print('原生窗口自检')

    alive, why = W.available()
    if not alive:
        print('  [--] pywebview 不可用（%s），跳过' % why)
        return 0
    check('pywebview 可用', True)

    # 回归：_Owner.hwnd 曾经被 __init__ 里的 self.hwnd = 0 盖成整数，
    # 于是 self.hwnd() 直接 TypeError，标题栏线程和关窗线程一起死。
    o = W._Owner()
    check('hwnd() 没被同名属性盖掉', callable(o.hwnd) and o.hwnd() == 0)

    res = {}
    done = threading.Event()

    def probe():
        """等窗口出来 -> 查状态 -> 关掉。"""
        try:
            for _ in range(80):
                time.sleep(0.25)
                if W.CURRENT is not None and W.CURRENT.win is not None:
                    break
            if W.CURRENT is None:
                res['err'] = '窗口没建起来'
                return
            time.sleep(3)                      # 给页面加载的时间

            o = W.CURRENT
            res['hwnd'] = o.hwnd()
            # 拿全表而不是「第一个匹配」：上次自检 / 用户自己开的同标题窗口
            # 也可能还在，那样 find_window 会返回一个别人的句柄误判。
            res['titled'] = winapi.find_windows(W.TITLE)
            res['theme'] = o.theme
            res['titlebar'] = o.sync_titlebar()

            win = o.win
            # 端到端：在**真窗口里**跑 JS，确认页面不是白板
            try:
                res['rows'] = win.evaluate_js(
                    "document.querySelectorAll('#bodyNames tr').length")
            except Exception as ex:
                res['rows'] = 'evaluate_js 失败：%r' % ex
            try:
                res['bridge'] = win.evaluate_js(
                    "typeof (window.pywebview && window.pywebview.api "
                    "&& window.pywebview.api.set_theme)")
            except Exception as ex:
                res['bridge'] = 'evaluate_js 失败：%r' % ex
            try:
                res['title'] = win.evaluate_js('document.title')
            except Exception:
                res['title'] = None
            # 「自动定位」是真窗口里的东西：按钮得在，且按下态要和设置一致
            try:
                res['follow'] = win.evaluate_js(
                    "!!document.getElementById('btnFollow')")
            except Exception as ex:
                res['follow'] = 'evaluate_js 失败：%r' % ex
            try:
                res['follow_on'] = win.evaluate_js(
                    "document.getElementById('btnFollow')"
                    ".getAttribute('aria-pressed')")
            except Exception:
                res['follow_on'] = None

            S.QUIT_HOOK()                      # 关窗
        except Exception as ex:
            res['err'] = repr(ex)
        finally:
            done.set()

    def watchdog():
        if not done.wait(90):
            print('  [!!] 超时：窗口没在 90 秒内关掉')
            FAIL.append('窗口能正常关闭')
            os._exit(9)

    threading.Thread(target=probe, daemon=True).start()
    threading.Thread(target=watchdog, daemon=True).start()

    try:
        W.run()
    except Exception as ex:
        check('run() 不抛异常', False, repr(ex))
        return 1

    done.wait(30)
    if 'err' in res:
        check('窗口跑通', False, res['err'])
        return 1

    check('拿到原生窗口句柄', bool(res.get('hwnd')), res.get('hwnd'))
    check('按标题也能找到同一个窗口',
          bool(res.get('hwnd')) and res.get('hwnd') in (res.get('titled') or []),
          'native=%s 同标题窗口=%s' % (res.get('hwnd'), res.get('titled')))
    check('标题栏深色设置成功', res.get('titlebar') is True, res.get('titlebar'))
    check('窗口里渲染出国名表',
          isinstance(res.get('rows'), int) and res.get('rows') > 0,
          res.get('rows'))
    check('JS 桥可用（主题能同步到标题栏）',
          res.get('bridge') == 'function', res.get('bridge'))
    # 别跟着设置硬写 true/false —— 用户可能已经把开关按掉了，
    # 这里只验「按钮在」和「按钮显示的态 = 后端的态」。
    check('页面里有自动定位开关', res.get('follow') is True, res.get('follow'))
    want = 'true' if S.load_settings().get('follow', True) else 'false'
    check('开关状态跟设置一致', res.get('follow_on') == want,
          '页面=%r 设置=%s' % (res.get('follow_on'), want))
    check('关窗后本地服务已退出',
          S.SERVER is None and S.SERVER_THREAD is None,
          'SERVER=%s THREAD=%s' % (S.SERVER, S.SERVER_THREAD))
    check('关窗后 CURRENT 已清空', W.CURRENT is None)

    print('\n  （主题读到 %s，页面标题 %r）' % (res.get('theme'), res.get('title')))
    print('\n%d 项 OK, %d 项失败' % (len(OK), len(FAIL)))
    for f in FAIL:
        print('  [!!] ' + f)
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
