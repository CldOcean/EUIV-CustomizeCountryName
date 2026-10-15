# -*- coding: utf-8 -*-
r"""
组合造词国名 —— 生成器（按区域拆分版）

设计目标：支持把原版全部 tag 的国名塞进来（几百到上千个），
所以所有产出都**按区域拆分**，避免单个文件过大。

字库来源：`区域-tag-国名对照表.md`（原版全部 tag 的国名，由另一个对话抽取）。
tools/region_names.py 负责解析它 + 按中文拼音排序 + 区域内去重，
所以**改字库不用动本文件**，那边重跑表、这边重跑生成器即可。

产出布局：
  decisions\hz_nb_start.txt                        启动 / 恢复原名（改自己）
  common\new_diplomatic_actions\hz_nb_rename.txt   「影响」分组里的外交行动（改对方）
  interface\hz_nb_icons.gfx                        外交行动图标
  events\hz_nb_root.txt                            选结构
  events\hz_nb_prefix.txt                          选前缀（共享）
  events\hz_nb_region.txt                          选区域（共享）
  events\hz_nb_suffix.txt                          选后缀（共享）
  events\hz_nb_body_<区域>.txt                     选国名（每区域一个）
  common\scripted_effects\hz_nb_clear.txt          清 flag
  common\scripted_effects\hz_nb_flow.txt           流程控制（回退 / 选完国名后去哪）
  common\scripted_effects\hz_nb_apply.txt          分派：按区域（必要时按前缀）
  common\scripted_effects\hz_nb_apply_<区域>[_pNN].txt   实际组合判定
  customizable_localization\hz_nb_show_*.txt       已选内容回显
  localisation\hz_nb_ui_l_english.yml              UI 文本 + 前缀/区域/后缀候选（编码版，交付用）
  localisation\hz_nb_name_<区域>_l_english.yml     各区域的候选名 + 成品名（编码版）
  localisation_decoded\hz_nb_*_l_english.yml       同上两份的明文版（引擎不读，改文案只改这里）

国名 / 形容词成对出现（每个国名 key 都配一份 `<key>_ADJ`，值相同）：
  引擎的 `override_country_name` 只改**国名**，形容词是它拿同一个 key 再拼 `_ADJ`
  去查的另一条路线（本体 `CHINA_STRING` + `CHINA_STRING_ADJ` 就是这个约定），
  所以被 override 的每个 key 都必须带 `_ADJ`，否则改名后形容词还是原 TAG 的。

两条核心设计：
  1. **事件链共享**：前缀/区域/后缀三个事件全模板共用，只有"选国名"按区域分裂。
     所以事件数 = 4 + 区域数，与字库大小无关。
  2. **事件只设 flag，最终 key 由 hz_nb_apply 判定**：
     事件不必按历史选择分裂，组合数再涨也不增加事件。

两条入口共用同一条链：
  · 决议   -> 改自己。入口处 save_global_event_target_as = hz_nb_target（= ROOT）
  · 外交行动 -> 改对方。入口处 FROM = { save_global_event_target_as = hz_nb_target }
  事件链全程跑在 ROOT（发起者）上，flag 也记在 ROOT 上，
  只有最后一步 override_country_name 作用在 event_target:hz_nb_target 上。
  → 两条入口共用同一套 apply 分支表，不需要复制一份。
"""

import os
import sys

# eu4_loc_codec.py 在哪儿：挨个候选目录试，**别写死绝对路径，也别只按
# __file__ 上溯固定层数** —— 本脚本在工作区 tools/、工作区根、工具目录、
# skill 的 scripts/ 四处的相对位置各不相同。
# 打包进 exe 后模块来自 PYZ，一个候选都不命中，import 自然走 PYZ。
_here = os.path.dirname(os.path.abspath(__file__))
_u1 = os.path.dirname(_here)
_u2 = os.path.dirname(_u1)
for _c in (_here, os.path.join(_here, 'tools'),
           _u1 if os.path.basename(_u1) == 'tools' else _here,
           os.path.join(_u2, 'eu4-mod-core', 'scripts'),
           os.path.join(_u1, 'eu4-mod-core', 'scripts'),
           os.path.expanduser(os.path.join('~', '.workbuddy', 'skills',
                                           'eu4-mod-core', 'scripts'))):
    if os.path.isfile(os.path.join(_c, 'eu4_loc_codec.py')):
        sys.path.insert(0, _c)
        break
import eu4_loc_codec as C

# ================================================================== 配置

# 前缀（第 1 格）
SLOT_PREFIX = ["大", "中", "东", "西", "南", "北", "新", "圣"]

# 后缀（第 3 格）
SLOT_SUFFIX = ["国", "帝国", "王国", "王朝", "联邦", "汗国", "公国", "共和国"]

# 国名主体，按区域分组。
# 字库来自「区域-tag-国名对照表.md」（原版全部 tag），由 tools/region_names.py
# 解析并按**中文拼音排序**、区域内去重。那边重跑表，这边重跑生成器即可同步。
from region_names import REGIONS

# 结构模板：(标识, 用到的步骤, 菜单名, 示例)
# 步骤类型：P=前缀 R=区域 B=国名 S=后缀
PATTERNS = [
    ('B',   ['R', 'B'],           '只有国名',           '中华、法兰西'),
    ('PB',  ['P', 'R', 'B'],      '前缀 + 国名',        '大中华、新法兰西'),
    ('BS',  ['R', 'B', 'S'],      '国名 + 后缀',        '中华帝国'),
    ('PBS', ['P', 'R', 'B', 'S'], '前缀 + 国名 + 后缀', '大中华帝国'),
]

