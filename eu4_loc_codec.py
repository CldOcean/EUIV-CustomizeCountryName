# -*- coding: utf-8 -*-
"""
EU4 本地化 (.yml) 0x10 转义编解码器 —— 权威实现（v2 · 2026-10-11）

来源：逆向自「ParaTranz Toolbox」(paratranz-toolbox v1.2.1, resources/app.asar,
js/app.f8a32c93.js 中的 converter / decoder 两个模块)，并与本机 5050 份
`*_l_english.yml`（创意工坊 + 本地模组）做全库 round-trip 校验通过。

★ v2 变更（2026-10-11，规则 v2 §2）：`l_simp_chinese` 通路整条出局（全库仅 8 份，
  无人使用）。本地化**只有 `l_english` 一条通路**，产出**两个形态**：

    {mod_dir}/localisation/{base}_l_english.yml          编码形式（转义态）← 引擎读，交付用
    {mod_dir}/localisation_decoded/{base}_l_english.yml  解码形式（明文）  ← 引擎不读，开发用

  两份都 UTF-8 带 BOM、首行都是 `l_english:`、换行都用 `\\n`。
  → 用 `write_loc()` 一次产出；改完明文再用 `encode_tree()` 批量回填。
  → 旧 API `write_loc_pair()`（出 `_l_simp_chinese.yml`）**已删除**。
    废止原因：① simp_chinese 通路无人使用；② 明文那份也在引擎加载路径里，改坏了直接影响游戏显示。

  引擎不读 `localisation_decoded/` 的依据（2026-10-11 实测）：
    · eu4.exe 里的本地化路径是**精确字符串**（`localisation` ×9、`localisation/replace`、
      `localisation/languages.yml`、`customizable_localization`），**无 `localisation_*` 前缀拼接**；
    · 语料先例：`3400977776/localisation_source/`、`3530845796/localisation_backup_before_rewrite/`
      两份同前缀目录装着标准格式真 yml，均未被加载。

------------------------------------------------------------------
★ 为什么 l_english 要转义
引擎流程： 文件字节 -> UTF-8 解码 -> 每个字符降成单个字节(cp1252) -> 扫转义序列还原汉字
所以 l_english 里不能直接写 UTF-8 汉字，必须写成 3 字符的转义序列。

★ 转义序列 = 3 个字符：  <标记> <低字节> <高字节>
    标记 0x10~0x13，末 2 bit 是偏移标志位：
        bit0 (标记 & 1) -> 低字节在编码时做过 +OFFSET_LO，解码时要 -OFFSET_LO
        bit1 (标记 & 2) -> 高字节在编码时做过 -9     ，解码时要 +9
    EU4: OFFSET_LO = 14 (0x0E)

★ 什么时候加偏移
    当该字节真值落在「禁用字节集」FORBIDDEN 里（这些值在流里有语法含义）。

★ 两种等价写法
    0x80~0x9F 区间的字节可以写成裸控制字符，也可以写成 cp1252 可打印符号
    （'„' '‹' '•' 'Œ' '—' …）。解码端统一做 cp1252 反查，两种都能还原。
    所以【判断是否解码成功不要比字节】，比「字符数 + 读出来通不通顺」。
------------------------------------------------------------------
"""

# ---------------------------------------------------------------- 常量

#: 禁用字节集（EU4）。低字节/高字节共用。
#: ★ 2026-10-11 存档实测补充（不要往这个集合里加 0x3A / 0x3F）：
#:   拿本机一个存档的 64872 条原始字符串做「解码→重新编码→逐字节比对」，
#:   本集合下 64769 条一致、103 条不符；那 103 条里 0x3A/0x3F 是被转义的
#:   （如 阿 U+963F 写成 11 4D 96），但同一个字在另外 7000 条里是**不转义**的（10 3F 96）。
#:   → 游戏里存在两套写入者（一套转义这两个字节、一套不转义），把 0x3A/0x3F 加进来
#:     只会把不符从 103 条涨到 7000 条，所以**保持 Toolbox 原集合**。
#:   对本脚本无实际影响：解码是看标记位的，两种写法都能正确还原。
FORBIDDEN = {
    0x00, 0x0A, 0x0D, 0x20, 0x22, 0x23, 0x24, 0x2F, 0x3B, 0x3D,
    0x40, 0x5B, 0x5C, 0x5D, 0x5F, 0x7B, 0x7D, 0x7E, 0x80, 0xA3,
    0xA4, 0xA7, 0xBD,
}

#: CK2（非 EU4）在 utf8 输出时会把空格 0x20 从禁用集里移除。
#: ★ 本项目已冻结在 EU4 v1.37.5.0，这一支永远不会被走到；
#:   保留仅为兼容历史调用（`game='ck2'`），删掉也无副作用。
FORBIDDEN_CK2_UTF8 = FORBIDDEN - {0x20}

