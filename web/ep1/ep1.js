import { C, MAPS, Plot, drawBifurcation, lyapunov, orbit, colormap } from "../assets/plot.js";

const logistic = MAPS.logistic;
const f = logistic.f;
const DATA = await (await fetch("../data/cascade.json")).json();
const UNIV = await (await fetch("../data/universality.json")).json();
const R_INF = 3.569945671870945, DELTA = 4.669201609102990, ALPHA = -2.502907875095892;
const $ = id => document.getElementById(id);
const bind = (id, cb) => { const el = $(id), out = $(id + "-out"); const go = () => { if (out) out.value = (+el.value).toFixed(el.dataset.dp ?? 3); cb(+el.value); }; el.addEventListener("input", go); return go; };

// ---------------------------------------------------------------- cobweb + time series
class Cobweb {
  constructor(prefix, { f2 = false } = {}) {
    this.web = new Plot($(prefix + "-web"), { x: [0, 1], y: [0, 1], aspect: 1, margin: [10, 10, 24, 32] });
    this.ts = new Plot($(prefix + "-ts"), { x: [0, 60], y: [0, 1], aspect: 0.62, margin: [10, 12, 24, 32] });
    this.p = prefix; this.r = 2.6; this.x0 = 0.2; this.showF2 = false;
    this.web.onresize = this.ts.onresize = () => this.draw();
    bind(prefix + "-r", v => { this.r = v; this.draw(); })();
    bind(prefix + "-x0", v => { this.x0 = v; this.draw(); })();
    if (f2) $(prefix + "-f2").addEventListener("change", e => { this.showF2 = e.target.checked; this.draw(); });
  }
  set(r) { $(this.p + "-r").value = r; $(this.p + "-r").dispatchEvent(new Event("input")); }
  draw() {
    const { web, ts, r } = this, xs = orbit(f, r, this.x0, 60);
    web.clear(); web.axes({ xt: 2, yt: 2, xl: "xₙ", yl: "xₙ₊₁" });
    web.line([[0, 0], [1, 1]], C.diag, 1.5);
    if (this.showF2) web.fn(x => f(r, f(r, x)), C.accent, 2);
    web.fn(x => f(r, x), C.map, 2.5);
    const pts = [[xs[0], 0]];
    for (let i = 0; i < 60; i++) pts.push([xs[i], xs[i + 1]], [xs[i + 1], xs[i + 1]]);
    web.clip(() => web.line(pts, C.orbit, 1.2, 0.85));
    const xstar = 1 - 1 / r, slope = 2 - r, stable = Math.abs(slope) < 1;
    if (r > 1) web.dot(xstar, xstar, stable ? C.stable : C.orbit, 4);
    ts.clear(); ts.axes({ xt: 6, yt: 2, xl: "n", yl: "xₙ" });
    ts.line(xs.map((v, i) => [i, v]), C.orbit, 1, 0.45);
    xs.forEach((v, i) => ts.dot(i, v, C.orbit, 2));
    const ro = $(this.p + "-read");
    if (ro) {
      let y = this.x0; for (let i = 0; i < 4000; i++) y = f(r, y);
      let period = 0, z = y; for (let p = 1; p <= 64; p++) { z = f(r, z); if (Math.abs(z - y) < 1e-7) { period = p; break; } }
      ro.innerHTML = r <= 1 ? `x* = 0 is the only fixed point in [0,1]; the population dies out.` :
        `x* = 1 − 1/r = <b>${xstar.toFixed(4)}</b> · f′(x*) = 2 − r = <b class="${stable ? "ok" : "bad"}">${slope.toFixed(3)}</b>
         → x* is <b class="${stable ? "ok" : "bad"}">${stable ? "stable" : "unstable"}</b>` +
        (period ? ` · long-run period: <b>${period}</b>` : ` · <b class="bad">no period ≤ 64 (chaos, or very slow convergence near a fork)</b>`);
    }
  }
}
new Cobweb("c1");
new Cobweb("c2", { f2: true });

