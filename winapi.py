# -*- coding: utf-8 -*-
r"""Windows 原生窗口的小工具（只依赖 ctypes，不碰 tkinter）。

标题栏是系统画的，ttk / WebView2 都管不到 —— 深色主题下那条白杠只能靠
DWM API 单独处理（这一段网页原生窗口要用）。

后半段是**通用对话框**（打开文件 / 另存为 / 选文件夹）：直接 CoCreate
Windows 的 ``IFileDialog``，也就是资源管理器用的那一套现代对话框。
为什么不走 pywebview 的 ``create_file_dialog``：它**不做线程编组**，
而我们的 API 请求都跑在 HTTP 工作线程里，从那儿调 WinForms 控件会跨线程炸；
自己调 COM 就没有这个亲和性问题，浏览器模式（没有原生窗口）也能用。
"""

import ctypes
import os


def supported():
    return os.name == 'nt'


def dialogs_supported():
    """这台机器能用原生对话框吗（非 Windows 一律不行，前端据此退回手填）。"""
    return supported()


def set_titlebar_dark(hwnd, dark=True):
    """给一个 HWND 的标题栏上深色（或还原成浅色）。成功返回 True。

    DWMWA_USE_IMMERSIVE_DARK_MODE：Win11 用 20，Win10 20H1 之前用 19，
    两个都试一遍，不支持的属性会返回非 0，忽略即可。

    **必须在窗口 mapped 之后调用** —— 之前拿不到真正的 HWND，设置了也白设。
    """
    if not supported():
        return False
    try:
        hwnd = int(hwnd)
    except Exception:
        return False
    if not hwnd:
        return False

    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return False

    try:
        dwm = ctypes.windll.dwmapi
        dsa = dwm.DwmSetWindowAttribute
        dsa.argtypes = [wintypes.HWND, wintypes.DWORD,
                        ctypes.c_void_p, wintypes.DWORD]
        dsa.restype = ctypes.c_long                  # HRESULT
        get_parent = ctypes.windll.user32.GetParent
        get_parent.argtypes = [wintypes.HWND]
        get_parent.restype = wintypes.HWND
    except Exception:
        return False

    value = ctypes.c_int(1 if dark else 0)
    ok = False
    # 有时拿到的是内部容器句柄，试完自己再试它的父窗
    for h in (hwnd, int(get_parent(wintypes.HWND(hwnd)) or 0)):
        if not h:
            continue
        for attr in (20, 19):
            try:
                if dsa(wintypes.HWND(h), attr,
                       ctypes.byref(value), ctypes.sizeof(value)) == 0:
                    ok = True
            except Exception:
                pass
    if ok:
        # Win11 顺手把方角掰圆（2 = DWMWCP_ROUND）
        try:
            corner = ctypes.c_int(2)
            dsa(wintypes.HWND(hwnd), 33, ctypes.byref(corner),
                ctypes.sizeof(corner))
        except Exception:
            pass
    return ok


def find_windows(title, contains=True):
    """按标题找**所有**可见的顶层窗口，返回 HWND 列表（找不到给空列表）。

    pywebview 用的是 WinForms，窗口类名长得随机
    （WindowsForms10.Window.8.app.0...），靠类名不可靠；按标题找反而稳。

    返回列表而不是单个：同标题的窗口可能不止一个 —— 上一轮自检的窗口
    没关干净、或者用户自己又开了一个，都会让「找第一个」找错人。
    调用方想断言「我的窗口在不在其中」就得拿全表。
    """
    if not supported():
        return []
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return []

    found = []

    try:
        enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND,
                                       wintypes.LPARAM)

        def _cb(hwnd, _lparam):
            try:
                n = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if n:
                    buf = ctypes.create_unicode_buffer(n + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buf, n + 1)
                    t = buf.value
                    hit = (title in t) if contains else (t == title)
                    if hit and ctypes.windll.user32.IsWindowVisible(hwnd):
                        found.append(int(hwnd))
            except Exception:
                pass
            return True

        ctypes.windll.user32.EnumWindows(enum_proc(_cb), 0)
    except Exception:
        return []
    return found