# （已废弃）过去用「单文件分支数超过阈值就按前缀再拆」来控制文件大小。
# 现在 apply 固定按后缀组拆（见 APPLY_GROUPS），单文件 = 该区域国名数 × (1+N前缀)，
# 中欧 125 个也只有 1125 分支，不需要再按前缀拆。

# 「选国名」事件每页最多几个选项。
# 硬需求，不是美观问题：中欧区域有 125 个国名，写成 126 个 option 的单个事件时
# 引擎会在载入 events 阶段**直接卡死**（实测：setup.log 最后一行停在
# events/hz_nb_body_CEU.txt，后面的文件全都不加载）。
# 原版单个事件最多 33 个 option（events/FlavorGBR.txt）且能正常载入。
# 这里 28 + 下一页 + 上一页 + 返回 = 31，给原版上限留 2 个余量。
PAGE_SIZE = 28

MOD_DIR = r'D:/Cldocean/文档/Paradox Interactive/Europa Universalis IV/mod/组词自定义国名'
BOM = b'\xef\xbb\xbf'
NS = 'hz_nb'

# 共享事件 id（只有这几个，与字库大小无关）
EV_ROOT, EV_PREFIX, EV_REGION, EV_SUFFIX = 1, 2, 3, 4

# 「确认」事件。存在理由：引擎解析事件时会把 option 里引用的 scripted_effect
# **内联展开**，而全量 apply 有 78570 个分支。1103 个「选国名」option 若各自引用它，
# 展开量是 1103 × 78570 ≈ 8700 万节点 —— 实测就是这么卡死在「载入事件」的。
# 改成所有 option 只跳事件 id（整数引用，不展开），由这一个事件展开唯一的一次。
# 代价：玩家选完国名后要多点一次「确定」。
EV_CONFIRM = 200


def pages_of(rid):
    """该区域的「选国名」分成几页"""
    n = len(REGION_BODY[rid])
    return (n + PAGE_SIZE - 1) // PAGE_SIZE if n else 1


# 每个区域的起始事件 id 偏移（按区域顺序累加页数）
_BODY_BASE = {}


def ev_body(ri, page=1):
    """第 ri 个区域、第 page 页的「选国名」事件 id"""
    return 100 + _BODY_BASE[ri] + page


# ================================================================== 派生数据

BODY = []          # 全部国名，按区域顺序展平
REGION_BODY = {}   # 区域 id -> [全局序号...]
_i = [1]
for _rid, _rname, _names in REGIONS:
    REGION_BODY[_rid] = list(range(_i[0], _i[0] + len(_names)))
    _i[0] += len(_names)
    BODY.extend(_names)

N_PREFIX, N_SUFFIX = len(SLOT_PREFIX), len(SLOT_SUFFIX)
# 每个国名派生出的组合数：B(1) + PB(N前缀) + BS(N后缀) + PBS(N前缀×N后缀)
UNIT = 1 + N_PREFIX + N_SUFFIX + N_PREFIX * N_SUFFIX

# 「选国名」事件的页数与 id 偏移
_off = 0
for _i2, (_rid2, _rn2, _ns2) in enumerate(REGIONS, 1):
    _BODY_BASE[_i2] = _off
    _off += pages_of(_rid2)
MAX_PAGES = max(pages_of(rid) for rid, _rn, _ns in REGIONS)
N_BODY_EVENTS = _off


def idx2(i):
    return '%02d' % i


def flag_of(kind, w):
    """kind: P/R/B/S。B 的 w 是**全局序号**"""
    if kind == 'P':
        return '%s_s1_%s' % (NS, idx2(w))
    if kind == 'R':
        return '%s_reg_%s' % (NS, REGIONS[w - 1][0])
    if kind == 'B':
        return '%s_s2_%s' % (NS, idx2(w))
    if kind == 'S':
        return '%s_s3_%s' % (NS, idx2(w))
    if kind == 'G':
        return '%s_pg_%s' % (NS, idx2(w))     # 国名列表的页码
    raise KeyError(kind)


def pat_flag(pat):
    return '%s_pat_%s' % (NS, pat)


def name_key(pat, d):
    """d: {'P':w,'B':gw,'S':w}，未用到的记 00"""
    return 'HZ_NB_%s_%s_%s_%s' % (pat, idx2(d.get('P', 0)),
                                  idx2(d.get('B', 0)), idx2(d.get('S', 0)))


def name_text(d):
    parts = []
    if 'P' in d:
        parts.append(SLOT_PREFIX[d['P'] - 1])
    if 'B' in d:
        parts.append(BODY[d['B'] - 1])
    if 'S' in d:
        parts.append(SLOT_SUFFIX[d['S'] - 1])
    return ''.join(parts)


_COMBOS = {}


def region_combos(rid):
    """某区域的全部成品组合 -> [(pat, d, group), ...]

    group 决定这个组合落在哪个 apply 文件里。**按"有没有后缀"分，不按前缀分**：
      'ns'   = 不含后缀的模板（B / PB）      -> hz_nb_apply_ns_<RID>
      'sNN'  = 后缀为 NN 的组合（BS / PBS）  -> hz_nb_apply_sNN_<RID>

    这样分组的理由：引擎解析事件时会把 option 引用的 scripted_effect 内联展开。
    "选国名"有 1103 个 option、"选后缀"有 9 个，如果它们都指向一份 78570 分支的
    hz_nb_apply，展开量就是 1103×78570 ≈ 8700 万节点，实测会卡死在载入 events。
    按后缀切开后，每个入口只展开自己那一份（约 8730 分支），总量 ≈ 全部分支数。

    结果缓存：上千个国名时这个列表会被用好几次，别重复构造。
    """
    if rid in _COMBOS:
        return _COMBOS[rid]
    out = []
    gws = REGION_BODY[rid]
    for pat, steps, label, example in PATTERNS:
        has_p, has_s = 'P' in steps, 'S' in steps
        if has_p and has_s:
            for p in range(1, N_PREFIX + 1):
                for gw in gws:
                    for s in range(1, N_SUFFIX + 1):
                        out.append((pat, {'P': p, 'B': gw, 'S': s}, 's%s' % idx2(s)))
        elif has_p:
            for p in range(1, N_PREFIX + 1):
                for gw in gws:
                    out.append((pat, {'P': p, 'B': gw}, 'ns'))
        elif has_s:
            for gw in gws:
                for s in range(1, N_SUFFIX + 1):
                    out.append((pat, {'B': gw, 'S': s}, 's%s' % idx2(s)))
        else:
            for gw in gws:
                out.append((pat, {'B': gw}, 'ns'))
    _COMBOS[rid] = out
    return out


