import { C, Plot } from "../assets/plot.js";

const $ = id => document.getElementById(id);
const D = await (await fetch("../data/ep4.json")).json();
const TAU = 2 * Math.PI, PI = Math.PI;
const REG = ["#5DA9E9", "#6CCB8B", "#C792EA", "#F2A541", "#7FD1C7"];
const wrapP = p => ((p + PI) % TAU + TAU) % TAU - PI;
const wrapT = t => (t % TAU + TAU) % TAU;
const mulberry = s => () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };

// ------------------------------------------------------------ 1. phase portrait
const ph = new Plot($("ph"), { x: [0, TAU], y: [-PI, PI], aspect: 1, margin: [8, 8, 22, 30] });
let K = +$("K").value, orbits = [], golden = null;
function stdOrbit(th, p, k, n) {
  const pts = new Float32Array(2 * n); let u = 1, v = 0, s = 0;
  for (let i = 0; i < n; i++) {
    const c = k * Math.cos(th); v += c * u; u += v; const r = Math.hypot(u, v); s += Math.log(r); u /= r; v /= r;
    p += k * Math.sin(th); th = wrapT(th + p); pts[2 * i] = th; pts[2 * i + 1] = wrapP(p);
  }
  return { pts, lyap: s / n };
}
function addOrbit(th, p, n = 2500) {
  const o = stdOrbit(th, p, K, n);
  o.color = o.lyap > 0.03 ? C.orbit : REG[orbits.length % REG.length];
  orbits.push({ ...o, th, p }); drawPh();
}
function fill() {
  const rnd = mulberry(7); orbits = [];
  for (let i = 0; i < 70; i++) {
    const th = i % 2 ? PI : 0, p = -PI + (i + 0.5) / 70 * TAU;
    const o = stdOrbit(th, p, K, 1500); o.color = o.lyap > 0.03 ? C.orbit : REG[i % REG.length]; orbits.push(o);
  }
  for (let i = 0; i < 40; i++) { const o = stdOrbit(rnd() * TAU, (rnd() - 0.5) * TAU, K, 1500);
    o.color = o.lyap > 0.03 ? C.orbit : REG[i % REG.length]; orbits.push(o); }
  drawPh();
}
function drawPh() {
  ph.clear(); ph.axes({ xt: 2, yt: 2, xl: "θ", yl: "p" });
  const c = ph.ctx;
  ph.clip(() => {
    for (const o of orbits) {
      c.fillStyle = o.color; c.globalAlpha = 0.85;
      for (let i = 0; i < o.pts.length; i += 2) c.fillRect(ph.px(o.pts[i]) - 0.6, ph.py(o.pts[i + 1]) - 0.6, 1.2, 1.2);
    }
    if (golden) { c.fillStyle = "#FFF4D6"; c.globalAlpha = 1;
      for (let i = 0; i < golden.length; i += 2) c.fillRect(ph.px(golden[i]) - 1, ph.py(golden[i + 1]) - 1, 2, 2); }
    c.globalAlpha = 1;
  });
  const tr = 2 - K;
  $("ph-read").innerHTML = `K = <b>${K.toFixed(4)}</b> · centre (π, 0): tr M = 2 − K = <b>${tr.toFixed(3)}</b> → ` +
    (Math.abs(tr) < 2 ? `<span class="ok">stable</span>` : `<span class="bad">unstable (period doubled)</span>`) +
    ` · golden curve ${K < 0.971635 ? '<span class="ok">exists</span>' : '<span class="bad">broken</span>'} (K_c = 0.971635) · ${orbits.length} orbits`;
}
ph.onresize = drawPh;
// symmetric orbit P/q by 1-D shooting (exact tangent map), continued in K
function mono(th, p, k, q) {
  let a = 1, b = 0, c = 0, d = 1;
  for (let i = 0; i < q; i++) { const s = k * Math.cos(th); c += s * a; d += s * b; a += c; b += d; p += k * Math.sin(th); th += p; }
  return [th, p, a, b, c, d];
}
function goldenOrbit(k, P = 377, q = 610, th0 = 0) {
  let p0 = TAU * P / q; const m = q % 2 ? (q + 1) / 2 : q / 2;
  for (let j = 1; j <= 80; j++) {
    const kk = k * j / 80;
    for (let it = 0; it < 40; it++) {
      const [t, p, , b, , d] = mono(th0, p0, kk, m);
      const g = q % 2 ? 2 * t - p - 2 * th0 - TAU * P : t - th0 - PI * P, dg = q % 2 ? 2 * b - d : b;
      const st = g / dg; p0 -= st; if (!isFinite(p0)) return null; if (Math.abs(st) < 1e-13) break;
    }
  }
  const out = new Float32Array(2 * q); let th = th0, p = p0;
  for (let i = 0; i < q; i++) { p += k * Math.sin(th); th = wrapT(th + p); out[2 * i] = th; out[2 * i + 1] = wrapP(p); }
  return out;
}
function setK(v) {
  K = v; $("K").value = v; $("K-o").textContent = v.toFixed(4);
  golden = $("gold").checked ? (K <= 0.9716 ? goldenOrbit(K) : null) : null;
  fill();
}
$("K").oninput = e => setK(+e.target.value);
$("gold").onchange = () => setK(K);
$("fill").onclick = fill; $("clr").onclick = () => { orbits = []; drawPh(); };
for (const v of [0, 0.3, 0.6, 0.9, 0.971635, 1.2, 2, 4.3, 5, 6.5]) {
  const b = document.createElement("button"); b.textContent = v === 0.971635 ? "K_c" : v; b.onclick = () => setK(v);
  $("presets").appendChild(b);
}
$("ph").addEventListener("click", e => { const r = $("ph").getBoundingClientRect();
  addOrbit(ph.ux(e.clientX - r.left), ph.uy(e.clientY - r.top)); });