def find_window(title, contains=True):
    """按标题找可见的顶层窗口，返回第一个 HWND（找不到给 0）。"""
    hits = find_windows(title, contains)
    return hits[0] if hits else 0


# ------------------------------------------------------------------ 通用对话框
# IFileDialog（Vista+ 那套资源管理器对话框）。COM 接口没有头文件和
# 类型库可引用，只能按 vtable 顺序手写下标注 —— 下标写错就是静默跑飞，
# 所以下面每个下标都注明是哪个方法。

_CLSID_FILE_OPEN = '{DC1C5A9C-E88A-4dde-A5A1-60F82A20AEF7}'
_CLSID_FILE_SAVE = '{C0B4E2F3-BA21-4773-8DBA-335EC946EB8B}'
_IID_FILE_DIALOG = '{42f85136-db7e-439c-85f1-e4075d135fc8}'
_IID_FILE_SAVE_DIALOG = '{84bccd23-5fde-4cdb-aea4-af64b83d78ab}'
_IID_SHELL_ITEM = '{43826d1e-e718-42ee-bc55-a1e261c37bfe}'

_SIGDN_FILESYSPATH = 0x80058000       # 要「能直接拿去用的文件系统路径」
_CANCELLED = -2147023673              # HRESULT_FROM_WIN32(ERROR_CANCELLED)

# FOS_* 选项位
_PICK_FOLDERS = 0x20
_FORCE_FILESYSTEM = 0x40
_PATH_MUST_EXIST = 0x800
_FILE_MUST_EXIST = 0x1000
_OVERWRITE_PROMPT = 0x2


class GUID(ctypes.Structure):
    _fields_ = [('Data1', ctypes.c_ulong), ('Data2', ctypes.c_ushort),
                ('Data3', ctypes.c_ushort), ('Data4', ctypes.c_ubyte * 8)]


class FILTERSPEC(ctypes.Structure):
    _fields_ = [('name', ctypes.c_wchar_p), ('spec', ctypes.c_wchar_p)]


def _guid(s):
    g = GUID()
    ctypes.windll.ole32.IIDFromString(s, ctypes.byref(g))
    return g


def _vcall(obj, idx, argtypes, args, restype=ctypes.c_long):
    """按 vtable 下标调一个 COM 方法（都是 stdcall，第一个参数是 this）。"""
    vt = ctypes.cast(obj, ctypes.POINTER(ctypes.c_void_p)).contents
    tbl = ctypes.cast(vt, ctypes.POINTER(ctypes.c_void_p))
    fn = ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, *argtypes)(tbl[idx])
    return fn(obj, *args)


def _release(obj):
    try:
        _vcall(obj, 2, [], [])          # IUnknown::Release
    except Exception:
        pass


def _set_start_folder(dlg, path):
    """让对话框一开就落在指定目录（不给就是系统记住的上次位置）。"""
    if not path or not os.path.isdir(path):
        return
    item = ctypes.c_void_p()
    iid = _guid(_IID_SHELL_ITEM)
    hr = ctypes.windll.shell32.SHCreateItemFromParsingName(
        path, None, ctypes.byref(iid), ctypes.byref(item))
    if hr != 0 or not item:
        return
    try:
        _vcall(dlg, 12, [ctypes.c_void_p], [item])       # IFileDialog::SetFolder
    finally:
        _release(item)


def _result_path(dlg):
    """Show 返回 OK 之后取结果路径。"""
    item = ctypes.c_void_p()
    hr = _vcall(dlg, 20, [ctypes.POINTER(ctypes.c_void_p)], [ctypes.byref(item)])
    if hr != 0 or not item:
        return ''
    out = ''
    try:
        name = ctypes.c_wchar_p()
        hr = _vcall(item, 5,                             # IShellItem::GetDisplayName
                    [ctypes.c_uint, ctypes.POINTER(ctypes.c_wchar_p)],
                    [_SIGDN_FILESYSPATH, ctypes.byref(name)])
        if hr == 0 and name.value:
            out = name.value
            ctypes.windll.ole32.CoTaskMemFree(ctypes.cast(name, ctypes.c_void_p))
    except Exception:
        pass
    finally:
        _release(item)
    return out


