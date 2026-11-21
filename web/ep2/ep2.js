import { C, Plot } from "../assets/plot.js";
import { FractalView } from "./fractal-gl.js";

const $ = id => document.getElementById(id);
const BULBS = await (await fetch("../data/bulbs.json")).json();
const M_WIN = [-2.25, 0.75, -1.25, 1.25], Z_WIN = [-2.0, 2.0, -1.6667, 1.6667];
const PHI = (Math.sqrt(5) - 1) / 2;

// ------------------------------------------------------------ complex helpers (double precision)
const cmul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
const cadd = (a, b) => [a[0] + b[0], a[1] + b[1]];
const cabs = a => Math.hypot(a[0], a[1]);
const cexp = t => [Math.cos(t), Math.sin(t)];
const cardioid = t => { const w = cexp(2 * Math.PI * t).map(v => v / 2); return [w[0] - (w[0] * w[0] - w[1] * w[1]), w[1] - 2 * w[0] * w[1]]; };
const fmt = c => `${c[0].toFixed(4)} ${c[1] < 0 ? "−" : "+"} ${Math.abs(c[1]).toFixed(4)}i`;

function orbitInfo(c, n = 60) {
  let z = [0, 0]; const pts = [[0, 0]]; let esc = -1;
  for (let k = 1; k <= 3000; k++) { z = cadd(cmul(z, z), c); if (k <= n) pts.push(z); if (cabs(z) > 2) { esc = k; break; } }
  let period = 0;
  if (esc < 0) { const a = z; for (let k = 1; k <= 64; k++) { z = cadd(cmul(z, z), c); if (cabs([z[0] - a[0], z[1] - a[1]]) < 1e-9) { period = k; break; } } }
  return { pts, esc, period };
}

function bulbCentre(p, q) {
  const th = p / q, root = cardioid(th), d = cardioid(th + 1e-6);
  let nrm = [-(root[1] - d[1]), root[0] - d[0]]; const L = cabs(nrm); nrm = nrm.map(v => v / L);
  if (cabs(cadd(root, nrm.map(v => v * 0.01))) < cabs(root)) nrm = nrm.map(v => -v);
  let c = cadd(root, nrm.map(v => v * Math.sin(Math.PI * p / q) / (q * q)));
  for (let it = 0; it < 100; it++) {
    let z = [0, 0], dz = [0, 0];
    for (let k = 0; k < q; k++) { dz = cadd(cmul([2 * z[0], 2 * z[1]], dz), [1, 0]); z = cadd(cmul(z, z), c); }
    const den = dz[0] ** 2 + dz[1] ** 2, step = [(z[0] * dz[0] + z[1] * dz[1]) / den, (z[1] * dz[0] - z[0] * dz[1]) / den];
    c = [c[0] - step[0], c[1] - step[1]]; if (cabs(step) < 1e-14) break;
  }
  return { c, size: cabs([c[0] - root[0], c[1] - root[1]]) };
}

// ------------------------------------------------------------ section 1: squaring
{
  const P = new Plot($("sq"), { x: [-2.4, 2.4], y: [-1.6, 1.6], aspect: 0.66, margin: [8, 8, 20, 28] });
  let z = [1.1, 0.5];
  const arrow = (a, col, w = 2.5) => { const c = P.ctx, x0 = P.px(0), y0 = P.py(0), x1 = P.px(a[0]), y1 = P.py(a[1]);
    c.strokeStyle = c.fillStyle = col; c.lineWidth = w; c.beginPath(); c.moveTo(x0, y0); c.lineTo(x1, y1); c.stroke();
    const ang = Math.atan2(y1 - y0, x1 - x0); c.beginPath(); c.moveTo(x1, y1);
    c.lineTo(x1 - 10 * Math.cos(ang - 0.4), y1 - 10 * Math.sin(ang - 0.4)); c.lineTo(x1 - 10 * Math.cos(ang + 0.4), y1 - 10 * Math.sin(ang + 0.4)); c.fill(); };
  const draw = () => {
    P.clear(); P.axes({ xt: 6, yt: 4 });
    const circ = []; for (let i = 0; i <= 100; i++) { const t = i / 100 * 2 * Math.PI; circ.push([Math.cos(t), Math.sin(t)]); }
    P.line(circ, C.diag, 1.2, 0.8);
    const z2 = cmul(z, z); arrow(z, C.map); P.clip(() => arrow(z2, C.orbit));
    $("sq-read").innerHTML = `z = <b>${fmt(z)}</b>, |z| = <b>${cabs(z).toFixed(3)}</b>, arg z = <b>${(Math.atan2(z[1], z[0]) * 180 / Math.PI).toFixed(1)}°</b> &nbsp;→&nbsp; z² : |z²| = <b>${cabs(z2).toFixed(3)}</b>, arg z² = <b>${(Math.atan2(z2[1], z2[0]) * 180 / Math.PI).toFixed(1)}°</b>`;
  };
  const set = e => { const b = P.cv.getBoundingClientRect(); z = [P.ux(e.clientX - b.left), P.uy(e.clientY - b.top)]; draw(); };
  P.cv.addEventListener("pointerdown", e => { P.cv.setPointerCapture(e.pointerId); set(e); });
  P.cv.addEventListener("pointermove", e => { if (e.buttons) set(e); });
  P.onresize = draw; draw();
}

