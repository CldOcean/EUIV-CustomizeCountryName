# -*- coding: utf-8 -*-
r"""把 `docs/用户手册.md` 转成一份能直接双击打开的 HTML。

    .buildenv\Scripts\python.exe md2html.py             # 图片走相对路径
    .buildenv\Scripts\python.exe md2html.py --embed     # 图片内嵌成 base64，单文件可发

为什么自己写而不用现成的 markdown 库：手册只用到很小一个子集
（标题 / 列表 / 表格 / 图片 / 行内代码），装个依赖再配模板反而更重，
而且这里要的是**单文件、零 CDN、离线能开**，顺便按 EU4 的配色自己排。

产出 `docs/用户手册.html`。HTML 跟 md 同目录，所以 `shots/*.png`
和 `../README.md` 这类相对链接不用改就能用。

⚠️ 内嵌模式（`--embed`）把十张图塞进 base64，文件会长到 2 MB 上下；
   默认模式只有 20 KB，但**换机器时必须连 shots/ 一起带走**。
"""

import base64
import html
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, 'docs')

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# 行内：先保护 `code`，再处理 **粗体** / [x](y) / ![alt](img)
INLINE_CODE = re.compile(r'`([^`]+)`')
BOLD = re.compile(r'\*\*([^*]+)\*\*')
LINK = re.compile(r'!?\[([^\]]*)\]\(([^)]+)\)')

ITEM = re.compile(r'^[-*]\s+')          # 列表项
ORD = re.compile(r'^\d+\.\s+')          # 有序列表项
CONT = re.compile(r'^\s+\S')            # 缩进的续行（且不是空行）


def slug(text, used):
    s = re.sub(r'[^\w\u4e00-\u9fff]+', '-', text).strip('-').lower()
    if not s:
        s = 'sec'
    base, i = s, 2
    while s in used:
        s = '%s-%d' % (base, i)
        i += 1
    used.add(s)
    return s


def inline(text):
    """行内标记 → HTML。图片单独留在块级处理，这里只管文字。"""
    spans = []

    def stash(s):
        spans.append(s)
        return '\x00%d\x00' % (len(spans) - 1)

    # 1) 行内代码：内容里的 * [ ] 都不该再被当标记，所以先抠出来
    text = INLINE_CODE.sub(lambda m: stash('<code>%s</code>'
                                           % html.escape(m.group(1))), text)
    # 2) 链接（非图片）
    def link(m):
        if m.group(0).startswith('!'):
            return m.group(0)                     # 图片留给块级
        return stash('<a href="%s">%s</a>' % (html.escape(m.group(2)),
                                              html.escape(m.group(1))))
    text = LINK.sub(link, text)
    # 3) 粗体
    text = BOLD.sub(lambda m: stash('<strong>%s</strong>'
                                    % html.escape(m.group(1))), text)

    text = html.escape(text)
    # 🩸 必须**倒着**回填：粗体里可以套行内代码（`**删掉 `hz_*` 文件**`），
    # 这时先抠出来的 code 占位符是**嵌在后来那个 strong 占位符里**的。
    # 正序回填的话，outer 文本此刻只有 \x001\x00，\x000\x00 压根不存在，
    # 于是它留在 span 内部原封不动地写进 HTML —— 文件里混进 NUL 字节，
    # grep 都把它当二进制。倒序先把外层填回去，内层才有机会被替换。
    for i in range(len(spans) - 1, -1, -1):
        text = text.replace('\x00%d\x00' % i, spans[i])
    return text


def img_src(path, embed, base):
    if not embed:
        return html.escape(path.replace('\\', '/'))
    f = os.path.normpath(os.path.join(base, path))
    if not os.path.isfile(f):
        return html.escape(path.replace('\\', '/'))
    with open(f, 'rb') as fh:
        raw = fh.read()
    ext = os.path.splitext(f)[1].lstrip('.').lower() or 'png'
    return 'data:image/%s;base64,%s' % (ext, base64.b64encode(raw).decode())


