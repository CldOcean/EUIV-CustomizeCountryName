/* 自定义国名生成器 · 网页引擎
 * 纯原生 JS，没有构建步骤也没有外部依赖（离线可用）。
 * 所有写操作都走 /api/*，界面只负责呈现；工程模型与生成在 project.py /
 * builder.py 里（跟命令行版共用同一份），所以产物必然一致。
 */

'use strict';

const S = {
  st: null,            // /api/state 的完整返回
  view: 'names',
  names: { q: '', region: '', page: 1, size: 100, sel: new Set() },
  slots: { P: { q: '', sel: new Set() }, S: { q: '', sel: new Set() } },
  regions: { sel: null },
  building: false,
};

const $ = (s, r) => (r || document).querySelector(s);
const $$ = (s, r) => Array.prototype.slice.call((r || document).querySelectorAll(s));

function esc(t) {
  return String(t == null ? '' : t)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* ------------------------------------------------------------ 网络 */

async function api(path, body) {
  const opt = body === undefined ? {} : {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  };
  let j;
  try {
    const r = await fetch(path, opt);
    j = await r.json();
  } catch (e) {
    throw new Error('连不上本地服务：' + e.message);
  }
  if (!j.ok) throw new Error(j.error || '请求失败');
  return j;
}

async function run(fn, okMsg) {
  try {
    const out = await fn();
    if (okMsg) toast(okMsg, 'ok');
    return out;
  } catch (e) {
    toast(e.message, 'err');
    return null;
  }
}

/* ------------------------------------------------------------ 提示 */

function toast(msg, kind) {
  const el = document.createElement('div');
  el.className = 'toast' + (kind === 'err' ? ' is-err' : kind === 'ok' ? ' is-ok' : '');
  el.textContent = msg;
  $('#toasts').appendChild(el);
  setTimeout(() => {
    el.style.transition = 'opacity .25s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 260);
  }, kind === 'err' ? 4200 : 2000);
}

/* ------------------------------------------------------------ 弹窗 */

function modal(opts) {
  /* opts: {title, body(html), okText, danger, onOk(ctx) -> false 阻止关闭} */
  const root = $('#modalRoot');
  root.hidden = false;
  root.innerHTML =
    '<div class="modal">' +
      '<div class="modal-head">' + esc(opts.title) + '</div>' +
      '<div class="modal-body">' + (opts.body || '') + '</div>' +
      '<div class="modal-foot">' +
        '<button class="btn" data-x="cancel">取消</button>' +
        '<button class="btn ' + (opts.danger ? 'btn-danger' : 'btn-primary') +
          '" data-x="ok">' + esc(opts.okText || '确定') + '</button>' +
      '</div>' +
    '</div>';

  function close() { root.hidden = true; root.innerHTML = ''; }

  root.onclick = (e) => {
    if (e.target === root) return close();
    const x = e.target.getAttribute && e.target.getAttribute('data-x');
    if (x === 'cancel') return close();
    if (x === 'ok') {
      if (opts.onOk && opts.onOk(root) === false) return;
      close();
    }
  };
  root.onkeydown = (e) => {
    if (e.key === 'Escape') return close();
    if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
      const b = $('[data-x="ok"]', root);
      if (b) b.click();
    }
  };
  // opts.focus：想让光标落在哪个控件上（选择器字符串）。不传就找第一个输入框。
  // 「添加国名」传 #fName —— 区域已经替你选好了，直接打字才是常态。
  const first = opts.focus
    ? $(opts.focus, root)
    : $('.modal-body input, .modal-body select', root);
  if (first) { first.focus(); if (first.select) first.select(); }
  if (opts.onOpen) opts.onOpen(root);
  return root;
}

function confirmBox(title, text, onYes, okText) {
  modal({
    title: title,
    body: '<div style="white-space:pre-wrap">' + esc(text) + '</div>',
    okText: okText || '确定',
    danger: true,
    onOk: onYes,
  });
}

/* ------------------------------------------------------------ 数据 */

async function refresh(keepSel) {
  const st = await api('/api/state');
  S.st = st;
  if (!keepSel) { S.names.sel.clear(); S.slots.P.sel.clear(); S.slots.S.sel.clear(); }
  renderAll();
}

function pr() { return S.st.project; }
function st() { return S.st.stats; }
function settings() { return (S.st && S.st.settings) || {}; }

/* ------------------------------------------------------------ 渲染 */

function renderAll() {
  renderHeader();
  renderNames();
  renderSlots('P');
  renderSlots('S');
  renderRegions();
  renderBuild();
  renderFollow();
}

function renderHeader() {
  const p = pr();
  $('#projName').textContent = p.name;
  $('#projPath').textContent = p.path || '（未保存）';
  $('#dirtyChip').classList.toggle('hidden', !p.dirty);
  $('#badgeNames').textContent = st().names;
  $('#badgePre').textContent = pr().prefixes.length;
  $('#badgeSuf').textContent = pr().suffixes.length;
  $('#badgeReg').textContent = st().regions;
  $('#msCombos').textContent = st().combos.toLocaleString();
  $('#msEvents').textContent = st().events;
  $('#msPages').textContent = st().pages;
  $('#msMax').textContent = st().max_options;
  $('#pinyinTip').textContent = S.st.pinyin_ok ? '' : '未装 pypinyin，排序退回码点序';
}

/* ---------------------------------------------------- 国名 */

function matchName(n, q) {
  const s = String(q || '').trim().toLowerCase();
  if (!s) return true;
  return (n.name || '').toLowerCase().includes(s)
      || (n.tag || '').toLowerCase().includes(s)
      || (n.note || '').toLowerCase().includes(s);
}

function filteredNames() {
  const p = pr(), f = S.names;
  const q = f.q;
  const out = [];
  for (let i = 0; i < p.names.length; i++) {
    const n = p.names[i];
    if (f.region && n.region !== f.region) continue;
    if (!matchName(n, q)) continue;
    out.push(i);
  }
  return out;
}

