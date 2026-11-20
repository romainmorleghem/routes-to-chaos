// Small helpers shared by all pages: HiDPI canvas, coordinate frames, colour maps, maps.
export const C = {
  bg: "#0E1116", fg: "#E6E6E6", muted: "#7A8291", line: "#262d38",
  map: "#F2A541", diag: "#5DA9E9", orbit: "#E85D75", stable: "#6CCB8B", accent: "#C792EA",
};
const STOPS = ["#0E1116", "#2B2D6E", "#7A3E9D", "#E85D75", "#F2A541", "#FFF4D6"].map(h =>
  [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16)));
export function colormap(t) {               // t in [0,1] -> [r,g,b]
  t = Math.min(1, Math.max(0, t)) * (STOPS.length - 1);
  const i = Math.min(STOPS.length - 2, Math.floor(t)), f = t - i;
  return STOPS[i].map((a, k) => a + (STOPS[i + 1][k] - a) * f);
}

export const MAPS = {
  logistic: { f: (r, x) => r * x * (1 - x), r: [2.8, 4], x: [0, 1], x0: 0.5, xc: () => 0.5,
              tex: "r\\,x(1-x)", name: "logistic" },
  sine:     { f: (a, x) => a * Math.sin(Math.PI * x), r: [0.7, 1], x: [0, 1], x0: 0.5, xc: () => 0.5,
              tex: "a\\sin(\\pi x)", name: "sine" },
  ricker:   { f: (r, x) => x * Math.exp(r * (1 - x)), r: [1.8, 3.4], x: [0, 4], x0: 0.5, xc: r => 1 / r,
              tex: "x\\,e^{r(1-x)}", name: "Ricker" },
  quartic:  { f: (a, x) => 1 - a * x ** 4, r: [0.6, 2], x: [-1, 1], x0: 0, xc: () => 0,
              tex: "1-a\\,x^4", name: "quartic top" },
};

// A canvas with a data frame [x0,x1]×[y0,y1] and margins for tick labels.
export class Plot {
  constructor(canvas, { x, y, aspect = 0.62, margin = [10, 12, 26, 38] } = {}) {
    this.cv = canvas; this.ctx = canvas.getContext("2d");
    this.x = x; this.y = y; this.aspect = aspect; this.m = margin;   // top right bottom left
    new ResizeObserver(() => this.resize()).observe(canvas);
    this.resize(false);
  }
  resize(redraw = true) {
    const dpr = window.devicePixelRatio || 1, w = this.cv.clientWidth || 600;
    this.cv.style.height = `${Math.round(w * this.aspect)}px`;
    this.cv.width = Math.round(w * dpr); this.cv.height = Math.round(w * this.aspect * dpr);
    this.dpr = dpr; this.W = w; this.H = w * this.aspect;
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (redraw && this.onresize) this.onresize();
  }
  get iw() { return this.W - this.m[1] - this.m[3]; }
  get ih() { return this.H - this.m[0] - this.m[2]; }
  px(v) { return this.m[3] + (v - this.x[0]) / (this.x[1] - this.x[0]) * this.iw; }
  py(v) { return this.m[0] + (this.y[1] - v) / (this.y[1] - this.y[0]) * this.ih; }
  ux(p) { return this.x[0] + (p - this.m[3]) / this.iw * (this.x[1] - this.x[0]); }
  uy(p) { return this.y[1] - (p - this.m[0]) / this.ih * (this.y[1] - this.y[0]); }
  clear() { const c = this.ctx; c.fillStyle = C.bg; c.fillRect(0, 0, this.W, this.H); }
  axes({ xt = 5, yt = 4, xl = "", yl = "" } = {}) {
    const c = this.ctx; c.strokeStyle = C.muted; c.lineWidth = 1; c.fillStyle = C.muted;
    c.font = "11px system-ui, sans-serif";
    c.beginPath(); c.moveTo(this.m[3], this.m[0]); c.lineTo(this.m[3], this.H - this.m[2]);
    c.lineTo(this.W - this.m[1], this.H - this.m[2]); c.stroke();
    const fmt = v => Math.abs(v) < 1e-12 ? "0" : +v.toPrecision(4) + "";
    c.textAlign = "center"; c.textBaseline = "top";
    for (let i = 0; i <= xt; i++) { const v = this.x[0] + i / xt * (this.x[1] - this.x[0]);
      c.fillText(fmt(v), this.px(v), this.H - this.m[2] + 5); }
    c.textAlign = "right"; c.textBaseline = "middle";
    for (let i = 0; i <= yt; i++) { const v = this.y[0] + i / yt * (this.y[1] - this.y[0]);
      c.fillText(fmt(v), this.m[3] - 5, this.py(v)); }
    c.font = "italic 13px Georgia, serif"; c.fillStyle = C.fg;
    if (xl) { c.textAlign = "right"; c.textBaseline = "bottom"; c.fillText(xl, this.W - this.m[1], this.H - this.m[2] - 3); }
    if (yl) { c.textAlign = "left"; c.textBaseline = "top"; c.fillText(yl, this.m[3] + 5, this.m[0]); }
  }
  line(pts, color, width = 1.5, alpha = 1, dash = null) {
    const c = this.ctx; c.save(); c.strokeStyle = color; c.lineWidth = width; c.globalAlpha = alpha;
    if (dash) c.setLineDash(dash);
    c.beginPath(); pts.forEach(([a, b], i) => i ? c.lineTo(this.px(a), this.py(b)) : c.moveTo(this.px(a), this.py(b)));
    c.stroke(); c.restore();
  }
  fn(f, color, width = 2, n = 400) {
    const pts = []; for (let i = 0; i <= n; i++) { const x = this.x[0] + i / n * (this.x[1] - this.x[0]); pts.push([x, f(x)]); }
    this.clip(() => this.line(pts, color, width));
  }
  dot(a, b, color, r = 3) { const c = this.ctx; c.fillStyle = color; c.beginPath(); c.arc(this.px(a), this.py(b), r, 0, 7); c.fill(); }
  clip(draw) { const c = this.ctx; c.save(); c.beginPath(); c.rect(this.m[3], this.m[0], this.iw, this.ih); c.clip(); draw(); c.restore(); }
}

