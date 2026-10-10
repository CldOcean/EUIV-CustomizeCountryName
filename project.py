# -*- coding: utf-8 -*-
r"""工程文件模型 —— 专用格式 .hznproj

为什么自己定格式而不是直接改 gen_namebuilder.py 顶部的常量：
  工程要能保存「多个版本并存 + 随时切换 + 记住上次状态」，
  而 gen_namebuilder.py 是「一份配置 = 一份代码」的写法，存不下多份。

.hznproj 就是 UTF-8 的 JSON，缩进 2 空格，字段一眼能看懂、能手工改、
能进 git。生成时由 builder.py 翻译成 gen_namebuilder 的入参。

    {
      "format": "hz-namebuilder-project",
      "version": 1,
      "meta":    {工程名 / 作者 / 创建 / 修改},
      "options": {每页选项数 / 命名空间 / 模组名 / 输出目录 / 排序方式},
      "regions": [{"id": "ZH", "name": "中华区域"}, ...],
      "prefixes": ["大", "中", ...],
      "suffixes": ["国", "帝国", ...],
      "names":   [{"name":"中华","region":"ZH","tag":"","note":"","seq":1}, ...]
    }

names 里的 seq 是「添加顺序」，列表本身的下标是「当前顺序」——
排序会改下标但不动 seq，所以"恢复添加顺序"随时可用。
"""

import json
import math
import os
import re
import sys
import time

# 路径基准走 paths.py：打包成 exe 后 __file__ 是临时解压目录，不能用。
import paths                                             # noqa: E402
HERE = paths.APP_HOME                                    # tools/自定义国名生成器
TOOLS = paths.TOOLS                                      # tools
ROOT = paths.ROOT                                        # 工作区根

FORMAT_ID = 'hz-namebuilder-project'
FORMAT_VERSION = 1
EXT = '.hznproj'

# 默认输出目录在工程文件里的**存法**：相对程序目录。
# 生成/显示时再 resolve_output_dir() 成绝对路径。
DEFAULT_OUTPUT_REL = '生成的mod'

DEFAULT_REGIONS = [
    ('ZH', '中华区域'),
    ('EA', '东亚区域'),
    ('TAT', '鞑靼大区'),
    ('WEU', '西欧区域'),
    ('CEU', '中欧区域'),
    ('EEU', '东欧区域'),
    ('MEAST', '中东区域'),
    ('NAFR', '北非区域'),
    ('SAFR', '南非区域'),
    ('IND', '印度大区'),
    ('EIND', '东印度大区'),
    ('OCE', '大洋洲大区'),
    ('NAME', '北美大区'),
    ('SAME', '中南美区域'),
]
DEFAULT_PREFIXES = ['大', '中', '东', '西', '南', '北', '新', '圣']
DEFAULT_SUFFIXES = ['国', '帝国', '王国', '王朝', '联邦', '汗国', '公国', '共和国']

# (标识, 菜单名, 说明)
SORT_MODES = [
    ('region_pinyin', '区域 + 拼音', '先按区域顺序，区域内按中文拼音（游戏里的默认观感）'),
    ('pinyin', '全局拼音', '不分区域，整表按中文拼音排'),
    ('region_added', '区域 + 添加顺序', '先按区域，区域内按录入先后'),
    ('added', '添加顺序', '完全按录入先后，区域不参与'),
    ('codepoint', 'Unicode 码点', '按字符编码排，中日韩混排时才用得上'),
]

# 「选国名」单页选项上限：原版单个事件最多 33 个 option，
# 这里还要留出「下一页 / 上一页 / 返回」三个，故默认 28。
MAX_PAGE_SIZE = 30


# ------------------------------------------------------------------ 拼音

def _load_pinyin_key():
    """优先复用 region_names 的拼音键（含译名多音字兜底），拿不到就退化"""
    if TOOLS not in sys.path:
        sys.path.insert(0, TOOLS)
    try:
        from region_names import pinyin_key
        return pinyin_key
    except Exception:
        return lambda t: (t,)


_pinyin_key = _load_pinyin_key()


def has_pinyin():
    return _pinyin_key('中华') != ('中华',)