function renderNames() {
  const p = pr(), f = S.names;
  const idxs = filteredNames();

  // 区域下拉
  const sel = $('#fNameRegion');
  const cur = f.region;
  sel.innerHTML = '<option value="">全部区域</option>' +
    p.regions.map(r => '<option value="' + esc(r.id) + '">' +
      esc(r.name) + '</option>').join('');
  sel.value = cur;

  // 排序下拉
  const ss = $('#fNameSort');
  if (!ss.options.length) {
    ss.innerHTML = S.st.sort_modes.map(m =>
      '<option value="' + esc(m.id) + '" title="' + esc(m.tip) + '">' +
      esc(m.label) + '</option>').join('');
  }
  ss.value = p.options.sort_mode;

  // 分页
  const size = f.size;
  const pages = Math.max(1, Math.ceil(idxs.length / size));
  if (f.page > pages) f.page = pages;
  const from = (f.page - 1) * size;
  const slice = idxs.slice(from, from + size);

  const body = $('#bodyNames');
  body.innerHTML = slice.map(i => {
    const n = p.names[i];
    return '<tr data-i="' + i + '"' +
        (f.sel.has(i) ? ' class="is-sel"' : '') + (n.dup ? ' data-dup="1"' : '') + '>' +
      '<td class="col-check"><input type="checkbox" data-pick="' + i + '"' +
        (f.sel.has(i) ? ' checked' : '') + '></td>' +
      '<td class="col-idx">' + (i + 1) + '</td>' +
      '<td class="col-region">' + esc(n.region_name) + '</td>' +
      '<td class="col-name">' + esc(n.name) +
        (n.dup ? ' <span class="muted">（重名）</span>' : '') + '</td>' +
      '<td class="col-py">' + esc(n.pinyin) + '</td>' +
      '<td class="col-tag">' + (n.tag ? '<span class="mono">' + esc(n.tag) + '</span>' : '') + '</td>' +
      '<td class="col-note">' + esc(n.note) + '</td>' +
    '</tr>';
  }).join('');

  $$('#bodyNames tr[data-dup]').forEach(tr => tr.classList.add('is-dup'));

  $('#emptyNames').hidden = idxs.length > 0;
  updateNameCount();
  $('#pagerInfo').textContent = f.page + ' / ' + pages;
  syncNameSelection();
}

/* 选中态同步 —— 这儿有个必须绕开的坑：

   **单击一行时绝不要整表重绘**。两次点击之间如果把 <tr> 换掉，第一次点击的
   那个节点已经脱离 DOM，浏览器算 dblclick 的目标时会塌到 tbody 上，
   `closest('tr[data-i]')` 拿不到东西 —— 表现就是「双击某一行没反应」。
   所以这里只改 class 和 checkbox，行本身一个都不动。 */
function syncNameSelection() {
  const f = S.names;
  const rows = $$('#bodyNames tr[data-i]');
  rows.forEach(tr => {
    const i = +tr.dataset.i;
    const on = f.sel.has(i);
    tr.classList.toggle('is-sel', on);
    const cb = tr.querySelector('input[data-pick]');
    if (cb) cb.checked = on;
  });
  $('#chkAllNames').checked =
    rows.length > 0 && rows.every(tr => f.sel.has(+tr.dataset.i));
  updateNameCount();
}

function updateNameCount() {
  const p = pr(), f = S.names;
  $('#nameCount').textContent =
    '显示 ' + filteredNames().length + ' / ' + p.names.length + ' 条' +
    (f.sel.size ? ' · 已选 ' + f.sel.size + ' 条' : '') +
    (st().dups ? ' · 区域内重名 ' + st().dups + ' 条' : '');
}

function syncSlotSelection(kind) {
  const f = S.slots[kind];
  $$('#body' + kind + ' tr[data-i]').forEach(tr =>
    tr.classList.toggle('is-sel', f.sel.has(+tr.dataset.i)));
}

function syncRegionSelection() {
  $$('#bodyRegions tr[data-id]').forEach(tr =>
    tr.classList.toggle('is-sel', tr.dataset.id === S.regions.sel));
}

/* ---------------------------------------------------- 自动定位 + 高亮 */

/* 「自动定位」开关：开了之后每次添加国名，自动翻到那一行所在页、
   选中它，并闪一下。状态存在后端 settings.json，重启还在。 */
function renderFollow() {
  const b = $('#btnFollow');
  if (!b) return;
  const on = !!settings().follow;
  b.classList.toggle('is-on', on);
  b.setAttribute('aria-pressed', on ? 'true' : 'false');
  b.title = on ? '自动定位：开（点一下关掉）' : '自动定位：关（点一下开启）';
}

async function toggleFollow() {
  const v = !settings().follow;
  const j = await run(() => api('/api/settings', { follow: v }));
  if (!j) return;
  if (j.settings) S.st.settings.follow = v;
  renderFollow();
  toast(v ? '已开启：添加国名后自动跳过去并高亮' : '已关闭自动定位', 'ok');
}

/* seq 是稳定唯一的自增号 —— 下标会因为排序 / 增删挪位，seq 不会。
   所以「跳到刚添加的那一行」用 seq 当锚点，而不是返回的 index。 */
function focusNameBySeq(seq) {
  const p = pr(), f = S.names;
  const i = p.names.findIndex(n => n.seq === seq);
  if (i < 0) return;

  // 当前搜索词 / 区域筛选可能正好把新行挡住 —— 那就先清掉筛选，
  // 否则翻页翻过去了也是看不见。
  const n = p.names[i];
  if ((f.region && n.region !== f.region) || !matchName(n, f.q)) {
    f.region = '';
    f.q = '';
    const rq = $('#fNameQ'), rr = $('#fNameRegion');
    if (rq) rq.value = '';
    if (rr) rr.value = '';
  }

  const pos = filteredNames().indexOf(i);
  if (pos < 0) return;
  f.page = Math.floor(pos / f.size) + 1;
  f.sel.clear();
  f.sel.add(i);
  f.last = i;
  renderNames();
  flashRow(i);
}

