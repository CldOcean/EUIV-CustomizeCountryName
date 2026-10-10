# -*- coding: utf-8 -*-
r"""网页引擎的后端：本机 HTTP 服务 + JSON API。

界面是浏览器画的，这里只管数据和生成。**不碰任何生成逻辑** ——
工程模型走 project.py，生成走 builder.py，跟命令行版共用同一份，
所以产物必然一致（check_web.py 会盯这条）。

只监听 127.0.0.1，不对外。

    <python> main.py

API 一律返回 JSON：成功 {'ok': true, ...}，出错 {'ok': false, 'error': '...'}。
"""

import json
import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import paths                 # noqa: E402

# HERE 仍按 __file__ 算：它是静态资源的家，打包后正是临时目录里的 web/，
# 要的就是那份被打包进去的副本。GUI / TOOLS 则必须走 paths（工程和设置的家）。
HERE = os.path.dirname(os.path.abspath(__file__))        # web/
for _p in (paths.TOOLS, paths.APP_HOME):
    if _p not in sys.path:
        sys.path.insert(0, _p)
GUI = paths.APP_HOME                                     # 自定义国名生成器/
TOOLS = paths.TOOLS                                      # tools/

import project as P          # noqa: E402
import builder               # noqa: E402
import winapi                # noqa: E402

STATIC = os.path.join(HERE, 'static')
SETTINGS_PATH = os.path.join(GUI, 'settings.json')

MIME = {'.html': 'text/html; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
        '.js': 'application/javascript; charset=utf-8',
        '.json': 'application/json; charset=utf-8',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        '.woff2': 'font/woff2'}


# ------------------------------------------------------------------ 设置

def load_settings():
    try:
        with open(SETTINGS_PATH, encoding='utf-8') as f:
            d = json.load(f)
        if isinstance(d, dict):
            return d
    except Exception:
        pass
    return default_settings()


def default_settings():
    """界面偏好的默认值。

    follow      添加国名后自动跳到那一行并高亮（国名工具栏上的开关）
    last_region 上次「添加国名」时选的区域 —— 下次打开弹窗就默认选它
    """
    return {'theme': 'light', 'recent': [], 'last_project': '',
            'follow': True, 'last_region': ''}


def save_settings(d):
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ------------------------------------------------------------------ 会话

class Session(object):
    """当前工程 + 设置。单用户本机用，不做并发保护。"""

    def __init__(self):
        self.settings = load_settings()
        self.project = None

    # ---------------------------------------------------------- 工程加载

    def boot(self):
        P.ensure_dirs()
        path = self.settings.get('last_project')
        if not (path and os.path.isfile(path)):
            lst = P.list_projects()
            path = lst[0] if lst else None
        if path and os.path.isfile(path):
            try:
                self.project = P.Project.load(path)
                return
            except Exception:
                pass
        md = os.path.join(P.ROOT, '区域-tag-国名对照表.md')
        if os.path.isfile(md):
            p = P.Project.new_from_vanilla('原版字库')
        else:
            p = P.Project.new_empty('默认工程')
        p.path = os.path.join(P.project_dir(), p.meta['name'] + P.EXT)
        self.project = p
        if not os.path.isfile(p.path):
            try:
                p.save()
                self.recent(p.path)
            except Exception:
                pass

    def recent(self, path):
        r = [path] + [x for x in self.settings.get('recent', []) if x != path]
        self.settings['recent'] = r[:8]
        self.settings['last_project'] = path
        save_settings(self.settings)

    def require(self):
        if self.project is None:
            raise ValueError('还没有打开任何工程')
        return self.project


SESSION = Session()


# ------------------------------------------------------------------ API

def _name_rows(pr, dup=None):
    if dup is None:
        dup = set(pr.duplicate_indices())
    out = []
    for i, n in enumerate(pr.names):
        out.append({'i': i,
                    'name': n.name,
                    'region': n.region,
                    'region_name': pr.region_name(n.region),
                    'pinyin': P.pinyin_of(n.name),
                    'tag': n.tag,
                    'note': n.note,
                    'seq': n.seq,
                    'dup': i in dup})
    return out