setK(K);

// ------------------------------------------------------------ 2. Greene table
$("gtab").innerHTML = `<tr><th>P/q</th><th>K_n (R = 1/4)</th><th>K_n − K_(n−1)</th></tr>` +
  D.greene.map((g, i) => `<tr><td>${g.P}/${g.q}</td><td class="acc">${g.K.toFixed(12)}</td><td>${i ? (g.K - D.greene[i - 1].K).toExponential(2) : ""}</td></tr>`).join("") +
  `<tr><td>limit</td><td class="acc">0.971635…</td><td>accepted: 0.9716354</td></tr>`;

// ------------------------------------------------------------ 3. random walk
const walk = new Plot($("walk"), { x: [0, 200], y: [0, 1], aspect: 0.75, margin: [10, 12, 26, 48] });
const dk = new Plot($("dk"), { x: [0, 30], y: [0, 3], aspect: 0.75, margin: [10, 12, 26, 30] });
let Kw = 5, gw = [];
function simWalk() {
  const rnd = mulberry(3), N = 3000, n = 200, th = new Float64Array(N), p = new Float64Array(N), p0 = new Float64Array(N);
  for (let i = 0; i < N; i++) { th[i] = rnd() * TAU; p[i] = p0[i] = rnd() * TAU; }
  gw = [[0, 0]];
  for (let t = 1; t <= n; t++) { let s = 0;
    for (let i = 0; i < N; i++) { p[i] += Kw * Math.sin(th[i]); th[i] = wrapT(th[i] + p[i]); s += (p[i] - p0[i]) ** 2; }
    gw.push([t, s / N]); }
}
function drawWalk() {
  const ymax = Math.max(gw[gw.length - 1][1], Kw * Kw / 2 * 200) * 1.1;
  walk.y = [0, ymax]; walk.clear(); walk.axes({ xt: 4, yt: 4, xl: "n", yl: "⟨(p_n − p_0)²⟩" });
  walk.clip(() => { walk.line([[0, 0], [200, Kw * Kw / 2 * 200]], C.diag, 1.5, 1, [5, 4]); walk.line(gw, C.orbit, 2); });
  const n = gw.length - 1, D_ = gw[n][1] / n;
  $("walk-read").innerHTML = `K = <b>${Kw.toFixed(2)}</b> · measured D = ⟨Δp²⟩/n = <b>${D_.toFixed(2)}</b> · K²/2 = <b>${(Kw * Kw / 2).toFixed(2)}</b> · ratio <b>${(D_ / (Kw * Kw / 2)).toFixed(3)}</b>` +
    (Kw < 0.9716 ? ` · <span class="bad">below K_c: the walk is blocked by KAM curves</span>` : "");
}
function drawDk() {
  dk.clear(); dk.axes({ xt: 6, yt: 3, xl: "K", yl: "D / (K²/2)" });
  dk.clip(() => {
    dk.line([[0, 1], [30, 1]], C.muted, 1, 1, [4, 4]);
    dk.line(D.diff.K.map((k, i) => [k, D.diff.rw[i]]), C.map, 2);
    D.diff.K.forEach((k, i) => dk.dot(k, Math.min(D.diff.ratio[i], 2.95), C.orbit, 1.8));
    dk.line([[Kw, 0], [Kw, 3]], C.accent, 1.5);
  });
}
function setKw(v) { Kw = v; $("Kw").value = v; $("Kw-o").textContent = v.toFixed(2); simWalk(); drawWalk(); drawDk(); }
walk.onresize = drawWalk; dk.onresize = drawDk;
$("Kw").oninput = e => setKw(+e.target.value);
$("dk").addEventListener("click", e => { const r = $("dk").getBoundingClientRect();
  setKw(Math.max(0.5, Math.min(30, dk.ux(e.clientX - r.left)))); });
