# -*- coding: utf-8 -*-
r"""给《用户手册》截真图 —— 开一个真的原生窗口，按脚本摆姿势逐张存盘。

    .buildenv\Scripts\python.exe shots.py

产出 `docs/shots/*.png`，手册里引用的就是这几张。

为什么不用手画的示意图：按钮位置、选中色、真实数据画不准也容易过期；
真截图只要重跑一次就跟得上改动。

**规矩**：每截一张之前都验一遍「该关的弹窗确实关了」。第一版脚本漏了这步，
点完「添加前缀」没关弹窗，于是后面九张全糊着一层遮罩 —— 全是废图，
而且不打开看根本发现不了。

窗口尺寸固定成 PHOTO_SIZE 而不是用上次记住的大小（那是用户偏好，
而且会随 DPI 缩放，取景不可控）。
"""

import ctypes
import os
import sys
import time
from ctypes import wintypes

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from web import server as S          # noqa: E402
from web import window as W          # noqa: E402

OUT = os.path.join(HERE, 'docs', 'shots')

# 固定取景：1600x1000 是这台机器 150% 缩放下的物理像素，正好装下 14 行表格
PHOTO_SIZE = (1600, 1000)

try:
    from PIL import Image
except Exception:
    Image = None


# ------------------------------------------------------------------ 截图

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD), ('biWidth', ctypes.c_long),
        ('biHeight', ctypes.c_long), ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD), ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD), ('biXPelsPerMeter', ctypes.c_long),
        ('biYPelsPerMeter', ctypes.c_long), ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [('bmiHeader', BITMAPINFOHEADER),
                ('bmiColors', wintypes.DWORD * 3)]


def _raise(hwnd):
    """把窗口提到最前，并确保它没被最小化 / 没被别的窗口压住。

    🩸 **SetForegroundWindow 有可能是空操作**：Windows 对它加了一堆限制
    （前台窗口属于别的进程、我们不是「被用户刚点过」的那个进程……），
    失败时**静默返回、不报错**，然后 BitBlt 就老老实实把上面那个窗口截下来了
    —— 表现是「手册里混进一张终端截图」，而且每张都还挺像那么回事。

    所以这里用 SetWindowPos：HWND_TOP(-1) + 不激活 + 不移动尺寸
    （SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE）。它不甩那套前台规则，
    只说「在 Z 序里把你排到最上面」。
    """
    user32 = ctypes.windll.user32
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)                    # SW_RESTORE
    SWP_NOSIZE, SWP_NOMOVE, SWP_NOACTIVATE = 0x1, 0x2, 0x10
    user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0,
                        SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.7)                                   # 等它真的画到前台


def _window_size(hwnd):
    r = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r.right - r.left, r.bottom - r.top


def grab(hwnd):
    """抓窗口的**当前**画面（含 WebView2 里渲染的内容）。

    🩸 **不能用 PrintWindow**：对 WebView2 它只交付第一次合成的那一帧，
    后面所有 DOM 变化（点行、切页签、弹窗）都不会重绘进那个 DC ——
    表现是十张图里八张一模一样，且不报任何错。
    （PrintWindow 抓普通 WinForms 窗口是好的，所以我们一度以为这条路通了。
    对 WebView2 不行，实测。）

    改用**屏幕位图**：先抬到最前，再从屏幕 DC 把窗口矩形那块 copy 出来。

    ⚠️ 别在这里调 SetProcessDpiAwareness：进程一旦「感知缩放」，
    GetWindowRect 拿到的单位就跟 GDI 实际画的不一致，截出来整体缩放
    或者画面错乱。不调用时反而是对的（窗口多大就截多大）。
    """
    _raise(hwnd)

    user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
    w, h = _window_size(hwnd)
    if w <= 0 or h <= 0:
        raise RuntimeError('窗口尺寸不对：%dx%d' % (w, h))

    r = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    screen = user32.GetDC(0)
    mdc = gdi32.CreateCompatibleDC(screen)
    bmp = gdi32.CreateCompatibleBitmap(screen, w, h)
    gdi32.SelectObject(mdc, bmp)
    # SRCCOPY | CAPTUREBLT(0x40000000)：把分层窗口也算进去
    gdi32.BitBlt(mdc, 0, 0, w, h, screen, r.left, r.top, 0x00CC0020 | 0x40000000)

    bi = BITMAPINFO()
    bi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bi.bmiHeader.biWidth = w
    bi.bmiHeader.biHeight = -h            # 负数 = 自上而下存，省得再翻一遍
    bi.bmiHeader.biPlanes = 1
    bi.bmiHeader.biBitCount = 32
    bi.bmiHeader.biCompression = 0        # BI_RGB
    buf = ctypes.create_string_buffer(w * h * 4)
    got = gdi32.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bi), 0)
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mdc)
    user32.ReleaseDC(0, screen)
    if not got:
        raise RuntimeError('GetDIBits 失败')
    return Image.frombuffer('RGB', (w, h), buf, 'raw', 'BGRX', 0, 1).copy()


