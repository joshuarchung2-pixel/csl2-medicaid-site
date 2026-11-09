from playwright.sync_api import sync_playwright
import os
sp=os.path.dirname(os.path.abspath(__file__))
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto("file://"+sp+"/pdf-source.html")
    pg.pdf(path="/Users/josh/code/csl2-medicaid-site/submission/Chung_CSL2_Educational_Project.pdf", format="Letter", prefer_css_page_size=True, print_background=True)
    b.close()
