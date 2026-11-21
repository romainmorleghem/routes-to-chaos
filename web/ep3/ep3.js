import { C, Plot } from "../assets/plot.js";

const $ = id => document.getElementById(id);
const D = await (await fetch("../data/ep3.json")).json();
const P = { s: 10, r: 28, b: 8 / 3 };
const RAMP = ["#5DA9E9", "#C792EA", "#E85D75", "#F2A541"];

// ------------------------------------------------------------ integration (RK4)
function rhs(x, y, z, p) { return [p.s * (y - x), x * (p.r - z) - y, x * y - p.b * z]; }
function step(v, dt, p) {
  const [x, y, z] = v, k1 = rhs(x, y, z, p);
  const k2 = rhs(x + dt / 2 * k1[0], y + dt / 2 * k1[1], z + dt / 2 * k1[2], p);
  const k3 = rhs(x + dt / 2 * k2[0], y + dt / 2 * k2[1], z + dt / 2 * k2[2], p);
  const k4 = rhs(x + dt * k3[0], y + dt * k3[1], z + dt * k3[2], p);
  return [x + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]), y + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]),
          z + dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])];
}
function run(v, n, dt, p, skip = 0) { const out = []; for (let i = 0; i < n + skip; i++) { v = step(v, dt, p); if (i >= skip) out.push(v); } return out; }
function fixedPoints(p) {
  const pts = [[0, 0, 0]];
  if (p.r > 1) { const q = Math.sqrt(p.b * (p.r - 1)); pts.push([q, q, p.r - 1], [-q, -q, p.r - 1]); }
  return pts;
}
// eigenvalues of the 3x3 Jacobian via the characteristic cubic (Cardano + deflation)
function eig3(J) {
  const tr = J[0][0] + J[1][1] + J[2][2];
  const m2 = J[0][0] * J[1][1] - J[0][1] * J[1][0] + J[0][0] * J[2][2] - J[0][2] * J[2][0] + J[1][1] * J[2][2] - J[1][2] * J[2][1];
  const det = J[0][0] * (J[1][1] * J[2][2] - J[1][2] * J[2][1]) - J[0][1] * (J[1][0] * J[2][2] - J[1][2] * J[2][0]) + J[0][2] * (J[1][0] * J[2][1] - J[1][1] * J[2][0]);
  // l^3 - tr l^2 + m2 l - det = 0 ; find a real root by Newton from a bound
  let l = Math.abs(tr) + Math.abs(m2) + Math.abs(det) + 1; l = -l;
  for (let i = 0; i < 200; i++) { const f = l ** 3 - tr * l * l + m2 * l - det, d = 3 * l * l - 2 * tr * l + m2; l -= f / d; }
  const a = tr - l, b = det / l;          // remaining quadratic: m^2 - a m + b
  const disc = a * a - 4 * b;
  return disc >= 0 ? [[l, 0], [(a + Math.sqrt(disc)) / 2, 0], [(a - Math.sqrt(disc)) / 2, 0]]
                   : [[l, 0], [a / 2, Math.sqrt(-disc) / 2], [a / 2, -Math.sqrt(-disc) / 2]];
}
const jac = (v, p) => [[-p.s, p.s, 0], [p.r - v[2], -1, -v[0]], [v[1], v[0], -p.b]];