# ------------------------------------------------------------------ 脚本

LOG = []
BAD = []


def shot(win, name, note=''):
    img = grab(W.CURRENT.hwnd())
    img.save(os.path.join(OUT, name + '.png'))
    LOG.append('  %-14s %4dx%-4d %s' % (name + '.png', img.width, img.height,
                                        note))
    return img


def expect(win, name, cond, extra=''):
    """断言 + 记一笔。不能把「没验」当「没问题」。"""
    ok = bool(cond)
    LOG.append('     %s %s%s' % ('[OK]' if ok else '[!!]', name,
                                 ('  <- ' + str(extra)) if (not ok and extra)
                                 else ''))
    if not ok:
        BAD.append(name)


def run_shots(win):
    def js(code):
        return win.evaluate_js(code)

    def click(sel):
        return js('(function(){var e=document.querySelector(%s);'
                  'if(!e) return "缺少 "+%s; e.click(); return "ok";})()'
                  % (repr(sel), repr(sel)))

    def modal_closed():
        return js('document.querySelector("#modalRoot").hasAttribute("hidden")')

    def close_modal():
        js('(function(){var b=document.querySelector('
           '"#modalRoot [data-x=\\"cancel\\"]"); if(b) b.click();})()')
        time.sleep(0.45)

    def nav(view):
        click('.nav-item[data-view="%s"]' % view)
        time.sleep(0.8)

    time.sleep(1.2)        # on_ready 已经等了 2.5 秒，这里再稳一下

    expect(win, '窗口开了', W.CURRENT is not None and W.CURRENT.hwnd())
    expect(win, '起步没有弹窗挡着', modal_closed())

    # 截图前必须抬到最前，否则 BitBlt 会把压在上面的窗口原样截进来
    _raise(W.CURRENT.hwnd())

    # ---------------------------------------------------------- 1 国名页
    nav('names')
    shot(win, '01-main', '国名页：搜索 / 区域筛选 / 自动定位开关 / 工具栏')

    # ---------------------------------------------------------- 2 选中行
    # 注意：**这一版只认 Shift 连选**（相邻多点一次 Shift + 单击），
    # 没有 Ctrl 逐个加选 —— 别在教程里写 Ctrl。
    r1 = js('document.querySelectorAll("#bodyNames tr[data-i]")[3]'
            '.dispatchEvent(new MouseEvent("click", {bubbles: true}))')
    time.sleep(0.3)
    r2 = js('document.querySelectorAll("#bodyNames tr[data-i]")[7]'
            '.dispatchEvent(new MouseEvent("click", {bubbles: true, '
            'shiftKey: true}))')
    time.sleep(0.5)
    n = js('document.querySelectorAll("#bodyNames tr.is-sel").length')
    expect(win, 'Shift 连选到第 8 行 = 选中 5 行', n == 5, 'got %s (%s %s)'
           % (n, r1, r2))
    shot(win, '02-select', '选中：整行变色，页脚显示「已选 N 条」')

    # ---------------------------------------------------------- 3 双击编辑
    expect(win, '截图前弹窗是关着的', modal_closed())
    js('document.querySelectorAll("#bodyNames tr[data-i]")[10]'
       '.dispatchEvent(new MouseEvent("dblclick", {bubbles: true}))')
    time.sleep(0.7)
    head = js('(document.querySelector("#modalRoot .modal-head")||{}).textContent')
    expect(win, '双击弹出「编辑国名」', head == '编辑国名', head)
    shot(win, '03-edit', '双击任意一行 = 编辑这一条（光标已落在国名上并全选）')
    close_modal()
    expect(win, '取消后弹窗关掉了', modal_closed())

    # ---------------------------------------------------------- 4 添加国名
    click('section[data-view="names"] .view-head-actions [data-act="name-add"]')
    time.sleep(0.7)
    head = js('(document.querySelector("#modalRoot .modal-head")||{}).textContent')
    expect(win, '弹出「添加国名」', head == '添加国名', head)
    shot(win, '04-add', '添加国名：区域已记住上次的选择，光标直接落在国名框')
    close_modal()
    expect(win, '取消后弹窗关掉了', modal_closed())

    # ---------------------------------------------------------- 5 自动定位
    js('window.__hz.focusNameBySeq(window.__hz.S.st.project.names[8].seq)')
    time.sleep(0.4)
    n = js('document.querySelectorAll("#bodyNames tr.is-flash").length')
    expect(win, '自动定位后恰好一行高亮', n == 1, n)
    shot(win, '05-follow', '自动定位：新加的那行被选中并蓝闪 1.8 秒')

    # ---------------------------------------------------------- 6~9 其余页签
    # 每个页签都先确认没有弹窗 —— 上一版就是在这儿栽的
    for view, name, note in (
            ('prefix', '06-prefix', '前缀：顺序 = 游戏里出现的顺序，右侧有示例'),
            ('suffix', '07-suffix', '后缀：跟前缀共用一套模板'),
            ('regions', '08-regions', '区域：顺序 = 游戏里「选择区域」的弹出顺序'),
            ('build', '09-build', '生成：输出目录 / 模组名 / 每页选项数 / 规模预览')):
        expect(win, '切到 %s 前无弹窗' % view, modal_closed())
        nav(view)
        shot(win, name, note)

    # ---------------------------------------------------------- 10 深色主题
    r = click('#btnTheme')                       # 返回 'ok' 或 '缺少 #xxx'
    time.sleep(1.5)
    t = js('document.documentElement.dataset.theme')
    expect(win, '切到深色主题', t == 'dark', 'theme=%s click=%s' % (t, r))
    shot(win, '10-dark', '深色主题：连 Windows 标题栏一起变')
    click('#btnTheme')                           # 切回浅色
    time.sleep(1.2)
    expect(win, '切回浅色主题',
           js('document.documentElement.dataset.theme') == 'light')


