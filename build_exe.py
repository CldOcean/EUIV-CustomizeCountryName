# -*- coding: utf-8 -*-
r"""把工具打包成一个 exe。

    .buildenv\Scripts\python.exe build_exe.py

产出（就在本目录，跟源码放一起 —— 打包后的路径基准是 exe 所在目录，
见 paths.py，所以 exe 必须待在这儿才找得到 工程文件/ 和 settings.json）：

    组词自定义国名工具.exe

只有一套界面（网页原生窗口），所以只打一个。tkinter 那套已经不维护了，
这里也不再额外引 tkinter。

打包环境是 .buildenv（基于系统 Python 3.14，--system-site-packages，
所以 pypinyin 直接沿用系统装的）。
"""

import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(HERE, '.buildenv', 'Scripts', 'python.exe')
BUILD = os.path.join(HERE, '_build')
ICON = os.path.join(BUILD, 'app.ico')

EXE_NAME = '组词自定义国名工具'

# 入口脚本：exe 双击就直接开原生窗口。
#
# 另外做两件窗口模式下很关键的事：
# 1) --windowed 下 sys.stdout / sys.stderr 是 **None**，子线程里随便 print
#    一下就是 AttributeError，而那种异常 main() 的 try 根本接不到，
#    只会弹一个「Unhandled exception in script」的框，什么都看不见。
#    所以把这两个流接到 error.log 上。
# 2) 挂全局 / 线程异常钩子，真出事也往 error.log 落一份。
ENTRY = """# -*- coding: utf-8 -*-
import os
import sys
import traceback

_HERE = %r
_LOG = os.path.join(_HERE, 'error.log')
sys.path.insert(0, _HERE)

# 替身 stdout/stderr：第一次真写入时才建 error.log。
# 直接 open 的话每次启动都会留下一个空 error.log，看着像出过事其实没有。
# （注意：ENTRY 本身是个三引号字符串，里面再出现连续三个双引号
#   会把外面的字符串提前截断 —— 所以这里一律用 # 注释，别写文档字符串。）
class _LazyLog(object):

    def __init__(self, path):
        self._path = path
        self._f = None
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.closed = False

    def _fp(self):
        if self._f is None:
            self._f = open(self._path, 'a', encoding='utf-8', buffering=1)
        return self._f

    def write(self, s):
        try:
            self._fp().write(s)
        except Exception:
            pass

    def flush(self):
        try:
            if self._f is not None:
                self._f.flush()
        except Exception:
            pass


try:
    if sys.stdout is None:
        sys.stdout = _LazyLog(_LOG)
    if sys.stderr is None:
        sys.stderr = _LazyLog(_LOG)
except Exception:
    pass


def _dump(tag, etype, value, tb):
    try:
        with open(_LOG, 'a', encoding='utf-8') as f:
            f.write('\\n=== %%s ===\\n' %% tag)
            traceback.print_exception(etype, value, tb, file=f)
    except Exception:
        pass


def _hook(etype, value, tb):
    _dump('excepthook', etype, value, tb)


sys.excepthook = _hook
try:
    import threading

    def _thook(args):
        _dump('thread ' + str(getattr(args.thread, 'name', '?')),
              type(args.exc_value), args.exc_value, args.exc_traceback)

    threading.excepthook = _thook
except Exception:
    pass

import main
# 注意是 main.main —— main 是**模块**名，模块里那个入口函数也叫 main。
# 直接写 main([...]) 是拿模块当函数调用，TypeError: 'module' object is not callable。
raise SystemExit(main.main([]))
"""


def make_icon():
    """画个图标：深海军蓝圆角方块 + 白字「名」。没 Pillow 就跳过。"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as ex:
        print('  [--] 没装 Pillow，跳过图标：%s' % ex)
        return None

    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 圆角方块：EU4 那套深海军蓝
    d.rounded_rectangle([8, 8, size - 8, size - 8], radius=52,
                        fill=(23, 42, 64, 255))
    d.rounded_rectangle([8, 8, size - 8, size - 8], radius=52,
                        outline=(35, 104, 162, 255), width=6)

    font = None
    for path in (r'C:\Windows\Fonts\msyhbd.ttc',
                 r'C:\Windows\Fonts\msyh.ttc',
                 r'C:\Windows\Fonts\simhei.ttf'):
        if os.path.isfile(path):
            try:
                font = ImageFont.truetype(path, 150)
                break
            except Exception:
                continue
    if font is None:
        return None

    text = '名'
    box = d.textbbox((0, 0), text, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(((size - w) / 2 - box[0], (size - h) / 2 - box[1] - 6),
           text, font=font, fill=(234, 241, 248, 255))

    img.save(ICON, format='ICO',
             sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (256, 256)])
    return ICON


def build(icon, name=EXE_NAME):
    entry = os.path.join(BUILD, 'entry.py')
    with open(entry, 'w', encoding='utf-8') as f:
        f.write(ENTRY % (HERE,))

    cmd = [PY, '-m', 'PyInstaller',
           '--noconfirm', '--clean', '--onefile', '--windowed',
           '--name', name,
           '--distpath', HERE,
           '--workpath', os.path.join(BUILD, 'work'),
           '--specpath', BUILD,
           '--paths', HERE,
           # pywebview 自带的 JS / pythonnet 的 runtime DLL 都是数据文件，
           # 不 collect 的话打进去也跑不起来
           '--collect-all', 'webview',
           '--collect-all', 'pythonnet',
           '--collect-all', 'clr_loader',
           '--collect-all', 'pypinyin',
           # 前端三件套
           '--add-data', os.path.join(HERE, 'web', 'static') + os.pathsep
           + os.path.join('web', 'static'),
           ]
    if icon and os.path.isfile(icon):
        cmd += ['--icon', icon]
    cmd.append(entry)

    print('\n=== %s ===' % name)
    t0 = time.time()
    r = subprocess.run(cmd, cwd=HERE)
    if r.returncode != 0:
        return False
    exe = os.path.join(HERE, name + '.exe')
    if os.path.isfile(exe):
        print('  产出 %s（%.1f MB / %.0f 秒）'
              % (os.path.basename(exe), os.path.getsize(exe) / 1048576.0,
                 time.time() - t0))
    return True


def main():
    if not os.path.isfile(PY):
        raise SystemExit('找不到打包环境：%s\n先跑：'
                         '<系统python> -m venv .buildenv --system-site-packages '
                         '&& .buildenv\\Scripts\\python.exe -m pip install '
                         'pywebview pyinstaller pillow' % PY)

    os.makedirs(BUILD, exist_ok=True)
    print('图标…')
    icon = make_icon()
    if icon:
        print('  ' + icon)

    ok = build(icon)
    bad = [] if ok else [EXE_NAME]

    # 中间产物留着没用，占几百 MB
    for d in (os.path.join(BUILD, 'work'),):
        shutil.rmtree(d, ignore_errors=True)

    print('\n' + ('全部完成' if not bad else '失败'))
    print('exe 就放在本目录：')
    print('  ' + EXE_NAME + '.exe')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
