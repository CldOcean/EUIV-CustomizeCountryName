# -*- coding: utf-8 -*-
r"""把网页界面装进一个**原生窗口**（pywebview + Edge WebView2）。

目标是 missiontree 那种观感：双击出来就是个普通桌面窗口 —— 没有地址栏、
没有标签页，任务栏上是自己的条目，Alt-Tab 也是一个独立应用。

后端完全复用 web/server.py：界面照旧走 HTTP 取数据，
只是承载它的容器从「用户的默认浏览器」换成「内嵌的 WebView2 控件」。
所以浏览器模式（``main.py --browser``）原样留着当退路 ——
没装 pywebview、或机器上没有 WebView2 运行时时自动降级过去。
"""

import sys
import threading
import time

import paths                                             # noqa: F401  保持导入顺序
from web import server as S

TITLE = '自定义国名生成器'

# 跟 app.css 里的 --bg 对齐：窗口刚出来、页面还没画好时别闪一下白/黑
BG = {'light': '#f2f5f9', 'dark': '#0d131b'}

DEFAULT_SIZE = (1280, 840)
MIN_SIZE = (960, 640)

# 当前窗口（_Owner 实例）。自检靠它拿句柄断言「窗口真的出来了」，
# 也方便将来在调试时看一眼状态。
CURRENT = None


def available():
    """pywebview 能用吗？返回 (能/不能, 说明)。"""
    try:
        import webview                                   # noqa: F401
        return True, ''
    except Exception as ex:
        return False, '%s: %s' % (type(ex).__name__, ex)


# ------------------------------------------------------------------ JS 桥

class _Bridge(object):
    """给页面用的原生能力。JS 里是 ``window.pywebview.api.*``。

    方法名别用下划线开头 —— pywebview 只暴露公开方法。
    """

    def __init__(self, owner):
        self._owner = owner

    def set_theme(self, theme):
        """页面里切深浅主题时，让窗口底色和标题栏跟着变。"""
        try:
            self._owner.apply_theme(str(theme))
            return True
        except Exception:
            return False


# ------------------------------------------------------------------ 窗口

class _Owner(object):
    """持有窗口引用，管主题同步与句柄获取。"""

    def __init__(self):
        self.win = None
        # 注意：这个属性**不能**叫 self.hwnd —— 那会把下面同名的 hwnd()
        # 方法盖成整数，self.hwnd() 立刻 TypeError（第一轮在 widgets.Dialog
        # 上踩过一模一样的坑：self.body / self._ok 盖掉同名方法）。
        self._hwnd = 0
        self.theme = 'light'

    def apply_theme(self, theme):
        self.theme = 'dark' if str(theme) == 'dark' else 'light'
        if self.win is not None:
            try:
                self.win.set_background_color(BG[self.theme])
            except Exception:
                pass
        return self.sync_titlebar()

    def hwnd(self):
        """原生窗口句柄。native 是 WinForms 的 Form，Handle 就是 HWND。"""
        if self._hwnd:
            return self._hwnd
        w = self.win
        if w is None:
            return 0
        try:
            v = int(w.native.Handle.ToInt32())
            if v:
                self._hwnd = v
                return v
        except Exception:
            pass
        # 退路：按标题找（WinForms 的窗口类名是随机的，靠类名不可靠）
        try:
            import winapi
            v = winapi.find_window(TITLE)
            if v:
                self._hwnd = v
        except Exception:
            pass
        return self._hwnd

    def sync_titlebar(self):
        h = self.hwnd()
        if not h:
            return False
        try:
            import winapi
            return winapi.set_titlebar_dark(h, self.theme == 'dark')
        except Exception:
            return False


def _sync_later(owner, times=10, delay=0.35):
    """标题栏要等窗口 mapped 之后才设得进去，所以后台重试几次。

    坑在于设早了 DWM 会静默失败，
    表现就是「深色主题启动了，标题栏却还是白的」。
    """
    def go():
        for _ in range(times):
            if owner.sync_titlebar():
                return
            time.sleep(delay)
    threading.Thread(target=go, name='hz-titlebar', daemon=True).start()