# apply 分支文件的分组：无后缀的一组，每种后缀各一组。
# 分组的目的是隔离内联展开（见 region_combos 的说明），不是控制文件大小。
APPLY_GROUPS = ['ns'] + ['s%s' % idx2(s) for s in range(1, N_SUFFIX + 1)]


def apply_split(rid):
    """该区域的 apply 分支按哪些组拆 → 返回 ['ns', 's01', ...]

    文件名：hz_nb_apply_<组>_<区域>.txt
    单文件分支数 = 该区域国名数 × (1 + N前缀)，中欧 125 个也只有 1125，足够小。
    """
    return APPLY_GROUPS


# ================================================================== decisions

def out_decisions():
    o = ['# generated by gen_namebuilder.py - do not edit by hand',
         'country_decisions = {',
         '\thz_nb_start = {',
         '\t\tpotential = { ai = no }',
         '\t\tallow = { always = yes }',
         '\t\teffect = {',
         '# 把"改名目标"存成全局事件目标。决议模式下目标就是自己；',
         '# 外交行动模式下入口会存成 FROM。两条入口共用同一套 apply 分支。',
         '\t\t\tsave_global_event_target_as = hz_nb_target',
         '\t\t\thidden_effect = { hz_nb_clear_all = yes  hz_nb_clear_pat = yes }',
         '\t\t\tcountry_event = { id = %s.%d }' % (NS, EV_ROOT),
         '\t\t}',
         '\t\tai_will_do = { factor = 0 }',
         '\t}',
         '',
         '\thz_nb_restore = {',
         '\t\tpotential = { ai = no }',
         '\t\tallow = { always = yes }',
         '\t\teffect = {',
         '\t\t\trestore_country_name = yes',
         '\t\t\thidden_effect = { hz_nb_clear_all = yes  hz_nb_clear_pat = yes }',
         '\t\t}',
         '\t\tai_will_do = { factor = 0 }',
         '\t}',
         '}', '']
    return {'decisions/hz_nb_start.txt': '\n'.join(o)}


# ================================================================== 外交行动

def out_diplo_actions():
    """「影响」分组里的自定义外交行动：修改目标国的国名。

    目录 common/new_diplomatic_actions 是 EU4 1.21 起的官方扩展点，
    category = influence 就是游戏里那个「影响」分组。
    ROOT = 发起者（玩家自己），FROM = 目标国。
    """
    o = ['# generated by gen_namebuilder.py - do not edit by hand',
         '# category 取值: alliance influence relation dynasty covert economy',
         '#              access emperor papacy great_powers',
         '# ROOT = 发起国（点这个按钮的人）  FROM = 目标国（被改名的那个）',
         '#',
         '# 这里只做两件事：把目标存成全局事件目标，然后触发同一条事件链。',
         '# 事件链全程跑在 ROOT 上（所以是**发起者**在选名字），',
         '# 最后一步 override_country_name 作用在 event_target:hz_nb_target 上。',
         '%s_rename = {' % NS,
         '\tcategory = influence',
         '',
         '\t# 点了就立刻执行，不弹给对方确认、不需要 AI 接受',
         '\trequire_acceptance = no',
         '',
         '\tis_visible = {',
         '\t\tai = no                       # 只有玩家能用',
         '\t\tFROM = {',
         '\t\t\tNOT = { tag = ROOT }        # 目标不能是自己',
         '\t\t}',
         '\t}',
         '',
         '\tis_allowed = { always = yes }',
         '',
         '\ton_accept = {',
         '\t\tFROM = { save_global_event_target_as = hz_nb_target }',
         '\t\thidden_effect = { hz_nb_clear_all = yes  hz_nb_clear_pat = yes }',
         '\t\tcountry_event = { id = %s.%d }' % (NS, EV_ROOT),
         '\t}',
         '',
         '\tai_will_do = { always = no }',
         '}', '']
    return {'common/new_diplomatic_actions/hz_nb_rename.txt': '\n'.join(o)}


def out_gfx():
    """外交行动按钮的图标。借用官方「影响」图标，省得自己画 dds。"""
    o = ['# generated by gen_namebuilder.py - do not edit by hand',
         '# 新外交行动的图标必须叫 GFX_diplomacy_action_<行动名>，',
         '# 这里直接复用官方的 icon_diplomacy_influence.dds（24x24）。',
         'spriteTypes = {',
         '\tspriteType = {',
         '\t\tname = "GFX_diplomacy_action_%s_rename"' % NS,
         '\t\ttexturefile = "gfx//interface//icon_diplomacy_influence.dds"',
         '\t\talwaystransparent = yes',
         '\t}',
         '}', '']
    return {'interface/hz_nb_icons.gfx': '\n'.join(o)}


# ================================================================== events

