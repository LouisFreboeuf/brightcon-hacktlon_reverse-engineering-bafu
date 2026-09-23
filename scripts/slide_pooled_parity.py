"""Render the pooled flow-parity plot (all flows of all counted rebuilds) as a PNG for the deck.

    python scripts/slide_pooled_parity.py        # needs results/flow_comparison.json and google-chrome

Draws the same density as the "All flows, all 51 datasets" chart on artifacts/flow-parity.html
(rebuilt vs original, one cell per bin, shaded by how many flows fall into it), in the deck's
colours (Départ de Sentier palette) and at slide scale, and writes artifacts/presentation/screenshots/pooled-parity.png.
No CO2 markers: on 24 decades a +-50 % miss looks like a hit, so the slide states CO2 in text.
"""

import struct
import subprocess
import tempfile
import zlib
from pathlib import Path

W, H = 1400, 1300
OUT = Path("artifacts/presentation/screenshots/pooled-parity.png")

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600&display=swap">
<style>html,body{margin:0;background:#ffffff}canvas{display:block}</style></head><body>
<canvas id="c" width="%(W)d" height="%(H)d"></canvas>
<script id="data" type="application/json">%(DATA)s</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent), F = D.flows;
const C = D.specs.filter(s => s.counted);
const SUP = {'-':'\\u207b','0':'\\u2070','1':'\\u00b9','2':'\\u00b2','3':'\\u00b3','4':'\\u2074','5':'\\u2075','6':'\\u2076','7':'\\u2077','8':'\\u2078','9':'\\u2079'};
const sup = n => String(n).split('').map(c => SUP[c] || c).join('');
function draw() {
  const g = document.getElementById('c').getContext('2d'), Wd = %(W)d, Ht = %(H)d;
  const M = {l: 150, r: 28, t: 24, b: 128}, B = 22;
  const X0 = M.l + B + 8, X1 = Wd - M.r, Y0 = M.t, Y1 = Ht - M.b - B - 8;
  let vmax = 0; const P = [];
  for (const s of C) for (const [r, o, m] of s.flows) {
    if (o < 0 || m < 0) continue;
    if (o > 0) vmax = Math.max(vmax, o); if (m > 0) vmax = Math.max(vmax, m);
    P.push([o, m]);
  }
  const SPAN = 24, hi = Math.ceil(Math.log10(vmax) + 0.05), lo = hi - SPAN, NX = 150, NY = 150;
  const fx = v => (Math.log10(v) - lo) / SPAN, cell = v => Math.min(NX - 1, Math.max(0, Math.floor(fx(v) * NX)));
  const sx = v => X0 + fx(v) * (X1 - X0), sy = v => Y1 - fx(v) * (Y1 - Y0);
  const cells = new Map(), bottom = new Map(), left = new Map(), inc = (m, k) => m.set(k, (m.get(k) || 0) + 1);
  for (const [o, m] of P) {
    if (o > 0 && m > 0) inc(cells, cell(o) + NX * cell(m));
    else if (o > 0) inc(bottom, cell(o)); else if (m > 0) inc(left, cell(m));
  }
  let cmax = 1; cells.forEach(c => { cmax = Math.max(cmax, c); });
  const a = c => 0.10 + 0.90 * Math.log(1 + c) / Math.log(1 + cmax);
  const cw = (X1 - X0) / NX, ch = (Y1 - Y0) / NY;
  g.font = '500 30px "Quicksand", sans-serif'; g.fillStyle = '#7E857F'; g.strokeStyle = '#E3DBCF'; g.lineWidth = 2;
  for (let d = Math.ceil(lo / 4) * 4; d <= hi; d += 4) {
    const x = sx(10 ** d), y = sy(10 ** d);
    g.beginPath(); g.moveTo(x, Y0); g.lineTo(x, Y1); g.stroke(); g.beginPath(); g.moveTo(X0, y); g.lineTo(X1, y); g.stroke();
    g.textAlign = 'center'; g.fillText('10' + sup(d), x, Y1 + B + 8 + 40);
    g.textAlign = 'right'; g.fillText('10' + sup(d), M.l - 14, y + 10);
  }
  g.textAlign = 'center'; g.fillStyle = '#555B57'; g.font = '500 30px "Quicksand", sans-serif';
  g.fillText('original amount', (X0 + X1) / 2, Y1 + B + 8 + 92);
  g.save(); g.translate(34, (Y0 + Y1) / 2); g.rotate(-Math.PI / 2); g.fillText('rebuilt amount', 0, 0); g.restore();
  const band = (f, fill) => { g.fillStyle = fill; g.beginPath(); g.moveTo(sx(10 ** lo), sy(10 ** lo * f)); g.lineTo(sx(10 ** hi / f), sy(10 ** hi));
    g.lineTo(sx(10 ** hi), sy(10 ** hi)); g.lineTo(sx(10 ** hi), sy(10 ** hi / f)); g.lineTo(sx(10 ** lo * f), sy(10 ** lo)); g.lineTo(sx(10 ** lo), sy(10 ** lo)); g.closePath(); g.fill(); };
  band(2, 'rgba(132,174,153,0.16)'); band(1.1, 'rgba(132,174,153,0.45)');
  g.fillStyle = 'rgba(60,83,67,0.06)'; g.fillRect(X0, Y1 + 8, X1 - X0, B); g.fillRect(M.l, Y0, B, Y1 - Y0);
  cells.forEach((c, k) => { g.fillStyle = `rgba(60,83,67,${a(c)})`; g.fillRect(X0 + (k %% NX) * cw, Y1 - (Math.floor(k / NX) + 1) * ch, Math.ceil(cw), Math.ceil(ch)); });
  bottom.forEach((c, i) => { g.fillStyle = `rgba(60,83,67,${a(c)})`; g.fillRect(X0 + i * cw, Y1 + 8, Math.ceil(cw), B); });
  left.forEach((c, j) => { g.fillStyle = `rgba(60,83,67,${a(c)})`; g.fillRect(M.l, Y1 - (j + 1) * ch, B, Math.ceil(ch)); });
  g.strokeStyle = '#2B2B2B'; g.lineWidth = 2.5; g.beginPath(); g.moveTo(sx(10 ** lo), sy(10 ** lo)); g.lineTo(sx(10 ** hi), sy(10 ** hi)); g.stroke();
  document.title = 'done';
}
Promise.all([document.fonts.load('500 30px "Quicksand"'), document.fonts.load('600 30px "Quicksand"')]).catch(() => {}).then(draw);
</script></body></html>"""


def crop_rows(png: Path, rows: int) -> None:
    """Keep the top `rows` scanlines of a PNG. Headless Chrome reserves part of --window-size for
    browser chrome (87 px here), so the page is rendered into a taller window and cut back to the
    canvas. PNG row filters only reference the row above, so the kept rows need no re-filtering."""
    data = png.read_bytes()
    pos, chunks = 8, []
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8]); chunks.append((kind, data[pos + 8:pos + 8 + n])); pos += 12 + n
    ihdr = next(c for k, c in chunks if k == b"IHDR")
    w, h, depth, ctype = struct.unpack(">IIBB", ihdr[:10])
    assert depth == 8 and ctype in (2, 6), (depth, ctype)
    stride = 1 + w * (3 if ctype == 2 else 4)
    raw = zlib.decompress(b"".join(c for k, c in chunks if k == b"IDAT"))[: stride * rows]
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    out = data[:8] + chunk(b"IHDR", struct.pack(">II", w, rows) + ihdr[8:])
    out += b"".join(chunk(k, c) for k, c in chunks if k not in (b"IHDR", b"IDAT", b"IEND"))
    out += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    png.write_bytes(out)


def main() -> None:
    data = Path("results/flow_comparison.json").read_text().replace("</", "<\\/")
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "pooled.html"
        page.write_text(PAGE % {"W": W, "H": H, "DATA": data})
        OUT.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                        "--force-device-scale-factor=1", f"--window-size={W},{H + 200}", "--virtual-time-budget=8000",
                        f"--screenshot={OUT.resolve()}", page.resolve().as_uri()],
                       check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, timeout=120)
    crop_rows(OUT, H)
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