// ---------------------------------------------------------------- bifurcation explorer
class Explorer {
  constructor(canvasId, map, { lyap = null, marks = false, onPick = null } = {}) {
    this.map = map; this.home = { x: [...map.r], y: [...map.x] };
    this.p = new Plot($(canvasId), { x: [...map.r], y: [...map.x], aspect: 0.55, margin: [10, 12, 24, 40] });
    this.lp = lyap ? new Plot($(lyap), { x: [...map.r], y: [-1.5, 0.75], aspect: 0.16, margin: [6, 12, 20, 40] }) : null;
    this.marks = marks; this.onPick = onPick; this.cursor = null;
    this.p.onresize = () => this.draw(); if (this.lp) this.lp.onresize = () => this.draw();
    this.wire(); this.draw();
  }
  setMap(map) { this.map = map; this.home = { x: [...map.r], y: [...map.x] }; this.reset(); }
  reset() { this.p.x = [...this.home.x]; this.p.y = [...this.home.y]; this.draw(); }
  wire() {
    const cv = this.p.cv; let drag = null, moved = false;
    const loc = e => { const b = cv.getBoundingClientRect(); return [e.clientX - b.left, e.clientY - b.top]; };
    cv.addEventListener("wheel", e => {
      e.preventDefault(); const [mx, my] = loc(e), k = e.deltaY < 0 ? 0.8 : 1.25;
      const ax = this.p.ux(mx), ay = this.p.uy(my);
      this.p.x = this.p.x.map(v => ax + (v - ax) * k); this.p.y = this.p.y.map(v => ay + (v - ay) * k); this.schedule();
    }, { passive: false });
    cv.addEventListener("pointerdown", e => { drag = { at: loc(e), x: [...this.p.x], y: [...this.p.y] }; moved = false; cv.setPointerCapture(e.pointerId); });
    cv.addEventListener("pointermove", e => {
      if (!drag) return; const [mx, my] = loc(e), dx = mx - drag.at[0], dy = my - drag.at[1];
      if (Math.hypot(dx, dy) > 4) moved = true; if (!moved) return;
      const sx = (drag.x[1] - drag.x[0]) / this.p.iw, sy = (drag.y[1] - drag.y[0]) / this.p.ih;
      this.p.x = drag.x.map(v => v - dx * sx); this.p.y = drag.y.map(v => v + dy * sy); this.schedule();
    });
    cv.addEventListener("pointerup", e => { if (drag && !moved && this.onPick) this.onPick(this.p.ux(loc(e)[0])); drag = null; });
    cv.addEventListener("dblclick", () => this.reset());
  }
  schedule() { if (!this.pending) { this.pending = true; requestAnimationFrame(() => { this.pending = false; this.draw(); }); } }
  draw() {
    const p = this.p; p.clear(); drawBifurcation(p, this.map); p.axes({ xt: 6, yt: 4, xl: "r", yl: "x" });
    const vline = (r, col, dash, lab) => { if (r < p.x[0] || r > p.x[1]) return;
      p.line([[r, p.y[0]], [r, p.y[1]]], col, 1.2, 0.85, dash);
      if (lab) { const c = p.ctx; c.fillStyle = col; c.font = "12px system-ui"; c.textAlign = "left"; c.textBaseline = "top"; c.fillText(lab, p.px(r) + 3, p.m[0] + 2); } };
    if (this.marks) { DATA.r.slice(0, 6).forEach((r, i) => vline(r, C.fg, [3, 3], i < 4 ? `r${"₁₂₃₄"[i]}` : "")); vline(R_INF, C.accent, [5, 3], "r∞"); }
    if (this.cursor != null) vline(this.cursor, C.orbit, null, `r = ${this.cursor.toFixed(4)}`);
    if (this.lp) {
      const l = this.lp; l.x = [...p.x]; l.clear(); l.axes({ xt: 6, yt: 2, yl: "λ" });
      l.line([[l.x[0], 0], [l.x[1], 0]], C.muted, 1, 0.6, [3, 3]);
      const n = Math.round(l.iw), pts = [];
      for (let i = 0; i <= n; i++) { const r = l.x[0] + i / n * (l.x[1] - l.x[0]); pts.push([r, Math.max(-1.5, lyapunov(this.map, r, 300, 600))]); }
      for (let i = 1; i < pts.length; i++) l.clip(() => l.line([pts[i - 1], pts[i]], pts[i][1] > 0 ? C.orbit : C.stable, 1.4));
    }
  }
}

const c3 = new Cobweb("c3");
const ex3 = new Explorer("bif3", logistic, { marks: true, onPick: r => { ex3.cursor = r; ex3.draw(); c3.set(Math.min(4, Math.max(0, r))); } });
ex3.cursor = 3.5; ex3.draw(); c3.set(3.5);
$("bif3-reset").onclick = () => ex3.reset();
$("bif3-marks").onchange = e => { ex3.marks = e.target.checked; ex3.draw(); };

