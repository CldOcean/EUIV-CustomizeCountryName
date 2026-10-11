# -*- coding: utf-8 -*-
r"""
区域国名字库 —— 从 `区域-tag-国名对照表.md` 读取并整理。

那张表由另一个对话用 tools/build_region_tag_table.py 从游戏文件里抽出来，
是本模组**国名字库的唯一来源**：那边重跑一遍表，这边重跑一遍生成器即可同步。

本模块负责三件事：
  1. 解析 markdown 表格 -> 区域 -> [(tag, 中文国名), ...]
  2. 区域内**按中文拼音排序**（点完区域事件后选项按拼音排，方便找）
  3. 区域内去重（同一个区域里出现两个一样的国名就只留一个）

排序依赖 pypinyin：
    <python> -m pip install pypinyin
没装就退化成 Unicode 码点序（不是拼音序），并在 stderr 上警告。
"""

import os
import re
import sys

MD_NAME = '区域-tag-国名对照表.md'


def find_md():
    r"""定位 `区域-tag-国名对照表.md`。

    这份表**不保证跟加载它的那个 .py 放一起**，几种形态各在一个地方，
    所以别只按 __file__ 上溯固定层数，按候选表挨个试：
      · 工作区 CLI       tools/region_names.py       -> 上一级 = 工作区根
      · 工具目录里的副本  <工具目录>/region_names.py  -> 同级 or 上一级(=tools/) or 上两级(=工作区根)
      · 打包后的 exe     exe 旁边（想临时换字库就放这儿）
                        -> 再退到 PyInstaller 的 _MEIPASS（build_exe.py --add-data 打进去的）
    """
    here = os.path.dirname(os.path.abspath(__file__))
    up1 = os.path.dirname(here)
    up2 = os.path.dirname(up1)
    cands = []
    if getattr(sys, 'frozen', False):
        cands.append(os.path.join(
            os.path.dirname(os.path.abspath(sys.executable)), MD_NAME))
    cands += [os.path.join(here, MD_NAME), os.path.join(up1, MD_NAME),
              os.path.join(up2, MD_NAME)]
    if getattr(sys, 'frozen', False):
        cands.append(os.path.join(getattr(sys, '_MEIPASS', ''), MD_NAME))
    for c in cands:
        if os.path.isfile(c):
            return c
    return cands[0]


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES_MD = find_md()

# 区域 id 与显示名，顺序 = 游戏里"选择区域"事件的弹出顺序。
# 显示名必须和 md 里的 `## xxx（N）` 小节标题一致。
REGION_IDS = [
    ('ZH',    '中华区域'),
    ('EA',    '东亚区域'),
    ('TAT',   '鞑靼大区'),
    ('WEU',   '西欧区域'),
    ('CEU',   '中欧区域'),
    ('EEU',   '东欧区域'),
    ('MEAST', '中东区域'),
    ('NAFR',  '北非区域'),
    ('SAFR',  '南非区域'),
    ('IND',   '印度大区'),
    ('EIND',  '东印度大区'),
    ('OCE',   '大洋洲大区'),
    ('NAME',  '北美大区'),
    ('SAME',  '中南美区域'),
]

# ------------------------------------------------------------------ 拼音

try:
    from pypinyin import lazy_pinyin, Style
    _HAS_PY = True
except ImportError:
    _HAS_PY = False
    sys.stderr.write('[warn] 未安装 pypinyin，国名改为 Unicode 码点排序（非拼音序）。'
                     '装一下：<python> -m pip install pypinyin\n')

# pypinyin 在译名多音字上会选错读法，这里按「整个国名」强制指定。
# 只列实测选错的：藏(cang→zang)、卡曾贝(ceng→zeng)、的黎波里(de→di)。
_PINYIN_FIX = {
    '藏': ('zang',),
    '卡曾贝': ('ka', 'zeng', 'bei'),
    '的黎波里': ('di', 'li', 'bo', 'li'),
}


def pinyin_key(text):
    """排序键：先按拼音，同音再按字形（码点）保证稳定"""
    if not _HAS_PY:
        return (text,)
    if text in _PINYIN_FIX:
        return (_PINYIN_FIX[text], text)
    return (tuple(lazy_pinyin(text, style=Style.NORMAL)), text)


# ------------------------------------------------------------------ 解析 md

_ROW = re.compile(r'^\|\s*`([A-Za-z0-9_]{2,4})`\s*\|\s*([^|]+?)\s*\|')


def parse_md(path=NAMES_MD):
    """-> {区域显示名: [(tag, 中文国名), ...]}，保持 md 里的原始顺序"""
    data = {}
    cur = None
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('## '):
                cur = line[3:].split('（')[0].strip()
                data.setdefault(cur, [])
                continue
            if cur is None:
                continue
            m = _ROW.match(line)
            if not m:
                continue
            tag, name = m.group(1), m.group(2)
            if not name or set(name) <= set('- '):
                continue
            data[cur].append((tag, name))
    return data


def build_regions(path=NAMES_MD, verbose=False):
    """-> [(区域id, 区域显示名, [国名...])]，区域内按拼音排序并去重"""
    raw = parse_md(path)
    out = []
    for rid, rname in REGION_IDS:
        rows = raw.get(rname)
        if rows is None:
            sys.stderr.write('[warn] md 里没有「%s」小节\n' % rname)
            rows = []
        rows = sorted(rows, key=lambda r: pinyin_key(r[1]))

        names, seen, dup = [], set(), []
        for tag, name in rows:
            if name in seen:
                dup.append('%s=%s' % (tag, name))
                continue
            seen.add(name)
            names.append(name)
        if dup and verbose:
            print('  %s 去重 %d 个：%s' % (rname, len(dup), ' '.join(dup)))
        out.append((rid, rname, names))
    return out


REGIONS = build_regions()

if __name__ == '__main__':
    tot = 0
    for rid, rname, names in REGIONS:
        tot += len(names)
        print('%-8s %-10s %3d 个   %s' % (rid, rname, len(names), '、'.join(names[:12])))
    print('\n合计 %d 个国名' % tot)