def main():
    if Image is None:
        print('需要 Pillow 才能截图。用打包环境跑：'
              '.buildenv\\Scripts\\python.exe shots.py')
        return 1
    ok, why = W.available()
    if not ok:
        print('pywebview 不可用：%s' % why)
        return 1

    os.makedirs(OUT, exist_ok=True)

    # 手册的图用浅色更好印字；跑完把用户原来的主题还回去
    orig = S.load_settings()
    orig_theme = orig.get('theme', 'light')
    tmp = dict(orig, theme='light')
    S.save_settings(tmp)

    def ready(win):
        try:
            run_shots(win)
        except Exception:
            import traceback
            BAD.append('截图过程中抛异常')
            traceback.print_exc()
            LOG.append(traceback.format_exc())
        finally:
            try:
                S.QUIT_HOOK()
            except Exception:
                pass

    print('开窗口（%dx%d）…' % PHOTO_SIZE)
    try:
        # 先把服务起来，这样 on_ready 里再调 run() 是幂等的，
        # 不会出现「窗口指着一个还没起来的端口」
        S.start_server()
        W.run(size=PHOTO_SIZE, on_ready=ready)
    finally:
        s = S.load_settings()
        s['theme'] = orig_theme
        S.save_settings(s)

    print('\n'.join(LOG))
    print('\n%d 张图 → %s' % (len([x for x in os.listdir(OUT)
                                   if x.endswith('.png')]), OUT))
    if BAD:
        print('\n%d 项没通过：' % len(BAD))
        for b in BAD:
            print('  [!!] ' + b)
        return 1
    print('全部检查通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