def pinyin_of(text):
    """用于「拼音」列显示；没装 pypinyin 时返回空串"""
    k = _pinyin_key(text)
    if isinstance(k[0], (tuple, list)):
        return ' '.join(k[0])
    return ''


def sort_key_of(mode, text):
    if mode in ('region_pinyin', 'pinyin'):
        return _pinyin_key(text)
    if mode == 'codepoint':
        return (text,)
    return None          # 按 seq


# ------------------------------------------------------------------ 数据类

class Region(object):
    __slots__ = ('id', 'name')

    def __init__(self, rid, name):
        self.id = rid
        self.name = name

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


class NameEntry(object):
    __slots__ = ('name', 'region', 'tag', 'note', 'seq')

    def __init__(self, name, region, tag='', note='', seq=0):
        self.name = name
        self.region = region
        self.tag = tag
        self.note = note
        self.seq = seq

    def to_dict(self):
        return {'name': self.name, 'region': self.region,
                'tag': self.tag, 'note': self.note, 'seq': self.seq}


# ------------------------------------------------------------------ 工程

class Project(object):

    def __init__(self):
        self.path = None
        self.dirty = False
        self.meta = {'name': '未命名工程',
                     'author': '',
                     'created': _now(),
                     'modified': _now(),
                     'note': ''}
        self.options = {
            'page_size': 28,
            'namespace': 'hz_nb',
            'mod_name': '组词自定义国名',
            'output_dir': '',
            'sort_mode': 'region_pinyin',
            'auto_sort': True,
        }
        self.regions = [Region(r, n) for r, n in DEFAULT_REGIONS]
        self.prefixes = list(DEFAULT_PREFIXES)
        self.suffixes = list(DEFAULT_SUFFIXES)
        self.names = []
        self._seq = 1

    # -------------------------------------------------------------- 构造

    @classmethod
    def new_empty(cls, name='未命名工程'):
        p = cls()
        p.meta['name'] = name
        # 存**相对**形式：整个工具目录搬走/改名，工程还能照常生成
        p.options['output_dir'] = DEFAULT_OUTPUT_REL
        return p

    @classmethod
    def new_from_vanilla(cls, name='原版字库'):
        """从 区域-tag-国名对照表.md 起一份工程"""
        p = cls.new_empty(name)
        md = os.path.join(ROOT, '区域-tag-国名对照表.md')
        if os.path.isfile(md):
            p.import_md(md, replace=True)
        return p

    @classmethod
    def load(cls, path):
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        if d.get('format') != FORMAT_ID:
            raise ValueError('不是自定义国名工程文件：%s' % path)
        if d.get('version', 1) > FORMAT_VERSION:
            raise ValueError('工程文件版本 %s 比本程序新，请升级生成器'
                             % d.get('version'))
        p = cls()
        p.path = path
        p.meta.update(d.get('meta') or {})
        p.options.update(d.get('options') or {})
        p.regions = [Region(r['id'], r['name']) for r in (d.get('regions') or [])]
        p.prefixes = list(d.get('prefixes') or [])
        p.suffixes = list(d.get('suffixes') or [])
        p.names = []
        for n in (d.get('names') or []):
            seq = int(n.get('seq') or 0)
            p.names.append(NameEntry(n.get('name', ''), n.get('region', ''),
                                     n.get('tag', ''), n.get('note', ''), seq))
            p._seq = max(p._seq, seq + 1)
        p.sync_regions_from_names()
        p.dirty = False
        return p

    # -------------------------------------------------------------- 存储

    def to_dict(self):
        return {
            'format': FORMAT_ID,
            'version': FORMAT_VERSION,
            'meta': dict(self.meta),
            'options': dict(self.options),
            'regions': [r.to_dict() for r in self.regions],
            'prefixes': list(self.prefixes),
            'suffixes': list(self.suffixes),
            'names': [n.to_dict() for n in self.names],
        }

    def save(self, path=None):
        path = path or self.path
        if not path:
            raise ValueError('还没有指定工程文件路径')
        self.meta['modified'] = _now()
        data = json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
            f.write(data)
        if os.path.exists(path):
            os.remove(path)
        os.rename(tmp, path)
        self.path = path
        self.dirty = False
        return path

    def touch(self):
        self.dirty = True

    # -------------------------------------------------------------- 区域

    def region_ids(self):
        return [r.id for r in self.regions]

    def region_name(self, rid):
        for r in self.regions:
            if r.id == rid:
                return r.name
        return '（未知区域 %s）' % rid

    def region_index(self, rid):
        for i, r in enumerate(self.regions):
            if r.id == rid:
                return i
        return len(self.regions)

    def has_region(self, rid):
        return any(r.id == rid for r in self.regions)

    def add_region(self, rid, name):
        if self.has_region(rid):
            return False, '区域标识 %s 已存在' % rid
        if not _valid_id(rid):
            return False, '区域标识只能用大写字母与数字，且不能为空'
        self.regions.append(Region(rid, name or rid))
        self.touch()
        return True, ''

    def rename_region(self, rid, name):
        for r in self.regions:
            if r.id == rid:
                r.name = name
                self.touch()
                return True
        return False

    def remove_region(self, rid):
        """删区域。返回 (删除的国名数,)"""
        before = len(self.names)
        self.regions = [r for r in self.regions if r.id != rid]
        self.names = [n for n in self.names if n.region != rid]
        self.touch()
        return before - len(self.names)

    def move_region(self, rid, delta):
        idx = self.region_index(rid)
        tgt = idx + delta
        if idx >= len(self.regions) or not (0 <= tgt < len(self.regions)):
            return False
        self.regions.insert(tgt, self.regions.pop(idx))
        self.touch()
        return True

    def sync_regions_from_names(self):
        """防御：工程文件里出现了区域表里没有的 region，补一个占位区域"""
        for n in self.names:
            if not self.has_region(n.region):
                self.regions.append(Region(n.region, n.region))

    def counts_by_region(self):
        c = dict((r.id, 0) for r in self.regions)
        for n in self.names:
            c[n.region] = c.get(n.region, 0) + 1
        return c

    # -------------------------------------------------------------- 国名

    def next_seq(self):
        s = self._seq
        self._seq += 1
        return s

    def add_name(self, name, region, tag='', note=''):
        name = (name or '').strip()
        if not name:
            return None, '国名不能为空'
        if not self.has_region(region):
            return None, '请先选择一个区域'
        self.names.append(NameEntry(name, region, tag.strip(), note.strip(),
                                    self.next_seq()))
        self.touch()
        return self.names[-1], ''

    def update_name(self, idx, name=None, region=None, tag=None, note=None):
        e = self.names[idx]
        if name is not None:
            e.name = name.strip()
        if region is not None:
            e.region = region
        if tag is not None:
            e.tag = tag.strip()
        if note is not None:
            e.note = note.strip()
        self.touch()

    def remove_indices(self, indices):
        for i in sorted(indices, reverse=True):
            if 0 <= i < len(self.names):
                del self.names[i]
        self.touch()

    def move_name(self, idx, delta):
        tgt = idx + delta
        if not (0 <= idx < len(self.names)) or not (0 <= tgt < len(self.names)):
            return False
        self.names.insert(tgt, self.names.pop(idx))
        self.touch()
        return True

    def duplicate_indices(self):
        """区域内重名的，返回重复项的下标（保留第一个）"""
        seen, dup = {}, []
        for i, n in enumerate(self.names):
            k = (n.region, n.name)
            if k in seen:
                dup.append(i)
            else:
                seen[k] = i
        return dup

    def sort_names(self, mode=None):
        """按排序方式重排 self.names。返回是否真的变了顺序"""
        mode = mode or self.options.get('sort_mode', 'region_pinyin')
        key = sort_key_of(mode, '')
        if mode in ('region_added', 'added'):
            self.names.sort(key=lambda n: (n.seq,))
        elif mode == 'codepoint':
            self.names.sort(key=lambda n: (n.name, n.seq))
        elif mode == 'pinyin':
            self.names.sort(key=lambda n: (_pinyin_key(n.name), n.seq))
        else:      # region_pinyin
            self.names.sort(key=lambda n: (self.region_index(n.region),
                                           _pinyin_key(n.name), n.seq))
        self.touch()
        return True

    # -------------------------------------------------------------- 词缀

    def slot_list(self, kind):
        return self.prefixes if kind == 'P' else self.suffixes

    def set_slot_list(self, kind, items):
        if kind == 'P':
            self.prefixes = list(items)
        else:
            self.suffixes = list(items)
        self.touch()

    def add_slot(self, kind, text):
        text = (text or '').strip()
        if not text:
            return False, '不能为空'
        lst = self.slot_list(kind)
        if text in lst:
            return False, '已经存在了'
        lst.append(text)
        self.touch()
        return True, ''

    def update_slot(self, kind, idx, text):
        text = (text or '').strip()
        if not text:
            return False, '不能为空'
        lst = self.slot_list(kind)
        if not (0 <= idx < len(lst)):
            return False, '下标越界'
        if text in lst and lst[idx] != text:
            return False, '已经存在了'
        lst[idx] = text
        self.touch()
        return True, ''

    def remove_slot_indices(self, kind, indices):
        lst = self.slot_list(kind)
        for i in sorted(indices, reverse=True):
            if 0 <= i < len(lst):
                del lst[i]
        self.touch()

    def move_slot(self, kind, idx, delta):
        lst = self.slot_list(kind)
        tgt = idx + delta
        if not (0 <= idx < len(lst)) or not (0 <= tgt < len(lst)):
            return False
        lst.insert(tgt, lst.pop(idx))
        self.touch()
        return True

    def sort_slot(self, kind):
        lst = self.slot_list(kind)
        lst.sort(key=lambda t: _pinyin_key(t))
        self.touch()

    # -------------------------------------------------------------- 导入

    def import_md(self, path, replace=False, region_of=None):
        """从 区域-tag-国名对照表.md 导入。

        区域按显示名匹配（md 的 `## xxx（N）` 小节标题）；
        region_of 可传 {显示名: 区域id} 覆盖。返回 (新增, 跳过重复, 未匹配区域)
        """
        raw = _parse_md(path)
        name_of = dict((r.name, r.id) for r in self.regions)
        if region_of:
            name_of.update(region_of)

        if replace:
            self.names = []
            self._seq = 1

        added, skipped, missed = 0, 0, {}
        existing = set((n.region, n.name) for n in self.names)
        for rname, rows in raw.items():
            rid = name_of.get(rname)
            if rid is None:
                missed[rname] = len(rows)
                continue
            for tag, name in rows:
                if (rid, name) in existing:
                    skipped += 1
                    continue
                existing.add((rid, name))
                self.names.append(NameEntry(name, rid, tag, '', self.next_seq()))
                added += 1
        self.touch()
        return added, skipped, missed

    # -------------------------------------------------------------- 统计

    def stats(self):
        ps = max(1, min(MAX_PAGE_SIZE, int(self.options.get('page_size') or 28)))
        np_, ns = len(self.prefixes), len(self.suffixes)
        unit = 1 + np_ + ns + np_ * ns
        counts = self.counts_by_region()
        pages = 0
        for r in self.regions:
            n = counts.get(r.id, 0)
            pages += max(1, int(math.ceil(n / float(ps)))) if n else 1
        n_names = len(self.names)
        return {
            'names': n_names,
            'regions': len(self.regions),
            'prefixes': np_,
            'suffixes': ns,
            'unit': unit,
            'combos': n_names * unit,
            'pages': pages,
            'events': 4 + 1 + pages,
            'page_size': ps,
            'max_options': ps + 3,
            'empty_regions': [r.id for r in self.regions if not counts.get(r.id)],
            'dups': len(self.duplicate_indices()),
        }

    def validate(self):
        """生成前的硬校验。返回问题列表，空列表 = 可以生成"""
        bad = []
        if not self.regions:
            bad.append('至少需要一个区域')
        if not self.names:
            bad.append('至少需要一个国名')
        for n in self.names:
            if not n.name.strip():
                bad.append('有空的国名条目')
                break
        for n in self.names:
            if not self.has_region(n.region):
                bad.append('国名「%s」指向了不存在的区域 %s' % (n.name, n.region))
                break
        ps = int(self.options.get('page_size') or 0)
        if not (1 <= ps <= MAX_PAGE_SIZE):
            bad.append('每页选项数必须在 1 ~ %d 之间（现在 %d）' % (MAX_PAGE_SIZE, ps))
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$',
                        self.options.get('namespace') or ''):
            bad.append('命名空间只能用字母/数字/下划线，且不能以数字开头')
        if not (self.options.get('output_dir') or '').strip():
            bad.append('还没有指定输出目录')
        ids = self.region_ids()
        if len(ids) != len(set(ids)):
            bad.append('区域标识有重复')
        for r in self.regions:
            if not _valid_id(r.id):
                bad.append('区域标识「%s」不合法（只能用大写字母与数字）' % r.id)
                break
        seen = set()
        for p in self.prefixes + self.suffixes:
            if not p.strip():
                bad.append('前缀/后缀里有空条目')
                break
        return bad

    def regions_for_build(self):
        """传给生成器的 [(id, 显示名, [国名...]), ...]，空区域也要占位"""
        out = []
        for r in self.regions:
            out.append((r.id, r.name,
                        [n.name for n in self.names if n.region == r.id]))
        return out