def _ev(eid, title, desc, options, back_lines=None, immediate=None):
    """options: [(loc_key, [effect 行...], ai_chance)]

    ai_chance 只影响 AI 自动选哪个；本模组事件全是 is_triggered_only，
    所以给"翻页 / 返回"这类非结果选项填 0，给真正的候选填 1。
    back_lines 为 None 时不生成返回选项。
    immediate 为 None 时不生成 immediate 块；写了就在事件打开时先执行一次
    （用来把"清 970 个 B flag"这类大 effect 从每个 option 摊薄到每次进页面一次）。
    """
    o = ['# generated by gen_namebuilder.py - do not edit by hand',
         'namespace = %s' % NS, '',
         'country_event = {',
         '\tid = %s.%d' % (NS, eid)]
    if title:
        o.append('\ttitle = "%s"' % title)
    if desc:
        o.append('\tdesc = "%s"' % desc)
    o.append('\tis_triggered_only = yes')
    o.append('')
    if immediate:
        o.append('\timmediate = {')
        for line in immediate:
            o.append('\t\t' + line)
        o.append('\t}')
        o.append('')
    for loc, eff, chance in options:
        o.append('\toption = {')
        o.append('\t\tname = "%s"' % loc)
        for line in eff:
            o.append('\t\t' + line)
        o.append('\t\tai_chance = { factor = %d }' % chance)
        o.append('\t}')
    if back_lines is not None:
        o.append('\toption = {')
        o.append('\t\tname = "%s.back"' % NS)
        for line in back_lines:
            o.append('\t\t' + line)
        o.append('\t\tai_chance = { factor = 0 }')
        o.append('\t}')
    o.append('}')
    o.append('')
    return '\n'.join(o)


def out_events():
    out = {}

    # --- 根事件：选结构 ---
    opts = []
    for pat, steps, label, example in PATTERNS:
        first = EV_PREFIX if 'P' in steps else EV_REGION
        opts.append(('%s.%d.o%s' % (NS, EV_ROOT, pat),
                     ['hidden_effect = { hz_nb_clear_all = yes  hz_nb_clear_pat = yes }',
                      'set_country_flag = %s' % pat_flag(pat),
                      'country_event = { id = %s.%d }' % (NS, first)], 1))
    out['events/hz_nb_root.txt'] = _ev(
        EV_ROOT, '%s.%d.t' % (NS, EV_ROOT), '%s.%d.desc' % (NS, EV_ROOT),
        opts, ['country_event = { id = %s.%d }' % (NS, EV_ROOT)])

    # --- 选前缀（共享）---
    opts = [('%s.cP_%s' % (NS, idx2(w)),
             ['hidden_effect = { hz_nb_clear_from_P = yes }',
              'set_country_flag = %s' % flag_of('P', w),
              'country_event = { id = %s.%d }' % (NS, EV_REGION)], 1)
            for w in range(1, N_PREFIX + 1)]
    out['events/hz_nb_prefix.txt'] = _ev(
        EV_PREFIX, '%s.step_P.t' % NS, '%s.step_P.desc' % NS,
        opts, ['country_event = { id = %s.%d }' % (NS, EV_ROOT)])

    # --- 选区域（共享）---
    # 选完区域顺便把页码清了并停在第 1 页（hz_nb_clear_from_R 里带清页码）
    opts = []
    for ri, (rid, rname, _ns) in enumerate(REGIONS, 1):
        opts.append(('%s.cR_%s' % (NS, idx2(ri)),
                     ['hidden_effect = { hz_nb_clear_from_R = yes }',
                      'set_country_flag = %s' % flag_of('R', ri),
                      'set_country_flag = %s' % flag_of('G', 1),
                      'country_event = { id = %s.%d }' % (NS, ev_body(ri, 1))], 1))
    out['events/hz_nb_region.txt'] = _ev(
        EV_REGION, '%s.step_R.t' % NS, '%s.step_R.desc' % NS,
        opts, ['hz_nb_back_from_region = yes'])

    # --- 选国名（每区域一页一个事件）---
    # 分页是硬需求：选项太多会让引擎载不进去，见 PAGE_SIZE 的注释。
    for ri, (rid, rname, _ns) in enumerate(REGIONS, 1):
        gws = REGION_BODY[rid]
        np_ = pages_of(rid)
        for p in range(1, np_ + 1):
            chunk = gws[(p - 1) * PAGE_SIZE:p * PAGE_SIZE]
            opts = []
            for gw in chunk:
                # 只记 flag + 跳 hz_nb_after_body。
                # after_body 里只有 4 个 if + country_event（约 4 个节点），
                # 所以 1103 个 option 各展开一份也只有几千节点；
                # 但绝不能让它引用 hz_nb_apply（78570 分支），否则会卡死载入。
                opts.append(('%s.cB_%s' % (NS, idx2(gw)),
                             ['set_country_flag = %s' % flag_of('B', gw),
                              'hz_nb_after_body = yes'], 1))
            if p < np_:
                opts.append(('%s.next' % NS,
                             ['hidden_effect = { hz_nb_clear_pg = yes }',
                              'set_country_flag = %s' % flag_of('G', p + 1),
                              'country_event = { id = %s.%d }'
                              % (NS, ev_body(ri, p + 1))], 0))
            if p > 1:
                opts.append(('%s.prev' % NS,
                             ['hidden_effect = { hz_nb_clear_pg = yes }',
                              'set_country_flag = %s' % flag_of('G', p - 1),
                              'country_event = { id = %s.%d }'
                              % (NS, ev_body(ri, p - 1))], 0))
            # 清 B / S 放在 immediate：每进一次页面执行一次，
            # 而不是每个 option 都内联一份 970 行的 clr_country_flag
            out['events/hz_nb_body_%s_%s.txt' % (rid, idx2(p))] = _ev(
                ev_body(ri, p), '%s.step_B.t' % NS,
                '%s.step_B_%s_%s.desc' % (NS, rid, idx2(p)),
                opts, ['country_event = { id = %s.%d }' % (NS, EV_REGION)],
                immediate=['%s_clear_B = yes' % NS, '%s_clear_S = yes' % NS])

    # --- 选后缀（共享）---
    # 每个后缀只引用自己那一组分支（8730 个），9 个 option 合计仍是全量，
    # 但都只展开一次；若统一写 hz_nb_apply 就会被展开 9 份 78570。
    opts = [('%s.cS_%s' % (NS, idx2(w)),
             ['hidden_effect = { hz_nb_clear_from_S = yes }',
              'set_country_flag = %s' % flag_of('S', w),
              '%s_apply_s%s = yes' % (NS, idx2(w))], 1)
            for w in range(1, N_SUFFIX + 1)]
    out['events/hz_nb_suffix.txt'] = _ev(
        EV_SUFFIX, '%s.step_S.t' % NS, '%s.step_S.desc' % NS,
        opts, ['hz_nb_back_to_body = yes'])

    # --- 确认事件：只给「不含后缀」的两个模板用（B / PB）。
    # 存在的理由：1103 个「选国名」option 若各自引用 apply，会被内联展开成
    # 上亿节点并卡死载入；这里只有 1 个 option 引用，展开一次就够。
    # 含后缀的模板（BS / PBS）最后一步就是选后缀，那一步直接定名，不再确认。
    out['events/hz_nb_confirm.txt'] = _ev(
        EV_CONFIRM, '%s.confirm.t' % NS, '%s.confirm.desc' % NS,
        [('%s.confirm.ok' % NS, ['%s_apply_ns = yes' % NS], 1)],
        ['%s_back_to_body = yes' % NS])
    return out


