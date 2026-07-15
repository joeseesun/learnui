#!/usr/bin/env python3
"""Preview a demo fragment in both stage sizes. Usage: python3 scripts/preview-demo.py <slug>"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main(slug):
    path = os.path.join(ROOT, "demos", slug + ".html")
    if not os.path.exists(path):
        print(f"missing: {path}")
        sys.exit(1)
    frag = open(path, encoding="utf-8").read()
    page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><link rel="stylesheet" href="http://localhost:8934/assets/site.css">
<style>body{{display:flex;gap:40px;align-items:flex-start;padding:40px;background:#fff}}
.stage{{width:340px;border:1px solid #eaeaea;border-radius:8px;background:#fafafa;position:relative}}
.h200{{height:220px}}.h400{{height:380px}}
.label{{font:11px monospace;color:#a3a3a3;margin-bottom:8px}}</style></head>
<body>
<div><p class="label">hub card (220px)</p><div class="stage h200"><div class="stage-center"><div class="fragment">{frag}</div></div></div></div>
<div><p class="label">detail (400px)</p><div class="stage h400"><div class="stage-center"><div class="fragment">{frag}</div></div></div></div>
<script>document.querySelectorAll('.fragment script')?.forEach(s=>{{}})</script>
</body></html>"""
    out = os.path.join(ROOT, "site", "_preview-" + slug + ".html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 820, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"http://localhost:8934/_preview-{slug}.html", wait_until="networkidle")
        pg.wait_for_timeout(600)
        pg.screenshot(path=f"/tmp/preview-{slug}.png")
        b.close()
    print(f"/tmp/preview-{slug}.png  js-errors: {errs or 'none'}")

if __name__ == "__main__":
    main(sys.argv[1])
