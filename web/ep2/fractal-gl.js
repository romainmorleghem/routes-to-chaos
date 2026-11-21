// WebGL renderer for the Mandelbrot set, Julia sets and the Julia mosaic.
// Same colour convention as the videos: cream = bounded, dark->purple->pink->orange = escape speed.
const VS = `attribute vec2 p; varying vec2 uv; void main(){ uv = p*0.5+0.5; gl_Position = vec4(p,0.,1.); }`;
const FS = `
precision highp float;
varying vec2 uv;
uniform vec4 win;        // re0, re1, im0, im1
uniform vec2 c;          // Julia parameter
uniform int mode;        // 0 Mandelbrot, 1 Julia, 2 mosaic
uniform int maxit;
uniform int periods;     // colour interior by period (Mandelbrot only)
uniform vec2 tiles;      // mosaic tiles nx, ny
const int MAXIT = 3000;
vec3 ext(float t){
  t = clamp(t,0.,1.)*4.;
  vec3 s0=vec3(14.,17.,22.)/255., s1=vec3(43.,45.,110.)/255., s2=vec3(122.,62.,157.)/255., s3=vec3(232.,93.,117.)/255., s4=vec3(242.,165.,65.)/255.;
  if(t<1.) return mix(s0,s1,t); if(t<2.) return mix(s1,s2,t-1.); if(t<3.) return mix(s2,s3,t-2.); return mix(s3,s4,t-3.);
}
vec3 pcol(int p){
  if(p==1) return vec3(93.,169.,233.)/255.; if(p==2) return vec3(108.,203.,139.)/255.;
  if(p==3) return vec3(242.,165.,65.)/255.; if(p==4) return vec3(232.,93.,117.)/255.;
  if(p==5) return vec3(199.,146.,234.)/255.; if(p==6) return vec3(255.,214.,102.)/255.;
  if(p==7) return vec3(120.,220.,220.)/255.; if(p==8) return vec3(240.,128.,70.)/255.;
  return vec3(170.)/255.;
}
void main(){
  vec2 pos = vec2(mix(win.x,win.y,uv.x), mix(win.z,win.w,uv.y));
  vec2 z, cc;
  if(mode==0){ z=vec2(0.); cc=pos; }
  else if(mode==1){ z=pos; cc=c; }
  else {
    vec2 t = uv*tiles; vec2 cell = floor(t); vec2 f = fract(t)*2.-1.;
    cc = vec2(mix(win.x,win.y,(cell.x+.5)/tiles.x), mix(win.z,win.w,(cell.y+.5)/tiles.y));
    z = f*1.9;
  }
  float esc=-1.;
  for(int k=0;k<MAXIT;k++){
    if(k>maxit) break;
    float r2 = dot(z,z);
    if(r2>16.){ esc = max(float(k) - log2(log(sqrt(r2))), 0.); break; }
    z = vec2(z.x*z.x-z.y*z.y, 2.*z.x*z.y) + cc;
  }
  if(esc>=0.){ gl_FragColor = vec4(ext(log(1.+esc)/log(1.+float(maxit))*1.6),1.); return; }
  vec3 col = vec3(255.,244.,214.)/255.;
  if(mode==0 && periods==1){
    vec2 a = z; int per = 0;
    for(int k=1;k<=64;k++){ z = vec2(z.x*z.x-z.y*z.y, 2.*z.x*z.y)+cc; if(per==0 && length(z-a)<1e-4){ per=k; } }
    col = per>0 ? pcol(per) : pcol(99);
  }
  gl_FragColor = vec4(col,1.);
}`;

export class FractalView {
  constructor(canvas, { mode = 0, win, maxit = 300 } = {}) {
    this.cv = canvas; this.mode = mode; this.home = [...win]; this.win = [...win];
    this.maxit = maxit; this.c = [0, 0]; this.periods = 0; this.tiles = [24, 20];
    const gl = this.gl = canvas.getContext("webgl", { preserveDrawingBuffer: true });
    if (!gl) throw new Error("WebGL not available");
    const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o);
      if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
    const pr = this.pr = gl.createProgram();
    gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr);
    gl.useProgram(pr);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(pr, "p"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    this.u = n => gl.getUniformLocation(pr, n);
    new ResizeObserver(() => this.resize()).observe(canvas);
    this.resize();
  }
  resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2), w = this.cv.clientWidth || 400;
    const h = w * (this.home[3] - this.home[2]) / (this.home[1] - this.home[0]);
    this.cv.style.height = `${h}px`; this.cv.width = Math.round(w * dpr); this.cv.height = Math.round(h * dpr);
    this.W = w; this.H = h; this.draw();
  }
  draw() {
    const gl = this.gl; gl.viewport(0, 0, this.cv.width, this.cv.height);
    const w = this.win;
    gl.uniform4f(this.u("win"), w[0], w[1], w[2], w[3]); gl.uniform2f(this.u("c"), this.c[0], this.c[1]);
    gl.uniform1i(this.u("mode"), this.mode); gl.uniform1i(this.u("maxit"), this.maxit);
    gl.uniform1i(this.u("periods"), this.periods); gl.uniform2f(this.u("tiles"), this.tiles[0], this.tiles[1]);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    if (this.ondraw) this.ondraw();
  }
  // pixel (CSS) <-> complex
  toC(px, py) { const w = this.win; return [w[0] + px / this.W * (w[1] - w[0]), w[3] - py / this.H * (w[3] - w[2])]; }
  toPx(re, im) { const w = this.win; return [(re - w[0]) / (w[1] - w[0]) * this.W, (w[3] - im) / (w[3] - w[2]) * this.H]; }
  zoomAt(px, py, k) {
    const [a, b] = this.toC(px, py), w = this.win;
    if (k < 1 && (w[1] - w[0]) < 2e-5) return false;            // float32 precision limit
    this.win = [a + (w[0] - a) * k, a + (w[1] - a) * k, b + (w[2] - b) * k, b + (w[3] - b) * k];
    this.maxit = Math.min(3000, Math.round(300 + 120 * Math.log2((this.home[1] - this.home[0]) / (this.win[1] - this.win[0]))));
    this.draw(); return true;
  }
  reset() { this.win = [...this.home]; this.maxit = 300; this.draw(); }
  center(re, im, width) {
    const asp = (this.home[3] - this.home[2]) / (this.home[1] - this.home[0]), h = width * asp;
    this.win = [re - width / 2, re + width / 2, im - h / 2, im + h / 2];
    this.maxit = Math.min(3000, Math.round(300 + 120 * Math.log2((this.home[1] - this.home[0]) / width)));
    this.draw();
  }
}