function flashRow(i) {
  const tr = $('#bodyNames tr[data-i="' + i + '"]');
  if (!tr) return;
  tr.classList.add('is-flash');
  // 滚动这一下纯属锦上添花，**不能因为它把整条定位流程打断**。
  // 曾经这里的兜底写成了 `else { tr.scrollIntoView(false) }` —— 方法本来就是
  // 「不存在」才走到 else 的，再调一次直接 TypeError（jsdom 把它抓出来了：
  // jsdom 没实现 scrollIntoView，浏览器都有，所以肉眼永远看不出）。
  try {
    if (tr.scrollIntoView) tr.scrollIntoView({ block: 'center', behavior: 'smooth' });
  } catch (e) {
    // 老内核不认 options 对象，退化成一次性跳过去
    try { tr.scrollIntoView(); } catch (e2) { /* 算了，别再折腾了 */ }
  }
  setTimeout(() => tr.classList.remove('is-flash'), 1800);
}

/* ---------------------------------------------------- 词缀 */

function slotSection(kind) {
  const name = kind === 'P' ? '前缀' : '后缀';
  const sec = $('section[data-view="' + (kind === 'P' ? 'prefix' : 'suffix') + '"]');
  if (sec.dataset.built) return sec;
  sec.dataset.built = '1';
  sec.innerHTML =
    '<div class="view-head"><div>' +
      '<h1>' + name + '</h1>' +
      '<p class="sub">顺序 = 游戏里该' + name + '的出现顺序。每加 1 个' + name +
      '，组合数 +' + '<b id="delta' + kind + '">0</b> 种。</p>' +
    '</div><div class="view-head-actions">' +
      '<button class="btn btn-primary" data-act="slot-add" data-kind="' + kind +
        '">添加' + name + '</button>' +
    '</div></div>' +
    '<div class="toolbar">' +
      '<input id="q' + kind + '" class="input" type="search" placeholder="查' + name + '…">' +
      '<span class="grow"></span>' +
      '<button class="btn" data-act="slot-edit" data-kind="' + kind + '">修改</button>' +
      '<button class="btn btn-danger" data-act="slot-del" data-kind="' + kind + '">删除</button>' +
      '<div class="btn-sep"></div>' +
      '<button class="btn" data-act="slot-up" data-kind="' + kind + '">↑</button>' +
      '<button class="btn" data-act="slot-down" data-kind="' + kind + '">↓</button>' +
      '<button class="btn" data-act="slot-sort" data-kind="' + kind + '">按拼音排序</button>' +
    '</div>' +
    '<div class="table-wrap"><table class="table">' +
      '<thead><tr><th class="col-idx">#</th><th class="col-name">' + name + '</th>' +
      '<th class="col-py">拼音</th><th class="col-note">示例</th></tr></thead>' +
      '<tbody id="body' + kind + '"></tbody></table></div>' +
    '<div class="table-foot"><span class="muted" id="count' + kind + '">—</span></div>';
  return sec;
}

function renderSlots(kind) {
  const sec = slotSection(kind);
  const p = pr(), f = S.slots[kind];
  const items = kind === 'P' ? p.prefixes : p.suffixes;
  const q = f.q.trim().toLowerCase();
  const sample = p.names.length ? p.names[0].name : '中华';

  const nOther = kind === 'P' ? p.suffixes.length : p.prefixes.length;
  $('#delta' + kind).textContent = (p.names.length * (1 + nOther)).toLocaleString();

  const rows = [];
  for (let i = 0; i < items.length; i++) {
    const t = items[i];
    if (q && !t.toLowerCase().includes(q)) continue;
    rows.push('<tr data-i="' + i + '"' + (f.sel.has(i) ? ' class="is-sel"' : '') + '>' +
      '<td class="col-idx">' + (i + 1) + '</td>' +
      '<td class="col-name">' + esc(t) + '</td>' +
      '<td class="col-py">' + esc(pinyinOf(t)) + '</td>' +
      '<td class="col-note">' + esc(kind === 'P' ? t + sample : sample + t) + '</td>' +
    '</tr>');
  }
  $('#body' + kind).innerHTML = rows.join('');
  $('#count' + kind).textContent =
    '显示 ' + rows.length + ' / ' + items.length + ' 条' +
    (f.sel.size ? ' · 已选 ' + f.sel.size + ' 条' : '') +
    ' · 全表派生 ' + (p.names.length * (1 + p.prefixes.length
      + p.suffixes.length + p.prefixes.length * p.suffixes.length)).toLocaleString() + ' 种';
}

/* 词缀的拼音前端算不了，后端在 /api/state 里一次给全（slot_pinyin）。 */
function pinyinOf(t) {
  const m = S.st && S.st.slot_pinyin;
  return (m && m[t]) || '';
}

/* ---------------------------------------------------- 区域 */

function renderRegions() {
  const p = pr(), counts = S.st.counts;
  $('#bodyRegions').innerHTML = p.regions.map((r, i) =>
    '<tr data-id="' + esc(r.id) + '"' +
      (S.regions.sel === r.id ? ' class="is-sel"' : '') + '>' +
      '<td class="col-idx">' + (i + 1) + '</td>' +
      '<td class="col-tag"><span class="mono">' + esc(r.id) + '</span></td>' +
      '<td class="col-name">' + esc(r.name) + '</td>' +
      '<td class="col-note">' + (counts[r.id] || 0) + '</td>' +
    '</tr>').join('');
  $('#regionCount').textContent = p.regions.length + ' 个区域 · 共 ' +
    st().names + ' 个国名' +
    (st().empty_regions.length ? ' · 空区域：' + st().empty_regions.join('、') : '');
}

/* ---------------------------------------------------- 生成 */

