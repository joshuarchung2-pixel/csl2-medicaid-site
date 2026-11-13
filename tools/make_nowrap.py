"""Keeps "Medi-Cal" from breaking at its hyphen: wraps every visible-text "Medi-Cal" in
<span class="nowrap"> on all 6 pages (EN + ES index, checklist, flyer).
Skips <head> (title, meta), <script>, <style>, <svg> and all attributes (alt, aria-label, href).
A run that sits right after an icon (</svg> or an <!--/ART:..--> marker) is in a flex row (.brand,
icon headings), so the whole run is also wrapped in <span class="nw-run"> to stay one flex item.
Safe to run more than once: earlier wraps are removed first, then put back.
make_es.py also calls nowrap() on its output, and strips the wraps from its input.
Full build: make_art.py -> make_es.py -> make_mouths.py -> make_map.py -> make_nowrap.py."""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "checklist.html", "flyer.html", "es/index.html", "es/checklist.html", "es/flyer.html"]
WORD = "Medi-Cal"
WRAP = '<span class="nowrap">' + WORD + "</span>"
SKIP = ("head", "script", "style", "svg")
TAG = re.compile(r"<!--.*?-->|<[^>]+>", re.S)
RUN = re.compile(r'<span class="nw-run">([^<]*(?:<span class="nowrap">[^<]*</span>[^<]*)*)</span>')


def unwrap(s):
    return RUN.sub(r"\1", s).replace(WRAP, WORD)


def wrap_run(text, prev):
    if WORD not in text:
        return text
    text = text.replace(WORD, WRAP)
    if prev == "</svg>" or prev.startswith("<!--/ART:"):
        body = text.strip()
        lead, trail = text[:len(text) - len(text.lstrip())], text[len(text.rstrip()):]
        text = lead + '<span class="nw-run">' + body + "</span>" + trail
    return text


def nowrap(s):
    s = unwrap(s)
    out, pos, depth, prev = [], 0, {t: 0 for t in SKIP}, ""
    for m in TAG.finditer(s):
        text = s[pos:m.start()]
        if not any(depth.values()):
            text = wrap_run(text, prev)
        out.append(text)
        tag = prev = m.group(0)
        name = re.match(r"</?([a-zA-Z][\w-]*)", tag)
        if name and name.group(1).lower() in SKIP and not tag.endswith("/>"):
            depth[name.group(1).lower()] += -1 if tag.startswith("</") else 1
        out.append(tag)
        pos = m.end()
    tail = s[pos:]
    out.append(tail if any(depth.values()) else wrap_run(tail, prev))
    return "".join(out)


if __name__ == "__main__":
    for p in PAGES:
        path = ROOT / p
        s = path.read_text()
        t = nowrap(s)
        path.write_text(t)
        print(p, "wrapped:", t.count(WRAP), "bare left:", t.count(WORD) - t.count(WRAP))