// ------------------------------------------------------------ the M | z-plane pair
class Pair {
  constructor(prefix, { julia = true, onChange = null } = {}) {
    this.p = prefix; this.julia = julia; this.onChange = onChange;
    this.M = new FractalView($(prefix + "-m"), { mode: 0, win: M_WIN });
    this.Z = new FractalView($(prefix + "-z"), { mode: 1, win: Z_WIN });
    this.mo = $(prefix + "-mo"); this.zo = $(prefix + "-zo");
    this.c = [-0.12256, 0.74486]; this.overlays = { cardioid: false };
    this.M.ondraw = () => this.drawM(); this.Z.ondraw = () => this.drawZ();
    this.wire(this.M, true); this.wire(this.Z, false);
    this.setC(this.c);
  }
  wire(V, isM) {
    const cv = V.cv, loc = e => { const b = cv.getBoundingClientRect(); return [e.clientX - b.left, e.clientY - b.top]; };
    cv.addEventListener("wheel", e => { e.preventDefault(); const [x, y] = loc(e); V.zoomAt(x, y, e.deltaY < 0 ? 0.8 : 1.25); }, { passive: false });
    cv.addEventListener("dblclick", () => V.reset());
    if (isM) {
      cv.addEventListener("pointerdown", e => { cv.setPointerCapture(e.pointerId); this.setC(V.toC(...loc(e))); });
      cv.addEventListener("pointermove", e => { if (e.buttons) this.setC(V.toC(...loc(e))); });
    }
  }
  setC(c) {
    this.c = c; this.info = orbitInfo(c);
    if (this.julia) { this.Z.c = c; this.Z.mode = 1; } else { this.Z.c = [0, 0]; }
    this.Z.draw(); this.M.draw();
    if (this.onChange) this.onChange(this);
  }
  layer(cv, V) { cv.width = V.cv.width; cv.height = V.cv.height; cv.style.width = V.W + "px"; cv.style.height = V.H + "px";
    const g = cv.getContext("2d"); const s = V.cv.width / V.W; g.setTransform(s, 0, 0, s, 0, 0); g.clearRect(0, 0, V.W, V.H); return g; }
  drawM() {
    if (!this.mo) return; const g = this.layer(this.mo, this.M), [x, y] = this.M.toPx(...this.c);
    if (this.overlays.cardioid) {
      g.strokeStyle = C.accent; g.lineWidth = 2; g.beginPath();
      for (let i = 0; i <= 400; i++) { const [a, b] = this.M.toPx(...cardioid(i / 400)); i ? g.lineTo(a, b) : g.moveTo(a, b); }
      g.stroke(); g.strokeStyle = C.diag; g.beginPath();
      for (let i = 0; i <= 200; i++) { const t = i / 200 * 2 * Math.PI, [a, b] = this.M.toPx(-1 + 0.25 * Math.cos(t), 0.25 * Math.sin(t)); i ? g.lineTo(a, b) : g.moveTo(a, b); }
      g.stroke();
    }
    g.lineWidth = 2.5; g.strokeStyle = C.orbit; g.fillStyle = C.fg; g.beginPath(); g.arc(x, y, 5, 0, 7); g.fill(); g.stroke();
  }
  drawZ() {
    if (!this.zo) return; const g = this.layer(this.zo, this.Z), pts = this.info.pts.map(p => this.Z.toPx(...p));
    if (!this.julia) { g.fillStyle = "rgba(14,17,22,1)"; g.fillRect(0, 0, this.Z.W, this.Z.H);
      g.strokeStyle = C.line; g.lineWidth = 1; g.beginPath(); const [ox, oy] = this.Z.toPx(0, 0);
      g.moveTo(0, oy); g.lineTo(this.Z.W, oy); g.moveTo(ox, 0); g.lineTo(ox, this.Z.H); g.stroke();
      g.strokeStyle = C.diag; g.beginPath(); const r = this.Z.toPx(2, 0)[0] - ox; g.arc(ox, oy, r, 0, 7); g.stroke(); }
    g.strokeStyle = "rgba(230,230,230,0.35)"; g.lineWidth = 1.2; g.beginPath(); pts.forEach(([a, b], i) => i ? g.lineTo(a, b) : g.moveTo(a, b)); g.stroke();
    pts.forEach(([a, b], i) => { g.fillStyle = i === 0 ? C.fg : (this.julia ? C.fg : C.orbit); g.beginPath(); g.arc(a, b, i === 0 ? 3.5 : 2.5, 0, 7); g.fill(); });
  }
}