OFFSET_LO = {'eu4': 14, 'ck2': 15}   # 低字节偏移量
OFFSET_HI = -9                       # 高字节偏移量（编码时加 -9，解码时加 +9）

#: 字节 -> cp1252 可打印符号的 Unicode 码位（仅 0x80~0x9F 中有定义的那些）
BYTE_TO_CP1252 = {
    0x80: 0x20AC, 0x82: 0x201A, 0x83: 0x0192, 0x84: 0x201E, 0x85: 0x2026,
    0x86: 0x2020, 0x87: 0x2021, 0x88: 0x02C6, 0x89: 0x2030, 0x8A: 0x0160,
    0x8B: 0x2039, 0x8C: 0x0152, 0x8E: 0x017D, 0x91: 0x2018, 0x92: 0x2019,
    0x93: 0x201C, 0x94: 0x201D, 0x95: 0x2022, 0x96: 0x2013, 0x97: 0x2014,
    0x98: 0x02DC, 0x99: 0x2122, 0x9A: 0x0161, 0x9B: 0x203A, 0x9C: 0x0153,
    0x9E: 0x017E, 0x9F: 0x0178,
}
CP1252_TO_BYTE = {v: k for k, v in BYTE_TO_CP1252.items()}

BOM = b'\xef\xbb\xbf'

#: 文件名/目录名常量（v2 形态）
LANG = 'english'                 # 唯一通路
LOC_DIRNAME = 'localisation'             # 引擎读，只放编码版
DECODED_DIRNAME = 'localisation_decoded'  # 引擎不读（英式拼写），只放明文版
LOC_SUFFIX = '_l_%s.yml' % LANG


# ---------------------------------------------------------------- 底层映射
def _char_to_byte(ch):
    """文件里的字符 -> 引擎眼中的单字节。<0x100 取原值；否则按 cp1252 反查。"""
    o = ord(ch)
    if o <= 0xFF:
        return o
    return CP1252_TO_BYTE.get(o)


def _byte_to_char(b, use_cp1252=True):
    """单字节 -> 要写进文件的字符。use_cp1252=True 时 0x80~0x9F 写成可打印符号。"""
    if use_cp1252 and b in BYTE_TO_CP1252:
        return chr(BYTE_TO_CP1252[b])
    return chr(b)


# ---------------------------------------------------------------- 解码
def decode_value(val, game='eu4'):
    """把 yml 里的内部字符串(含转义)还原成可读文本。"""
    off_lo = OFFSET_LO.get(game, 14)
    out, i, n = [], 0, len(val)
    while i < n:
        m = ord(val[i])
        if 0x10 <= m <= 0x13 and i + 2 < n:
            hi = _char_to_byte(val[i + 2])   # 注意：第 3 个字符是高字节
            lo = _char_to_byte(val[i + 1])
            if lo is not None and hi is not None:
                if m & 1:
                    lo = (lo - off_lo) & 0xFF
                if m & 2:
                    hi = (hi + 9) & 0xFF     # 解码端 +9
                out.append(chr(lo | (hi << 8)))
                i += 3
                continue
        out.append(val[i])
        i += 1
    return ''.join(out)


def read_yml(path, game='eu4'):
    """读 yml -> 可读文本（自动去 BOM）"""
    raw = open(path, 'rb').read()
    if raw[:3] == BOM:
        raw = raw[3:]
    return decode_value(raw.decode('utf-8'), game)


def is_encoded(text):
    """粗判形态：True = 转义态(编码形式)，False = 明文 UTF-8(解码形式)"""
    return any(0x10 <= ord(c) <= 0x14 for c in text)


# ---------------------------------------------------------------- 编码
def encode_char(ch, game='eu4', use_cp1252=True):
    """单个字符 -> 转义序列字符串（非 CJK 原样返回）"""
    cp = ord(ch)
    if cp <= 0xFF:
        return ch
    off_lo = OFFSET_LO.get(game, 14)
    forbidden = FORBIDDEN if game != 'ck2' else FORBIDDEN_CK2_UTF8
    lo, hi = cp & 0xFF, (cp >> 8) & 0xFF
    marker = 0x10
    if lo in forbidden:
        lo = (lo + off_lo) & 0xFF
        marker |= 1
    if hi in forbidden:
        hi = (hi + OFFSET_HI) & 0xFF         # 编码端 -9
        marker |= 2
    return chr(marker) + _byte_to_char(lo, use_cp1252) + _byte_to_char(hi, use_cp1252)


def encode_text(text, game='eu4', use_cp1252=True):
    """可读文本 -> 内部字符串(含转义)，用于写编码版 yml"""
    return ''.join(encode_char(c, game, use_cp1252) for c in text)


def risky_chars(text):
    """
    列出明文里会让转义态失真的字符（0x10~0x14 会被引擎当成转义标记）。
    正常文案不应出现；出现说明上游解码时踩到了损坏的转义序列，需人工确认。
    """
    return [(i, hex(ord(c))) for i, c in enumerate(text) if 0x10 <= ord(c) <= 0x14]


