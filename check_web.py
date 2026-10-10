# -*- coding: utf-8 -*-
r"""网页引擎自检：起服务 → 打一遍所有 API → 生成一次 → 关服务。

    <python> check_web.py

只测 HTTP 这一层（界面是浏览器画的，脚本测不到，靠肉眼）。
要点跟 check_gui.py 一样：**破坏性测试必须在临时工程上做**，
别动 工程文件/ 里的真实工程，也别往 生成的mod/ 里写 ——
那边是正式产物目录。
"""

import io
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from web import server          # noqa: E402

OK, FAIL = [], []


def check(name, cond, extra=''):
    (OK if cond else FAIL).append(name)
    print('  %s %s%s' % ('[OK]' if cond else '[!!]', name,
                         ('  <- ' + str(extra)) if (extra and not cond) else ''))


class Client(object):

    def __init__(self, base):
        self.base = base

    def get(self, path):
        with urllib.request.urlopen(self.base + path, timeout=60) as r:
            raw = r.read().decode('utf-8')
        if path.startswith('/api/'):
            return json.loads(raw)
        return raw

    def post(self, path, body=None):
        data = json.dumps(body or {}).encode('utf-8')
        req = urllib.request.Request(self.base + path, data=data,
                                     headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode('utf-8'))


def main():
    holder = {}

    # 记住用户原来的设置：自检会把 last_project 指到临时工程上，
    # 跑完必须还回去 —— 不然用户下次打开界面就不是自己那个工程了。
    # 主题 / 自动定位 / 上次区域同理，自检顺手改过也得还原。
    orig = server.load_settings()
    orig_last = orig.get('last_project')
    tmp_proj = os.path.join(server.P.project_dir(), '网页自检.hznproj')

    def run():
        server.serve(port=0, open_browser=False, quiet=True)

    t = threading.Thread(target=run, daemon=True)
    t.start()

    # 等端口起来
    port = 0
    for _ in range(100):
        if server.SERVER is not None:
            port = server.SERVER.server_address[1]
            break
        time.sleep(0.05)
    if not port:
        raise SystemExit('服务没起来')

    c = Client('http://127.0.0.1:%d' % port)
    print('服务: http://127.0.0.1:%d' % port)

    # ---------------------------------------------------------- 静态资源
    html = c.get('/')
    check('GET / 返回页面', '自定义国名生成器' in html)
    check('GET /app.css', 'data-theme' in c.get('/app.css'))
    check('产出 app.js', 'api/state' in c.get('/app.js'))
    check('未知路径回退到首页', '自定义国名生成器' in c.get('/nope'))

    # ---------------------------------------------------------- 单引擎改造
    # 原生（tkinter）界面已经不再维护，页面上不能还留着切过去的入口。
    check('页面里没有「经典界面」入口',
          '经典界面' not in html and 'btnEngine' not in html)
    check('页面有自动定位开关', 'id="btnFollow"' in html)
    css = io.open(os.path.join(HERE, 'web', 'static', 'app.css'),
                  encoding='utf-8').read()
    js = io.open(os.path.join(HERE, 'web', 'static', 'app.js'),
                 encoding='utf-8').read()
    check('有开关按下态样式', '.btn-toggle.is-on' in css)
    check('有高亮动画', 'is-flash' in css and '@keyframes flash' in css)
    check('后端没有引擎切换接口',
          not any('/api/engine/switch' in k[1] for k in server.ROUTES))
    check('前端没有引擎切换残留', 'engine/switch' not in js and 'btnEngine' not in js)

    # ---------------------------------------------------------- 状态
    # 基准口径必须在**现造的干净种子**上断言，不能拿界面里的活工程 ——
    # 用户在界面上多加一个国名 / 多几个词缀，这里立刻假红（真发生过：
    # 活工程被加成 971 国名 / 13 前缀 / 12 后缀，970/78570 全线飘红）。
    c.post('/api/project/new', {'name': '网页自检', 'seed': 'vanilla'})
    st = c.get('/api/state')
    p = st['project']
    check('/api/state 有工程', p['name'] and p['names'])
    check('国名 970', st['stats']['names'] == 970, st['stats']['names'])
    check('组合 78570', st['stats']['combos'] == 78570, st['stats']['combos'])
    check('事件 46', st['stats']['events'] == 46, st['stats']['events'])
    check('拼音可用', st['pinyin_ok'], '没装 pypinyin')
    check('排序方式有 5 种', len(st['sort_modes']) == 5)
    check('词缀拼音已给全',
          all(t in st['slot_pinyin'] for t in p['prefixes'] + p['suffixes']))
    check('校验通过', not st['issues'], st['issues'])
    holder['st'] = st

    # ---------------------------------------------------------- 临时工程
    c.post('/api/project/new', {'name': '网页自检', 'seed': 'empty'})
    st = c.get('/api/state')
    check('新建空白工程', st['stats']['names'] == 0, st['stats']['names'])
    check('空白工程仍带默认区域', st['stats']['regions'] == 14)

    rid = st['project']['regions'][0]['id']
    r2 = c.post('/api/regions/add', {'id': 'ZZ9', 'name': '自检区'})
    check('加区域', r2.get('ok'))
    st = c.get('/api/state')
    check('新区域在列表末尾', st['project']['regions'][-1]['id'] == 'ZZ9')

    a = c.post('/api/names/add', {'name': '甲国', 'region': rid})
    check('加国名', a.get('ok'))
    # seq 是「添加后自动定位」唯一的锚点 —— 排序 / 增删会把下标挪走，seq 不会。
    check('加国名返回 seq', isinstance(a.get('seq'), int), a)
    b = c.post('/api/names/add', {'name': '甲国', 'region': rid})
    check('区域内重名要确认', b.get('need_confirm'), b)
    b2 = c.post('/api/names/add',
                {'name': '甲国', 'region': rid, 'allow_dup': True})
    check('确认后能强行加', b2.get('ok'))
    c.post('/api/names/add', {'name': '乙国', 'region': rid})
    c.post('/api/names/add', {'name': '丙国', 'region': 'ZZ9'})

    # 甲国 / 甲国(强行重复) / 乙国 / 丙国 = 4 条
    st = c.get('/api/state')
    check('4 个国名', st['stats']['names'] == 4, st['stats']['names'])
    check('重名被标出来', sum(1 for n in st['project']['names'] if n['dup']) == 1)
    check('seq 互不重复',
          len(set(n['seq'] for n in st['project']['names'])) == 4,
          [n['seq'] for n in st['project']['names']])

    # 先清重名（保留第一个），再改名 —— 顺序反了就沒得可清了
    d = c.post('/api/names/dedup', {})
    check('清重名删掉 1 条', d.get('removed') == 1, d)
    check('清完剩 3 条', c.get('/api/state')['stats']['names'] == 3)

    c.post('/api/names/update',
           {'index': 0, 'name': '甲国改名', 'region': rid})
    check('改名生效',
          c.get('/api/state')['project']['names'][0]['name'] == '甲国改名')

    names = [n['name'] for n in c.get('/api/state')['project']['names']]
    c.post('/api/names/move', {'index': names.index('丙国'), 'delta': -1})
    check('上移生效',
          [n['name'] for n in c.get('/api/state')['project']['names']]
          == ['甲国改名', '丙国', '乙国'],
          [n['name'] for n in c.get('/api/state')['project']['names']])

    c.post('/api/names/sort', {'mode': 'pinyin'})
    names = [n['name'] for n in c.get('/api/state')['project']['names']]
    check('按拼音排序', names == ['丙国', '甲国改名', '乙国'], names)

    # ---------------------------------------------------------- 词缀
    c.post('/api/slots/add', {'kind': 'P', 'text': '自检前缀'})
    check('加前缀', '自检前缀' in c.get('/api/state')['project']['prefixes'])
    c.post('/api/slots/add', {'kind': 'P', 'text': '自检前缀'})
    check('词缀不许重复', len(
        [x for x in c.get('/api/state')['project']['prefixes']
         if x == '自检前缀']) == 1)
    idx = c.get('/api/state')['project']['prefixes'].index('自检前缀')
    c.post('/api/slots/update', {'kind': 'P', 'index': idx, 'text': '改后前缀'})
    check('改前缀', '改后前缀' in c.get('/api/state')['project']['prefixes'])
    c.post('/api/slots/sort', {'kind': 'P'})
    check('前缀能排序', len(c.get('/api/state')['project']['prefixes']) == 9)
    # 按值定位再删（排序会换位置）
    idx = c.get('/api/state')['project']['prefixes'].index('改后前缀')
    c.post('/api/slots/delete', {'kind': 'P', 'indices': [idx]})
    check('删前缀', '改后前缀' not in c.get('/api/state')['project']['prefixes'])

    # ---------------------------------------------------------- 区域
    c.post('/api/regions/rename', {'id': 'ZZ9', 'name': '自检区改名'})
    check('区域改名',
          c.get('/api/state')['project']['regions'][-1]['name'] == '自检区改名')
    r = c.post('/api/regions/delete', {'id': 'ZZ9'})
    check('删区域带走国名', r.get('removed') == 1, r)
    check('区域已删',
          'ZZ9' not in [x['id'] for x in
                        c.get('/api/state')['project']['regions']])

    # ---------------------------------------------------------- 导入
    # 生成放在最后单独一节：它会一口气落 218 个文件，清理时容易触发外部
    # 保护直接把进程掐掉 —— 那一掐会把后面所有用例一起带走。放最后最安全。
    imp = c.post('/api/names/import', {'replace': True})
    check('导入原版字库', imp.get('added') == 970, imp)
    check('导入后 970', c.get('/api/state')['stats']['names'] == 970)
    check('导入后组合 78570', c.get('/api/state')['stats']['combos'] == 78570)

    # ---------------------------------------------------------- 设置
    c.post('/api/settings', {'theme': 'dark'})
    check('设置能存', c.get('/api/state')['settings']['theme'] == 'dark')

    c.post('/api/settings', {'follow': True, 'last_region': rid})
    s2 = c.get('/api/state')['settings']
    check('自动定位开关能存', s2.get('follow') is True, s2)
    check('上次选的区域能存', s2.get('last_region') == rid, s2)
    check('设置只往外给白名单字段',
          set(s2) == {'theme', 'follow', 'last_region'}, sorted(s2))
    try:
        c.post('/api/no-such-api', {})
        check('未知接口返回 404', False)
    except urllib.error.HTTPError as e:
        check('未知接口返回 404', e.code == 404, e.code)

    # ---------------------------------------------------------- 遮罩
    # 曾经 .modal-root 直接写 display:grid，盖掉 HTML 的 hidden 属性
    # （UA 的 [hidden]{display:none} 优先级低于作者样式）→ 整页糊一层模糊还点不动。
    # jsdom 的样式级联不靠谱，所以这里直接拿 CSS 文本做静态断言。
    css = io.open(os.path.join(HERE, 'web', 'static', 'app.css'),
                  encoding='utf-8').read()
    bare = re.search(r'\.modal-root\s*\{([^}]*)\}', css)
    check('遮罩裸规则里没有 display', bare and 'display' not in bare.group(1),
          bare.group(1) if bare else '没找到 .modal-root')
    check('遮罩有 [hidden] 兜底', '.modal-root[hidden]' in css)

    # ---------------------------------------------------------- 前端
    # HTTP 层测不出「语法没错但一运行就炸」，用 jsdom 真跑一遍 app.js。
    # 没装 jsdom 就跳过，不算失败。
    node = r'C:\Users\CldOcean\.workbuddy\binaries\node\versions\22.22.2-6\node.exe'
    ws = r'C:\Users\CldOcean\.workbuddy\binaries\node\workspace\node_modules'
    if os.path.isfile(node) and os.path.isdir(os.path.join(ws, 'jsdom')):
        env = dict(os.environ, NODE_PATH=ws)
        try:
            r = subprocess.run([node, os.path.join(HERE, 'check_web_ui.js'),
                                str(port), rid],
                               capture_output=True, timeout=120, env=env)
            out = (r.stdout or b'').decode('utf-8', 'replace')
            check('前端无运行时错误', r.returncode == 0,
                  (r.stderr or b'').decode('utf-8', 'replace')[:400])
            check('前端渲染出国名表', '"国名行数": 100' in out, out[:300])
            check('前端渲染出区域表', '"区域行数": 14' in out)
            check('遮罩初始不可见（别挡住页面）',
                  '"遮罩初始 display": "none"' in out, out[-300:])
            # 下面这几条都是真踩过坑的地方，做成回归：
            need = [
                # 单击一行不能重绘表格，否则双击的目标节点会塌掉
                ('单击不重绘行（双击的前提）', '"单击后行还在 DOM 里": true'),
                ('双击能弹出编辑框', '"双击后弹窗": "编辑国名"'),
                ('编辑框带出这一行的原值', '"弹窗带出非空原值": true'),
                ('编辑时光标落在国名输入框', '"弹窗光标在国名上": "fName"'),
                ('点取消能关掉弹窗', '"取消后弹窗关了": true'),
                ('自动定位开关能切换', '"开关状态翻转了": true'),
                ('开关的高亮样式跟着状态走', '"开关的高亮样式跟着翻": true'),
                ('添加弹窗默认用上次的区域', '"默认区域对了": true'),
                ('自动定位后恰好一行高亮', '"自动定位后高亮行数": 1'),
                ('高亮的正是刚加的那行', '"高亮行就是目标 seq": true'),
            ]
            for name, frag in need:
                check(name, frag in out, out[-900:])
        except Exception as ex:
            check('前端自检能跑起来', False, ex)
    else:
        print('  [--] 跳过前端自检（没找到 node 或 jsdom）')

    # ---------------------------------------------------------- 还原设置
    # 必须排在「生成」前面：那一节会一口气落 218 个文件再删掉，
    # 有可能被外部保护中途掐断。用户自己的工程指向 / 主题不能跟着陪葬。
    try:
        s = server.SESSION.settings
        s['last_project'] = orig_last
        s['recent'] = [x for x in s.get('recent', []) if '网页自检' not in x]
        # 原来没写过的键就别塞个 None 进去，让后端继续用自己的默认值
        for k in ('theme', 'follow', 'last_region'):
            if k in orig:
                s[k] = orig[k]
            else:
                s.pop(k, None)
        server.save_settings(s)
        if os.path.isfile(tmp_proj):
            os.remove(tmp_proj)
        # 上一次自检要是没跑到还原这步就被掐断了，last_project 会指着一个
        # 已经删掉的临时工程 —— 下次打开就是空工程，看着像文件丢了（真发生过）。
        lp = s.get('last_project') or ''
        if lp and not os.path.isfile(lp):
            s['last_project'] = ''
            server.save_settings(s)
            print('  [--] last_project 指的工程不存在，已清空')
    except Exception as ex:
        print('  [--] 还原设置失败（不影响结果）：%s' % ex)

    # ---------------------------------------------------------- 生成
    # 每次换一个全新的临时目录，而不是先删旧的：生成会落 218 个文件，
    # 无论建还是删，一口气动上百个文件都容易踩到外部保护把进程掐掉。
    # 用完也不 rm —— 交给系统 temp 自己回收。
    tmp = tempfile.mkdtemp(prefix='hzweb_smoke_')
    c.post('/api/project/options', {'output_dir': tmp})
    bad = c.get('/api/state')['issues']
    check('改输出目录后仍通过校验', not bad, bad)
    out = c.post('/api/build', {})
    check('生成成功', out.get('ok'), out.get('error'))
    if out.get('ok'):
        s = out['stats']
        files = sorted(os.path.relpath(os.path.join(rr, f), tmp)
                       .replace(os.sep, '/')
                       for rr, _d, fs in os.walk(tmp) for f in fs)
        check('产出 events/hz_nb_root.txt', 'events/hz_nb_root.txt' in files)
        check('产出本地化', any(f.startswith('localisation/') for f in files))
        check('产出 218 个文件', len(files) == 218, len(files))
        check('生成组合数与 /api/state 一致', s['combos'] == 78570, s['combos'])
        print('  生成: %d 文件 / %.0f KB / %.1f 秒'
              % (s['files'], s['bytes'] / 1024.0, s['seconds']))

    # ---------------------------------------------------------- 关服务
    try:
        c.post('/api/shutdown', {})
    except Exception:
        pass
    time.sleep(1.2)

    print('\n%d 项 OK, %d 项失败' % (len(OK), len(FAIL)))
    for f in FAIL:
        print('  [!!] ' + f)
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
