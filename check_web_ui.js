/* 用 jsdom 真跑一遍前端：能抓到「语法没问题但一运行就炸」的那类错误。
 * HTTP 层测不到运行时异常，所以 check_web.py 会拉起本脚本补这一刀。
 *
 *   node check_web_ui.js <port> [期望的「上次添加用的区域」id]
 *
 * 需要 jsdom（装在托管 node 的 workspace 里，用 NODE_PATH 指过去）。
 */
const fs = require('fs');
const path = require('path');
const { JSDOM, VirtualConsole } = require('jsdom');

const DIR = path.join(__dirname, 'web', 'static');
const BASE = 'http://127.0.0.1:' + (process.argv[2] || 8769);
const EXPECT_REGION = process.argv[3] || '';

const errs = [];
const vc = new VirtualConsole();
vc.on('jsdomError', (e) => errs.push('jsdomError: ' + e.message));
vc.on('error', (...a) => errs.push('console.error: ' + a.join(' ')));

const html = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');
const dom = new JSDOM(html, {
  url: BASE + '/',
  pretendToBeVisual: true,
  virtualConsole: vc,
  runScripts: 'outside-only',   // 不加这个，window.eval 拿不到 window 作用域
  resources: 'usable',          // 让它去取 /app.css，才能检查遮罩的计算样式
});
const w = dom.window;
w.fetch = (p, o) => fetch(new URL(p, BASE), o);

// jsdom 不会真的去取 <link> 的样式表（resources:'usable' 也没用），
// 直接把 app.css 文本塞进 <style>，这样 getComputedStyle 才看得到我们的规则。
const st = w.document.createElement('style');
st.textContent = fs.readFileSync(path.join(DIR, 'app.css'), 'utf8');
w.document.head.appendChild(st);