def api_state(_body):
    pr = SESSION.require()
    # 词缀的拼音前端算不了，这里一次给全（前后缀加起来才十几个）
    slot_py = {}
    for t in pr.prefixes + pr.suffixes:
        slot_py[t] = P.pinyin_of(t)
    return {'project': {
                'name': pr.meta['name'],
                'path': pr.path or '',
                'dirty': pr.dirty,
                'meta': dict(pr.meta),
                'options': dict(pr.options),
                'regions': [r.to_dict() for r in pr.regions],
                'prefixes': list(pr.prefixes),
                'suffixes': list(pr.suffixes),
                'names': _name_rows(pr),
            },
            'stats': pr.stats(),
            'issues': pr.validate(),
            'counts': pr.counts_by_region(),
            'settings': public_settings(),
            'projects': [{'path': p, 'name': os.path.splitext(
                            os.path.basename(p))[0]}
                         for p in P.list_projects()],
            'sort_modes': [{'id': k, 'label': l, 'tip': t}
                           for k, l, t in P.SORT_MODES],
            'slot_pinyin': slot_py,
            'pinyin_ok': P.has_pinyin(),
            'output_default': P.default_output_dir(),
            # 工程里存的是相对形式（可搬家），这里给出它此刻真正指向哪，
            # 界面上显示这条，免得用户看着「生成的mod」不知道落到哪去了
            'output_resolved': P.resolve_output_dir(
                pr.options.get('output_dir')),
            # 对话框的起始目录：打开/另存为落在工程目录，输出目录落在生成目录
            'project_dir': P.project_dir(),
            'native_pick': winapi.dialogs_supported()}


def api_save(body):
    pr = SESSION.require()
    path = (body or {}).get('path') or pr.path
    if not path:
        raise ValueError('还没指定工程文件路径')
    name = (body or {}).get('name')
    if name:
        pr.meta['name'] = name
    pr.save(path)
    SESSION.recent(path)
    return {'path': pr.path}


def api_open(body):
    path = (body or {}).get('path')
    if not path or not os.path.isfile(path):
        raise ValueError('文件不存在：%s' % path)
    pr = P.Project.load(path)
    SESSION.project = pr
    SESSION.recent(path)
    return {'path': path}


def api_reset_paths(_body):
    """把工程里的路径重置回**本机工具目录**下 —— 换机器/换盘符的救命钮。

    工程文件会带着上一位作者机器上的绝对路径（比如输出目录指向他
    `D:/.../mod/组词自定义国名`，而你这台机器上压根没有那个盘）。生成会
    照那个路径去建目录，于是模组落到一个莫名其妙的地方。点一下这个按钮就
    全部拉回工具根目录下的「生成的mod」。
    """
    pr = SESSION.require()
    pr.options['output_dir'] = P.DEFAULT_OUTPUT_REL
    pr.touch()
    return {'output_dir': pr.options['output_dir'],
            'output_resolved': P.resolve_output_dir(pr.options['output_dir']),
            'project_dir': P.project_dir()}


def api_new(body):
    body = body or {}
    name = (body.get('name') or '新建工程').strip()
    seed = body.get('seed') or 'vanilla'
    if seed == 'vanilla':
        pr = P.Project.new_from_vanilla(name)
    elif seed == 'copy' and SESSION.project:
        pr = P.Project()
        src = SESSION.project
        pr.meta = dict(src.meta)
        pr.meta['name'] = name
        pr.options = dict(src.options)
        pr.regions = [P.Region(r.id, r.name) for r in src.regions]
        pr.prefixes = list(src.prefixes)
        pr.suffixes = list(src.suffixes)
        pr.names = [P.NameEntry(n.name, n.region, n.tag, n.note, n.seq)
                    for n in src.names]
        pr._seq = src._seq
        pr.options['output_dir'] = P.DEFAULT_OUTPUT_REL
    else:
        pr = P.Project.new_empty(name)
    pr.meta['name'] = name
    pr.path = os.path.join(P.project_dir(), name + P.EXT)
    SESSION.project = pr
    return {'path': pr.path}


