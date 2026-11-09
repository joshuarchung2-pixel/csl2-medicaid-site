"""Links in-text citations and reference entries both ways in index.html.
Each (Author, year) link gets an id; each reference entry gets a back link to the first citation
a visitor can see without tapping anything (app.js then points it at whichever citation was clicked).
Safe to run more than once. Run after editing index.html, before make_es.py."""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "index.html"
s = P.read_text()

# reset earlier runs
s = re.sub(r'<a class="cite" id="c-[a-z0-9-]+" href=', '<a class="cite" href=', s)
s = re.sub(r'<a class="back" href="#[^"]*" aria-label="[^"]*">↑</a>', '', s)

# parts of the page that start hidden or folded: result card, tooth panels, myth backs, the dates list
hidden = []
for start, end in (('<div class="plan" id="plan"', '<p class="privacy">'),
                   ('<div class="tooth-info"', '<!-- MYTHS -->'),
                   ('<div class="face back">', '</div>'),
                   ('<details>', '</details>')):
    i = 0
    while (i := s.find(start, i)) != -1:
        j = s.index(end, i)
        hidden.append((i, j)); i = j

def is_hidden(pos):
    return any(a <= pos < b for a, b in hidden)

count, first_seen, first_any = {}, {}, {}
out, last = [], 0
for m in re.finditer(r'<a class="cite" href="#(ref-[a-z-]+)">', s):
    ref = m.group(1)
    count[ref] = count.get(ref, 0) + 1
    cid = f'c-{ref[4:]}-{count[ref]}'
    first_any.setdefault(ref, (cid, m.start()))
    if not is_hidden(m.start()):
        first_seen.setdefault(ref, cid)
    out.append(s[last:m.start()])
    out.append(f'<a class="cite" id="{cid}" href="#{ref}">')
    last = m.end()
out.append(s[last:])
s = "".join(out)

def section_of(pos):
    secs = [m for m in re.finditer(r'<section id="([a-z]+)"', s[:pos])]
    return secs[-1].group(1) if secs else "main"

for m in list(re.finditer(r'<li id="(ref-[a-z-]+)">', s)):
    ref = m.group(1)
    if ref not in first_any:
        raise SystemExit("never cited: " + ref)
target = {}
for ref, (cid, pos) in first_any.items():
    target[ref] = first_seen.get(ref) or section_of(s.index(f'id="{cid}"'))

def add_back(m):
    ref, body = m.group(1), m.group(2)
    return f'<li id="{ref}">{body}<a class="back" href="#{target[ref]}" aria-label="Back to the text">↑</a></li>'
s = re.sub(r'<li id="(ref-[a-z-]+)">(.*?)</li>', add_back, s)
P.write_text(s)
print("cites:", sum(count.values()), "refs:", len(target))