def blocks(lines, embed, base):
    """把 md 行流切成块，返回 (html片段列表, 目录条目列表)。"""
    out, toc, used = [], [], set()
    i, n = 0, len(lines)

    def para_image(text):
        """整段只有一张图 → 当 figure 处理（带图注，比裸 <img> 好认）。"""
        m = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', text.strip())
        if not m:
            return None
        alt, path = m.group(1), m.group(2)
        src = img_src(path, embed, base)
        cap = ('<figcaption>图：%s</figcaption>' % html.escape(alt)) if alt else ''
        return ('<figure><a href="%s" target="_blank" rel="noreferrer">'
                '<img src="%s" alt="%s"></a>%s</figure>'
                % (src, src, html.escape(alt), cap))

    while i < n:
        line = lines[i]

        # 代码块
        if line.startswith('```'):
            i += 1
            buf = []
            while i < n and not lines[i].startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append('<pre><code>%s</code></pre>' % html.escape('\n'.join(buf)))
            continue

        # 标题
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            lv = len(m.group(1))
            txt = m.group(2).strip()
            sid = slug(re.sub(r'[*`\[\]]', '', txt), used)
            out.append('<h%d id="%s">%s</h%d>' % (lv, sid, inline(txt), lv))
            if lv in (2, 3):
                toc.append((lv, sid, re.sub(r'[*`\[\]]', '', txt)))
            i += 1
            continue

        # 分隔线
        if re.fullmatch(r'-{3,}', line.strip()):
            out.append('<hr>')
            i += 1
            continue

        # 表格：当前行 | ...，下一行是 |---|
        if line.startswith('|') and i + 1 < n and re.match(r'^\|[\s:|-]+\|$',
                                                           lines[i + 1]):
            def cells(row):
                return [c.strip() for c in row.strip().strip('|').split('|')]
            head = cells(line)
            i += 2
            body = []
            while i < n and lines[i].startswith('|'):
                body.append(cells(lines[i]))
                i += 1
            th = ''.join('<th>%s</th>' % inline(c) for c in head)
            tb = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c)
                                                 for c in row) for row in body)
            out.append('<table><thead><tr>%s</tr></thead><tbody>%s</tbody>'
                       '</table>' % (th, tb))
            continue

        # 列表（缩进的续行并入上一个 li —— 手册里的列表项常常折成两行）
        # 🩸 外层进了这个分支，内层 while 就必须**至少能吃掉当前这一行**，
        # 否则 i 一步不动、`continue` 回到循环头又是同一行 —— 死循环。
        # 踩过：while 条件里只写了 ITEM（`- `），忘了 ORD（`1. `），
        # 于是「1. …」既吃不掉也跳不过，脚本直接挂住不报错。
        if ITEM.match(line) or ORD.match(line):
            ordered = bool(ORD.match(line))
            items = []
            while i < n:
                cur = lines[i]
                if ITEM.match(cur) or ORD.match(cur):
                    items.append(re.sub(r'^(?:[-*]|\d+\.)\s+', '', cur))
                elif CONT.match(cur) and items:      # 续行，且确实有上一项
                    items[-1] += ' ' + cur.strip()
                else:
                    break
                i += 1
            tag = 'ol' if ordered else 'ul'
            out.append('<%s>%s</%s>' % (tag, ''.join('<li>%s</li>' % inline(t)
                                                     for t in items), tag))
            continue

        # 空行
        if not line.strip():
            i += 1
            continue

        # 普通段落（吃到空行 / 下一个块开始）
        buf = [line]
        i += 1
        while i < n and lines[i].strip() and not _block_start(lines[i]):
            buf.append(lines[i])
            i += 1
        text = ' '.join(buf)
        fig = para_image(text)
        out.append(fig if fig else '<p>%s</p>' % inline(text))

    return out, toc


def _block_start(line):
    return bool(re.match(r'^(#{1,6}\s|\||-{3,}\s*$|```|[-*]\s|\d+\.\s)', line))


