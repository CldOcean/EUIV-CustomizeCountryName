# -*- coding: utf-8 -*-
"""临时脚本：把 exe 里的静态资源解出来，跟源码逐字节比对。

exe 是无图形的 onefile，直接双击起来再 curl 不可靠（端口被别的实例占、
进程又被 shells 回收），所以从 PyInstaller 归档里取更稳。
"""
import io
import os
import sys

from PyInstaller.archive.readers import CArchiveReader

HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, '组词自定义国名工具.exe')
OUT = os.path.join(HERE, '_build', 'extracted')

NAMES = [('web\\static\\app.js', 'app.js'),
         ('web\\static\\app.css', 'app.css'),
         ('web\\static\\index.html', 'index.html')]


def main():
    os.makedirs(OUT, exist_ok=True)
    r = CArchiveReader(EXE)
    for arc, local in NAMES:
        got = r.extract(arc)
        # 不同版本返回个数的 tuple：最后一个才是文件内容
        data = got[-1] if isinstance(got, tuple) else got
        if isinstance(data, str):
            data = data.encode('utf-8')
        p = os.path.join(OUT, local)
        with open(p, 'wb') as f:
            f.write(data)

        src = os.path.join(HERE, 'web', 'static', local)
        with open(src, 'rb') as f:
            want = f.read()
        same = (data == want)
        print('%-12s %6d B  与源码一致=%s' % (local, len(data), same))

        keys = {'app.js': ['btnFollow', 'focusNameBySeq', 'flashRow', '__hz',
                           'last_region', 'engine/switch'],
                'app.css': ['is-flash', 'btn-toggle', '@keyframes flash'],
                'index.html': ['btnFollow', 'btnEngine', '经典界面']}[local]
        txt = data.decode('utf-8', 'replace')
        for k in keys:
            print('   %-18s %d' % (k, txt.count(k)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