setKw(5);

// ------------------------------------------------------------ 4. Henon + doubling table
const hen = new Plot($("hen"), { x: [-0.1, 0.7], y: [-0.7, 0.1], aspect: 1, margin: [8, 8, 22, 34] });
let A = 3.3, horb = [];
function henOrbit(x, y, a, n = 2000) {
  const pts = new Float32Array(2 * n); let u = 1, v = 0, s = 0;
  for (let i = 0; i < n; i++) { [u, v] = [-2 * a * x * u + v, -u]; const r = Math.hypot(u, v); s += Math.log(r); u /= r; v /= r;
    [x, y] = [1 - a * x * x + y, -x]; if (Math.abs(x) > 8) return null; pts[2 * i] = x; pts[2 * i + 1] = y; }
  return { pts, color: s / n > 0.03 ? C.orbit : REG[horb.length % REG.length] };
}
function hfill() { const rnd = mulberry(11); horb = [];
  for (let i = 0; i < 1500 && horb.length < 140; i++) { const o = henOrbit(-0.1 + 0.8 * rnd(), -0.7 + 0.8 * rnd(), A, 1500); if (o) horb.push(o); }
  drawHen(); }
function drawHen() {
  hen.clear(); hen.axes({ xt: 4, yt: 4, xl: "x", yl: "y" }); const c = hen.ctx;
  hen.clip(() => { for (const o of horb) { c.fillStyle = o.color;
    for (let i = 0; i < o.pts.length; i += 2) c.fillRect(hen.px(o.pts[i]) - 0.6, hen.py(o.pts[i + 1]) - 0.6, 1.2, 1.2); } });
}
hen.onresize = drawHen;
$("a").oninput = e => { A = +e.target.value; $("a-o").textContent = A.toFixed(3); hfill(); };
$("hfill").onclick = hfill;
$("hen").addEventListener("click", e => { const r = $("hen").getBoundingClientRect();
  const o = henOrbit(hen.ux(e.clientX - r.left), hen.uy(e.clientY - r.top), A); if (o) { horb.push(o); drawHen(); } });
$("a-o").textContent = A.toFixed(3); hfill();
$("dtab").innerHTML = `<tr><th>k</th><th>period</th><th>a_k (multipliers −1)</th><th>δ_k</th></tr>` +
  D.a_k.map((a, i) => `<tr><td>${i + 1}</td><td>${D.periods[i]}</td><td>${a.toFixed(12)}</td><td class="acc">${i > 0 && i < D.a_k.length - 1 ? D.delta_k[i - 1].toFixed(5) : ""}</td></tr>`).join("") +
  `<tr><td colspan="3">limit (area-preserving)</td><td class="acc">8.72110</td></tr><tr><td colspan="3">Part 1 (dissipative)</td><td>4.66920</td></tr>`;