CSS = """
:root{
  --bg:#f7f9fb; --panel:#ffffff; --ink:#1d2733; --ink-dim:#5b6b7c;
  --line:#dfe6ee; --navy:#172a40; --blue:#2368a2; --blue-soft:#eaf2fb;
  --code-bg:#eef2f7; --warn:#8a4b00;
}
html[data-theme="dark"]{
  --bg:#131a22; --panel:#1b2430; --ink:#e3eaf2; --ink-dim:#9db0c4;
  --line:#2c3947; --navy:#0e1620; --blue:#5ea8e8; --blue-soft:#1e2c3c;
  --code-bg:#0f171f; --warn:#e2a758;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.75 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif;
  -webkit-font-smoothing:antialiased}
a{color:var(--blue)}
code{background:var(--code-bg);padding:.12em .38em;border-radius:4px;
  font:13.5px/1.6 Consolas,"Cascadia Mono",monospace}
pre{background:var(--code-bg);padding:12px 14px;border-radius:8px;overflow:auto}

/* 布局：宽屏左侧目录，窄屏目录挪到正文上方 */
.wrap{display:flex;gap:28px;max-width:1240px;margin:0 auto;padding:0 24px 80px}
#toc{position:sticky;top:0;align-self:flex-start;width:230px;flex:none;
  max-height:100vh;overflow:auto;padding:26px 0}
#toc .t{font-weight:700;color:var(--ink-dim);font-size:12px;letter-spacing:.12em;
  text-transform:uppercase;margin-bottom:10px}
#toc a{display:block;padding:5px 10px;border-radius:6px;color:var(--ink-dim);
  text-decoration:none;font-size:14px;border-left:2px solid transparent}
#toc a:hover{background:var(--blue-soft)}
#toc a.on{color:var(--blue);border-left-color:var(--blue);background:var(--blue-soft)}
#toc a.lv3{padding-left:22px;font-size:13.5px}
main{flex:1;min-width:0;padding-bottom:60px}
@media (max-width:980px){
  .wrap{display:block;max-width:840px}
  #toc{position:static;width:auto;max-height:none;padding:18px 0 0}
  #toc a{display:inline-block;margin:0 4px 4px 0;border:1px solid var(--line)}
}

h1{font-size:27px;line-height:1.35;margin:26px 0 14px;padding-bottom:14px;
  border-bottom:2px solid var(--line)}
h2{font-size:21px;margin:34px 0 12px;padding-left:11px;
  border-left:4px solid var(--blue)}
h3{font-size:17px;margin:24px 0 8px;color:var(--navy)}
h3[id]{scroll-margin-top:16px}
html[data-theme="dark"] h3{color:var(--blue)}
p{margin:11px 0}
ul,ol{padding-left:1.5em;margin:11px 0}
li{margin:5px 0}
hr{border:0;border-top:1px solid var(--line);margin:30px 0}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:15px}
th,td{border:1px solid var(--line);padding:8px 11px;text-align:left;vertical-align:top}
th{background:var(--blue-soft);color:var(--navy)}
html[data-theme="dark"] th{color:var(--blue)}
figure{margin:18px 0}
figure img{display:block;width:100%;border:1px solid var(--line);
  border-radius:9px;background:var(--panel)}
figcaption{margin-top:7px;font-size:13px;color:var(--ink-dim)}
blockquote{margin:14px 0;padding:2px 0 2px 14px;color:var(--ink-dim);
  border-left:3px solid var(--blue)}

/* 顶栏按钮 */
#bar{position:fixed;right:16px;top:14px;display:flex;gap:8px;z-index:9}
#bar button{background:var(--panel);color:var(--ink);border:1px solid var(--line);
  border-radius:8px;padding:6px 11px;font-size:13px;cursor:pointer;
  box-shadow:0 1px 4px rgba(0,0,0,.08)}
#bar button:hover{border-color:var(--blue);color:var(--blue)}

@media print{
  #bar,#toc{display:none}
  .wrap{display:block;max-width:none;padding:0}
  body{background:#fff}
  figure{page-break-inside:avoid}
  h2{page-break-after:avoid}
}
"""

JS = """
(function(){
  var doc=document.documentElement;
  var btn=document.getElementById('btnTheme');
  var saved='';
  try{saved=localStorage.getItem('hz-manual-theme')||''}catch(e){}
  function set(t){
    doc.setAttribute('data-theme',t);
    btn.textContent = t==='dark' ? '☀ 浅色' : '◐ 深色';
    try{localStorage.setItem('hz-manual-theme',t)}catch(e){}
  }
  set(saved==='dark'?'dark':'light');
  btn.onclick=function(){ set(doc.getAttribute('data-theme')==='dark'?'light':'dark'); };
  document.getElementById('btnTop').onclick=function(){
    window.scrollTo({top:0,behavior:'smooth'});
  };
  // 目录高亮：滚到哪一节就把对应链接点亮
  var links=[].slice.call(document.querySelectorAll('#toc a'));
  var heads=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1))});
  function mark(){
    var y=window.scrollY+120,best=0;
    heads.forEach(function(h,i){ if(h && h.offsetTop<=y) best=i; });
    links.forEach(function(a,i){ a.classList.toggle('on', i===best); });
  }
  window.addEventListener('scroll',mark,{passive:true});
  window.addEventListener('resize',mark);
  mark();
})();
"""


def build(md_path, out_path, embed=False):
    with io.open(md_path, encoding='utf-8') as f:
        lines = f.read().splitlines()

    parts, toc = blocks(lines, embed, os.path.dirname(os.path.abspath(md_path)))

    nav = []
    for lv, sid, txt in toc:
        nav.append('<a class="lv%d" href="#%s">%s</a>' % (lv, sid, html.escape(txt)))

    h1 = ''
    if parts and parts[0].startswith('<h1'):
        h1 = parts.pop(0)

    page = u'''<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>组词自定义国名工具 · 用户手册</title>
<style>%s</style>
</head>
<body>
<div id="bar">
  <button id="btnTheme" type="button">◐ 深色</button>
  <button id="btnTop" type="button">↑ 顶部</button>
</div>
<div class="wrap">
  <nav id="toc"><div class="t">目录</div>%s</nav>
  <main>
    %s
    %s
  </main>
</div>
<script>%s</script>
</body>
</html>
''' % (CSS, '\n    '.join(nav), h1, '\n    '.join(parts), JS)

    with io.open(out_path, 'w', encoding='utf-8') as f:
        f.write(page)
    return out_path


def main():
    embed = '--embed' in sys.argv
    src = os.path.join(DOCS, '用户手册.md')
    dst = os.path.join(DOCS, '用户手册.html')
    if not os.path.isfile(src):
        print('找不到 %s' % src)
        return 1
    build(src, dst, embed)
    size = os.path.getsize(dst)
    print('已生成 %s（%.0f KB%s）'
          % (dst, size / 1024.0, '，图片已内嵌' if embed else '，图片用相对路径'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