// cascade table
{
  const tb = $("cascade-table");
  let html = "<tr><th>n</th><th>period</th><th>rₙ</th><th>Δₙ₋₁ / Δₙ</th></tr>";
  for (let n = 1; n <= 12; n++) {
    html += `<tr><td>${n}</td><td>${2 ** (n - 1)} → ${2 ** n}</td><td>${DATA.r_str[n - 1]}</td>` +
            `<td class="acc">${n >= 3 ? DATA.delta_r[n - 3].toFixed(9) : ""}</td></tr>`;
  }
  tb.innerHTML = html;
}

// ---------------------------------------------------------------- chaos: two orbits
{
  const top = new Plot($("sens-top"), { x: [0, 60], y: [0, 1], aspect: 0.3, margin: [10, 12, 22, 40] });
  const bot = new Plot($("sens-bot"), { x: [0, 60], y: [-14, 0], aspect: 0.3, margin: [10, 12, 22, 40] });
  let r = 3.9, k = 8;
  const draw = () => {
    const a = orbit(f, r, 0.2, 60), b = orbit(f, r, 0.2 + 10 ** -k, 60);
    top.clear(); top.axes({ xt: 6, yt: 2, yl: "xₙ" });
    top.line(a.map((v, i) => [i, v]), C.orbit, 1.5); top.line(b.map((v, i) => [i, v]), C.diag, 1.2, 0.9);
    bot.clear(); bot.axes({ xt: 6, yt: 7, yl: "log₁₀ εₙ" });
    const e = a.map((v, i) => [i, Math.max(-14, Math.log10(Math.abs(v - b[i]) + 1e-300))]);
    e.forEach(([i, v]) => bot.dot(i, v, C.accent, 2.2));
    const lam = lyapunov(logistic, r, 500, 4000);
    bot.line([[0, -k], [60, -k + 60 * lam / Math.LN10]], C.map, 1.2, 0.8, [5, 4]);
    const sep = e.findIndex(([, v]) => v > -1.3);
    $("sens-read").innerHTML = `λ(r) = <b class="${lam > 0 ? "bad" : "ok"}">${lam.toFixed(3)}</b> · ` +
      (lam > 0 ? `the orbits separate after about <b>${sep < 0 ? "> 60" : sep}</b> steps (≈ k·ln10/λ = ${(k * Math.LN10 / lam).toFixed(0)})`
               : `λ < 0: both orbits converge to the same cycle, the error dies out`);
  };
  top.onresize = bot.onresize = draw;
  bind("sens-r", v => { r = v; draw(); })(); bind("sens-k", v => { k = v; draw(); })();
}
const ex4 = new Explorer("bif4", logistic, { lyap: "lyap4" });
$("bif4-reset").onclick = () => ex4.reset();
$("bif4-window").onclick = () => { ex4.p.x = [3.8284, 3.8572]; ex4.p.y = [0.455, 0.555]; ex4.draw(); };

// ---------------------------------------------------------------- universality
{
  const ex5 = new Explorer("bif5", MAPS.logistic);
  const g = new Plot($("map5"), { x: [0, 1], y: [0, 1], aspect: 0.75, margin: [10, 10, 22, 32] });
  const show = key => {
    const m = MAPS[key]; ex5.setMap(m); g.x = [...m.x]; g.y = [...m.x];
    const par = m.r[0] + 0.75 * (m.r[1] - m.r[0]);
    g.clear(); g.axes({ xt: 2, yt: 2 }); g.fn(x => m.f(par, x), key === "quartic" ? C.orbit : C.map, 2.5);
    const d = UNIV[key].delta;
    $("univ-read").innerHTML = `f(x) = ${m.name} map · δ estimated from its own cascade: <b class="${key === "quartic" ? "bad" : "ok"}">${d.toFixed(6)}</b>` +
      (key === "quartic" ? " (flat top → another universality class)" : "");
  };
  $("univ-map").onchange = e => show(e.target.value);
  g.onresize = () => show($("univ-map").value);
  show("logistic");
  $("bif5-reset").onclick = () => ex5.reset();
}

