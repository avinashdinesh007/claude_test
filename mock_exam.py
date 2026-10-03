#!/usr/bin/env python3
"""CCDV-F style mock exam: run `python3 mock_exam.py` and the exam opens in your browser."""
import argparse
import hashlib
import json
import threading
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS_DIR = BASE / "results"

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CCDV-F Mock Test</title>
<style>
:root{--bg:#f4f6fa;--card:#fff;--ink:#1d2433;--mute:#667085;--line:#e3e7ee;--pri:#3b5bdb;--pri2:#2f4ac0;
--ok:#12a150;--bad:#d92d20;--warn:#f79009;--rev:#7a5af8;--nv:#d0d5dd}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink)}
button{font:inherit;cursor:pointer;border-radius:8px;border:1px solid var(--line);background:#fff;padding:9px 16px}
button.pri{background:var(--pri);border-color:var(--pri);color:#fff}button.pri:hover{background:var(--pri2)}
button.danger{background:var(--bad);border-color:var(--bad);color:#fff}
button:disabled{opacity:.5;cursor:not-allowed}
.hidden{display:none!important}
header{position:sticky;top:0;z-index:5;background:#101828;color:#fff;display:flex;align-items:center;gap:16px;padding:10px 20px}
header .title{font-weight:600;flex:1}
#timer{font:600 20px ui-monospace,Menlo,monospace;background:#1d2939;padding:6px 14px;border-radius:8px}
#timer.low{background:var(--bad);animation:pulse 1s infinite}@keyframes pulse{50%{opacity:.7}}
.wrap{max-width:1180px;margin:0 auto;padding:20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:24px}
.intro h1{margin:0 0 6px}.intro ul{padding-left:20px}.intro li{margin:4px 0}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0}
.stat{border:1px solid var(--line);border-radius:10px;padding:14px;background:#fafbfc}.stat b{display:block;font-size:22px}
.exam{display:grid;grid-template-columns:1fr 290px;gap:20px}
@media(max-width:860px){.exam{grid-template-columns:1fr}}
.qhead{display:flex;justify-content:space-between;color:var(--mute);font-size:13px;margin-bottom:10px}
.qtext{font-size:16.5px;margin:0 0 18px;white-space:pre-wrap}
.hint{display:inline-block;background:#fff4e5;color:#b54708;border:1px solid #fedf89;border-radius:6px;padding:2px 8px;font-size:12.5px;font-weight:600;margin-bottom:12px}
.opt{display:flex;gap:12px;align-items:flex-start;border:1.5px solid var(--line);border-radius:10px;padding:13px 14px;margin:10px 0;cursor:pointer;transition:.12s}
.opt:hover{border-color:#98a2b3}.opt.sel{border-color:var(--pri);background:#eef2ff}
.opt .k{flex:none;width:26px;height:26px;border-radius:50%;border:1.5px solid #98a2b3;display:grid;place-items:center;font-weight:600;font-size:13px}
.opt.multi .k{border-radius:6px}.opt.sel .k{background:var(--pri);border-color:var(--pri);color:#fff}
.nav{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}.nav .sp{flex:1}
.side h3{margin:0 0 10px;font-size:15px}
.grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}
.grid button{padding:6px 0;font-size:13px;font-weight:600;border-radius:6px;position:relative}
.g-nv{background:#fff}.g-na{background:#fee4e2;border-color:#fda29b}.g-a{background:#d1fadf;border-color:#6ce9a6}
.g-r{background:#ebe9fe;border-color:#bdb4fe}.g-ra{background:#ebe9fe;border-color:var(--rev)}
.g-ra::after{content:"";position:absolute;right:3px;top:3px;width:6px;height:6px;border-radius:50%;background:var(--ok)}
.grid button.cur{outline:2px solid var(--ink);outline-offset:1px}
.legend{font-size:12.5px;color:var(--mute);margin:14px 0;display:grid;gap:5px}.legend span{display:inline-block;width:14px;height:14px;border-radius:4px;vertical-align:-2px;margin-right:6px;border:1px solid var(--line)}
.modal{position:fixed;inset:0;background:rgba(16,24,40,.55);display:grid;place-items:center;z-index:20}
.modal .card{max-width:460px;width:92%}
.res-top{display:flex;flex-wrap:wrap;gap:20px;align-items:center}
.badge{font-weight:700;padding:6px 14px;border-radius:999px;font-size:15px}.pass{background:#d1fadf;color:#05603a}.fail{background:#fee4e2;color:#912018}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:8px;border-bottom:1px solid var(--line);text-align:left}
.bar{height:8px;background:#eaecf0;border-radius:4px;overflow:hidden;min-width:80px}.bar i{display:block;height:100%}
.rq{border:1px solid var(--line);border-radius:10px;padding:16px;margin:14px 0;background:#fff}
.rq.ok{border-left:5px solid var(--ok)}.rq.bad{border-left:5px solid var(--bad)}
.ro{padding:8px 12px;border-radius:8px;margin:6px 0;border:1px solid var(--line);font-size:14.5px}
.ro.c{background:#ecfdf3;border-color:#6ce9a6}.ro.w{background:#fef3f2;border-color:#fda29b}
.tag{font-size:11.5px;font-weight:700;margin-left:8px;padding:1px 6px;border-radius:4px}
.tag.c{background:var(--ok);color:#fff}.tag.y{background:#344054;color:#fff}
.exp{background:#f8f9fc;border-radius:8px;padding:10px 12px;margin-top:10px;font-size:14px;color:#344054}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}.filters button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.mute{color:var(--mute)}
</style></head><body>
<header><div class="title">CCDV-F Certification — Mock Test</div><div id="progress" class="mute" style="color:#98a2b3"></div><div id="timer" class="hidden">--:--:--</div></header>

<div class="wrap">
<section id="intro" class="card intro">
  <h1>CCDV-F Mock Test</h1>
  <p class="mute">Claude Certified Developer – Foundations practice exam</p>
  <div class="stats">
    <div class="stat"><b id="i-n"></b>Questions</div>
    <div class="stat"><b id="i-t"></b>Duration</div>
    <div class="stat"><b id="i-m"></b>Total marks</div>
    <div class="stat"><b id="i-p"></b>Pass mark</div>
  </div>
  <ul>
    <li>Each question carries <b id="i-each"></b> marks. There is <b>no negative marking</b>.</li>
    <li>Questions marked <b>"Select TWO"</b> need both correct options; partial answers score 0.</li>
    <li>The timer starts when you click <b>Start Test</b>. The test <b>auto-submits</b> when time runs out.</li>
    <li>You can move freely between questions and <b>mark for review</b> using the palette.</li>
    <li>Keyboard: <b>1–4</b> select option, <b>→ / ←</b> next / previous, <b>M</b> mark for review.</li>
    <li>If you refresh or close the tab, your progress and timer are kept; relaunching resumes the test.</li>
  </ul>
  <div id="resumeBox" class="hidden" style="margin:14px 0;padding:12px;border-radius:8px;background:#eef2ff">An unfinished attempt was found. <button class="pri" id="resumeBtn">Resume</button> <button id="discardBtn">Discard &amp; start fresh</button></div>
  <button class="pri" id="startBtn" style="padding:12px 28px;font-size:16px">Start Test</button>
</section>

<section id="exam" class="exam hidden">
  <div class="card">
    <div class="qhead"><span id="qnum"></span><span id="qdom"></span></div>
    <div id="qhint" class="hint hidden">Select TWO options</div>
    <p id="qtext" class="qtext"></p>
    <div id="opts"></div>
    <div class="nav">
      <button id="prevBtn">&larr; Previous</button>
      <button id="clearBtn">Clear response</button>
      <button id="markBtn">Mark for review</button>
      <span class="sp"></span>
      <button class="pri" id="nextBtn">Save &amp; Next &rarr;</button>
    </div>
  </div>
  <aside class="card side">
    <h3>Question palette</h3>
    <div class="grid" id="grid"></div>
    <div class="legend">
      <div><span class="g-a"></span>Answered</div>
      <div><span class="g-na"></span>Visited, not answered</div>
      <div><span class="g-nv"></span>Not visited</div>
      <div><span class="g-r"></span>Marked for review</div>
      <div><span class="g-ra"></span>Answered &amp; marked</div>
    </div>
    <div id="counts" class="mute" style="font-size:13px;margin-bottom:12px"></div>
    <button class="danger" id="submitBtn" style="width:100%">Submit Test</button>
  </aside>
</section>

<section id="result" class="hidden"></section>
</div>

<div id="confirm" class="modal hidden"><div class="card">
  <h3 style="margin-top:0">Submit test?</h3>
  <div id="confirmBody"></div>
  <div class="nav"><span class="sp"></span><button id="cancelSubmit">Go back</button><button class="danger" id="doSubmit">Submit</button></div>
</div></div>

<script>
const BANK = __QUESTIONS__;
const CFG = __CONFIG__;
const KEY = "ccdvf_mock_state_v1_" + CFG.bank_hash;
const L = "ABCDEFGH";
const $ = id => document.getElementById(id);
const esc = s => s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
let S = null, tick = null;

const N = Math.min(CFG.count, BANK.length);
const perMark = CFG.marks_per_question, total = N * perMark;
$("i-n").textContent = N;
$("i-t").textContent = CFG.minutes + " min";
$("i-m").textContent = total;
$("i-p").textContent = CFG.pass_percent + "%";
$("i-each").textContent = perMark;

function shuffle(a){ a = a.slice(); for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; }
function save(){ try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} }
function load(){ try{ return JSON.parse(localStorage.getItem(KEY)); }catch(e){ return null; } }

const existing = load();
if (existing && !existing.submitted) { $("resumeBox").classList.remove("hidden"); $("startBtn").classList.add("hidden"); }
else if (existing && existing.submitted) { showResult(existing); }

$("resumeBtn").onclick = () => { S = existing; begin(); };
$("discardBtn").onclick = () => { localStorage.removeItem(KEY); location.reload(); };
$("startBtn").onclick = () => {
  const idx = BANK.map((_, i) => i);
  const order = (CFG.shuffle ? shuffle(idx) : idx).slice(0, N);
  S = { order, perm: order.map(i => CFG.shuffle ? shuffle(BANK[i].options.map((_, k) => k)) : BANK[i].options.map((_, k) => k)),
        ans: order.map(() => []), marked: order.map(() => false), visited: order.map(() => false),
        cur: 0, start: Date.now(), end: Date.now() + CFG.minutes * 60000, submitted: false };
  save(); begin();
};

function begin(){
  $("intro").classList.add("hidden"); $("exam").classList.remove("hidden"); $("timer").classList.remove("hidden");
  window.onbeforeunload = () => S && !S.submitted ? "Test in progress" : undefined;
  render(); tick = setInterval(updateTimer, 500); updateTimer();
}

function updateTimer(){
  const left = Math.max(0, S.end - Date.now()), s = Math.floor(left / 1000);
  const t = [Math.floor(s/3600), Math.floor(s%3600/60), s%60].map(x => String(x).padStart(2,"0")).join(":");
  $("timer").textContent = t; $("timer").classList.toggle("low", s <= 300);
  if (left <= 0) { finish(true); }
}

function status(i){
  const a = S.ans[i].length > 0;
  if (S.marked[i]) return a ? "g-ra" : "g-r";
  if (a) return "g-a";
  return S.visited[i] ? "g-na" : "g-nv";
}

function render(){
  const i = S.cur, q = BANK[S.order[i]]; S.visited[i] = true;
  const multi = q.type === "multi";
  $("qnum").textContent = `Question ${i+1} of ${N}`;
  $("qdom").textContent = CFG.show_domain ? q.domain : "";
  $("qhint").classList.toggle("hidden", !multi);
  $("qtext").textContent = q.q;
  $("opts").innerHTML = S.perm[i].map((orig, pos) =>
    `<div class="opt ${multi?"multi":""} ${S.ans[i].includes(orig)?"sel":""}" data-o="${orig}"><div class="k">${L[pos]}</div><div>${esc(q.options[orig])}</div></div>`).join("");
  document.querySelectorAll(".opt").forEach(el => el.onclick = () => choose(+el.dataset.o));
  $("prevBtn").disabled = i === 0;
  $("nextBtn").innerHTML = i === N - 1 ? "Save" : "Save &amp; Next &rarr;";
  $("markBtn").textContent = S.marked[i] ? "Unmark review" : "Mark for review";
  $("grid").innerHTML = S.order.map((_, k) => `<button class="${status(k)} ${k===i?"cur":""}" data-k="${k}">${k+1}</button>`).join("");
  document.querySelectorAll("#grid button").forEach(b => b.onclick = () => go(+b.dataset.k));
  const answered = S.ans.filter(a => a.length).length, marked = S.marked.filter(Boolean).length;
  $("counts").textContent = `Answered ${answered} / ${N} · Marked ${marked}`;
  $("progress").textContent = `${answered}/${N} answered`;
  save();
}

function choose(o){
  const i = S.cur, q = BANK[S.order[i]], a = S.ans[i];
  if (q.type === "multi") {
    const need = q.answer.length;
    if (a.includes(o)) a.splice(a.indexOf(o), 1);
    else { if (a.length >= need) a.shift(); a.push(o); }
  } else S.ans[i] = [o];
  render();
}
function go(k){ if (k >= 0 && k < N) { S.cur = k; render(); window.scrollTo(0,0); } }
$("prevBtn").onclick = () => go(S.cur - 1);
$("nextBtn").onclick = () => go(S.cur + 1);
$("clearBtn").onclick = () => { S.ans[S.cur] = []; render(); };
$("markBtn").onclick = () => { S.marked[S.cur] = !S.marked[S.cur]; render(); };
document.addEventListener("keydown", e => {
  if (!S || S.submitted || $("exam").classList.contains("hidden") || !$("confirm").classList.contains("hidden")) return;
  if (e.key === "ArrowRight") go(S.cur + 1);
  else if (e.key === "ArrowLeft") go(S.cur - 1);
  else if (e.key.toLowerCase() === "m") $("markBtn").click();
  else if (/^[1-8]$/.test(e.key)) { const p = S.perm[S.cur][+e.key - 1]; if (p !== undefined) choose(p); }
});

$("submitBtn").onclick = () => {
  const answered = S.ans.filter(a => a.length).length;
  const incomplete = S.order.filter((qi, i) => S.ans[i].length && S.ans[i].length < BANK[qi].answer.length).length;
  $("confirmBody").innerHTML = `<p>Answered: <b>${answered}</b> / ${N}<br>Not answered: <b>${N - answered}</b><br>Marked for review: <b>${S.marked.filter(Boolean).length}</b>` +
    (incomplete ? `<br><span style="color:var(--bad)">Select-TWO questions with only one option chosen: <b>${incomplete}</b></span>` : "") +
    `</p><p class="mute">You cannot change answers after submitting.</p>`;
  $("confirm").classList.remove("hidden");
};
$("cancelSubmit").onclick = () => $("confirm").classList.add("hidden");
$("doSubmit").onclick = () => { $("confirm").classList.add("hidden"); finish(false); };

function finish(auto){
  if (S.submitted) return;
  clearInterval(tick); S.submitted = true; S.finished = Math.min(Date.now(), S.end); S.auto = auto; save();
  window.onbeforeunload = null;
  const r = grade(S);
  fetch("/save", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(r)}).catch(() => {});
  showResult(S);
}

function grade(st){
  const rows = st.order.map((qi, i) => {
    const q = BANK[qi], a = st.ans[i].slice().sort(), c = q.answer.slice().sort();
    const ok = a.length === c.length && a.every((v, k) => v === c[k]);
    return { n: i+1, domain: q.domain, type: q.type, ok, answered: a.length > 0, score: ok ? perMark : 0, q: q.q };
  });
  const score = rows.reduce((s, r) => s + r.score, 0);
  return { when: new Date(st.start).toISOString(), minutes_allowed: CFG.minutes, seconds_taken: Math.round((st.finished - st.start)/1000),
           auto_submitted: !!st.auto, score, total, percent: +(100*score/total).toFixed(1), passed: 100*score/total >= CFG.pass_percent,
           correct: rows.filter(r => r.ok).length, wrong: rows.filter(r => !r.ok).length, rows };
}

function showResult(st){
  S = st; const r = grade(st);
  ["intro","exam"].forEach(id => $(id).classList.add("hidden")); $("timer").classList.add("hidden");
  $("progress").textContent = "";
  const dur = s => `${Math.floor(s/3600)}h ${Math.floor(s%3600/60)}m ${s%60}s`;
  const doms = {};
  r.rows.forEach(x => { (doms[x.domain] ||= {n:0,ok:0}); doms[x.domain].n++; if (x.ok) doms[x.domain].ok++; });
  const domRows = Object.entries(doms).sort((a,b) => a[1].ok/a[1].n - b[1].ok/b[1].n).map(([d, v]) => {
    const p = Math.round(100*v.ok/v.n), col = p >= 75 ? "var(--ok)" : p >= 50 ? "var(--warn)" : "var(--bad)";
    return `<tr><td>${esc(d)}</td><td>${v.ok} / ${v.n}</td><td style="width:40%"><div class="bar"><i style="width:${p}%;background:${col}"></i></div></td><td>${p}%</td></tr>`; }).join("");
  const el = $("result"); el.classList.remove("hidden");
  el.innerHTML = `<div class="card">
    <div class="res-top"><div><div class="mute">Your score</div><div style="font-size:34px;font-weight:700">${r.score.toFixed(1)} / ${r.total} <span class="mute" style="font-size:20px">(${r.percent}%)</span></div></div>
    <span class="badge ${r.passed?"pass":"fail"}">${r.passed?"PASSED":"NOT PASSED"}</span><span class="mute">Cut-off ≥ ${CFG.pass_percent}%</span></div>
    <div class="stats">
      <div class="stat"><b style="color:var(--ok)">${r.correct}</b>Solutions accepted</div>
      <div class="stat"><b style="color:var(--bad)">${r.wrong}</b>Solutions rejected</div>
      <div class="stat"><b>${r.rows.filter(x=>!x.answered).length}</b>Not attempted</div>
      <div class="stat"><b>${dur(r.seconds_taken)}</b>Time taken${r.auto_submitted?" (auto-submitted)":""}</div>
    </div>
    <h3>Performance by topic</h3><div style="overflow-x:auto"><table><tr><th>Topic</th><th>Correct</th><th></th><th></th></tr>${domRows}</table></div>
    <div class="nav"><button class="pri" id="newBtn">Start a new attempt</button><span class="mute" style="align-self:center">Result saved to the results/ folder.</span></div>
  </div>
  <h2 style="margin:28px 0 0">Detailed report</h2>
  <div class="filters"><button data-f="all" class="on">All</button><button data-f="bad">Rejected only</button><button data-f="ok">Accepted only</button><button data-f="multi">Select-TWO only</button></div>
  <div id="review"></div>`;
  $("newBtn").onclick = () => { localStorage.removeItem(KEY); location.reload(); };
  const renderReview = f => {
    $("review").innerHTML = st.order.map((qi, i) => {
      const q = BANK[qi], row = r.rows[i];
      if ((f === "bad" && row.ok) || (f === "ok" && !row.ok) || (f === "multi" && q.type !== "multi")) return "";
      const opts = st.perm[i].map((o, pos) => {
        const c = q.answer.includes(o), y = st.ans[i].includes(o);
        return `<div class="ro ${c?"c":y?"w":""}"><b>${L[pos]}.</b> ${esc(q.options[o])}${y?'<span class="tag y">YOUR ANSWER</span>':""}${c?'<span class="tag c">CORRECT</span>':""}</div>`; }).join("");
      return `<div class="rq ${row.ok?"ok":"bad"}"><div class="qhead"><b>Problem ${i+1} · ${row.ok?"ACCEPTED":"REJECTED"} · ${row.score.toFixed(1)} / ${perMark}</b><span>${esc(q.domain)}</span></div>
        ${q.type==="multi"?'<div class="hint">Select TWO</div>':""}<p class="qtext" style="font-size:15px">${esc(q.q)}</p>${opts}
        ${row.answered?"":'<div class="mute" style="margin-top:6px">Not attempted</div>'}<div class="exp"><b>Explanation:</b> ${esc(q.exp)}</div></div>`; }).join("");
  };
  document.querySelectorAll(".filters button").forEach(b => b.onclick = () => {
    document.querySelectorAll(".filters button").forEach(x => x.classList.remove("on")); b.classList.add("on"); renderReview(b.dataset.f); });
  renderReview("all");
}
</script></body></html>"""


def build_page(questions, cfg):
    return (HTML.replace("__QUESTIONS__", json.dumps(questions))
                .replace("__CONFIG__", json.dumps(cfg))).encode()


def make_handler(page):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ("/", "/index.html"):
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(page)

        def do_POST(self):
            if self.path != "/save":
                self.send_error(404)
                return
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            result = json.loads(body)
            RESULTS_DIR.mkdir(exist_ok=True)
            out = RESULTS_DIR / f"attempt_{datetime.now():%Y%m%d_%H%M%S}.json"
            out.write_text(json.dumps(result, indent=2))
            print(f"\nResult: {result['score']:.0f}/{result['total']} ({result['percent']}%) "
                  f"- {'PASSED' if result['passed'] else 'NOT PASSED'}  -> saved {out.name}")
            self.send_response(204)
            self.end_headers()

        def log_message(self, *args):
            pass
    return Handler


def main():
    p = argparse.ArgumentParser(description="CCDV-F browser mock exam")
    p.add_argument("--questions", default=str(BASE / "questions.json"), help="question bank JSON file")
    p.add_argument("--count", type=int, default=53, help="questions per attempt, drawn from the bank (default 53)")
    p.add_argument("--minutes", type=int, default=120, help="exam duration in minutes (default 120)")
    p.add_argument("--pass-percent", type=float, default=70, help="pass cut-off percentage (default 70)")
    p.add_argument("--marks", type=float, default=19, help="marks per question (default 19)")
    p.add_argument("--no-shuffle", action="store_true", help="keep question and option order fixed")
    p.add_argument("--show-domain", action="store_true", help="show each question's topic during the test")
    p.add_argument("--port", type=int, default=8765)
    a = p.parse_args()

    questions = json.loads(Path(a.questions).read_text())
    count = min(a.count, len(questions))
    cfg = {"count": count, "minutes": a.minutes, "pass_percent": a.pass_percent, "marks_per_question": a.marks,
           "shuffle": not a.no_shuffle, "show_domain": a.show_domain,
           "bank_hash": hashlib.sha1(json.dumps(questions).encode()).hexdigest()[:12]}
    server = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(build_page(questions, cfg)))
    url = f"http://127.0.0.1:{a.port}/"
    print(f"CCDV-F mock exam: {count} questions (bank of {len(questions)}), {a.minutes} minutes, "
          f"{count * a.marks:.0f} marks, pass >= {a.pass_percent}%")
    print(f"Open {url}  (Ctrl+C to stop the server)")
    threading.Thread(target=lambda: (time.sleep(0.6), webbrowser.open(url)), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