def _dialog(kind, title='', start='', name='', types=(), ext='', hwnd=0):
    """弹一个通用对话框，返回选中的路径；取消 / 失败返回 ''。

    kind: 'open' 选已有文件 | 'save' 另存为 | 'folder' 选文件夹
    """
    if not supported():
        return ''
    ole = ctypes.windll.ole32
    # 对话框要求调用线程有 COM 且是 STA；HTTP 工作线程默认没有，自己起一个。
    # 已经起过（S_FALSE）或模式不合（RPC_E_CHANGED_MODE）就别再 CoUninitialize。
    hr_init = ole.CoInitializeEx(None, 0x2)              # COINIT_APARTMENTTHREADED
    uninit = hr_init in (0, 1)

    dlg = ctypes.c_void_p()
    try:
        clsid = _guid(_CLSID_FILE_SAVE if kind == 'save' else _CLSID_FILE_OPEN)
        iid = _guid(_IID_FILE_SAVE_DIALOG if kind == 'save' else _IID_FILE_DIALOG)
        hr = ole.CoCreateInstance(ctypes.byref(clsid), None, 1,
                                  ctypes.byref(iid), ctypes.byref(dlg))
        if hr != 0 or not dlg:
            return ''
        try:
            if title:
                _vcall(dlg, 17, [ctypes.c_wchar_p], [title])      # SetTitle
            _set_start_folder(dlg, start)

            if kind == 'folder':
                _vcall(dlg, 9, [ctypes.c_uint],                   # SetOptions
                       [_PICK_FOLDERS | _FORCE_FILESYSTEM | _PATH_MUST_EXIST])
                _vcall(dlg, 18, [ctypes.c_wchar_p], ['选择此文件夹'])
            else:
                opts = _FORCE_FILESYSTEM | _PATH_MUST_EXIST
                opts |= _FILE_MUST_EXIST if kind == 'open' else _OVERWRITE_PROMPT
                _vcall(dlg, 9, [ctypes.c_uint], [opts])           # SetOptions
                if types:
                    arr = (FILTERSPEC * len(types))(
                        *[FILTERSPEC(n, s) for n, s in types])
                    _vcall(dlg, 4,                                # SetFileTypes
                           [ctypes.c_uint, ctypes.c_void_p],
                           [len(types), ctypes.cast(arr, ctypes.c_void_p)])
                    _vcall(dlg, 5, [ctypes.c_uint], [1])          # SetFileTypeIndex
                if kind == 'save':
                    if ext:
                        _vcall(dlg, 22, [ctypes.c_wchar_p], [ext])
                    if name:
                        _vcall(dlg, 15, [ctypes.c_wchar_p], [name])

            # IModalWindow::Show —— 父窗给主窗口能让它模态（挡住主窗口）。
            # 万一跨线程挂父窗失败（hr 非 0 且不是「取消」），去掉父窗再试一次。
            # 整段包 try：弹不出来就当取消，绝不能把异常抛给 HTTP 请求。
            try:
                for owner in (int(hwnd or 0), 0):
                    hr = _vcall(dlg, 3, [ctypes.c_void_p],
                                [ctypes.c_void_p(owner)])
                    if hr == 0:
                        return _result_path(dlg)
                    if hr == _CANCELLED or owner == 0:
                        break
            except Exception:
                pass
            return ''
        finally:
            _release(dlg)
    finally:
        if uninit:
            try:
                ole.CoUninitialize()
            except Exception:
                pass


PROJ_TYPES = (('工程文件 (*.hznproj)', '*.hznproj'),)


def pick_open_file(title='打开工程', start='', types=PROJ_TYPES, hwnd=0):
    return _dialog('open', title, start, types=types, hwnd=hwnd)


def pick_save_file(title='另存为', start='', name='', ext='hznproj',
                   types=PROJ_TYPES, hwnd=0):
    return _dialog('save', title, start, name=name, types=types,
                   ext=ext, hwnd=hwnd)


def pick_folder(title='选择文件夹', start='', hwnd=0):
    return _dialog('folder', title, start, hwnd=hwnd)