// ------------------------------------------------------------ a rotatable 3-D view on a 2-D canvas
class View3 {
  constructor(cv, { yaw = 0.0, pitch = -0.1 } = {}) {
    this.cv = cv; this.ctx = cv.getContext("2d"); this.yaw = yaw; this.pitch = pitch;
    this.center = [0, 0, 25]; this.scale = 1; this.onchange = null;
    let drag = null;
    cv.addEventListener("pointerdown", e => { drag = [e.clientX, e.clientY]; cv.setPointerCapture(e.pointerId); this.userMoved = true; });
    cv.addEventListener("pointermove", e => {
      if (!drag) return;
      this.yaw += (e.clientX - drag[0]) * 0.008; this.pitch = Math.max(-1.5, Math.min(1.5, this.pitch + (e.clientY - drag[1]) * 0.008));
      drag = [e.clientX, e.clientY]; this.onchange && this.onchange();
    });
    cv.addEventListener("pointerup", () => drag = null);
    this.resize(); addEventListener("resize", () => { this.resize(); this.onchange && this.onchange(); });
  }
  resize() {
    const r = this.cv.getBoundingClientRect(), dpr = Math.min(devicePixelRatio || 1, 2);
    this.cv.width = Math.round(r.width * dpr); this.cv.height = Math.round(r.width * dpr * 10 / 16);
    this.W = this.cv.width; this.H = this.cv.height;
  }
  fit(pts) {
    let lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9];
    for (const p of pts) for (let k = 0; k < 3; k++) { lo[k] = Math.min(lo[k], p[k]); hi[k] = Math.max(hi[k], p[k]); }
    this.center = lo.map((v, k) => (v + hi[k]) / 2);
    const span = Math.max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], 1e-6);
    this.scale = 0.92 * Math.min(this.W, this.H) / span;
  }
  proj(p) {
    const x = p[0] - this.center[0], y = p[1] - this.center[1], z = p[2] - this.center[2];
    const cy = Math.cos(this.yaw), sy = Math.sin(this.yaw), cp = Math.cos(this.pitch), sp = Math.sin(this.pitch);
    const X = cy * x - sy * y, Y = sy * x + cy * y;
    const Z = sp * Y + cp * z;
    return [this.W / 2 + X * this.scale, this.H / 2 - Z * this.scale];
  }
  clear() { this.ctx.fillStyle = C.bg; this.ctx.fillRect(0, 0, this.W, this.H); }
  path(pts, color, width = 1, alpha = 1) {
    const c = this.ctx; c.strokeStyle = color; c.lineWidth = width; c.globalAlpha = alpha; c.beginPath();
    pts.forEach((p, i) => { const q = this.proj(p); i ? c.lineTo(q[0], q[1]) : c.moveTo(q[0], q[1]); });
    c.stroke(); c.globalAlpha = 1;
  }
  ramp(pts, width = 1, alpha = 0.85) {           // colour along the curve (Part 2's teaser palette)
    const n = pts.length, seg = Math.ceil(n / 24);
    for (let s = 0; s < 24; s++) {
      const a = pts.slice(s * seg, (s + 1) * seg + 1); if (a.length < 2) continue;
      const t = s / 23 * 3, i = Math.min(2, Math.floor(t));
      this.path(a, mix(RAMP[i], RAMP[i + 1], t - i), width, alpha);
    }
  }
  dot(p, color, r = 4) { const q = this.proj(p), c = this.ctx; c.fillStyle = color; c.beginPath(); c.arc(q[0], q[1], r, 0, 7); c.fill(); }
}
function mix(a, b, t) {
  const h = s => [1, 3, 5].map(i => parseInt(s.slice(i, i + 2), 16));
  const A = h(a), B = h(b); return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * t)).join(",")})`;
}

// ------------------------------------------------------------ §1 explorer
const att = new View3($("att"));
let trail = [], head = [1, 1, 1], spinT = 0;
function resetTrail() {
  head = [1, 1, 1]; trail = run(head, 6000, 0.005, P, 2000); head = trail[trail.length - 1];
  att.fit(trail.length ? trail : [[0, 0, 0]]); att.scale *= 1.0;
  const fp = fixedPoints(P);
  $("att-read").innerHTML = fp.map((v, i) => {
    const ev = eig3(jac(v, P)), st = ev.every(e => e[0] < 0);
    return `${["O", "C₊", "C₋"][i]}: <b class="${st ? "ok" : "bad"}">${st ? "stable" : "unstable"}</b>`;
  }).join(" · ") + ` · divergence <b>${(-(P.s + 1 + P.b)).toFixed(2)}</b>`;
  updateLorenzMap(); drawFP();
}
const sliders = [["sig", "s"], ["rho", "r"], ["bet", "b"]];
for (const [id, k] of sliders) {
  $(id).addEventListener("input", () => { P[k] = +$(id).value; $(id + "-o").textContent = (+$(id).value).toFixed(2); resetTrail(); });
  $(id + "-o").textContent = (+$(id).value).toFixed(2);
}
function setRho(r) { $("rho").value = r; P.r = r; $("rho-o").textContent = r.toFixed(2); resetTrail(); }
const PRESETS = [[0.5, "rest"], [10, "steady rolls"], [20, "transient chaos"], [24.5, "bistable"], [28, "strange attractor"],
                 [99.65, "period-doubled orbit"], [160, "periodic again"]];
for (const [r, name] of PRESETS) {
  const b = document.createElement("button"); b.textContent = `ρ = ${r} · ${name}`;
  b.onclick = () => { P.s = 10; P.b = 8 / 3; $("sig").value = 10; $("bet").value = 2.6667; $("sig-o").textContent = "10.00"; $("bet-o").textContent = "2.67"; setRho(r); };
  $("presets").appendChild(b);
}
function frameAtt() {
  for (let i = 0; i < 6; i++) { head = step(head, 0.005, P); trail.push(head); }
  if (trail.length > 6000) trail.splice(0, trail.length - 6000);
  if ($("spin").checked && !att.userMoved) att.yaw += 0.003;
  att.clear(); att.ramp(trail, 1.1, 0.8);
  for (const v of fixedPoints(P)) att.dot(v, C.muted, 3);
  att.dot(head, C.orbit, 4.5);
}

function drawFP() {
  const rows = fixedPoints(P).map((v, i) => {
    const ev = eig3(jac(v, P)).map(e => e[1] ? `${e[0].toFixed(3)} ${e[1] < 0 ? "−" : "+"} ${Math.abs(e[1]).toFixed(3)}i` : e[0].toFixed(3));
    return `<tr><td>${["O", "C₊", "C₋"][i]}</td><td>(${v.map(a => a.toFixed(2)).join(", ")})</td><td>${ev.join(", ")}</td></tr>`;
  });
  $("fp").innerHTML = `<tr><th>ρ = ${P.r.toFixed(2)}</th><th>equilibrium</th><th>eigenvalues of the Jacobian</th></tr>` + rows.join("");
}

// ------------------------------------------------------------ §3 twins
const duo = new View3($("duo")), lg = new Plot($("duo-log"), { x: [0, 40], y: [-15, 2], aspect: 0.625 });
let A, B, tt, logd;
function duoStart() {
  const k = +$("k").value; $("k-o").textContent = k;
  A = run([1, 1, 1], 1, 0.005, { s: 10, r: 28, b: 8 / 3 }, 3000)[0]; B = [A[0] + 10 ** -k, A[1], A[2]];
  tt = 0; logd = []; duo.trA = []; duo.trB = [];
  duo.fit(run([1, 1, 1], 3000, 0.005, { s: 10, r: 28, b: 8 / 3 }, 1000));
}
$("k").addEventListener("input", duoStart); $("duo-go").onclick = duoStart;
const L1 = D.lyapunov[0];
$("spec").textContent = `λ₁ = ${D.lyapunov[0].toFixed(3)}, λ₂ ≈ 0, λ₃ = ${D.lyapunov[2].toFixed(2)}; sum ${(D.lyapunov[0] + D.lyapunov[1] + D.lyapunov[2]).toFixed(3)}`;
function frameDuo() {
  const p = { s: 10, r: 28, b: 8 / 3 };
  if (tt < 40) for (let i = 0; i < 8; i++) {
    A = step(A, 0.005, p); B = step(B, 0.005, p); tt += 0.005;
    duo.trA.push(A); duo.trB.push(B);
    if (i % 4 === 0) logd.push([tt, Math.log10(Math.hypot(A[0] - B[0], A[1] - B[1], A[2] - B[2]) + 1e-300)]);
  }
  if (duo.trA.length > 900) { duo.trA.splice(0, duo.trA.length - 900); duo.trB.splice(0, duo.trB.length - 900); }
  duo.yaw += 0.002; duo.clear();
  duo.path(duo.trA, C.diag, 1.6, 0.9); duo.path(duo.trB, C.orbit, 1.6, 0.9);
  duo.dot(A, C.diag, 4); duo.dot(B, C.orbit, 4);
  lg.clear(); lg.axes({ xl: "t", yl: "log₁₀ |δ|" });
  const k = +$("k").value;
  lg.clip(() => {
    lg.line([[0, -k], [40, -k + 40 * L1 / Math.LN10]], C.accent, 1.5, 0.8, [5, 4]);
    lg.line(logd, C.map, 2);
  });
  const horizon = Math.log(10 ** k) / L1;       // time to reach O(1)
  $("duo-read").innerHTML = `t = <b>${tt.toFixed(1)}</b> · distance <b>10^${(logd.length ? logd[logd.length - 1][1] : -k).toFixed(1)}</b>` +
    ` · dashed slope λ₁/ln10 · predicted divergence time ≈ <b>${horizon.toFixed(1)}</b> (each extra digit adds ${(Math.LN10 / L1).toFixed(2)})`;
}

// ------------------------------------------------------------ §4 ink
const ink = new View3($("ink"), { yaw: 0.55, pitch: -0.25 });
const NI = 20000; let cloud = [], inkT = 0;
function inkStart() {
  const R = 10 ** +$("ink-r").value; $("ink-r-o").textContent = R.toPrecision(2);
  const c0 = run([1, 1, 1], 1, 0.005, { s: 10, r: 28, b: 8 / 3 }, 1200)[0];
  cloud = [];
  for (let i = 0; i < NI; i++) {
    let v; do { v = [Math.random() * 2 - 1, Math.random() * 2 - 1, Math.random() * 2 - 1]; } while (Math.hypot(...v) > 1);
    cloud.push([c0[0] + R * v[0], c0[1] + R * v[1], c0[2] + R * v[2]]);
  }
  inkT = 0; ink.fit(run([1, 1, 1], 3000, 0.005, { s: 10, r: 28, b: 8 / 3 }, 1000));
}
$("ink-go").onclick = inkStart; $("ink-r").addEventListener("input", inkStart);
function frameInk() {
  const p = { s: 10, r: 28, b: 8 / 3 };
  if (inkT < 12) { for (let i = 0; i < NI; i++) cloud[i] = step(cloud[i], 0.01, p); inkT += 0.01; }
  const c = ink.ctx; ink.clear(); c.globalCompositeOperation = "lighter"; c.fillStyle = "rgba(93,169,233,0.35)";
  for (const v of cloud) { const q = ink.proj(v); c.fillRect(q[0], q[1], 1.6, 1.6); }
  c.globalCompositeOperation = "source-over";
  $("ink-read").innerHTML = `t = <b>${inkT.toFixed(2)}</b> · ${NI.toLocaleString("en")} points`;
}

// ------------------------------------------------------------ §5 Lorenz map + cobweb
const lm = new Plot($("lmap"), { x: [0, 1], y: [0, 1], aspect: 0.62 });
let peaks = [], cob = 0;
function updateLorenzMap() {
  const tr = run([1, 1, 1], 80000, 0.005, P, 4000);
  peaks = [];
  for (let i = 1; i < tr.length - 1; i++) if (tr[i][2] > tr[i - 1][2] && tr[i][2] >= tr[i + 1][2]) peaks.push(tr[i][2]);
  if (peaks.length < 3) { lm.x = [0, 1]; lm.y = [0, 1]; } else {
    const lo = Math.min(...peaks), hi = Math.max(...peaks), pad = Math.max(0.05 * (hi - lo), 0.5);
    lm.x = [lo - pad, hi + pad]; lm.y = [lo - pad, hi + pad];
  }
  cob = 0; drawLorenzMap();
}
function drawLorenzMap() {
  lm.clear(); lm.axes({ xl: "z_n", yl: "z_{n+1}" });
  lm.clip(() => {
    lm.line([[lm.x[0], lm.x[0]], [lm.x[1], lm.x[1]]], C.diag, 1.5);
    for (let i = 0; i + 1 < peaks.length; i++) lm.dot(peaks[i], peaks[i + 1], C.map, 1.6);
    const pts = [];
    for (let i = 0; i < Math.min(cob, peaks.length - 1); i++) { pts.push([peaks[i], peaks[i]], [peaks[i], peaks[i + 1]]); }
    if (pts.length) lm.line(pts, C.orbit, 1.6);
  });
  $("lmap-read").innerHTML = peaks.length < 3 ? "No sustained oscillation at this ρ: the orbit settles (no peaks to record)."
    : `<b>${peaks.length}</b> peaks recorded at ρ = <b>${P.r.toFixed(2)}</b>. Distinct values: <b>${new Set(peaks.slice(-60).map(v => v.toFixed(2))).size}</b> among the last 60 (a period-n orbit gives n points).`;
}
$("lmap-cob").onclick = () => { const target = cob + 20; const go = () => { if (cob < target) { cob++; drawLorenzMap(); setTimeout(go, 120); } }; go(); };

// ------------------------------------------------------------ §5 bifurcation diagram
const bf = new Plot($("bif"), { x: [99.3, 100.85], y: [141, 146.5], aspect: 0.5 });
let bmode = "window";
function drawBif() {
  const data = D[bmode];
  if (bmode === "window") { bf.x = [99.3, 100.85]; bf.y = [141, 146.5]; } else { bf.x = [20, 220]; bf.y = D.wideY; }
  bf.clear(); bf.axes({ xl: "ρ", yl: bmode === "window" ? "peaks of z (top branch)" : "z-peak / (ρ − 1)" });
  bf.clip(() => {
    for (const [r, m] of data) for (const v of m) {
      if (bmode === "window" && v < 138) continue;
      const y = bmode === "window" ? v : v / (r - 1);
      bf.dot(r, y, C.map, 0.9);
    }
    if (bmode === "window") for (const r of D.rho_k) bf.line([[r, bf.y[0]], [r, bf.y[1]]], C.accent, 1, 0.8, [4, 4]);
    bf.line([[P.r, bf.y[0]], [P.r, bf.y[1]]], C.orbit, 1.2, 0.8);
  });
}
{ // the wide diagram is normalised by rho - 1 (the height of the rolls): zoom y to the data
  const ys = D.wide.flatMap(([r, m]) => m.map(v => v / (r - 1)));
  D.wideY = [Math.min(...ys) - 0.05, Math.max(...ys) + 0.05];
}
document.querySelectorAll("input[name=bw]").forEach(el => el.addEventListener("change", () => { bmode = el.value; drawBif(); }));
$("bif").addEventListener("click", e => {
  const r = $("bif").getBoundingClientRect(), dpr = $("bif").width / r.width;
  setRho(Math.round(bf.ux((e.clientX - r.left) * dpr) * 1000) / 1000); drawBif();
  $("s1").scrollIntoView({ behavior: "smooth" });
});
const rk = D.rho_k;
$("dtab").innerHTML = `<tr><th>k</th><th>ρ_k (doubling to period 3·2^k peaks)</th><th>δ_k = (ρ_{k−1} − ρ_k)/(ρ_k − ρ_{k+1})</th></tr>` +
  rk.map((r, i) => `<tr><td>${i + 1}</td><td>${r.toFixed(4)}</td><td class="acc">${i > 0 && i < rk.length - 1 ? D.delta_k[i - 1].toFixed(3) : ""}</td></tr>`).join("") +
  `<tr><td></td><td>Feigenbaum (Part 1)</td><td class="acc">4.669…</td></tr>`;

// ------------------------------------------------------------ §6 skeleton
const up = new View3($("upo"), { yaw: 0, pitch: 0 });
const bgTr = run([1, 1, 1], 8000, 0.005, { s: 10, r: 28, b: 8 / 3 }, 1000);
let cur = D.upo[0];
function drawUpo() {
  up.clear(); up.path(bgTr, C.muted, 0.6, 0.35); up.path(cur.pts, C.map, 2.4, 1);
  $("upo-read").innerHTML = `orbit <b>${cur.word}</b> · period T = <b>${cur.T}</b> · return-map multiplier μ = <b>${cur.mu}</b> (neighbours pushed away ×${cur.mu} per lap)`;
}
for (const o of D.upo) {
  const b = document.createElement("button"); b.textContent = o.word; b.style.fontFamily = "monospace";
  b.onclick = () => { cur = o; drawUpo(); }; $("upo-btn").appendChild(b);
}
up.onchange = drawUpo;
up.fit(bgTr);

// ------------------------------------------------------------ main loop: only animate what is visible
const vis = new Set();
const io = new IntersectionObserver(es => es.forEach(e => e.isIntersecting ? vis.add(e.target.id) : vis.delete(e.target.id)));
["att", "duo", "ink"].forEach(id => io.observe($(id)));
function loop() {
  if (vis.has("att")) frameAtt();
  if (vis.has("duo")) frameDuo();
  if (vis.has("ink")) frameInk();
  requestAnimationFrame(loop);
}
resetTrail(); duoStart(); inkStart(); drawBif(); drawUpo();
lm.onresize = drawLorenzMap; bf.onresize = drawBif; addEventListener("resize", drawUpo);
loop();