# ------------------------------------------------------------------ 工具

def _now():
    return time.strftime('%Y-%m-%d %H:%M:%S')


_ID_RE = re.compile(r'^[A-Z0-9_]{1,12}$')


def _valid_id(rid):
    return bool(rid) and bool(_ID_RE.match(rid))


_ROW = re.compile(r'^\|\s*`?([A-Za-z0-9_]{2,4})`?\s*\|\s*([^|]+?)\s*\|')


def _parse_md(path):
    """-> {区域显示名: [(tag, 国名), ...]}

    直接用 tools/region_names.py 的实现。**别在这儿再写一份正则**：
    曾经自己写过一份（把 tag 的反引号改成可选），结果把表格表头
    `| TAG | 中文国名 |` 也当成数据，每区凭空多一个叫「中文国名」的条目
    （14 个区域 = 多 14 个）。
    """
    if TOOLS not in sys.path:
        sys.path.insert(0, TOOLS)
    try:
        from region_names import parse_md
        return parse_md(path)
    except Exception:
        pass

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
            tag, name = m.group(1), m.group(2).strip()
            if not name or set(name) <= set('- '):
                continue
            data[cur].append((tag, name))
    return data


def default_output_dir():
    """默认输出目录的**绝对**路径 —— 只用于显示 / 兼容旧工程。

    工程文件里存的是 `DEFAULT_OUTPUT_REL`（相对形式），别把这个写进去。
    """
    return os.path.join(HERE, DEFAULT_OUTPUT_REL)