const verdict = ({ esc, period }) => esc > 0
  ? `the orbit of 0 <b class="bad">escapes</b> (leaves |z| ≤ 2 after ${esc} steps) → c ∉ M`
  : `the orbit of 0 <b class="ok">stays bounded</b> → c ∈ M` + (period ? `, attracting cycle of period <b>${period}</b>` : ` (no attracting cycle found: boundary or Siegel-type point)`);

// section 2–5: orbits, cardioid, bulbs
const A = new Pair("a", { julia: false, onChange: p => { $("a-read").innerHTML = `c = <b>${fmt(p.c)}</b> · ` + verdict(p.info); } });
A.setC([0.2, 0.35]);
$("a-periods").onchange = e => { A.M.periods = e.target.checked ? 1 : 0; A.M.draw(); };
$("a-card").onchange = e => { A.overlays.cardioid = e.target.checked; A.M.draw(); };
$("a-reset").onclick = () => { A.M.reset(); A.Z.reset(); };
const theta = $("a-theta");
theta.oninput = () => { const t = +theta.value, k = +$("a-k").value, w = cexp(2 * Math.PI * t).map(v => v * k / 2);
  $("a-theta-out").value = t.toFixed(3);
  A.setC([w[0] - (w[0] * w[0] - w[1] * w[1]), w[1] - 2 * w[0] * w[1]]); };
$("a-k").oninput = () => { $("a-k-out").value = (+$("a-k").value).toFixed(2); theta.oninput(); };
$("a-bulb").onclick = () => {
  const p = +$("a-p").value, q = +$("a-q").value;
  if (!(q >= 2 && p >= 1 && p < q)) { $("a-read").textContent = "Choose 1 ≤ p < q."; return; }
  const b = bulbCentre(p, q); A.M.periods = 1; $("a-periods").checked = true;
  A.M.center(b.c[0], b.c[1], Math.max(14 * b.size, 1e-3)); A.setC(b.c);
  $("a-read").innerHTML += ` · bulb ${p}/${q}: size ≈ <b>${b.size.toExponential(2)}</b>, sin(πp/q)/q² = <b>${(Math.sin(Math.PI * p / q) / q / q).toExponential(2)}</b>`;
};
$("a-mini").onclick = () => { A.M.periods = 1; $("a-periods").checked = true; A.M.center(-1.7548776662, 0, 0.06); A.setC([-1.7548776662, 0]); };