# ------------------------------------------------------------------ 入口

def run(port=0, size=None, on_ready=None):
    """起服务 + 开原生窗口 + 阻塞到窗口关闭。返回 (port, url)。

    size      固定窗口尺寸 (w, h)，不给就用上次记住的 / 默认值。
              截图脚本要用：窗口尺寸决定取景，不能跟着用户上次拉的大小跑。
    on_ready  窗口和页面都就绪后调一次，参数是 webview 的窗口对象。
              做「截几张图就自己关掉」这类自动化时挂在这儿。

    🩸 自动化只能走**同进程**（on_ready 里调 win.evaluate_js）：
    跨进程驱动别人窗口里的 WebView2 走不通 —— 窗口句柄包不出对方的
    托管对象（两个 CLR 实例），pywebview 默认也不开 CDP 调试端口。
    还有，`evaluate_js` 不适合连调十几次：它把 JS 丢进桥里等结果，
    WebView2 一旦不响应就**永久阻塞且没法超时**（DEBUG 日志刷满、
    窗口看着还活着）。所以自动化脚本要一次交互一次 sleep，
    不并发、不重试。
    """
    global CURRENT
    import webview

    S.SESSION.boot()
    st = S.SESSION.settings
    port, url = S.start_server(port)

    owner = _Owner()
    owner.theme = 'dark' if st.get('theme') == 'dark' else 'light'

    if size:
        w, h = int(size[0]), int(size[1])
    else:
        geom = st.get('web_geometry') or {}
        try:
            w = int(geom.get('w') or 0) or DEFAULT_SIZE[0]
            h = int(geom.get('h') or 0) or DEFAULT_SIZE[1]
        except Exception:
            w, h = DEFAULT_SIZE

    win = webview.create_window(
        TITLE, url=url,
        width=max(w, MIN_SIZE[0]), height=max(h, MIN_SIZE[1]),
        min_size=MIN_SIZE,
        background_color=BG[owner.theme],
        js_api=_Bridge(owner),
        text_select=True,          # 表格里的字要能选中复制
        confirm_close=False,
    )
    owner.win = win
    CURRENT = owner

    def _on_closing():
        # 记住窗口大小，下次开还是这么大（调用方指定了 size 就不记，
        # 那是脚本要的固定取景，不该污染用户偏好）
        if not size:
            try:
                st['web_geometry'] = {'w': int(win.width), 'h': int(win.height)}
                S.save_settings(st)
            except Exception:
                pass
        return True

    try:
        win.events.closing += _on_closing
    except Exception:
        pass

    # 页面上点「退出」：先关窗，再关服务（顺序在 server.api_shutdown 里）
    S.QUIT_HOOK = lambda: win.destroy()

    _sync_later(owner)
    if on_ready is not None:
        def _fire():
            try:
                on_ready(win)
            except Exception:
                import traceback
                traceback.print_exc()
        win.events.loaded += lambda: threading.Thread(
            target=_fire, name='hz-on-ready', daemon=True).start()
    try:
        webview.start(private_mode=False)
    finally:
        S.QUIT_HOOK = None
        S.stop_server()
        CURRENT = None
    return port, url


def launch(port=0):
    """按可用性选容器：能开原生窗口就开，不行就退回浏览器。

    返回 ('window' | 'browser', port, url)。
    """
    ok, why = available()
    if ok:
        try:
            p, u = run(port=port)
            return 'window', p, u
        except Exception as ex:
            sys.stderr.write('原生窗口起不来，退回浏览器：%r\n' % (ex,))
            if why:
                sys.stderr.write('  (%s)\n' % why)
    else:
        sys.stderr.write('pywebview 不可用（%s），退回浏览器。\n' % why)
    p, u = S.serve(port=port, open_browser=True, quiet=False)
    return 'browser', p, u