// ---------------------------------------------------------------- renormalisation
{
  const L = new Plot($("ren-left"), { x: [0, 1], y: [0, 1], aspect: 1, margin: [10, 10, 22, 32] });
  const Rt = new Plot($("ren-right"), { x: [-0.5, 0.5], y: [-0.5, 0.5], aspect: 1, margin: [10, 10, 22, 32] });
  const cols = [C.map, C.accent, C.stable, C.diag, C.orbit, C.fg];
  let n = 1;
  const draw = () => {
    const R = DATA.R[n], fk = x => { for (let i = 0; i < 2 ** n; i++) x = f(R, x); return x; };
    L.clear(); L.axes({ xt: 2, yt: 2 }); L.line([[0, 0], [1, 1]], C.diag, 1.2);
    L.fn(fk, cols[n % 6], 1.8, 1500);
    const s = 1 / Math.abs(ALPHA) ** n;
    L.line([[0.5 - s / 2, 0.5 - s / 2], [0.5 + s / 2, 0.5 - s / 2], [0.5 + s / 2, 0.5 + s / 2], [0.5 - s / 2, 0.5 + s / 2], [0.5 - s / 2, 0.5 - s / 2]], C.fg, 1.5);
    Rt.clear(); Rt.axes({ xt: 2, yt: 2 });
    const ys = DATA.renorm_y;
    for (let k = 0; k <= n; k++) {
      const pts = ys.map((y, i) => [y, DATA.renorm_curves[k][i]]).filter(([y]) => Math.abs(y) <= 0.5);
      Rt.clip(() => Rt.line(pts, cols[k % 6], k === n ? 2.5 : 1.2, k === n ? 1 : 0.45));
    }
    $("ren-read").innerHTML = `R<sub>${n}</sub> = <b>${DATA.R[n].toFixed(10)}</b> · showing f<sup>${2 ** n}</sup> · box size 1/|α|<sup>${n}</sup> = <b>${s.toPrecision(3)}</b>`;
  };
  L.onresize = Rt.onresize = draw;
  bind("ren-n", v => { n = v; draw(); })();
}

// ---------------------------------------------------------------- epilogue: Mandelbrot
{
  const quad = { f: (c, z) => z * z + c, r: [-2.05, 0.35], x: [-2, 2], x0: 0 };
  const top = new Plot($("man-top"), { x: quad.r, y: quad.x, aspect: 0.25, margin: [6, 12, 4, 12] });
  const bot = new Plot($("man-bot"), { x: quad.r, y: [-0.6, 0.6], aspect: 0.3, margin: [4, 12, 20, 12] });
  const draw = () => {
    top.clear(); drawBifurcation(top, quad);
    const h = 0.5 * (bot.x[1] - bot.x[0]) * bot.ih / bot.iw; bot.y = [-h, h];
    bot.clear();
    const dpr = bot.dpr, W = Math.round(bot.iw * dpr), H = Math.round(bot.ih * dpr), img = bot.ctx.createImageData(W, H);
    for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
      const cr = bot.x[0] + (i + 0.5) / W * (bot.x[1] - bot.x[0]), ci = bot.y[1] - (j + 0.5) / H * (bot.y[1] - bot.y[0]);
      let zr = 0, zi = 0, k = 0;
      for (; k < 200 && zr * zr + zi * zi < 16; k++) { const t = zr * zr - zi * zi + cr; zi = 2 * zr * zi + ci; zr = t; }
      const [r, g, b] = k === 200 ? [255, 244, 214] : colormap(Math.min(1, 1.6 * Math.log1p(k) / Math.log1p(200)) * 0.85);
      const o = 4 * (j * W + i); img.data[o] = r; img.data[o + 1] = g; img.data[o + 2] = b; img.data[o + 3] = 255;
    }
    bot.ctx.putImageData(img, Math.round(bot.m[3] * dpr), Math.round(bot.m[0] * dpr)); bot.axes({ xt: 8, yt: 2 });
    for (const [c, lab] of [[-0.75, "r₁"], [-1.25, "r₂"], [-1.401155, "r∞"], [-1.75, "1+√8"]]) {
      top.line([[c, -2], [c, 2]], C.fg, 1, 0.7, [3, 3]); bot.line([[c, bot.y[0]], [c, bot.y[1]]], C.fg, 1, 0.7, [3, 3]);
      const t = top.ctx; t.fillStyle = C.fg; t.font = "12px system-ui"; t.textAlign = "left"; t.textBaseline = "top"; t.fillText(lab, top.px(c) + 3, 8);
    }
  };
  top.onresize = bot.onresize = draw; draw();
}