// Farey & delta tables
{
  const by = Object.fromEntries(BULBS.bulbs.map(b => [`${b.p}/${b.q}`, b]));
  const rows = [["1/3", "1/2", "2/5"], ["1/3", "2/5", "3/8"], ["2/5", "1/2", "3/7"], ["1/4", "1/3", "2/7"]].map(([a, b, m]) => {
    const fa = a.split("/").map(Number), fb = b.split("/").map(Number);
    const inside = BULBS.bulbs.filter(x => x.p / x.q > fa[0] / fa[1] && x.p / x.q < fb[0] / fb[1]);
    const big = inside.reduce((u, v) => v.size > u.size ? v : u);
    return `<tr><td>${a} and ${b}</td><td>${big.p}/${big.q}</td><td>${m}</td><td class="acc">${big.p + "/" + big.q === m ? "✓" : "✗"}</td></tr>`;
  });
  $("farey").innerHTML = "<tr><th>between the bulbs</th><th>largest bulb (computed)</th><th>Farey sum</th><th></th></tr>" + rows.join("");
  const d = BULBS.real_delta;
  $("delta").innerHTML = "<tr><th>n</th><th>bulb centre cₙ (period 2ⁿ)</th><th>(cₙ₋₁ − cₙ)/(cₙ − cₙ₊₁)</th></tr>" +
    BULBS.real_centres.slice(0, 10).map((c, n) => `<tr><td>${n}</td><td>${c.toFixed(10)}</td><td class="acc">${n >= 1 && d[n - 1] ? d[n - 1].toFixed(6) : ""}</td></tr>`).join("");
}

// section 6: Julia explorer
const GALLERY = [
  ["cauliflower", [0.25, 0], "The cusp of the cardioid. Inside the cardioid every Julia set is a single blob bounded by a closed curve; at the cusp it becomes this cauliflower."],
  ["San Marco", [-0.75, 0], "Where the cardioid meets the period-2 disk (Part 1's r₁ = 3): pinched at infinitely many points."],
  ["basilica", [-1, 0], "Centre of the period-2 bulb: the orbit of 0 is the 2-cycle 0 → −1 → 0."],
  ["rabbit", [-0.122561166876654, 0.744861766619744], "Douady's rabbit, centre of the 1/3 bulb: three ears meet at each junction and the dynamics rotates them by a third of a turn."],
  ["Siegel disk", cardioid(1 - PHI), "On the cardioid at the golden angle: no cycle; orbits inside turn forever around a hidden centre by an irrational angle."],
  ["dendrite (c = i)", [0, 1], "0 → i → −1+i → −i → −1+i … never returns to 0: no interior at all, a tree of curves."],
  ["airplane", [-1.754877666246693, 0], "Centre of the period-3 mini-Mandelbrot on the real axis (Part 1's period-3 window)."],
  ["spiral", [-0.7436423016578859, 0.13182651981259472], "Centre of the period-39 mini-Mandelbrot of the video's cold open, in seahorse valley."],
  ["dragon (outside!)", [-0.8, 0.156], "Just outside M: the orbit of 0 escapes after 252 steps. It looks solid, but raise the iterations: it is dust."],
  ["dust", [0.45, 0.35], "Far outside M: a Cantor set — infinitely many points, no two connected."],
];
const J = new Pair("j", { julia: true, onChange: p => {
  const it = p.info; $("j-read").innerHTML = `c = <b>${fmt(p.c)}</b> · ` + verdict(it) +
    ` · K<sub>c</sub> is <b class="${it.esc > 0 ? "bad" : "ok"}">${it.esc > 0 ? "a cloud of dust (disconnected)" : "connected"}</b>`; } });
$("gallery").innerHTML = GALLERY.map(([n], i) => `<button data-i="${i}">${n}</button>`).join("");
$("gallery").onclick = e => { const i = e.target.dataset.i; if (i == null) return; const [n, c, txt] = GALLERY[i];
  J.setC(c); $("j-note").innerHTML = `<b>${n}.</b> ${txt}`; };
$("j-it").oninput = () => { const v = +$("j-it").value; $("j-it-out").value = v; J.Z.maxit = v; J.Z.draw(); };
$("j-mosaic").onchange = e => { J.M.mode = e.target.checked ? 2 : 0; J.M.maxit = e.target.checked ? 150 : 300; J.M.draw(); };
$("j-tiles").oninput = () => { const n = +$("j-tiles").value; $("j-tiles-out").value = n; J.M.tiles = [n, Math.round(n * 2.5 / 3)]; J.M.draw(); };
$("j-reset").onclick = () => { J.M.reset(); J.Z.reset(); };
document.querySelector('#gallery button[data-i="3"]').click();
