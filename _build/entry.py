# -*- coding: utf-8 -*-
import os
import sys
import traceback

_HERE = 'F:\\WorkPlace\\.ProjectsDateless\\自定义国名\\tools\\组词自定义国名工具 - github'
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
            f.write('\n=== %s ===\n' % tag)
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