function renderBuild() {
  const p = pr(), o = p.options, s = st();
  if (document.activeElement !== $('#optOut')) $('#optOut').value = o.output_dir || '';
  if (document.activeElement !== $('#optMod')) $('#optMod').value = o.mod_name || '';
  if (document.activeElement !== $('#optNs')) $('#optNs').value = o.namespace || '';
  if (document.activeElement !== $('#optPage')) $('#optPage').value = o.page_size;

  $('#stNames').textContent = s.names.toLocaleString();
  $('#stRegions').textContent = s.regions;
  $('#stCombos').textContent = s.combos.toLocaleString();
  $('#stPages').textContent = s.pages;
  $('#stEvents').textContent = s.events;
  $('#stUnit').textContent = s.unit;

  const bad = S.st.issues;
  $('#issues').innerHTML = bad.length
    ? bad.map(b => '<div class="issue">· ' + esc(b) + '</div>').join('')
    : '<div class="issue is-ok">校验通过，可以生成。</div>';
}

/* ------------------------------------------------------------ 动作：国名 */

function nameForm(n) {
  const p = pr();
  // 添加时默认落在「上次添加用的区域」上：连续往同一个区里塞名字很常见，
  // 每次都从列表第一项开始改很烦。编辑时当然还是用这一行自己的区域。
  // last_region 指向的区域可能已经被删了 —— 校验一下，没有就退回第一个。
  const remembered = settings().last_region;
  const def = n ? n.region
    : (p.regions.some(r => r.id === remembered) ? remembered
        : (p.regions[0] && p.regions[0].id));
  const opts = p.regions.map(r =>
    '<option value="' + esc(r.id) + '"' +
      (r.id === def ? ' selected' : '') + '>' + esc(r.name) + '</option>').join('');
  return '<label class="form-row"><span>区域</span><select id="fRegion" class="input">' +
      opts + '</select></label>' +
    '<label class="form-row"><span>国名</span><input id="fName" class="input" value="' +
      esc(n ? n.name : '') + '"></label>' +
    '<label class="form-row"><span>TAG（选填）</span><input id="fTag" class="input" value="' +
      esc(n ? n.tag : '') + '"></label>' +
    '<label class="form-row"><span>备注（选填）</span><input id="fNote" class="input" value="' +
      esc(n ? n.note : '') + '"></label>';
}

function readNameForm(root) {
  return {
    name: $('#fName', root).value.trim(),
    region: $('#fRegion', root).value,
    tag: $('#fTag', root).value.trim(),
    note: $('#fNote', root).value.trim(),
  };
}

function actNameAdd() {
  if (!pr().regions.length) return toast('请先到「区域」页添加一个区域。', 'err');
  modal({
    title: '添加国名',
    body: nameForm(null),
    focus: '#fName',
    onOk: (root) => {
      const d = readNameForm(root);
      if (!d.name) { toast('国名不能为空', 'err'); return false; }
      addName(d);
    },
  });
}

/* 添加跟编辑不一样：要记住这次选的区域，还要（开关打开时）跳到新行。 */
async function addName(d) {
  let j = await run(() => api('/api/names/add', d));
  if (!j) return;
  if (j.need_confirm) {
    confirmBox('区域内重名', j.error + '\n\n游戏里会出现两个一模一样的选项，确定还要吗？',
      () => run(() => api('/api/names/add',
        Object.assign({}, d, { allow_dup: true })))
        .then(j2 => afterAdd(d, j2 && j2.seq)), '仍然添加');
    return;
  }
  await afterAdd(d, j.seq);
}

async function afterAdd(d, seq) {
  await rememberRegion(d.region);
  await refresh();
  // refresh() 之后才按 seq 找位置：这时服务端已经是最新列表了
  if (seq != null && settings().follow) focusNameBySeq(seq);
}

/* 记住上次「添加国名」用的区域，下次打开弹窗就默认它 ——
   连续往同一个区域里加名字很常见，每次都跳回第一个区域很烦。 */
async function rememberRegion(region) {
  if (!region) return;
  const j = await run(() => api('/api/settings', { last_region: region }));
  if (j && j.settings) S.st.settings.last_region = region;
}

function actNameEdit(i) {
  const n = pr().names[i];
  if (!n) return;
  modal({
    title: '编辑国名',
    body: nameForm(n),
    // 双击进来多半就是想改名字，光标直接落在名字上并且全选 —— 打字就覆盖
    focus: '#fName',
    onOk: (root) => {
      const d = readNameForm(root);
      if (!d.name) { toast('国名不能为空', 'err'); return false; }
      d.index = i;
      submitName('/api/names/update', d);
    },
  });
}

async function submitName(path, d) {
  let j = await run(() => api(path, d));
  if (j && j.need_confirm) {
    confirmBox('区域内重名', j.error + '\n\n游戏里会出现两个一模一样的选项，确定还要吗？',
      () => run(() => api(path, Object.assign({}, d, { allow_dup: true })))
        .then(() => refresh()), '仍然添加');
    return;
  }
  if (j) await refresh();
}

function actNameDelete() {
  const idx = Array.from(S.names.sel);
  if (!idx.length) return toast('先勾选要删除的行。', 'err');
  const names = idx.slice(0, 8).map(i => pr().names[i].name).join('、');
  confirmBox('确认删除', '删除这 ' + idx.length + ' 个国名？\n\n' + names +
    (idx.length > 8 ? ' …' : ''), () => {
    run(() => api('/api/names/delete', { indices: idx })).then(() => refresh());
  });
}

