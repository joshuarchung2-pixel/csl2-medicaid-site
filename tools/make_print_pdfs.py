"""Renders the printable pages to one-page US Letter PDFs in submission/print/ (needs a local server on :8765)."""
import sys
from playwright.sync_api import sync_playwright
OUT = "/Users/josh/code/csl2-medicaid-site/submission/print/"
PAGES = {"checklist-en.pdf": "checklist.html", "checklist-es.pdf": "es/checklist.html",
         "flyer-en.pdf": "flyer.html", "flyer-es.pdf": "es/flyer.html"}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 816, "height": 1056})
    for out, path in PAGES.items():
        pg.goto("http://localhost:8765/" + path); pg.emulate_media(media="print"); pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        # content must fit the sheet: the sheet has overflow hidden, so check its scrollHeight
        over = pg.evaluate("(() => { const s = document.querySelector('.sheet'); return s.scrollHeight - s.clientHeight; })()")
        pg.pdf(path=OUT + out, format="Letter", prefer_css_page_size=True, print_background=True)
        print(out, "overflow px:", over)
    b.close()