// ------------------------------------------------------------ 5. quantum kicked rotor (FFT)
const NQ = 2048, LOG = Math.log2(NQ);
const rev = new Uint32Array(NQ); for (let i = 0; i < NQ; i++) { let r = 0; for (let b = 0; b < LOG; b++) r |= ((i >> b) & 1) << (LOG - 1 - b); rev[i] = r; }
function fft(re, im, inv) {
  for (let i = 0; i < NQ; i++) { const j = rev[i]; if (j > i) { [re[i], re[j]] = [re[j], re[i]]; [im[i], im[j]] = [im[j], im[i]]; } }
  for (let len = 2; len <= NQ; len <<= 1) {
    const ang = (inv ? 2 : -2) * PI / len, wr = Math.cos(ang), wi = Math.sin(ang);
    for (let i = 0; i < NQ; i += len) { let cr = 1, ci = 0;
      for (let j = 0; j < len / 2; j++) { const a = i + j, b = a + len / 2;
        const xr = re[b] * cr - im[b] * ci, xi = re[b] * ci + im[b] * cr;
        re[b] = re[a] - xr; im[b] = im[a] - xi; re[a] += xr; im[a] += xi;
        const t = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = t; } } }
  if (inv) for (let i = 0; i < NQ; i++) { re[i] /= NQ; im[i] /= NQ; }
}
const prof = new Plot($("prof"), { x: [-NQ / 2, NQ / 2], y: [-8, 0], aspect: 0.75, margin: [10, 12, 26, 30] });
const m2p = new Plot($("m2"), { x: [0, 1000], y: [0, 1], aspect: 0.75, margin: [10, 12, 26, 52] });
const mOf = j => (j < NQ / 2 ? j : j - NQ);
let Q = null, raf = 0;
function startQ() {
  const k = +$("kq").value, h = +$("hq").value, NC = 4000, rnd = mulberry(5);
  const re = new Float64Array(NQ), im = new Float64Array(NQ); re[0] = 1;
  const kr = new Float64Array(NQ), ki = new Float64Array(NQ), fr = new Float64Array(NQ), fi = new Float64Array(NQ);
  for (let j = 0; j < NQ; j++) { const t = TAU * j / NQ; kr[j] = Math.cos(k * Math.cos(t)); ki[j] = -Math.sin(k * Math.cos(t));
    const m = mOf(j), ph_ = (h * m * m / 2) % TAU; fr[j] = Math.cos(ph_); fi[j] = -Math.sin(ph_); }
  const th = new Float64Array(NC), p = new Float64Array(NC); for (let i = 0; i < NC; i++) th[i] = rnd() * TAU;
  Q = { k, h, re, im, kr, ki, fr, fi, th, p, n: 0, mq: [[0, 0]], mc: [[0, 0]], edge: false };
  cancelAnimationFrame(raf); raf = requestAnimationFrame(tickQ);
}
function kickQ() {
  const { re, im, kr, ki, fr, fi } = Q;
  fft(re, im, true);
  for (let j = 0; j < NQ; j++) { const a = re[j], b = im[j]; re[j] = a * kr[j] - b * ki[j]; im[j] = a * ki[j] + b * kr[j]; }
  fft(re, im, false);
  let s = 0, m2 = 0, edge = 0;
  for (let j = 0; j < NQ; j++) { const a = re[j], b = im[j]; re[j] = a * fr[j] - b * fi[j]; im[j] = a * fi[j] + b * fr[j];
    const P = re[j] * re[j] + im[j] * im[j], m = mOf(j); s += P; m2 += P * m * m; if (Math.abs(m) > NQ / 2 - 60) edge += P; }
  const K_ = Q.k * Q.h; let c2 = 0;
  for (let i = 0; i < Q.th.length; i++) { Q.p[i] += K_ * Math.sin(Q.th[i]); Q.th[i] = wrapT(Q.th[i] + Q.p[i]); c2 += Q.p[i] ** 2; }
  Q.n++; Q.mq.push([Q.n, m2 / s]); Q.mc.push([Q.n, c2 / Q.th.length / Q.h ** 2]);
  if (edge > 1e-5) Q.edge = true;
}
function tickQ() {
  for (let i = 0; i < 4 && Q.n < 1000 && !Q.edge; i++) kickQ();
  drawQ();
  if (Q.n < 1000 && !Q.edge) raf = requestAnimationFrame(tickQ);
}
function drawQ() {
  if (!Q) return;
  prof.clear(); prof.axes({ xt: 4, yt: 4, xl: "m", yl: "log₁₀ P(m)" });
  const bw = 16, nb = NQ / bw, hist = new Float64Array(nb);
  for (let i = 0; i < Q.p.length; i++) { const b = Math.floor((Q.p[i] / Q.h + NQ / 2) / bw); if (b >= 0 && b < nb) hist[b]++; }
  const pts = [];
  for (let j = NQ / 2; j < NQ + NQ / 2; j++) { const jj = j % NQ, P = Q.re[jj] ** 2 + Q.im[jj] ** 2; pts.push([mOf(jj), Math.log10(Math.max(P, 1e-9))]); }
  prof.clip(() => {
    const cl = []; for (let b = 0; b < nb; b++) if (hist[b] > 0) cl.push([(b + 0.5) * bw - NQ / 2, Math.log10(hist[b] / Q.p.length / bw)]);
    prof.line(cl, C.orbit, 1.5); prof.line(pts, C.accent, 1.2);
  });
  const ymax = Math.max(10, ...Q.mc.map(v => v[1]), ...Q.mq.map(v => v[1])) * 1.1;
  m2p.y = [0, ymax]; m2p.clear(); m2p.axes({ xt: 4, yt: 4, xl: "n", yl: "⟨m²⟩" });
  m2p.clip(() => { m2p.line(Q.mc, C.orbit, 2); m2p.line(Q.mq, C.accent, 2); });
  const res = Math.abs(Q.h - 4 * PI) < 1e-6;
  $("q-read").innerHTML = `kick <b>${Q.n}</b> · K = kħ = <b>${(Q.k * Q.h).toFixed(3)}</b> · ⟨m²⟩ quantum <b>${Q.mq[Q.n][1].toFixed(0)}</b>` +
    ` (<span style="color:${C.accent}">purple</span>) vs classical <b>${Q.mc[Q.n][1].toFixed(0)}</b> (<span style="color:${C.orbit}">red</span>)` +
    (res ? ` · resonance: k²n²/2 = <b>${(Q.k * Q.k * Q.n * Q.n / 2).toFixed(0)}</b>` : ` · estimate λ ≈ D/ħ² ≈ <b>${(Q.k * Q.k / 2).toFixed(0)}</b> states`) +
    (Q.edge ? ` · <span class="bad">the wave reached the edge of the simulated range: stopped</span>` : "");
  drawLat();
}
prof.onresize = drawQ; m2p.onresize = drawQ;
for (const id of ["kq", "hq"]) { $(id).oninput = e => { $(id + "-o").textContent = (+e.target.value).toFixed(id === "hq" ? 3 : 1); startQ(); };
  $(id + "-o").textContent = (+$(id).value).toFixed(id === "hq" ? 3 : 1); }