// Bifurcation density image rendered into the plot's inner area.
export function drawBifurcation(plot, map, { transient = 700, samples = null } = {}) {
  const dpr = plot.dpr, W = Math.max(2, Math.round(plot.iw * dpr)), H = Math.max(2, Math.round(plot.ih * dpr));
  samples = samples || Math.round(H * 1.2);
  const dens = new Float32Array(W * H), [r0, r1] = plot.x, [y0, y1] = plot.y;
  for (let i = 0; i < W; i++) {
    const r = r0 + (i + 0.5) / W * (r1 - r0); let x = map.x0;
    for (let k = 0; k < transient; k++) x = map.f(r, x);
    for (let k = 0; k < samples; k++) {
      x = map.f(r, x);
      const j = Math.round((y1 - x) / (y1 - y0) * (H - 1));
      if (j >= 0 && j < H) dens[j * W + i] += 1;
    }
  }
  const img = plot.ctx.createImageData(W, H);
  for (let i = 0; i < W; i++) {
    let mx = 0; for (let j = 0; j < H; j++) mx = Math.max(mx, dens[j * W + i]);
    for (let j = 0; j < H; j++) {
      const v = mx ? Math.pow(dens[j * W + i] / mx, 0.45) : 0, [r, g, b] = colormap(v), o = 4 * (j * W + i);
      img.data[o] = r; img.data[o + 1] = g; img.data[o + 2] = b; img.data[o + 3] = 255;
    }
  }
  plot.ctx.putImageData(img, Math.round(plot.m[3] * dpr), Math.round(plot.m[0] * dpr));
}

export function lyapunov(map, r, transient = 400, n = 1200, h = 1e-7) {
  let x = map.x0, s = 0;
  for (let k = 0; k < transient; k++) x = map.f(r, x);
  for (let k = 0; k < n; k++) {
    const d = (map.f(r, x + h) - map.f(r, x - h)) / (2 * h);
    s += Math.log(Math.abs(d) + 1e-300); x = map.f(r, x);
  }
  return s / n;
}

export function orbit(f, r, x0, n) { const xs = [x0]; for (let i = 0; i < n; i++) xs.push(f(r, xs[i])); return xs; }