def api_options(body):
    pr = SESSION.require()
    for k, v in (body or {}).items():
        if k == 'page_size':
            pr.options['page_size'] = max(1, min(P.MAX_PAGE_SIZE, int(v)))
        elif k == 'output_dir':
            # 存的时候压成相对路径（在程序目录内的话），
            # 这样整个工具目录搬家 / 改名都不会让工程指错地方
            pr.options['output_dir'] = P.rel_output_dir(
                P.resolve_output_dir(str(v)))
        elif k in pr.options:
            pr.options[k] = v
    pr.touch()
    return {'options': dict(pr.options), 'stats': pr.stats()}


def api_meta(body):
    pr = SESSION.require()
    for k in ('name', 'author', 'note'):
        if k in (body or {}):
            pr.meta[k] = body[k]
    pr.touch()
    return {'meta': dict(pr.meta)}


# -------------------------------------------------------------- 国名

def _dup_check(pr, name, region, skip=-1):
    return any(i != skip and n.region == region and n.name == name
               for i, n in enumerate(pr.names))


def api_names_add(body):
    pr = SESSION.require()
    b = body or {}
    name = (b.get('name') or '').strip()
    if not name:
        raise ValueError('国名不能为空')
    region = b.get('region')
    if not pr.has_region(region):
        raise ValueError('请先选择一个区域')
    dup = _dup_check(pr, name, region)
    if dup and not b.get('allow_dup'):
        return {'ok': False, 'need_confirm': True,
                'error': '「%s」在%s里已经有了' % (name, pr.region_name(region))}
    e, err = pr.add_name(name, region, b.get('tag', ''), b.get('note', ''))
    if err:
        raise ValueError(err)
    # seq 是稳定唯一的自增号：下标会因为排序/增删挪位，seq 不会。
    # 前端靠它「添加完自动定位到这一行」。
    return {'index': len(pr.names) - 1, 'seq': e.seq,
            'stats': pr.stats()}


def api_names_update(body):
    pr = SESSION.require()
    b = body or {}
    i = int(b.get('index', -1))
    if not (0 <= i < len(pr.names)):
        raise ValueError('下标越界')
    name = (b.get('name') or '').strip()
    region = b.get('region') or pr.names[i].region
    if not name:
        raise ValueError('国名不能为空')
    if _dup_check(pr, name, region, skip=i) and not b.get('allow_dup'):
        return {'ok': False, 'need_confirm': True,
                'error': '「%s」在%s里已经有了' % (name, pr.region_name(region))}
    pr.update_name(i, name, region, b.get('tag', ''), b.get('note', ''))
    return {'stats': pr.stats()}


def api_names_delete(body):
    pr = SESSION.require()
    idx = [int(x) for x in (body or {}).get('indices', [])]
    pr.remove_indices(idx)
    return {'stats': pr.stats()}


def api_names_move(body):
    pr = SESSION.require()
    i = int((body or {}).get('index', -1))
    d = int((body or {}).get('delta', 0))
    ok = pr.move_name(i, d)
    return {'moved': ok}


def api_names_sort(body):
    pr = SESSION.require()
    mode = (body or {}).get('mode') or pr.options.get('sort_mode')
    pr.options['sort_mode'] = mode
    pr.sort_names(mode)
    return {'stats': pr.stats()}


def api_names_dedup(_body):
    pr = SESSION.require()
    dup = pr.duplicate_indices()
    pr.remove_indices(dup)
    return {'removed': len(dup), 'stats': pr.stats()}


def api_names_import(body):
    pr = SESSION.require()
    replace = bool((body or {}).get('replace'))
    md = os.path.join(P.ROOT, '区域-tag-国名对照表.md')
    if not os.path.isfile(md):
        raise ValueError('找不到 区域-tag-国名对照表.md')
    added, skipped, missed = pr.import_md(md, replace=replace)
    if pr.options.get('auto_sort', True):
        pr.sort_names()
    return {'added': added, 'skipped': skipped, 'missed': missed,
            'stats': pr.stats()}


