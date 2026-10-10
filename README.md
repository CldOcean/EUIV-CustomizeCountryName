# 组词自定义国名工具

给「组合造词国名」模组用的生成器。改字库、选区域、排顺序、导出模组，
全程点鼠标，不用改 Python。

**用户手册**：
[docs/用户手册.html](docs/用户手册.html)（**打开这个**，单文件、离线可看、带目录和深浅主题）
｜ [docs/用户手册.md](docs/用户手册.md)（源文件）
本文讲开发与打包。

## 发布须知（给别人用之前先记住）

- **不支持铁人模式**：选国名靠一大批事件实现，**加事件会改校验码**，铁人存档校验
  不过、拿不到成就。这一条要在发布页显眼处写出来。
- **联机必须双方同一套**：EU4 联机有校验码，模组内容必须逐字节一致。正确做法是
  把 `.hznproj` **工程文件**给对方，让他用本工具**重新生成一次**（走一遍生成器
  才保证产物相同）。
- 授权口径：开源、**勿商用**；仅供交流学习，切勿上升现实。
- 用户若不知道「模组文件夹」在哪：P 社启动器 → 该 mod → 三个点 →「在文件夹中显示」。

**只有一套界面**：网页引擎，装在一个独立的桌面窗口里。

## 启动

双击 exe 就行，**不需要装 Python**：

```
组词自定义国名工具.exe
```

不是开浏览器标签页 —— 它是一个正经的桌面窗口（pywebview + Edge WebView2），
没有地址栏、没有标签页，任务栏上是自己的条目，观感跟 missiontree 那类工具一致。

> ⚠️ **exe 是源码的冻结快照**：你改了任何 `.py` / `.html` / `.css` / `.js` 之后，
> 要么重跑 `build_exe.py` 重新打包，要么用命令行跑源码。
> 平时你爱自己动手改文件，这条最容易忘。

源码模式：

```bash
# 原生窗口（默认）
"C:/Users/CldOcean/AppData/Local/Programs/Python/Python314/python.exe" main.py

# 退回系统默认浏览器（调试前端时方便按 F12）
"C:/Users/CldOcean/AppData/Local/Programs/Python/Python314/python.exe" main.py --browser
```

> 要用**系统 Python 3.14**（上面那个路径）。托管版 Python 3.13 编译时没带
> tkinter，跑不了 tkinter 那类东西 —— 本工具虽然不再依赖 tkinter，
> 但 pypinyin 是装在系统版里的，换解释器就找不到了。
> 依赖：`pywebview`（原生窗口）、`pypinyin`（按拼音排序）。
> 没装 pypinyin 的话国名会退回 Unicode 码点序，界面左下角会提示。

机器上没有 pywebview 或 WebView2 时，会自动降级到浏览器打开，不会白屏。

### 历史：为什么没有「经典界面」了

以前有两套界面（tkinter 原生窗口 + 网页引擎），可以在界面里一键互切。
现在**只维护网页版**：tkinter 那套（`app.py` / `theme.py` / `widgets.py`）
没有复制过来，`/api/engine/switch` 接口和页面上的切换按钮也都删了。
两份代码做同一件事只会互相拖后腿。

## 网页引擎的几个点

- 只监听 `127.0.0.1`，不对外；端口从 8765 起自动找空的。
- 退出：窗口右上角 ×，或页面顶栏〔退出〕。
- 深浅主题切换会**连窗口标题栏一起变** —— 页面通过 `window.pywebview.api`
  通知 Python，Python 再用 DWM 改原生标题栏（`web/window.py` + `winapi.py`）。
- 窗口大小会记住（存 `settings.json` 的 `web_geometry`）。
- 界面偏好也存 `settings.json`：`theme` / `follow` / `last_region`。
- **路径一律「相对工具目录」**：工程文件放 `工程文件/`，默认输出目录写
  `DEFAULT_OUTPUT_REL = '生成的mod'`（相对形式，不是绝对路径）。
  换机器 / 换盘符 / 改目录名都不会失效 —— 实际使用时由
  `project.resolve_output_dir()` 换算成本机绝对路径，
  `rel_output_dir()` 负责写回时压成相对形式（只在位于工具目录内时）。
  🩸 别用裸 `os.path.abspath()` 解析：它按 **CWD** 算，双击 exe 启动时
  CWD 可能是任意地方，生成的东西就飞了。
- **〔重置路径〕= `/api/project/reset-paths`**：工程是从别人那儿拿来的时，
  输出目录里还写着人家机器的绝对路径（换个盘符就没有那个盘）。
  这个接口把它拉回本机工具目录下的 `生成的mod`，前端在「打开工程」左边。