# ================================================================== scripted_effects

def out_scripted_effects():
    out = {}
    head = '# generated by gen_namebuilder.py - do not edit by hand\n\n'

    # --- 清 flag ---
    o = [head, '# 按步清 flag：选了某一步，它自己及后面的都要清掉重选']
    for kind, n in (('P', N_PREFIX), ('B', len(BODY)), ('S', N_SUFFIX)):
        o.append('%s_clear_%s = {' % (NS, kind))
        for w in range(1, n + 1):
            o.append('\tclr_country_flag = %s' % flag_of(kind, w))
        o.append('}')
        o.append('')
    o.append('%s_clear_R = {' % NS)
    for rid, _rn, _ns in REGIONS:
        o.append('\tclr_country_flag = %s_reg_%s' % (NS, rid))
    o.append('}')
    o.append('')
    # 页码：进入"选区域"时清干净，随后在事件里设成第 1 页
    o.append('%s_clear_pg = {' % NS)
    for p in range(1, MAX_PAGES + 1):
        o.append('\tclr_country_flag = %s' % flag_of('G', p))
    o.append('}')
    o.append('')
    # 注意 chain 里的页码写 'pg' 而不是 'G'：清页码的 effect 叫 hz_nb_clear_pg，
    # 并没有 hz_nb_clear_G（写过一次，引擎报 Unknown effect type hz_nb_clear_G）
    for kind, chain in (('P', 'P R B S pg'), ('R', 'R B S pg'),
                        ('B', 'B S'), ('S', 'S')):
        o.append('%s_clear_from_%s = {' % (NS, kind))
        for k in chain.split():
            o.append('\t%s_clear_%s = yes' % (NS, k))
        o.append('}')
        o.append('')
    o.append('%s_clear_all = { %s_clear_from_P = yes }' % (NS, NS))
    o.append('')
    o.append('%s_clear_pat = {' % NS)
    for pat, _s, _l, _e in PATTERNS:
        o.append('\tclr_country_flag = %s' % pat_flag(pat))
    o.append('}')
    o.append('')
    out['common/scripted_effects/hz_nb_clear.txt'] = '\n'.join(o)

    # --- 流程控制 ---
    o = [head,
         '# 选完国名后：B/PB 直接定名，BS/PBS 还要选后缀',
         '%s_after_body = {' % NS]
    for pat, steps, label, example in PATTERNS:
        o.append('\tif = {')
        o.append('\t\tlimit = { has_country_flag = %s }' % pat_flag(pat))
        if 'S' in steps:
            # 还要选后缀，选完那一步直接定名，不需要再确认
            o.append('\t\tcountry_event = { id = %s.%d }' % (NS, EV_SUFFIX))
        else:
            # 没有后缀这一步了，弹一次确认再定名
            o.append('\t\tcountry_event = { id = %s.%d }' % (NS, EV_CONFIRM))
        o.append('\t}')
    o.append('}')
    o.append('')
    o.append('# 从"选区域"回退：不含前缀的模板回根事件，含前缀的回"选前缀"')
    o.append('%s_back_from_region = {' % NS)
    for pat, steps, label, example in PATTERNS:
        o.append('\tif = {')
        o.append('\t\tlimit = { has_country_flag = %s }' % pat_flag(pat))
        o.append('\t\tcountry_event = { id = %s.%d }'
                 % (NS, EV_PREFIX if 'P' in steps else EV_ROOT))
        o.append('\t}')
    o.append('}')
    o.append('')
    o.append('# 从"选后缀"回退：后缀事件是共享的，靠 区域 flag + 页码 flag 回到原来那一页')
    o.append('%s_back_to_body = {' % NS)
    for ri, (rid, rname, _ns) in enumerate(REGIONS, 1):
        rflag = flag_of('R', ri)
        for p in range(1, pages_of(rid) + 1):
            o.append('\tif = {')
            o.append('\t\tlimit = { has_country_flag = %s  has_country_flag = %s }'
                     % (rflag, flag_of('G', p)))
            o.append('\t\tcountry_event = { id = %s.%d }' % (NS, ev_body(ri, p)))
            o.append('\t}')
    o.append('}')
    o.append('')
    out['common/scripted_effects/hz_nb_flow.txt'] = '\n'.join(o)

    # --- apply 分派 ---
    # 每个组的入口 effect：按区域分派到该组的分支文件。
    # 调用方只有两处 ——「确认」事件（无后缀组）和「选后缀」的 9 个 option（各一组），
    # 所以每份分支最多被展开一次。
    for grp in APPLY_GROUPS:
        label = ('无后缀（B / PB）' if grp == 'ns'
                 else '后缀 %s（BS / PBS）' % SLOT_SUFFIX[int(grp[1:]) - 1])
        o = [head, '# 分组 %s：%s' % (grp, label),
             '%s_apply_%s = {' % (NS, grp)]
        for ri, (rid, rname, _ns) in enumerate(REGIONS, 1):
            o.append('\tif = {')
            o.append('\t\tlimit = { has_country_flag = %s }' % flag_of('R', ri))
            o.append('\t\t%s_apply_%s_%s = yes' % (NS, grp, rid))
            o.append('\t}')
        o.append('}')
        o.append('')
        out['common/scripted_effects/hz_nb_apply_%s.txt' % grp] = '\n'.join(o)

    # --- 各组 × 各区域的实际分支 ---
    for grp in APPLY_GROUPS:
        for ri, (rid, rname, _ns) in enumerate(REGIONS, 1):
            items = [c for c in region_combos(rid) if c[2] == grp]
            if not items:
                continue
            fname = 'hz_nb_apply_%s_%s' % (grp, rid)
            o = [head, '# 区域：%s　分组：%s　分支 %d 个' % (rname, grp, len(items)),
                 '%s = {' % fname]
            for pat, d, _g in items:
                keys = [k for k in ('P', 'B', 'S') if k in d]
                o.append('\tif = {')
                o.append('\t\tlimit = {')
                o.append('\t\t\thas_country_flag = %s' % pat_flag(pat))
                for k in keys:
                    o.append('\t\t\thas_country_flag = %s' % flag_of(k, d[k]))
                o.append('\t\t}')
                # 改的是「改名目标」而不是触发事件的人：
                # 决议模式下 hz_nb_target = 自己；外交行动模式下 = 对方。
                o.append('\t\tevent_target:hz_nb_target = { override_country_name = %s }'
                         % name_key(pat, d))
                o.append('\t}')
            o.append('}')
            o.append('')
            out['common/scripted_effects/%s.txt' % fname] = '\n'.join(o)
    return out