# -------------------------------------------------------------- 词缀

def _slot_api(body, fn):
    pr = SESSION.require()
    b = body or {}
    kind = b.get('kind') or 'P'
    return fn(pr, kind, b)


def api_slots_add(body):
    def fn(pr, kind, b):
        ok, err = pr.add_slot(kind, b.get('text', ''))
        if not ok:
            raise ValueError(err)
        return {'stats': pr.stats()}
    return _slot_api(body, fn)


def api_slots_update(body):
    def fn(pr, kind, b):
        ok, err = pr.update_slot(kind, int(b.get('index', -1)), b.get('text', ''))
        if not ok:
            raise ValueError(err)
        return {'stats': pr.stats()}
    return _slot_api(body, fn)


def api_slots_delete(body):
    def fn(pr, kind, b):
        pr.remove_slot_indices(kind, [int(x) for x in b.get('indices', [])])
        return {'stats': pr.stats()}
    return _slot_api(body, fn)


def api_slots_move(body):
    def fn(pr, kind, b):
        ok = pr.move_slot(kind, int(b.get('index', -1)), int(b.get('delta', 0)))
        return {'moved': ok}
    return _slot_api(body, fn)


def api_slots_sort(body):
    def fn(pr, kind, b):
        pr.sort_slot(kind)
        return {'stats': pr.stats()}
    return _slot_api(body, fn)


# -------------------------------------------------------------- 区域

def api_regions_add(body):
    pr = SESSION.require()
    b = body or {}
    rid = (b.get('id') or '').strip().upper()
    ok, err = pr.add_region(rid, (b.get('name') or '').strip())
    if not ok:
        raise ValueError(err)
    return {'stats': pr.stats()}


def api_regions_rename(body):
    pr = SESSION.require()
    b = body or {}
    if not pr.rename_region(b.get('id'), (b.get('name') or '').strip()):
        raise ValueError('区域不存在')
    return {'stats': pr.stats()}


def api_regions_delete(body):
    pr = SESSION.require()
    n = pr.remove_region((body or {}).get('id'))
    return {'removed': n, 'stats': pr.stats()}


def api_regions_move(body):
    pr = SESSION.require()
    b = body or {}
    ok = pr.move_region(b.get('id'), int(b.get('delta', 0)))
    return {'moved': ok}


# -------------------------------------------------------------- 生成

def api_build(body):
    pr = SESSION.require()
    bad = pr.validate()
    if bad:
        return {'ok': False, 'error': '还不能生成：\n· ' + '\n· '.join(bad)}
    outdir = (body or {}).get('outdir') or pr.options.get('output_dir')
    lines = []

    def log(s):
        lines.append(s)

    t0 = time.time()
    st = builder.build(pr, outdir=outdir, log=log)
    st['seconds'] = round(time.time() - t0, 1)
    st['log'] = lines
    SESSION.settings['last_project'] = pr.path or ''
    save_settings(SESSION.settings)
    return {'stats': st, 'project_stats': pr.stats()}


# -------------------------------------------------------------- 其它

def api_settings(body):
    """改界面偏好。允许任意键，返回当前生效的那几个。"""
    for k, v in (body or {}).items():
        SESSION.settings[k] = v
    save_settings(SESSION.settings)
    return {'settings': public_settings()}


def public_settings():
    """给前端的那份设置白名单 —— 别把 recent 之类的全都塞过去。"""
    s = SESSION.settings
    return {'theme': s.get('theme', 'light'),
            'follow': bool(s.get('follow', True)),
            'last_region': s.get('last_region', '')}


def api_open_folder(body):
    path = (body or {}).get('path') or ''
    if not path:
        pr = SESSION.require()
        path = pr.options.get('output_dir') or ''
    if not path:
        raise ValueError('路径为空')
    path = P.resolve_output_dir(path)
    if not os.path.isdir(path):
        os.makedirs(path)
    if os.name == 'nt':
        os.startfile(path)                       # noqa: S606 本机用户主动打开
    else:
        subprocess.Popen(['xdg-open', path])
    return {'path': path}