function actNameBatch() {
  const p = pr();
  const idxs = filteredNames();
  const dup = p.names.map((n, i) => n.dup ? i : -1).filter(i => i >= 0);
  modal({
    title: '批量删除',
    body: '<label class="form-row"><span>范围</span><select id="bScope" class="input">' +
        '<option value="sel">当前勾选（' + S.names.sel.size + ' 条）</option>' +
        '<option value="filter">当前筛选结果（' + idxs.length + ' 条）</option>' +
        '<option value="dup">区域内重名（' + dup.length + ' 条）</option>' +
        '<option value="all">全部（' + p.names.length + ' 条）</option>' +
      '</select></label>' +
      '<p class="hint">重名指的是同一区域里出现了两个一模一样的国名，删掉后只保留第一个。</p>',
    danger: true,
    okText: '删除',
    onOk: (root) => {
      const scope = $('#bScope', root).value;
      const target = scope === 'sel' ? Array.from(S.names.sel)
        : scope === 'filter' ? idxs
        : scope === 'dup' ? dup
        : p.names.map((n, i) => i);
      if (!target.length) { toast('这个范围是空的。', 'err'); return false; }
      confirmBox('确认删除', '将删除 ' + target.length + ' 个国名，不可撤销。', () => {
        run(() => api('/api/names/delete', { indices: target })).then(() => refresh());
      });
    },
  });
}

function actNameMove(delta) {
  const sel = Array.from(S.names.sel);
  if (sel.length !== 1) return toast('先选中单独一行（上下移只对一条生效）。', 'err');
  run(async () => {
    const j = await api('/api/names/move', { index: sel[0], delta: delta });
    if (!j.moved) return;
    S.names.sel.clear();
    S.names.sel.add(sel[0] + delta);
    await refresh(true);
  });
}

/* ------------------------------------------------------------ 动作：词缀 */

function actSlotAdd(kind) {
  const name = kind === 'P' ? '前缀' : '后缀';
  modal({
    title: '添加' + name,
    body: '<label class="form-row"><span>' + name + '</span>' +
      '<input id="sText" class="input" placeholder="' +
      (kind === 'P' ? '大 / 新 / 圣' : '帝国 / 王国 / 共和国') + '"></label>',
    onOk: (root) => {
      const t = $('#sText', root).value.trim();
      if (!t) { toast('不能为空', 'err'); return false; }
      run(() => api('/api/slots/add', { kind: kind, text: t })).then(() => refresh());
    },
  });
}

function actSlotEdit(kind) {
  const sel = Array.from(S.slots[kind].sel);
  if (sel.length !== 1) return toast('先选中单独一行。', 'err');
  const items = kind === 'P' ? pr().prefixes : pr().suffixes;
  const name = kind === 'P' ? '前缀' : '后缀';
  modal({
    title: '修改' + name,
    body: '<label class="form-row"><span>' + name + '</span>' +
      '<input id="sText" class="input" value="' + esc(items[sel[0]]) + '"></label>',
    onOk: (root) => {
      const t = $('#sText', root).value.trim();
      if (!t) { toast('不能为空', 'err'); return false; }
      run(() => api('/api/slots/update', { kind: kind, index: sel[0], text: t }))
        .then(() => refresh());
    },
  });
}

function actSlotDelete(kind) {
  const sel = Array.from(S.slots[kind].sel);
  if (!sel.length) return toast('先勾选要删除的行。', 'err');
  run(() => api('/api/slots/delete', { kind: kind, indices: sel })).then(() => refresh());
}

function actSlotMove(kind, delta) {
  const sel = Array.from(S.slots[kind].sel);
  if (sel.length !== 1) return toast('先选中单独一行。', 'err');
  run(async () => {
    const j = await api('/api/slots/move', { kind: kind, index: sel[0], delta: delta });
    if (!j.moved) return;
    S.slots[kind].sel.clear();
    S.slots[kind].sel.add(sel[0] + delta);
    await refresh(true);
  });
}

/* ------------------------------------------------------------ 动作：区域 */

function actRegionAdd() {
  modal({
    title: '添加区域',
    body: '<label class="form-row"><span>区域标识</span>' +
        '<input id="rId" class="input" placeholder="ZH"></label>' +
      '<label class="form-row"><span>显示名称</span>' +
        '<input id="rName" class="input" placeholder="中华区域"></label>' +
      '<p class="hint">标识只能用大写字母 / 数字 / 下划线，会写进事件 id 与本地化 key，建好后不让改。</p>',
    onOk: (root) => {
      const id = $('#rId', root).value.trim().toUpperCase();
      const nm = $('#rName', root).value.trim();
      if (!id) { toast('标识不能为空', 'err'); return false; }
      run(() => api('/api/regions/add', { id: id, name: nm || id })).then(() => refresh());
    },
  });
}

function actRegionEdit(id) {
  const r = pr().regions.find(x => x.id === id);
  if (!r) return;
  modal({
    title: '编辑区域',
    body: '<label class="form-row"><span>区域标识</span>' +
        '<input class="input" value="' + esc(r.id) + '" disabled></label>' +
      '<label class="form-row"><span>显示名称</span>' +
        '<input id="rName" class="input" value="' + esc(r.name) + '"></label>',
    onOk: (root) => {
      run(() => api('/api/regions/rename',
        { id: r.id, name: $('#rName', root).value.trim() })).then(() => refresh());
    },
  });
}

function actRegionDelete(id) {
  const n = S.st.counts[id] || 0;
  confirmBox('确认删除', '删除区域「' + (pr().regions.find(r => r.id === id) || {}).name +
    '」？' + (n ? '\n\n它下面还有 ' + n + ' 个国名，会一并删除。' : ''),
    () => run(() => api('/api/regions/delete', { id: id })).then(() => refresh()));
}

/* ------------------------------------------------------------ 工程 */

function actNew() {
  modal({
    title: '新建工程',
    body: '<label class="form-row"><span>工程名</span>' +
        '<input id="pName" class="input" value="新建工程"></label>' +
      '<label class="form-row"><span>初始内容</span><select id="pSeed" class="input">' +
        '<option value="vanilla">从「区域-tag-国名对照表.md」导入原版全部国名</option>' +
        '<option value="empty">空白工程（只有区域表，国名自己加）</option>' +
        '<option value="copy">复制当前工程的字库</option>' +
      '</select></label>',
    onOk: (root) => {
      run(() => api('/api/project/new',
        { name: $('#pName', root).value.trim() || '新建工程',
          seed: $('#pSeed', root).value })).then(() => refresh());
    },
  });
}