# ================================================================== customizable_localization

def out_custom_loc():
    out = {}
    head = '# generated by gen_namebuilder.py - do not edit by hand\n\n'

    o = [head]
    for kind, n in (('P', N_PREFIX), ('R', len(REGIONS)), ('S', N_SUFFIX)):
        o.append('defined_text = {')
        o.append('\tname = HZ_NB_SHOW_%s' % kind)
        for w in range(1, n + 1):
            o.append('\ttext = {')
            o.append('\t\ttrigger = { has_country_flag = %s }' % flag_of(kind, w))
            o.append('\t\tlocalisation_key = HZ_NB_CH_%s_%s' % (kind, idx2(w)))
            o.append('\t}')
        o.append('\ttext = { localisation_key = HZ_NB_EMPTY }')
        o.append('}')
        o.append('')
    out['customizable_localization/hz_nb_show_base.txt'] = '\n'.join(o)

    # 国名回显：只有一份（后缀事件是共享的，必须能显示任意区域的国名）
    o = [head, 'defined_text = {', '\tname = HZ_NB_SHOW_B']
    for gw in range(1, len(BODY) + 1):
        o.append('\ttext = {')
        o.append('\t\ttrigger = { has_country_flag = %s }' % flag_of('B', gw))
        o.append('\t\tlocalisation_key = HZ_NB_CH_B_%s' % idx2(gw))
        o.append('\t}')
    o.append('\ttext = { localisation_key = HZ_NB_EMPTY }')
    o.append('}')
    o.append('')
    out['customizable_localization/hz_nb_show_body.txt'] = '\n'.join(o)
    return out


# ================================================================== localisation