def api_pick(body):
    """弹一个 Windows 原生对话框（资源管理器那套），返回选中的路径。

    kind: 'open' 选工程文件 | 'save' 另存为 | 'folder' 选输出目录
    返回 ``path=''`` = 用户取消（不是错误，前端别报错）。

    为什么由后端弹而不是走 pywebview 的 ``create_file_dialog``：
    那个不做线程编组，而我们这儿是 HTTP 工作线程在调用，跨线程调 WinForms
    会炸。直接 COM 调 ``IFileDialog``（见 winapi）就没有线程亲和性要求，
    浏览器模式下（根本没有原生窗口）照样能弹。
    """
    b = body or {}
    kind = b.get('kind') or 'open'
    start = b.get('start') or ''
    title = b.get('title') or ''
    # 起始目录可能是工程里存的相对形式（'生成的mod'），对话框只认绝对路径
    if start and not os.path.isabs(start):
        start = P.resolve_output_dir(start)

    # 父窗给主窗口，对话框才会模态地压在它上面。
    hwnd = 0
    try:
        from web import window as W
        if W.CURRENT is not None:
            hwnd = W.CURRENT.hwnd() or 0
    except Exception:
        pass

    import winapi
    if kind == 'folder':
        path = winapi.pick_folder(title or '选择输出目录', start, hwnd)
    elif kind == 'save':
        path = winapi.pick_save_file(title or '另存为工程', start,
                                     b.get('name') or '', hwnd=hwnd)
    else:
        path = winapi.pick_open_file(title or '打开工程', start, hwnd=hwnd)
    return {'path': path or '', 'ok': bool(path),
            'native': winapi.dialogs_supported()}


def api_shutdown(_body):
    """退出。原生窗口模式下先关窗（QUIT_HOOK），再关服务。

    顺序不能反：先 shutdown 的话界面上那个「已退出」提示还没渲染完，
    WebView2 就取不到内容了。
    """
    global QUIT_HOOK
    hook, QUIT_HOOK = QUIT_HOOK, None
    if hook is not None:
        threading.Timer(0.8, hook).start()
    threading.Timer(1.2, stop_server).start()
    return {'bye': True}


ROUTES = {
    ('GET', '/api/state'): api_state,
    ('POST', '/api/project/save'): api_save,
    ('POST', '/api/project/open'): api_open,
    ('POST', '/api/project/new'): api_new,
    ('POST', '/api/project/reset-paths'): api_reset_paths,
    ('POST', '/api/project/options'): api_options,
    ('POST', '/api/project/meta'): api_meta,
    ('POST', '/api/names/add'): api_names_add,
    ('POST', '/api/names/update'): api_names_update,
    ('POST', '/api/names/delete'): api_names_delete,
    ('POST', '/api/names/move'): api_names_move,
    ('POST', '/api/names/sort'): api_names_sort,
    ('POST', '/api/names/dedup'): api_names_dedup,
    ('POST', '/api/names/import'): api_names_import,
    ('POST', '/api/slots/add'): api_slots_add,
    ('POST', '/api/slots/update'): api_slots_update,
    ('POST', '/api/slots/delete'): api_slots_delete,
    ('POST', '/api/slots/move'): api_slots_move,
    ('POST', '/api/slots/sort'): api_slots_sort,
    ('POST', '/api/regions/add'): api_regions_add,
    ('POST', '/api/regions/rename'): api_regions_rename,
    ('POST', '/api/regions/delete'): api_regions_delete,
    ('POST', '/api/regions/move'): api_regions_move,
    ('POST', '/api/build'): api_build,
    ('POST', '/api/settings'): api_settings,
    ('POST', '/api/pick'): api_pick,
    ('POST', '/api/open-folder'): api_open_folder,
    ('POST', '/api/shutdown'): api_shutdown,
}


# ------------------------------------------------------------------ HTTP

