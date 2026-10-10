# -*- coding: utf-8 -*-
r"""把工程翻译成 gen_namebuilder 的入参，生成模组文件。

生成逻辑仍然只有 tools/gen_namebuilder.py 一份（它已经过 check_mod.py 校验），
这里只负责「换字库」+「换输出目录」，一行重复实现都没有。
"""

import os
import sys

import paths                                             # noqa: E402
HERE = paths.APP_HOME                                    # tools/自定义国名生成器
TOOLS = paths.TOOLS                                      # tools
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import project as P                                      # noqa: E402


def build(project, outdir=None, log=None):
    """按工程生成。返回 gen_namebuilder.generate() 的统计 dict。

    log 会被逐行回调（GUI 拿它刷日志）。整个过程是同步的，
    970 个国名约 6 秒，GUI 里请放到后台线程。
    """
    import gen_namebuilder as G

    # 用 P.resolve_output_dir：相对路径按**程序目录**解析，而不是 CWD
    outdir = P.resolve_output_dir(outdir or project.options.get('output_dir'))
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    # 生成前自动排序（默认开）。排序只改列表顺序，不改 seq。
    if project.options.get('auto_sort', True):
        project.sort_names(project.options.get('sort_mode', 'region_pinyin'))

    G.reconfigure(regions=project.regions_for_build(),
                  prefixes=list(project.prefixes),
                  suffixes=list(project.suffixes),
                  page_size=project.options.get('page_size', 28),
                  mod_dir=outdir)
    st = G.generate(outdir, log=log)
    st['outdir'] = outdir
    return st