def out_localisation():
    """返回 {basename: entries}；每个 basename 出两份：
    localisation/ 下的编码版 + localisation_decoded/ 下的明文版（v2 形态）。

    每个国名 key 都会多出一份 `<key>_ADJ`（形容词，值 = 国名）——
    `override_country_name` 只改国名，形容词由引擎按 `key + '_ADJ'` 另查。
    """

    # --- UI ---
    ui = [('HZ_NB_EMPTY', 0, '')]
    for kind, texts in (('P', SLOT_PREFIX),
                        ('R', [rn for _r, rn, _n in REGIONS]),
                        ('S', SLOT_SUFFIX)):
        for w, t in enumerate(texts, 1):
            ui.append(('HZ_NB_CH_%s_%s' % (kind, idx2(w)), 0, t))
            ui.append(('%s.c%s_%s' % (NS, kind, idx2(w)), 0, t))

    ui.append(('%s.%d.t' % (NS, EV_ROOT), 0, '自定义国名'))
    ui.append(('%s.%d.desc' % (NS, EV_ROOT), 0, '新国名按哪种结构来拼？'))
    for pat, steps, label, example in PATTERNS:
        ui.append(('%s.%d.o%s' % (NS, EV_ROOT, pat), 0,
                   '%s（例：%s）' % (label, example)))
    ui.append(('%s.%d.o99' % (NS, EV_ROOT), 0, '取消'))

    ui.append(('%s.step_P.t' % NS, 0, '选择前缀'))
    ui.append(('%s.step_P.desc' % NS, 0, '选择新国名的前缀。'))
    ui.append(('%s.step_R.t' % NS, 0, '选择区域'))
    ui.append(('%s.step_R.desc' % NS, 0,
               '先选国名所在的区域，后面只会列出该区域的名字。'))
    ui.append(('%s.step_B.t' % NS, 0, '选择国名'))
    # 每页一条 desc（要显示"第 x / y 页"，desc 是静态 key 只能预先生成）
    for ri, (rid, rname, _ns) in enumerate(REGIONS, 1):
        np_ = pages_of(rid)
        for p in range(1, np_ + 1):
            ui.append(('%s.step_B_%s_%s.desc' % (NS, rid, idx2(p)), 0,
                       '已定：§Y[HZ_NB_SHOW_P][HZ_NB_SHOW_R]§!\\n'
                       '请选择国名。（%s　第 %d / %d 页）' % (rname, p, np_)))
    ui.append(('%s.next' % NS, 0, '下一页 →'))
    ui.append(('%s.prev' % NS, 0, '← 上一页'))
    ui.append(('%s.step_S.t' % NS, 0, '选择后缀'))
    ui.append(('%s.step_S.desc' % NS, 0,
               '已定：§Y[HZ_NB_SHOW_P][HZ_NB_SHOW_R][HZ_NB_SHOW_B]§!\\n请选择后缀。'))
    ui.append(('%s.back' % NS, 0, '← 返回上一步'))
    ui.append(('%s.confirm.t' % NS, 0, '确认新国名'))
    ui.append(('%s.confirm.desc' % NS, 0,
               '即将应用：§Y[HZ_NB_SHOW_P][HZ_NB_SHOW_R][HZ_NB_SHOW_B]'
               '[HZ_NB_SHOW_S]§!\\n确定要改吗？'))
    ui.append(('%s.confirm.ok' % NS, 0, '确定，就是这个'))
    ui.append(('hz_nb_start_title', 0, '自定义国名'))
    ui.append(('hz_nb_start_desc', 0, '按区域和结构逐段选择，组合出一个新的国家名称。'))
    ui.append(('hz_nb_restore_title', 0, '恢复原始国名'))
    ui.append(('hz_nb_restore_desc', 0, '取消自定义名称，还原为本来的国名。'))

    # 外交行动（common/new_diplomatic_actions）
    ui.append(('%s_rename_title' % NS, 0, '修改该国国名'))
    ui.append(('%s_rename_desc' % NS, 0,
               '为该国组合一个新的名称。选择流程与本国改名一致，'
               '新名称会同步给所有玩家。'))
    # 注意：国名位置不解析 [ ] 动态文本，所以这里不要写 [FROM.GetName]，
    # 否则会原样回显成一串方括号。
    ui.append(('%s_rename_tooltip' % NS, 0, '修改该国的国名'))

    groups = {'hz_nb_ui': ui}

    # --- 各区域：候选名 + 成品名（并且都带一份 _ADJ 形容词）---
    #
    # 形容词为什么要单独出一份：`override_country_name` 只管**国名**，
    # 形容词是另一条查表路线 —— 引擎拿同一个 key 再拼 `_ADJ` 去查
    # （本体实证：`override_country_name = CHINA_STRING` 对应
    #   `CHINA_STRING:0 "China"` + `CHINA_STRING_ADJ:0 "Chinese"`；
    #   TURKEY_STRING / GURKANI_EMPIRE_STRING 等同款成对出现）。
    # 所以**凡是会被 override 的 key 都必须有 `_ADJ`**，否则改名后形容词还是旧 TAG 的。
    # 这里按需求让形容词 = 同一个国名，直接复制值。
    for rid, rname, _ns in REGIONS:
        e = []
        for gw in REGION_BODY[rid]:
            t = BODY[gw - 1]
            e.append(('HZ_NB_CH_B_%s' % idx2(gw), 0, t))
            e.append(('%s.cB_%s' % (NS, idx2(gw)), 0, t))
            e.append(('HZ_NB_CH_B_%s_ADJ' % idx2(gw), 0, t))
        for pat, d, _g in region_combos(rid):
            k, t = name_key(pat, d), name_text(d)
            e.append((k, 0, t))
            e.append((k + '_ADJ', 0, t))
        groups['hz_nb_name_%s' % rid] = e
    return groups


# ================================================================== 落盘

def clean_old(keep, mod_dir=None):
    """删除上一次生成、这一版不再存在的 hz_* 文件。

    不删就出事：旧的 events/hz_name_builder.txt 里那 65 个事件 id
    会和新的共享链 id 撞车。
    """
    base = mod_dir or MOD_DIR
    removed = []
    for root, _d, files in os.walk(base):
        for f in files:
            if not f.startswith('hz_'):
                continue
            rel = os.path.relpath(os.path.join(root, f), base).replace('\\', '/')
            if rel not in keep:
                os.remove(os.path.join(root, f))
                removed.append(rel)
    return removed


# ================================================================== 可编程入口