class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, fmt, *args):
        pass                      # 别把每条请求打进控制台

    # ---------------------------------------------------------- 分发

    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError):
            pass

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def _file(self, rel):
        rel = rel.strip('/') or 'index.html'
        rel = rel.replace('..', '')               # 别让它爬出 static
        path = os.path.join(STATIC, rel)
        if not os.path.isfile(path):
            path = os.path.join(STATIC, 'index.html')
        ext = os.path.splitext(path)[1].lower()
        with open(path, 'rb') as f:
            data = f.read()
        self._send(200, data, MIME.get(ext, 'application/octet-stream'))

    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith('/api/'):
            fn = ROUTES.get(('GET', path))
            if fn is None:
                return self._json({'ok': False, 'error': '没有这个接口'}, 404)
            return self._dispatch(fn, {})
        self._file(path)

    def do_POST(self):
        path = urlparse(self.path).path
        fn = ROUTES.get(('POST', path))
        if fn is None:
            return self._json({'ok': False, 'error': '没有这个接口'}, 404)
        n = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(n) if n else b'{}'
        try:
            body = json.loads(raw.decode('utf-8'))
        except Exception:
            body = {}
        self._dispatch(fn, body)

    def _dispatch(self, fn, body):
        try:
            out = fn(body) or {}
            if 'ok' not in out:
                out['ok'] = True
            self._json(out)
        except ValueError as ex:
            self._json({'ok': False, 'error': str(ex)})
        except Exception as ex:
            self._json({'ok': False, 'error': '%s: %s' % (type(ex).__name__, ex)})


# ------------------------------------------------------------------ 启动

SERVER = None
SERVER_THREAD = None
QUIT_HOOK = None      # 原生窗口模式下由 window.py 挂上：点了「退出」就关窗


def pick_port(start=8765, tries=60):
    for p in range(start, start + tries):
        s = socket.socket()
        try:
            s.bind(('127.0.0.1', p))
            return p
        except OSError:
            continue
        finally:
            s.close()
    return 0


def start_server(port=0):
    """起服务，**不阻塞**（服务跑在后台线程）。返回 (port, url)。

    原生窗口模式要用：pywebview 的 start() 自己会占住主线程，
    服务不能再阻塞在这里。幂等：已经起过就直接返回原来那个（截图脚本
    和自检都靠这个先起服务、再单独开窗口）。
    """
    global SERVER, SERVER_THREAD
    if SERVER is not None:
        return SERVER.server_address[1], 'http://127.0.0.1:%d/' \
            % SERVER.server_address[1]
    SESSION.boot()
    port = port or pick_port()
    if not port:
        raise RuntimeError('找不到空闲端口')
    SERVER = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    SERVER_THREAD = threading.Thread(target=SERVER.serve_forever,
                                     name='hz-http', daemon=True)
    SERVER_THREAD.start()
    return port, 'http://127.0.0.1:%d/' % port


def stop_server():
    """关服务。重复调用无害。"""
    global SERVER, SERVER_THREAD
    s, t = SERVER, SERVER_THREAD
    SERVER, SERVER_THREAD = None, None
    if s is None:
        return
    try:
        s.shutdown()          # 让 serve_forever() 返回
    except Exception:
        pass
    try:
        s.server_close()
    except Exception:
        pass
    if t is not None:
        t.join(timeout=3)


def serve(port=0, open_browser=True, quiet=False):
    """起服务并阻塞（浏览器模式）。返回 (port, url)。"""
    port, url = start_server(port)
    if not quiet:
        print('自定义国名生成器 · 网页引擎')
        print('  ' + url)
        print('  关闭这个窗口即退出。')
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        # 服务在后台线程跑，这里只是等它结束（被 shutdown 唤醒或 Ctrl-C）
        while SERVER_THREAD is not None and SERVER_THREAD.is_alive():
            SERVER_THREAD.join(0.4)
    except KeyboardInterrupt:
        pass
    finally:
        stop_server()
    return port, url


if __name__ == '__main__':
    serve()