def write_yml(path, internal_text, bom=True):
    """内部字符串落盘：UTF-8 (+BOM)。换行统一用 \\n。"""
    data = internal_text.encode('utf-8')
    with open(path, 'wb') as f:
        f.write((BOM if bom else b'') + data)


# ---------------------------------------------------------------- 建文件
def make_loc(entries, encode, game='eu4', eol='\n'):
    """
    拼一份本地化文件正文。

    entries  [(key, index, value), ...] 或 [(key, value), ...]
    encode   **必须由调用方显式指定**：True = 转义态（写 localisation/）
                                         False = 明文（写 localisation_decoded/）
    首行恒为 `l_english:`（v2：只有 l_english 一条通路；解码版首行也跟文件名走，
    这样一键编码回填时 key 与首行都不用改）。
    """
    lines = ['l_%s:' % LANG]
    for e in entries:
        if len(e) == 3:
            k, idx, v = e
        else:
            k, idx, v = e[0], 0, e[1]
        if encode:
            v = encode_text(v, game)
        lines.append(' %s:%d "%s"' % (k, idx, v))
    return eol.join(lines) + eol


def write_loc(base_name, entries, mod_dir, game='eu4', bom=True, eol='\n'):
    """
    产出两份（v2 的唯一产出入口）：
        {mod_dir}/localisation/{base}_l_english.yml          编码形式
        {mod_dir}/localisation_decoded/{base}_l_english.yml  解码形式
    两份都 UTF-8+BOM、首行都是 `l_english:`、换行都用 \\n。
    返回 [编码版路径, 解码版路径]。
    """
    import os
    loc_dir = os.path.join(mod_dir, LOC_DIRNAME)
    dec_dir = os.path.join(mod_dir, DECODED_DIRNAME)
    for d in (loc_dir, dec_dir):
        if not os.path.isdir(d):
            os.makedirs(d)
    enc_path = os.path.join(loc_dir, base_name + LOC_SUFFIX)
    dec_path = os.path.join(dec_dir, base_name + LOC_SUFFIX)
    write_yml(enc_path, make_loc(entries, encode=True, game=game, eol=eol), bom)
    write_yml(dec_path, make_loc(entries, encode=False, game=game, eol=eol), bom)
    return [enc_path, dec_path]


def encode_tree(decoded_dir, loc_dir, game='eu4', bom=True):
    """
    批量回填：decoded_dir 下所有 *.yml -> 读明文 -> 重新编码 -> 写 loc_dir 同名文件。
    （`localisation_decoded/` 是唯一允许出现明文的地方；改完文案跑这一条命令即可生效。）
    返回处理过的文件清单（loc_dir 下的目标路径）。
    """
    import os
    done = []
    if not os.path.isdir(decoded_dir):
        return done
    if not os.path.isdir(loc_dir):
        os.makedirs(loc_dir)
    for fn in sorted(os.listdir(decoded_dir)):
        if not fn.endswith('.yml'):
            continue
        src = os.path.join(decoded_dir, fn)
        if not os.path.isfile(src):
            continue
        plain = read_yml(src, game)                  # 明文 -> 可读文本（本步是恒等变换）
        dst = os.path.join(loc_dir, fn)
        write_yml(dst, encode_text(plain, game), bom)
        done.append(dst)
    return done


# ---------------------------------------------------------------- CLI
if __name__ == '__main__':
    import sys
    usage = __doc__ + """
用法:
  python eu4_loc_codec.py d <file.yml> [行数]   解码查看
  python eu4_loc_codec.py e <file.yml>          编码回填 -> *.new.yml
  python eu4_loc_codec.py s <中文文本>           单句编码(repr)
  python eu4_loc_codec.py f <file.yml>          判定形态(编码/明文)
  python eu4_loc_codec.py t <decoded_dir> <loc_dir>   批量回填整个解码目录
"""
    if len(sys.argv) < 3:
        print(usage)
        sys.exit(0)
    mode, arg = sys.argv[1], sys.argv[2]
    if mode == 'd':
        t = read_yml(arg)
        lim = int(sys.argv[3]) if len(sys.argv) > 3 else 40
        print('\n'.join(t.split('\n')[:lim]))
    elif mode == 'e':
        write_yml(arg.replace('.yml', '.new.yml'), encode_text(read_yml(arg)))
        print('已生成', arg.replace('.yml', '.new.yml'))
    elif mode == 's':
        print(repr(encode_text(arg)))
    elif mode == 'f':
        raw = open(arg, 'rb').read()
        t = (raw[3:] if raw[:3] == BOM else raw).decode('utf-8')
        print('文件:', arg)
        print('BOM :', raw[:3] == BOM)
        print('形态:', '编码形式(转义态)' if is_encoded(t) else '明文 UTF-8(解码态)')
    elif mode == 't':
        for p in encode_tree(arg, sys.argv[3]):
            print('回填 ->', p)
    else:
        print(usage)