def reconfigure(regions=None, prefixes=None, suffixes=None,
                page_size=None, mod_dir=None):
    """换一套字库 / 配置，重算全部派生数据。

    本模块原本是「导入即定」的常量模块（派生数据在 import 时算好），
    GUI 生成器需要在同一进程里反复指向不同的工程数据，所以补这个入口。
    只传要改的项，其余保持当前值。

    regions 形如 [(区域id, 区域显示名, [国名...]), ...]，顺序 = 游戏里弹出顺序。
    """
    g = globals()
    if regions is not None:
        g['REGIONS'] = [(rid, rname, list(names))
                        for rid, rname, names in regions]
    if prefixes is not None:
        g['SLOT_PREFIX'] = list(prefixes)
    if suffixes is not None:
        g['SLOT_SUFFIX'] = list(suffixes)
    if page_size is not None:
        g['PAGE_SIZE'] = max(1, int(page_size))
    if mod_dir is not None:
        g['MOD_DIR'] = mod_dir

    # --- 国名展平 + 区域 -> 全局序号 ---
    body, rbody = [], {}
    n = 1
    for rid, _rname, names in g['REGIONS']:
        rbody[rid] = list(range(n, n + len(names)))
        n += len(names)
        body.extend(names)
    g['BODY'], g['REGION_BODY'] = body, rbody

    g['N_PREFIX'], g['N_SUFFIX'] = len(g['SLOT_PREFIX']), len(g['SLOT_SUFFIX'])
    g['UNIT'] = (1 + g['N_PREFIX'] + g['N_SUFFIX']
                 + g['N_PREFIX'] * g['N_SUFFIX'])

    # --- 「选国名」页数与事件 id 偏移 ---
    base, off = {}, 0
    for i, (rid, _rname, _names) in enumerate(g['REGIONS'], 1):
        base[i] = off
        off += pages_of(rid)
    g['_BODY_BASE'] = base
    g['N_BODY_EVENTS'] = off
    g['MAX_PAGES'] = max([pages_of(rid) for rid, _rn, _ns in g['REGIONS']] or [1])

    # --- apply 分组随后缀数变化 ---
    g['APPLY_GROUPS'] = (['ns']
                         + ['s%s' % idx2(s) for s in range(1, g['N_SUFFIX'] + 1)])
    g['_COMBOS'].clear()


def generate(mod_dir=None, log=None):
    """按当前配置生成全部文件 -> 统计 dict。CLI 与 GUI 共用。

    mod_dir 省略时用模块默认目录；log 是可选的日志回调（GUI 用来刷进度）。
    返回 {'lines': [...], 'files': n, 'removed': [...], 'names': n, ...}
    """
    base = mod_dir or MOD_DIR
    lines = []

    def emit(s=''):
        lines.append(s)
        if log:
            log(s)

    files = {}
    files.update(out_decisions())
    files.update(out_diplo_actions())
    files.update(out_gfx())
    files.update(out_events())
    files.update(out_scripted_effects())
    files.update(out_custom_loc())
    loc_groups = out_localisation()

    total_combos = sum(len(region_combos(rid)) for rid, _rn, _n in REGIONS)
    n_events = 4 + 1 + N_BODY_EVENTS
    emit('国名 %d 个（%d 个区域） / 前缀 %d / 后缀 %d'
         % (len(BODY), len(REGIONS), N_PREFIX, N_SUFFIX))
    emit('每个国名派生 %d 种组合  →  合计 %d 种' % (UNIT, total_combos))
    emit('事件 %d 个：4 个共享 + 1 个确认 + 「选国名」%d 页'
         '（每页最多 %d 个选项，与字库大小只差页数）'
         % (n_events, N_BODY_EVENTS, PAGE_SIZE))
    emit('  每页最多选项数 %d（原版单个事件最多 33，超了引擎会卡在载入 events）'
         % (PAGE_SIZE + 3))
    big = max((len(region_combos(rid)) for rid, _rn, _n in REGIONS), default=0)
    emit('最大区域 %d 分支 → 按后缀拆成 %d 组，单文件最多约 %d 分支'
         % (big, len(APPLY_GROUPS),
            max((len(REGION_BODY[rid]) * (1 + N_PREFIX)
                 for rid, _rn, _n in REGIONS), default=0)))
    emit()

    # --- txt：无 BOM ---
    nbytes = 0
    for rel, text in sorted(files.items()):
        p = os.path.join(base, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        data = text.encode('utf-8')
        if data[:3] == BOM:
            data = data[3:]
        open(p, 'wb').write(data)
        nbytes += len(data)
        emit('  %-56s %7dB' % (rel, len(data)))

    # --- yml：v2「一条通路两个形态」---
    #   localisation/          编码版（转义态）  ← 引擎读，交付用
    #   localisation_decoded/  明文版            ← 引擎不读，开发用
    #   规则 v2（2026-10-11）起不再产出 _l_simp_chinese.yml；两份都带 BOM、首行都是 l_english:。
    keep = set(files)
    for gname, entries in sorted(loc_groups.items()):
        for p in C.write_loc(gname, entries, base):
            d = open(p, 'rb').read()
            rel = os.path.relpath(p, base).replace('\\', '/')
            keep.add(rel)
            nbytes += len(d)
            emit('  %-56s %7dB  BOM=%s' % (rel, len(d), d[:3] == BOM))
    emit('\n本地化 %d 组，共 %d 条（每组两份：localisation/ 编码 + localisation_decoded/ 明文）'
         % (len(loc_groups), sum(len(v) for v in loc_groups.values())))

    removed = clean_old(keep, base)
    if removed:
        emit('\n已删除 %d 个上一版遗留文件（否则事件 id 会冲突）：' % len(removed))
        for r in removed:
            emit('  - ' + r)
    emit('\n注意：改文案只改 localisation_decoded/，然后跑 eu4_loc_codec.encode_tree() 回填；'
         '不要把明文手拷进 localisation/（那里只能放编码版）。')

    return {'lines': lines, 'files': len(files) + 2 * len(loc_groups),
            'removed': removed, 'bytes': nbytes,
            'names': len(BODY), 'regions': len(REGIONS),
            'prefixes': N_PREFIX, 'suffixes': N_SUFFIX,
            'combos': total_combos, 'events': n_events,
            'pages': N_BODY_EVENTS, 'loc_groups': len(loc_groups),
            'loc_entries': sum(len(v) for v in loc_groups.values())}


def main():
    st = generate(log=print)
    print('\n共 %d 个文件，%.1f MB' % (st['files'], st['bytes'] / 1048576.0))


if __name__ == '__main__':
    main()