/* 弹 Windows 原生对话框（资源管理器那套）拿一个路径。
   返回 '' = 用户取消；返回 null = 弹不出来（非 Windows / 后端不支持），
   调用方要退回手填。 */
async function pickPath(kind, opt) {
  if (S.st.native_pick === false) return null;
  try {
    const j = await api('/api/pick', Object.assign({ kind: kind }, opt || {}));
    return j.path || '';
  } catch (e) {
    return null;
  }
}

/* 原生对话框用不了时的退路：手填路径。 */
function openByHand() {
  const list = S.st.projects;
  modal({
    title: '打开工程（手填路径）',
    body: '<label class="form-row"><span>工程文件</span><select id="pPick" class="input">' +
        (list.length ? list.map(p =>
          '<option value="' + esc(p.path) + '">' + esc(p.name) + '</option>').join('')
          : '<option value="">（工程文件目录里还没有工程）</option>') +
      '</select></label>' +
      '<p class="hint">目录：' + esc(S.st.project_dir) + '</p>' +
      '<label class="form-row"><span>或路径</span><input id="pPath" class="input"></label>',
    onOk: (root) => {
      const path = $('#pPath', root).value.trim() || $('#pPick', root).value;
      if (!path) { toast('请选一个工程', 'err'); return false; }
      run(() => api('/api/project/open', { path: path })).then(() => refresh());
    },
  });
}

async function actOpen() {
  const p = await pickPath('open', {
    title: '打开工程', start: S.st.project_dir || '',
  });
  if (p === null) { openByHand(); return; }        // 弹不出来 → 手填
  if (!p) return;                                   // 用户取消
  const before = pr().meta.name;
  const j = await run(() => api('/api/project/open', { path: p }));
  if (!j) return;
  await refresh();
  // 顶栏工程名显示的是 meta.name，两个工程可能同名 —— 光看名字会以为没打开。
  // 所以这里连文件名一起报出来，国名数也带上，一眼能看出换了。
  const file = p.split(/[\\/]/).pop();
  const nm = pr().meta.name === before ? '' : '「' + pr().meta.name + '」';
  toast('已打开 ' + nm + '：' + file + '（' + pr().names.length + ' 个国名）', 'ok');
}

/* 把路径拉回本机工具目录 —— 工程是别人给的、或在别的机器上做的时候，
   输出目录里还写着人家机器上的绝对路径（换个盘符就没有那个盘）。 */
async function actResetPaths() {
  const cur = pr().options.output_dir || '（空）';
  confirmBox('重置路径',
    '把路径重置回本机工具目录？\n\n现在：' + cur +
    '\n重置为：' + (S.st.output_default || '工具目录/生成的mod') +
    '\n\n工程文件本身的路径不用管 —— 它就在「工程文件」里。',
    () => run(() => api('/api/project/reset-paths', {})).then(() => refresh(true)),
    '重置');
}

async function actSave() {
  // 新建的工程还没落过盘，保存 = 另存为（得先问清楚存哪儿）
  if (!pr().path) return actSaveAs();
  const j = await run(() => api('/api/project/save', {}));
  if (j) { toast('已保存', 'ok'); await refresh(true); }
}

async function actSaveAs() {
  const name = (pr().meta.name || '工程') + '.hznproj';
  const p = await pickPath('save', {
    title: '另存为', start: S.st.project_dir || '', name: name,
  });
  if (p === null) {                                 // 弹不出来 → 手填
    modal({
      title: '另存为（手填路径）',
      body: '<label class="form-row"><span>另存为</span>' +
        '<input id="sPath" class="input" value="' +
        esc(pr().path || S.st.project_dir || '') + '"></label>',
      onOk: (root) => {
        const v = $('#sPath', root).value.trim();
        if (!v) { toast('请填路径', 'err'); return false; }
        run(() => api('/api/project/save', { path: v })).then(() => refresh(true));
      },
    });
    return;
  }
  if (!p) return;
  const j = await run(() => api('/api/project/save', { path: p }));
  if (j) { toast('已另存为：' + p.split(/[\\/]/).pop(), 'ok'); await refresh(true); }
}

async function actBuild() {
  if (S.building) return;
  const bad = S.st.issues;
  if (bad.length) {
    toast('还不能生成：' + bad[0], 'err');
    go('build');
    return;
  }
  S.building = true;
  const btn = $('#btnBuild');
  btn.disabled = true;
  const old = btn.textContent;
  btn.textContent = '生成中…';
  $('#buildLog').textContent = '正在生成，970 个国名约需几秒…\n';
  try {
    const j = await api('/api/build', {});
    const s = j.stats;
    $('#buildLog').textContent = (s.log || []).join('\n') +
      '\n\n完成：' + s.files + ' 个文件 / ' +
      (s.bytes / 1024).toFixed(0) + ' KB / ' + s.combos.toLocaleString() +
      ' 组合 / ' + s.seconds + ' 秒\n输出：' + s.outdir;
    toast('生成完成：' + s.files + ' 个文件', 'ok');
    await refresh(true);
  } catch (e) {
    $('#buildLog').textContent = '失败：' + e.message;
    toast(e.message, 'err');
  } finally {
    S.building = false;
    btn.disabled = false;
    btn.textContent = old;
  }
}

/* ------------------------------------------------------------ 视图切换 */

function go(view) {
  S.view = view;
  $$('.nav-item').forEach(b => b.classList.toggle('is-active', b.dataset.view === view));
  $$('.view').forEach(s => s.classList.toggle('is-active', s.dataset.view === view));
  $('#content').scrollTop = 0;
}

/* ------------------------------------------------------------ 绑定 */