def resolve_output_dir(value=None):
    """把工程里存的 output_dir 变成能直接用的绝对路径。

    空 → 默认目录；绝对路径 → 原样；**相对路径 → 相对程序目录**（不是当前
    工作目录！直接 `os.path.abspath()` 会按 CWD 解析，双击 exe 启动时
    CWD 可能是任意地方，生成的东西就飞了）。
    """
    v = (value or '').strip()
    if not v:
        return default_output_dir()
    if os.path.isabs(v):
        return os.path.normpath(v)
    return os.path.normpath(os.path.join(HERE, v))


def rel_output_dir(path):
    """存回工程文件前尽量压缩成相对路径（只在它确实位于程序目录里时）。

    这样整个 `tools/组词自定义国名工具/` 换机器、换盘符、重命名目录都不会
    让工程里的路径烂掉 —— 之前写死绝对路径时踩过一次：工具目录从
    「自定义国名生成器」改名后，老工程里那条路径直接指到了不存在的地方。
    不在程序目录里的（比如 EU4 的 mod 文件夹）保持绝对路径不动。
    """
    p = (path or '').strip()
    if not p:
        return ''
    try:
        rel = os.path.relpath(os.path.normpath(p), HERE)
    except Exception:
        return os.path.normpath(p)
    if rel.startswith('..') or os.path.isabs(rel):
        return os.path.normpath(p)          # 在程序目录外面，没法相对化
    return rel


def project_dir():
    return os.path.join(HERE, '工程文件')


def ensure_dirs():
    for d in (project_dir(), default_output_dir()):
        if not os.path.isdir(d):
            os.makedirs(d)


def list_projects():
    ensure_dirs()
    out = []
    for f in sorted(os.listdir(project_dir())):
        if f.lower().endswith(EXT):
            out.append(os.path.join(project_dir(), f))
    return out