try {
  w.eval(fs.readFileSync(path.join(DIR, 'app.js'), 'utf8'));
} catch (e) {
  errs.push('eval: ' + e.stack);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

setTimeout(async () => {
  const d = w.document;
  const t = (s) => { const e = d.querySelector(s); return e ? e.textContent.trim() : '<缺失 ' + s + '>'; };
  const out = {
    '国名行数': d.querySelectorAll('#bodyNames tr').length,
    '国名徽标': t('#badgeNames'),
    '计数文案': t('#nameCount'),
    '分页': t('#pagerInfo'),
    '首行': (d.querySelector('#bodyNames tr') || { textContent: '-' }).textContent.replace(/\s+/g, ' ').trim(),
    '区域行数': d.querySelectorAll('#bodyRegions tr').length,
    '前缀行数': d.querySelectorAll('#bodyP tr').length,
    '后缀行数': d.querySelectorAll('#bodyS tr').length,
    '组合数': t('#msCombos'),
    '输出目录': (d.querySelector('#optOut') || {}).value,
    '校验': t('#issues').slice(0, 40),
    '工程名': t('#projName'),
    '词缀示例': (d.querySelector('#bodyP tr td:nth-child(4)') || {}).textContent,
    // 遮罩必须一开始就是 none。曾经 .modal-root 直接写了 display:grid，
    // 盖掉 HTML 的 hidden 属性，整个页面糊一层模糊还点不动。
    '遮罩初始 display': w.getComputedStyle(d.querySelector('#modalRoot')).display,
    '遮罩 hidden 属性': d.querySelector('#modalRoot').hasAttribute('hidden'),
  };
  console.log(JSON.stringify(out, null, 2));

  /* ---------------------------------------------------------------- 交互
   * 这几条都是真的踩过坑的地方，所以做成回归而不是「看着没问题就行」。 */

  const mouse = (el, type) =>
    el.dispatchEvent(new w.MouseEvent(type, { bubbles: true, cancelable: true }));

  try {
    // 双击能不能调出编辑框。
    // 病根：以前单击一行会整表重绘，两次点击之间 <tr> 被换掉了，
    // 第二次点击的目标已经脱离 DOM，浏览器算 dblclick 目标时塌到 tbody，
    // `closest('tr[data-i]')` 拿不到东西 —— 双击等于没反应，还不报错。
    const row = d.querySelector('#bodyNames tr[data-i]');
    mouse(row, 'click');
    out['单击后行还在 DOM 里'] = row.isConnected;      // false = 重绘了 = 双击必失效
    mouse(row, 'click');
    mouse(row, 'dblclick');
    out['双击后弹窗'] = t('#modalRoot .modal-head');
    out['双击后弹窗可见'] = !d.querySelector('#modalRoot').hasAttribute('hidden');
    // 不认名字内容 —— 列表顺序会因为排序 / 导入变，只认「带出来了东西」
    out['弹窗带出非空原值'] = !!((d.querySelector('#fName') || {}).value || '');
    out['弹窗光标在国名上'] = d.activeElement && d.activeElement.id;
    // 关掉弹窗，别挡着后面的步骤
    mouse(d.querySelector('#modalRoot [data-x="cancel"]'), 'click');
    await sleep(50);
    out['取消后弹窗关了'] = d.querySelector('#modalRoot').hasAttribute('hidden');
  } catch (e) { errs.push('双击编辑: ' + e.stack); }

  try {
    // 自动定位：开关点一下，状态要跟着翻
    const b = d.querySelector('#btnFollow');
    out['开关初始 aria-pressed'] = b.getAttribute('aria-pressed');
    mouse(b, 'click');
    await sleep(400);
    out['开关点击后 aria-pressed'] = b.getAttribute('aria-pressed');
    // 不写死 true/false —— 默认值可能被人改过，只认「点一下翻面」
    out['开关状态翻转了'] = out['开关初始 aria-pressed'] !==
      out['开关点击后 aria-pressed'];
    out['开关的高亮样式跟着翻'] = b.classList.contains('is-on') ===
      (out['开关点击后 aria-pressed'] === 'true');
  } catch (e) { errs.push('自动定位开关: ' + e.stack); }

  try {
    // 添加弹窗里的区域，应该默认是「上次添加用的那个」而不是列表第一项
    mouse(d.querySelector('section[data-view="names"] .view-head-actions [data-act="name-add"]'), 'click');
    await sleep(60);
    out['添加弹窗默认区域'] = (d.querySelector('#fRegion') || {}).value;
    out['期望的默认区域'] = EXPECT_REGION;
    out['默认区域对了'] = (d.querySelector('#fRegion') || {}).value === EXPECT_REGION;
    mouse(d.querySelector('#modalRoot [data-x="cancel"]'), 'click');
    await sleep(50);
  } catch (e) { errs.push('记住区域: ' + e.stack); }

  try {
    // 自动定位到某一行：翻页 + 选中 + 加高亮 class
    // （直接调前端函数，省得真的往工程里加数据把后面的基准打乱）
    const hz = w.__hz;
    if (!hz) throw new Error('app.js 没挂 window.__hz 自检钩子');
    const seq = hz.S.st.project.names[500].seq;
    hz.focusNameBySeq(seq);
    const tr = d.querySelector('#bodyNames tr.is-flash');
    out['自动定位后高亮行数'] = d.querySelectorAll('#bodyNames tr.is-flash').length;
    out['高亮行就是目标 seq'] =
      tr ? hz.S.st.project.names[+tr.dataset.i].seq === seq : false;
    out['高亮行也被选中'] = tr ? tr.classList.contains('is-sel') : false;
  } catch (e) { errs.push('自动定位: ' + e.stack); }

  // 顺手点一下导航与视图切换，看有没有运行时错误
  try {
    d.querySelector('.nav-item[data-view="build"]').click();
    w.document.querySelector('.nav-item[data-view="prefix"]').click();
  } catch (e) { errs.push('切换视图: ' + e.message); }

  console.log('\n--- 交互 ---');
  console.log(JSON.stringify({
    '单击后行还在 DOM 里': out['单击后行还在 DOM 里'],
    '双击后弹窗': out['双击后弹窗'],
    '双击后弹窗可见': out['双击后弹窗可见'],
    '弹窗带出非空原值': out['弹窗带出非空原值'],
    '弹窗光标在国名上': out['弹窗光标在国名上'],
    '取消后弹窗关了': out['取消后弹窗关了'],
    '开关状态翻转了': out['开关状态翻转了'],
    '开关的高亮样式跟着翻': out['开关的高亮样式跟着翻'],
    '默认区域对了': out['默认区域对了'],
    '添加弹窗默认区域': out['添加弹窗默认区域'],
    '自动定位后高亮行数': out['自动定位后高亮行数'],
    '高亮行就是目标 seq': out['高亮行就是目标 seq'],
    '高亮行也被选中': out['高亮行也被选中'],
  }, null, 2));

  if (errs.length) {
    console.log('\n运行时错误：');
    errs.forEach(e => console.log('  ' + e));
    process.exit(1);
  }
  console.log('\n前端无运行时错误');
  process.exit(0);
}, 4000);