function bind() {
  $('#navGroup').addEventListener('click', (e) => {
    const b = e.target.closest('.nav-item');
    if (b) go(b.dataset.view);
  });

  // 页签头部的按钮
  $$('.view-head-actions').forEach(box => {
    box.addEventListener('click', (e) => {
      const b = e.target.closest('[data-act]');
      if (!b) return;
      const act = b.dataset.act, kind = b.dataset.kind;
      if (act === 'name-add') actNameAdd();
      else if (act === 'slot-add') actSlotAdd(kind);
      else if (act === 'region-add') actRegionAdd();
    });
  });

  // 国名工具栏
  $$('section[data-view="names"] .toolbar').forEach(box => {
    box.addEventListener('click', (e) => {
      const b = e.target.closest('[data-act]');
      if (!b) return;
      const act = b.dataset.act;
      const sel = Array.from(S.names.sel);
      if (act === 'name-edit') {
        if (sel.length !== 1) return toast('先选中单独一行（双击行也行）。', 'err');
        actNameEdit(sel[0]);
      } else if (act === 'name-del') actNameDelete();
      else if (act === 'name-batch') actNameBatch();
      else if (act === 'name-up') actNameMove(-1);
      else if (act === 'name-down') actNameMove(1);
      else if (act === 'name-import') {
        confirmBox('导入字库',
          '从「区域-tag-国名对照表.md」导入原版字库。\n\n' +
          '已存在的同名条目会跳过，不会重复添加。导入后自动按当前排序方式重排。',
          () => run(() => api('/api/names/import', {})).then(() => refresh()),
          '导入');
      }
    });
  });

  // 词缀工具栏
  ['prefix', 'suffix'].forEach(v => {
    const box = $('section[data-view="' + v + '"] .toolbar');
    if (!box) return;
    box.addEventListener('click', (e) => {
      const b = e.target.closest('[data-act]');
      if (!b) return;
      const kind = b.dataset.kind, act = b.dataset.act;
      if (act === 'slot-add') actSlotAdd(kind);
      else if (act === 'slot-edit') actSlotEdit(kind);
      else if (act === 'slot-del') actSlotDelete(kind);
      else if (act === 'slot-up') actSlotMove(kind, -1);
      else if (act === 'slot-down') actSlotMove(kind, 1);
      else if (act === 'slot-sort') {
        run(() => api('/api/slots/sort', { kind: kind })).then(() => refresh());
      }
    });
  });

  // 区域工具栏
  const rbox = $('section[data-view="regions"] .toolbar');
  rbox.addEventListener('click', (e) => {
    const b = e.target.closest('[data-act]');
    if (!b) return;
    const id = S.regions.sel;
    if (!id) return toast('先选中一个区域。', 'err');
    if (b.dataset.act === 'region-edit') actRegionEdit(id);
    else if (b.dataset.act === 'region-del') actRegionDelete(id);
    else if (b.dataset.act === 'region-up' || b.dataset.act === 'region-down') {
      run(() => api('/api/regions/move',
        { id: id, delta: b.dataset.act === 'region-up' ? -1 : 1 }))
        .then(() => refresh(true));
    }
  });

  // 表格：勾选 / 选中行 / 双击编辑
  // 这三处都只调 sync* 改样式，**不重绘** —— 原因见 syncNameSelection() 的注释。
  $('#bodyNames').addEventListener('click', (e) => {
    const tr = e.target.closest('tr[data-i]');
    if (!tr) return;
    const i = +tr.dataset.i;
    if (e.target.closest('input[data-pick]')) {
      const cb = tr.querySelector('input[data-pick]');
      cb.checked ? S.names.sel.add(i) : S.names.sel.delete(i);
      S.names.last = i;
      syncNameSelection();
      return;
    }
    if (e.shiftKey && S.names.last != null) {
      const a = Math.min(S.names.last, i), b = Math.max(S.names.last, i);
      for (let k = a; k <= b; k++) S.names.sel.add(k);
    } else {
      S.names.sel.clear();
      S.names.sel.add(i);
    }
    S.names.last = i;
    syncNameSelection();
  });

  $('#bodyNames').addEventListener('dblclick', (e) => {
    if (e.target.closest('input[data-pick]')) return;   // 连点复选框不算要编辑
    const tr = e.target.closest('tr[data-i]');
    if (!tr) return;
    const i = +tr.dataset.i;
    S.names.sel.clear();
    S.names.sel.add(i);
    S.names.last = i;
    syncNameSelection();
    actNameEdit(i);
  });

  $('#chkAllNames').addEventListener('change', (e) => {
    const idxs = filteredNames().slice((S.names.page - 1) * S.names.size,
      S.names.page * S.names.size);
    idxs.forEach(i => e.target.checked ? S.names.sel.add(i) : S.names.sel.delete(i));
    syncNameSelection();
  });

  ['P', 'S'].forEach(kind => {
    const body = $('#body' + kind);
    if (!body) return;
    body.addEventListener('click', (e) => {
      const tr = e.target.closest('tr[data-i]');
      if (!tr) return;
      const i = +tr.dataset.i;
      const f = S.slots[kind];
      if (e.shiftKey && f.last != null) {
        const a = Math.min(f.last, i), b = Math.max(f.last, i);
        for (let k = a; k <= b; k++) f.sel.add(k);
      } else {
        f.sel.clear();
        f.sel.add(i);
      }
      f.last = i;
      syncSlotSelection(kind);
    });
    body.addEventListener('dblclick', (e) => {
      const tr = e.target.closest('tr[data-i]');
      if (!tr) return;
      const f = S.slots[kind];
      f.sel.clear();
      f.sel.add(+tr.dataset.i);
      f.last = +tr.dataset.i;
      syncSlotSelection(kind);
      actSlotEdit(kind);
    });
  });

  $('#bodyRegions').addEventListener('click', (e) => {
    const tr = e.target.closest('tr[data-id]');
    if (!tr) return;
    S.regions.sel = tr.dataset.id;
    syncRegionSelection();
  });
  $('#bodyRegions').addEventListener('dblclick', (e) => {
    const tr = e.target.closest('tr[data-id]');
    if (!tr) return;
    S.regions.sel = tr.dataset.id;
    syncRegionSelection();
    actRegionEdit(tr.dataset.id);
  });

  // 搜索 / 筛选
  let t = null;
  $('#fNameQ').addEventListener('input', (e) => {
    clearTimeout(t);
    const v = e.target.value;
    t = setTimeout(() => { S.names.q = v; S.names.page = 1; renderNames(); }, 160);
  });
  $('#fNameRegion').addEventListener('change', (e) => {
    S.names.region = e.target.value; S.names.page = 1; renderNames();
  });
  // 自动定位开关 —— 状态存后端 settings.json，关掉程序再开还是上次那个值。
  $('#btnFollow').addEventListener('click', toggleFollow);
  $('#fNameSort').addEventListener('change', (e) => {
    run(() => api('/api/names/sort', { mode: e.target.value })).then(() => refresh());
  });
  $('#pageSize').addEventListener('change', (e) => {
    S.names.size = +e.target.value; S.names.page = 1; renderNames();
  });
  $('#pagerNames').addEventListener('click', (e) => {
    const b = e.target.closest('[data-page]');
    if (!b) return;
    const pages = Math.max(1, Math.ceil(filteredNames().length / S.names.size));
    const p = b.dataset.page;
    S.names.page = p === 'first' ? 1 : p === 'last' ? pages
      : Math.min(pages, Math.max(1, S.names.page + (p === 'next' ? 1 : -1)));
    renderNames();
  });

  ['P', 'S'].forEach(kind => {
    const q = $('#q' + kind);
    if (!q) return;
    q.addEventListener('input', (e) => { S.slots[kind].q = e.target.value; renderSlots(kind); });
  });

  // 生成页输入
  ['optOut', 'optMod', 'optNs', 'optPage'].forEach(id => {
    $('#' + id).addEventListener('change', (e) => {
      const map = { optOut: 'output_dir', optMod: 'mod_name',
                    optNs: 'namespace', optPage: 'page_size' };
      const o = {};
      o[map[id]] = (id === 'optPage') ? +e.target.value : e.target.value.trim();
      run(() => api('/api/project/options', o)).then(() => refresh(true));
    });
  });

  $('#btnPickOut').addEventListener('click', async () => {
    const cur = pr().options.output_dir || S.st.output_default || '';
    const p = await pickPath('folder', {
      title: '选择「组词自定义国名」模组文件夹', start: cur,
    });
    if (p === null) {                               // 弹不出来 → 手填
      modal({
        title: '输出目录',
        body: '<label class="form-row"><span>绝对路径</span>' +
          '<input id="oPath" class="input" value="' + esc(cur) + '"></label>' +
          '<p class="hint">默认：' + esc(S.st.output_default) + '</p>',
        onOk: (root) => {
          run(() => api('/api/project/options',
            { output_dir: $('#oPath', root).value.trim() })).then(() => refresh(true));
        },
      });
      return;
    }
    if (!p) return;
    await run(() => api('/api/project/options', { output_dir: p }));
    await refresh(true);
  });
  $('#btnBuild').addEventListener('click', actBuild);

  // 顶栏
  $('#btnSave').addEventListener('click', actSave);
  $('#btnSaveAs').addEventListener('click', actSaveAs);
  $('#btnResetPaths').addEventListener('click', actResetPaths);
  $('#btnNew').addEventListener('click', actNew);
  $('#btnOpen').addEventListener('click', actOpen);
  $('#btnTheme').addEventListener('click', async () => {
    const cur = document.documentElement.dataset.theme;
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    // 原生窗口模式下让标题栏和窗口底色也跟着走。
    // 浏览器里没有 pywebview 这个对象，静默跳过即可。
    try {
      if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.set_theme(next);
      }
    } catch (e) { /* 忽略 */ }
    await run(() => api('/api/settings', { theme: next }));
  });
  $('#btnQuit').addEventListener('click', () => {
    confirmBox('退出', '退出程序？\n\n未保存的改动会丢失。', () => {
      run(() => api('/api/shutdown', {}));
      setTimeout(() => {
        document.body.innerHTML =
          '<div style="display:grid;place-items:center;height:100vh;' +
          'font:14px \'Microsoft YaHei UI\'">已退出。</div>';
      }, 1400);
    }, '退出');
  });

  // 快捷键
  document.addEventListener('keydown', (e) => {
    const tag = (e.target.tagName || '').toLowerCase();
    const typing = tag === 'input' || tag === 'select' || tag === 'textarea';
    if (e.ctrlKey && e.key === 's') { e.preventDefault(); actSave(); return; }
    if (typing) return;
    if (e.key === 'Delete' && S.view === 'names' && S.names.sel.size) {
      e.preventDefault(); actNameDelete();
    }
  });

  window.addEventListener('beforeunload', (e) => {
    if (pr() && pr().dirty) { e.preventDefault(); e.returnValue = ''; }
  });
}

/* ------------------------------------------------------------ 启动 */

(async function boot() {
  try {
    await refresh();
  } catch (e) {
    document.body.innerHTML = '<div style="padding:40px;font:14px sans-serif">' +
      '连不上本地服务：' + esc(e.message) + '</div>';
    return;
  }
  document.documentElement.dataset.theme = S.st.settings.theme || 'light';
  bind();
})();

/* 自检钩子。给 check_web_ui.js 用的：它在 jsdom 里 eval 本文件，
   而 **strict 模式下的 eval 会把顶层 const / function 都关在自己的作用域里**，
   外面再 eval 一次是看不见 S 的（浏览器里没有这个问题 —— script 标签加载的
   顶层 function 会挂在 window 上）。界面自己不碰它。 */
window.__hz = { S: S, focusNameBySeq: focusNameBySeq, flashRow: flashRow };
