#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成离线求职投递台账（单文件 HTML，零依赖，双击即用）。

用法:
    python3 make_tracker.py --out 求职台账.html --name "张同学-2027届"

特性:
    - 单文件，无外链、无 CDN、无网络请求；数据存浏览器 localStorage
    - 截止日倒计时：逾期标红、3 天内标黄
    - 状态流转：待投 / 已投 / 笔试 / 面试 / offer / 放弃
    - 导出 / 导入 JSON（换电脑、备份用）
    - 打印视图（Ctrl+P 出 A4）
"""
import argparse
import datetime
import os
import sys

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>求职投递台账 · __NAME__</title>
<style>
  :root{
    --bg:#f5f8fc; --card:#ffffff; --line:#e3eaf3; --ink:#1b2433; --ink2:#5b6b80;
    --blue:#2e5fa3; --blue-l:#e8f0fb; --red:#c0392b; --red-l:#fdecea;
    --amber:#b7791f; --amber-l:#fdf5e6; --green:#1e7d4f; --green-l:#e6f5ee;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
       font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;font-size:14px;line-height:1.6}
  header{background:var(--card);border-bottom:1px solid var(--line);padding:16px 20px;
         display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between}
  h1{font-size:18px;margin:0;font-weight:600}
  h1 small{font-weight:400;color:var(--ink2);font-size:12px;margin-left:8px}
  main{padding:16px 20px 60px;max-width:1180px;margin:0 auto}
  .stats{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px}
  .stat{background:var(--card);border:1px solid var(--line);border-radius:10px;
        padding:10px 14px;min-width:104px}
  .stat b{display:block;font-size:20px;line-height:1.2}
  .stat span{color:var(--ink2);font-size:12px}
  .stat.warn b{color:var(--red)}
  section{background:var(--card);border:1px solid var(--line);border-radius:12px;
          padding:14px 16px;margin-bottom:16px}
  section h2{font-size:14px;margin:0 0 10px;color:var(--ink2);font-weight:600}
  .form{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
  label{display:block;font-size:12px;color:var(--ink2);margin-bottom:3px}
  input,select,textarea{width:100%;padding:7px 9px;border:1px solid var(--line);border-radius:7px;
        font:inherit;background:#fff;color:var(--ink)}
  input:focus,select:focus,textarea:focus{outline:2px solid var(--blue-l);border-color:var(--blue)}
  .wide{grid-column:1/-1}
  .btns{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
  button{padding:8px 14px;border-radius:8px;border:1px solid var(--line);background:#fff;
         font:inherit;cursor:pointer;color:var(--ink)}
  button.primary{background:var(--blue);border-color:var(--blue);color:#fff}
  button:hover{filter:brightness(.97)}
  button.danger{color:var(--red);border-color:#f0d3cf}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{text-align:left;padding:8px 8px;border-bottom:1px solid var(--line);vertical-align:top}
  th{color:var(--ink2);font-weight:600;font-size:12px;white-space:nowrap}
  tr:hover td{background:#fbfdff}
  .tag{display:inline-block;padding:1px 8px;border-radius:20px;font-size:12px;white-space:nowrap}
  .st-待投{background:var(--blue-l);color:var(--blue)}
  .st-已投{background:#eef1f6;color:var(--ink2)}
  .st-笔试,.st-面试{background:var(--amber-l);color:var(--amber)}
  .st-offer{background:var(--green-l);color:var(--green)}
  .st-放弃{background:#f2f2f2;color:#8a8a8a}
  .due-over{color:var(--red);font-weight:600}
  .due-soon{color:var(--amber);font-weight:600}
  .due-ok{color:var(--ink2)}
  .hint{color:var(--ink2);font-size:12px;margin:6px 0 0}
  .empty{color:var(--ink2);text-align:center;padding:24px 0}
  .row-act button{padding:3px 8px;font-size:12px}
  footer{color:var(--ink2);font-size:12px;text-align:center;padding:20px}
  @media print{
    header,section.f-edit,.stats,footer,.btns,.row-act{display:none}
    body{background:#fff}
    main{padding:0;max-width:none}
    section{border:0;padding:0}
    table{font-size:11px}
    th,td{padding:4px}
  }
  @media (max-width:640px){
    main{padding:12px}
    th:nth-child(4),td:nth-child(4),th:nth-child(5),td:nth-child(5){display:none}
  }
</style>
</head>
<body>
<header>
  <h1>求职投递台账 <small>__NAME__ · 生成于 __DATE__ · 数据只存在本机浏览器</small></h1>
  <div class="btns">
    <button onclick="exportJson()">导出 JSON</button>
    <button onclick="document.getElementById('imp').click()">导入 JSON</button>
    <input id="imp" type="file" accept="application/json" hidden onchange="importJson(event)">
    <button onclick="window.print()">打印</button>
  </div>
</header>
<main>
  <div class="stats" id="stats"></div>

  <section class="f-edit">
    <h2>新增一条</h2>
    <div class="form">
      <div><label>单位 / 公司 *</label><input id="f-co" placeholder="国网河北省电力"></div>
      <div><label>岗位 / 方向</label><input id="f-role" placeholder="电子信息类-信息系统检修维护"></div>
      <div><label>城市</label><input id="f-city" placeholder="石家庄"></div>
      <div><label>学历与专业口径</label><input id="f-major" placeholder="本科及以上；名单未点名物联网工程，需电话确认"></div>
      <div><label>投递入口</label><input id="f-url" placeholder="zhaopin.sgcc.com.cn"></div>
      <div><label>截止时间</label><input id="f-due" type="date"></div>
      <div><label>状态</label>
        <select id="f-status">
          <option>待投</option><option>已投</option><option>笔试</option>
          <option>面试</option><option>offer</option><option>放弃</option>
        </select>
      </div>
      <div><label>简历版本</label><input id="f-resume" placeholder="v2-央国企-20261124"></div>
      <div class="wide"><label>备注（把公告专业名单整段抄进来）</label>
        <textarea id="f-note" rows="2" placeholder="电子信息类名单：计算机应用技术、软件工程、网络与信息安全、计算机科学与技术、人工智能、通信工程、信息与通信工程、通信与信息系统"></textarea>
      </div>
    </div>
    <div class="btns">
      <button class="primary" onclick="addItem()">加入台账</button>
      <button onclick="loadDemo()">载入示例（国网四家）</button>
      <button class="danger" onclick="clearAll()">清空全部</button>
    </div>
    <p class="hint">提示：专业口径没核实过的，状态先留「待投」，备注里写清要打哪个电话问什么。</p>
  </section>

  <section>
    <h2>台账（按截止时间排序，逾期标红）</h2>
    <table>
      <thead>
        <tr>
          <th>单位</th><th>岗位</th><th>城市</th><th>专业口径</th>
          <th>入口</th><th>截止</th><th>状态</th><th>简历</th><th>备注</th><th></th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
    <div class="empty" id="empty" style="display:none">还没有记录，上面加一条，或点「载入示例」看看格式。</div>
  </section>
</main>
<footer>本页不联网、不上传。换电脑前先「导出 JSON」，在新电脑上「导入 JSON」。</footer>

<script>
const KEY = 'qiuzhi-tracker-v1';
const SEED = __SEED__;
let items = [];

function today(){ const d=new Date(); d.setHours(0,0,0,0); return d; }
function daysLeft(due){
  if(!due) return null;
  const d=new Date(due+'T00:00:00'); if(isNaN(d)) return null;
  return Math.round((d-today())/86400000);
}
function esc(s){ return String(s==null?'':s).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

function load(){
  let raw=null;
  try{ raw = JSON.parse(localStorage.getItem(KEY)||'null'); }catch(e){ raw=null; }
  if(!Array.isArray(raw)){
    raw = (Array.isArray(SEED)? SEED : []).map(x=>Object.assign({id:'s'+Math.random().toString(36).slice(2,9)}, x));
  }
  items = Array.isArray(raw)? raw : [];
  render();
}
function save(){ localStorage.setItem(KEY, JSON.stringify(items)); }

function render(){
  const tb=document.getElementById('tbody');
  const sorted=items.slice().sort((a,b)=>{
    const da=daysLeft(a.due), db=daysLeft(b.due);
    if(da===null&&db===null) return (a.co||'').localeCompare(b.co||'');
    if(da===null) return 1; if(db===null) return -1; return da-db;
  });
  tb.innerHTML = sorted.map(it=>{
    const dl=daysLeft(it.due);
    let cls='due-ok', txt=it.due||'—';
    if(dl!==null){
      if(dl<0){ cls='due-over'; txt=it.due+'（已过 '+(0-dl)+' 天）'; }
      else if(dl===0){ cls='due-soon'; txt=it.due+'（今天！）'; }
      else if(dl<=3){ cls='due-soon'; txt=it.due+'（剩 '+dl+' 天）'; }
      else { txt=it.due+'（剩 '+dl+' 天）'; }
    }
    return '<tr>'
      +'<td><b>'+esc(it.co)+'</b></td>'
      +'<td>'+esc(it.role)+'</td>'
      +'<td>'+esc(it.city)+'</td>'
      +'<td>'+esc(it.major)+'</td>'
      +'<td>'+esc(it.url)+'</td>'
      +'<td class="'+cls+'">'+esc(txt)+'</td>'
      +'<td><span class="tag st-'+esc(it.status||'待投')+'">'+esc(it.status||'待投')+'</span></td>'
      +'<td>'+esc(it.resume)+'</td>'
      +'<td>'+esc(it.note)+'</td>'
      +'<td class="row-act"><button onclick="cycleStatus(\''+it.id+'\')">改状态</button> '
      +'<button onclick="delItem(\''+it.id+'\')">删</button></td>'
      +'</tr>';
  }).join('');
  document.getElementById('empty').style.display = sorted.length? 'none':'block';

  const c = s => items.filter(x=>(x.status||'待投')===s).length;
  const soon = items.filter(x=>{ const d=daysLeft(x.due); return d!==null && d>=0 && d<=3 && (x.status||'待投')!=='放弃'; }).length;
  const over = items.filter(x=>{ const d=daysLeft(x.due); return d!==null && d<0 && (x.status||'待投')!=='放弃'; }).length;
  document.getElementById('stats').innerHTML =
      '<div class="stat"><b>'+items.length+'</b><span>总记录</span></div>'
    + '<div class="stat"><b>'+c('待投')+'</b><span>待投</span></div>'
    + '<div class="stat"><b>'+(c('已投')+c('笔试')+c('面试'))+'</b><span>进行中</span></div>'
    + '<div class="stat"><b>'+c('offer')+'</b><span>offer</span></div>'
    + '<div class="stat'+(soon?' warn':'')+'"><b>'+soon+'</b><span>3 天内截止</span></div>'
    + '<div class="stat'+(over?' warn':'')+'"><b>'+over+'</b><span>已逾期未处理</span></div>';
}

function addItem(){
  const v = id => document.getElementById(id).value.trim();
  const it = { id:'i'+Date.now()+Math.floor(Math.random()*1000) };
  it.co=v('f-co'); it.role=v('f-role'); it.city=v('f-city'); it.major=v('f-major');
  it.url=v('f-url'); it.due=v('f-due'); it.status=document.getElementById('f-status').value;
  it.resume=v('f-resume'); it.note=v('f-note');
  if(!it.co){ alert('单位/公司名字得填一个'); return; }
  items.push(it); save(); render();
  FIELDS.forEach(f=>{ const el=document.getElementById('f-'+f); if(el) el.value=''; });
  document.getElementById('f-status').value='待投';
  document.getElementById('f-co').focus();
}

const CYCLE=['待投','已投','笔试','面试','offer','放弃'];
function cycleStatus(id){
  const it=items.find(x=>x.id===id); if(!it) return;
  const i=CYCLE.indexOf(it.status||'待投');
  it.status=CYCLE[(i+1)%CYCLE.length];
  it['t_'+it.status]=new Date().toISOString().slice(0,10);
  save(); render();
}
function delItem(id){
  if(!confirm('删掉这条？')) return;
  items=items.filter(x=>x.id!==id); save(); render();
}
function clearAll(){
  if(!items.length) return;
  if(!confirm('清空全部 '+items.length+' 条？建议先导出备份。')) return;
  items=[]; save(); render();
}
function dplus(n){ const d=new Date(); d.setDate(d.getDate()+n); return d.toISOString().slice(0,10); }
function loadDemo(){
  // 示例数据：日期按今天往后推，避免过几天打开全变成"已逾期"
  const demo=[
    {co:'国网河北省电力',role:'电子信息类·信息系统检修维护',city:'石家庄/保定等',major:'本科及以上；名单未点名你的专业→须打电话确认',url:'zhaopin.sgcc.com.cn',due:dplus(1),status:'待投',resume:'v1-央国企',note:'示例：约 65 人，公告电话见原文'},
    {co:'国网冀北电力',role:'电子信息类',city:'唐山/廊坊/张家口等',major:'本科及以上，京外单位；名单带"等"',url:'zhaopin.sgcc.com.cn',due:dplus(3),status:'待投',resume:'v1-央国企',note:'示例：约 520 人，在京岗位要硕士'},
    {co:'国网四川省电力',role:'电子信息类',city:'成都等',major:'本科及以上；"计算机科学与技术及其相关专业"',url:'zhaopin.sgcc.com.cn',due:dplus(5),status:'待投',resume:'v1-央国企',note:'示例：约 1140 人'},
    {co:'国网信通产业集团',role:'技术研发类',city:'成都/保定/天津等',major:'本科及以上（在京要硕士）；以电子信息类为主',url:'zhaopin.sgcc.com.cn',due:dplus(7),status:'待投',resume:'v1-央国企',note:'示例：约 300 人，含中电启明星'}
  ];
  if(items.length && !confirm('示例会追加到现有台账后面，继续？')) return;
  demo.forEach(d=>{ d.id='i'+Date.now()+Math.floor(Math.random()*100000); items.push(d); });
  save(); render();
}
function exportJson(){
  const blob=new Blob([JSON.stringify(items,null,2)],{type:'application/json'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='求职台账-'+new Date().toISOString().slice(0,10)+'.json';
  a.click(); URL.revokeObjectURL(a.href);
}
function importJson(ev){
  const f=ev.target.files[0]; if(!f) return;
  const r=new FileReader();
  r.onload=()=>{
    try{
      const arr=JSON.parse(r.result);
      if(!Array.isArray(arr)) throw new Error('格式不对');
      if(!confirm('导入 '+arr.length+' 条，替换当前台账？')) return;
      items=arr.map(x=>Object.assign({id:'i'+Date.now()+Math.floor(Math.random()*100000)},x));
      save(); render();
    }catch(e){ alert('导入失败：'+e.message); }
    ev.target.value='';
  };
  r.readAsText(f);
}
load();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="生成离线求职投递台账（单文件 HTML）")
    ap.add_argument("--out", default="求职台账.html", help="输出文件路径")
    ap.add_argument("--name", default="我的求职台账", help="台账主人标识，如 张同学-2027届")
    ap.add_argument("--seed", default="", help="预置数据的 JSON 文件（数组），首次打开时载入")
    args = ap.parse_args()

    seed_json = "[]"
    if args.seed:
        if not os.path.exists(args.seed):
            print(f"种子文件不存在: {args.seed}", file=sys.stderr)
            return 2
        with open(args.seed, encoding="utf-8") as f:
            seed_json = f.read().strip() or "[]"

    html = (HTML
            .replace("__SEED__", seed_json)
            .replace("__NAME__", args.name)
            .replace("__DATE__", datetime.date.today().isoformat()))

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    size = os.path.getsize(out)
    print(f"已生成: {out} ({size} bytes)")
    print("用法: 双击用浏览器打开；数据存在本机 localStorage，换电脑前先导出 JSON。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