$("go").onclick = startQ;
$("res").onclick = () => { $("hq").value = 2; $("hq-o").textContent = "4π"; $("kq").value = 1; $("kq-o").textContent = "1.0";
  startQ(); Q.h = 4 * PI; for (let j = 0; j < NQ; j++) { Q.fr[j] = 1; Q.fi[j] = 0; } };
$("stab").innerHTML = `<tr><th>ħ (K = 5)</th><th>D/ħ²</th><th>λ measured</th><th>λ / (D/ħ²)</th></tr>` +
  D.sweep.map(s => `<tr><td>${s.hbar.toFixed(3)}</td><td>${s.D_m.toFixed(1)}</td><td>${s.lam.toFixed(1)}</td><td class="acc">${s.ratio.toFixed(2)}</td></tr>`).join("");

// ------------------------------------------------------------ 6. lattice energies
const lat = new Plot($("lat"), { x: [-40.5, 40.5], y: [-4, 4], aspect: 0.3, margin: [10, 12, 26, 30] });
function drawLat() {
  const h = Q ? Q.h : 0.4; lat.clear(); lat.axes({ xt: 4, yt: 2, xl: "m", yl: "T_m" });
  lat.clip(() => { for (let m = -40; m <= 40; m++) { const T = Math.max(-4, Math.min(4, Math.tan(0.5 * (0.7 - h * m * m / 2))));
    lat.line([[m, 0], [m, T]], Math.abs(h - 4 * PI) < 1e-6 ? C.stable : C.map, 3); } });
}
lat.onresize = drawLat;
startQ();