- **文件 / 文件夹对话框走 `/api/pick`**，由后端用 ctypes 直接 CoCreate Windows 的
  `IFileDialog`（`winapi.py`）—— 就是资源管理器那套现代表单。
  🩸 别换成 pywebview 的 `create_file_dialog`：它**不做线程编组**，
  而我们的 API 都跑在 HTTP 工作线程上，跨线程调 WinForms 控件会炸；
  自己调 COM 没有线程亲和性问题，浏览器模式（无原生窗口）也能弹。
  弹不出来时 `/api/pick` 返回 `path=''`，前端（`app.js` 的 `pickPath()`）
  会退回手填路径的弹窗，不会卡死。

## 界面速览

### 国名页

| 操作 | 怎么做 |
|---|---|
| 搜索 | 左上角搜索框，匹配国名 / TAG / 备注 |
| 筛选 | 区域下拉选「全部区域」之外的任意一项 |
| 添加 | 页签右上角〔添加国名〕——光标直接落在国名输入框上，区域已经替你选好了 |
| 编辑 | **双击任意一行**，或选中一行点〔编辑〕 |
| 多选 | 单击选中，Shift + 单击连选，行首复选框逐个勾 |
| 删除 | 〔删除〕删勾选的，〔批量删除〕可按「当前筛选 / 区域内重名 / 全部」删 |
| 排序 / 移动 | 右上角排序下拉；〔↑〕〔↓〕单条挪位 |
| 导入 | 〔导入字库〕从「区域-tag-国名对照表.md」灌进去，已存在的跳过 |

**自动定位**（工具栏上的开关，默认开）：

开的时候，每加完一个国名会自动翻到那一行所在的页、选中它，并蓝闪一下
（1.8 秒褪掉）。如果当前的搜索词 / 区域筛选正好把新行挡住了，会顺手把
筛选清掉 —— 否则翻过去也是看不见。关了就安静地加，光标不动。

开关的状态记在 `settings.json` 的 `follow` 里，关掉程序再开还是上次那个值。

**记住上次选的区域**：

上次添加国名时选的区域就是下次打开弹窗的默认区域（`settings.json` 的
`last_region`）。连续往同一个区域里塞名字是常态，每次都跳回列表第一项很烦。
那个区域要是不存在了（比如被删了），自动退回第一个。

这两个背后共用一个锚点：每个国名条目有个稳定唯一的自增号 `seq`，
列表下标会因为排序 / 增删挪位，`seq` 不会。所以「跳到刚添加的那一行」
按 `seq` 找，而不是按下标找。

### 其它页签

| 页签 | 能做什么 |
|---|---|
| **前缀** | 增 / 查 / 改（双击行也行）、删除、上移下移、按拼音排序；右边「示例」列显示「前缀＋第一个国名」 |
| **后缀** | 同上 |
| **区域** | 增 / 改 / 删、上移下移。**顺序 = 游戏里「选择区域」的弹出顺序** |
| **生成** | 模组名 / 命名空间 / 输出目录 / 每页选项数、规模预览、生成按钮、日志 |

## 打包成 exe

```bash
.buildenv\Scripts\python.exe build_exe.py
```

产出 `组词自定义国名工具.exe`，放在本目录 —— **必须待在这儿**：
打包后的路径基准是 exe 所在目录（见 `paths.py`），它要靠这个找到
`工程文件/` 和 `settings.json`。

首次要建打包环境：

```bash
<系统python> -m venv .buildenv --system-site-packages
.buildenv\Scripts\python.exe -m pip install pywebview pyinstaller pillow
```

（`--system-site-packages` 是为了沿用系统里已装的 pypinyin；
`pillow` 只用来画图标。）

## 目录

```
tools/组词自定义国名工具/
├─ 组词自定义国名工具.exe        ← 双击这个
├─ 使用说明.txt                 ← 给玩家的发放入口（四步上手 + 三条 FAQ）
├─ main.py                     入口
├─ paths.py                    路径基准（打包后 __file__ 是临时目录，全靠它）
├─ winapi.py                   DWM 深色标题栏 + 按标题找窗口
├─ web/
│  ├─ server.py                后端：本机 HTTP + JSON API
│  ├─ window.py                把页面装进原生窗口（pywebview + WebView2）
│  └─ static/                  前端（index.html / app.css / app.js，无构建步骤）
├─ project.py                  工程文件模型 —— 专用格式 .hznproj
├─ builder.py                  把工程翻译成 gen_namebuilder 的入参并落盘
├─ build_exe.py                打包 exe
├─ check_web.py                自检：HTTP + 前端（72 项）
├─ check_window.py             自检：真开一个桌面窗口（11 项）
├─ check_bundle.py             自检：exe 里那三个前端文件跟源码逐字节一致
├─ check_web_ui.js             前端运行时自检（jsdom，被 check_web.py 调用）
├─ shots.py                    手册截图：真开窗口按脚本摆姿势逐张存盘
├─ md2html.py                  手册 md → 单文件 HTML（自带目录 / 主题切换）
├─ docs/
│  ├─ 用户手册.md              ← 给使用者看的，引用下面这套截图
│  ├─ 用户手册.html            md2html.py 产出，打开就能看
│  └─ shots/                   手册截图（shots.py 产出，10 张）
├─ settings.json               界面偏好（别手改，界面上有开关）
├─ 工程文件/                    ← 工程文件（.hznproj）都放这儿
└─ 生成的mod/                   ← 生成的模组文件都放这儿
```

`.buildenv/` 是打包用的虚拟环境，`_build/` 是打包中间产物，都可以删，
删了重跑 `build_exe.py` 会自己重建。

## 工程文件（.hznproj）

UTF-8 的 JSON，缩进 2 空格，能手工改、能进 git。

```json
{
  "format": "hz-namebuilder-project",
  "version": 1,
  "meta":    { "name": "原版字库", "author": "", "created": "...", "modified": "..." },
  "options": { "page_size": 28, "namespace": "hz_nb", "mod_name": "自定义国名",
               "output_dir": "...", "sort_mode": "region_pinyin", "auto_sort": true },
  "regions": [ { "id": "ZH", "name": "中华区域" }, ... ],
  "prefixes": ["大", "中", "东", "西", "南", "北", "新", "圣"],
  "suffixes": ["国", "帝国", "王国", "王朝", "联邦", "汗国", "公国", "共和国"],
  "names":   [ { "name": "中华", "region": "ZH", "tag": "CHI", "note": "", "seq": 1 }, ... ]
}
```

`names` 里的 `seq` 是**添加顺序**，列表的下标是**当前顺序**。
排序只动下标、不动 `seq`，所以「按添加顺序还原」随时可用。

区域标识（`id`）只能是大写字母 / 数字 / 下划线 —— 它会写进事件 id 与本地化 key，
建好后界面上不让改。

## 生成

点〔生成模组〕，产物直接写进你指定的输出目录（默认 `生成的mod/`）：

- 生成前会按「生成选项」里的方式自动排序（可关）。
- 会**删掉输出目录里所有上一版生成的 `hz_*` 文件** —— 残留文件会让事件 id 撞车。
  所以输出目录里别放自己的东西。
- 生成完把这个目录挂到 playset 里，**彻底重开游戏**才生效。
- 页面数会自动跟着「每页选项数」变，别的都不用改。

规模参考（970 国名 / 8 前缀 / 8 后缀）：**78,570 种组合、46 个事件、218 个文件、约 25 MB**。
加国名不增事件（每区域只按页数增），是边际成本最低的操作。

## 自检

```bash
"C:/Users/CldOcean/AppData/Local/Programs/Python/Python314/python.exe" check_web.py
"C:/Users/CldOcean/AppData/Local/Programs/Python/Python314/python.exe" check_window.py
```

`check_web.py` 起一个临时服务（随机端口），把全部 API 打一遍再关掉，
并在一个**全新的临时目录**里端到端生成一次，断言 **218 个文件 / 78,570 组合**。
基准口径锁死 `970 / 78570 / 46`，且一律**用现造的干净种子断言，不用界面里的
活工程** —— 用户在界面上多排一次序就能让这类断言假红。
最后用 jsdom 真跑一遍 `app.js`（`check_web_ui.js`），
抓「语法没错但一运行就炸」那类错误；没装 jsdom 会自动跳过。

> 生成那一节特意排在**最后**，而且用 `tempfile.mkdtemp` 每次换新的输出目录：
> 一口气落 218 个文件再删掉，容易被外部保护当成危险操作把进程掐了，
> 那一掐会把后面所有用例一起带走。

`check_window.py` 真的开一个桌面窗口出来：拿句柄、在窗口里跑 JS 数表格行数、
验 JS 桥、确认自动定位按钮在且状态跟设置一致，关窗后确认服务退干净。
**pywebview 必须跑在主线程**，所以关窗是靠后台线程调 `QUIT_HOOK`，不能反过来。

`check_bundle.py` 直接把 exe 里的 `web\static\*` 从 PyInstaller 归档里解出来，
跟源码**逐字节比对** —— 专门对付「改了源码忘了重新打包」这件事
（exe 是源码的冻结快照，双击起来看到的是旧界面，而且不会报错提示你）。

```bash
.buildenv\Scripts\python.exe check_bundle.py
```

（它要用打包环境里的 PyInstaller 读归档，所以得在 `.buildenv` 下跑。）

## 与命令行版的关系

生成逻辑**只有一份**：`tools/gen_namebuilder.py`（它已过 `check_mod.py` 校验）。
本工具只是换字库 + 换输出目录（`gen_namebuilder.reconfigure()` / `generate()`），
没有重复实现。实测两者产物 **218 个文件逐字节一致**。

命令行版仍然可用：

```bash
python tools/gen_namebuilder.py     # 按 tools/region_names.py 读到的字库生成到模组目录
python check_mod.py                 # 9 节自检
```
