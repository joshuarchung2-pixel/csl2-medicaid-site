"""Writes the warm-character illustrations (v5) into index.html, between <!--ART:name--> and <!--/ART:name-->.
Run before make_es.py (the Spanish page copies the art from index.html), then make_mouths.py, make_map.py and make_nowrap.py.
All art is original flat SVG drawn here from simple shapes: a tooth "buddy" (white tooth, warm shade, rosy cheeks),
a parent and a child. Every piece is decorative (aria-hidden); the text next to it carries the meaning.
Shared shapes live once in the page sprite (#bd-tooth, #bd-body) and every piece <use>s them.
Buddy space: the tooth spans x 68..172, y 36..215; eyes sit at y 108, the mouth at y 132."""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

PLUM, CREAM, WHITE, SHADE = "#3a1f3d", "#fff6ec", "#fffdf8", "#f6e2cb"
MARIGOLD, CORAL, MINT, MINT_D, BERRY, SKY = "#ffbd3a", "#ff7f66", "#5cc8a8", "#2f9d7e", "#e0457b", "#8cc8f0"
DISC_MYTH, DISC_FACT = "#ffcdbd", "#b9e8d6"

TOOTH = ("M70 70C70 45 95 36 120 48 145 36 170 45 170 70 172 100 165 125 160 150 155 180 152 215 "
         "140 215 128 215 130 182 120 182 110 182 112 215 100 215 88 215 85 180 80 150 75 125 68 100 70 70Z")
DEFS = (
    f'<path id="bd-tooth" d="{TOOTH}"/>'
    '<clipPath id="bd-clip"><use href="#bd-tooth"/></clipPath>'
    f'<g id="bd-body"><g clip-path="url(#bd-clip)"><use href="#bd-tooth" fill="{SHADE}"/>'
    f'<use href="#bd-tooth" fill="{WHITE}" transform="translate(-16 -8)"/></g>'
    '<circle cx="94" cy="130" r="10" fill="#ffb3a1"/><circle cx="146" cy="130" r="10" fill="#ffb3a1"/></g>'
)


# ---------- buddy parts (buddy space) ----------
def arm(d, w=16):
    return f'<path d="{d}" fill="none" stroke="{WHITE}" stroke-width="{w}" stroke-linecap="round"/>'


def line(d, w=6, c=PLUM):
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


EYES = {
    "open": f'<g fill="{PLUM}"><ellipse cx="104" cy="108" rx="8" ry="10"/><ellipse cx="136" cy="108" rx="8" ry="10"/></g>'
            '<circle cx="107" cy="104" r="3" fill="#fff"/><circle cx="139" cy="104" r="3" fill="#fff"/>',
    "dot": f'<g fill="{PLUM}"><circle cx="106" cy="109" r="8"/><circle cx="136" cy="107" r="8"/></g>',
    "wide": f'<g fill="{PLUM}"><circle cx="105" cy="110" r="9"/><circle cx="135" cy="110" r="9"/></g>'
            '<circle cx="108" cy="106" r="3" fill="#fff"/><circle cx="138" cy="106" r="3" fill="#fff"/>',
    "happy": line("M96 110q10-12 20 0M124 110q10-12 20 0"),
}
BROWS = {
    "puzzled": line("M92 86q12-8 22-2M128 80q12-4 20 4"),
    "worried": line("M93 91q11-2 19-10M128 81q8 8 19 10"),
    "": "",
}
TONGUE = line("M112 140q8 5 16 0", 5, CORAL)
MOUTH = {
    "smile": f'<path d="M104 132q16 20 32 0z" fill="{PLUM}"/>' + TONGUE,
    "beam": f'<path d="M100 128q20 28 40 0z" fill="{PLUM}"/>' + line("M111 142q9 6 18 0", 5, CORAL),
    "squiggle": line("M104 142q8-8 16 0t16 0"),
    "o": f'<ellipse cx="120" cy="141" rx="7" ry="8" fill="{PLUM}"/>',
    "small": line("M110 136q10 9 20 0"),
    "braces": f'<path d="M100 128q20 28 40 0z" fill="{PLUM}"/><path d="M103 131h34" stroke="#fff" stroke-width="7"/>'
              + line("M104 131h32", 2, "#9a8aa0") + ''.join(f'<rect x="{x}" y="128.5" width="5" height="5" rx="1" fill="#9a8aa0"/>' for x in (106, 115, 124, 132)),
}


def face(eyes, mouth, brows="", blink=False):
    e = EYES[eyes]
    if blink:
        e = f'<g class="blink">{e}</g>'
    return BROWS[brows] + e + MOUTH[mouth]


def buddy(cx, bottom, s, inner, cls=""):
    """Place a buddy (whose body is drawn by `inner`, which must include <use href="#bd-body"/>) so its
    feet sit at (cx, bottom) at scale s."""
    x, y = cx - 120 * s, bottom - 215 * s
    c = f' class="{cls}"' if cls else ""
    return f'<g{c} transform="translate({x:.1f} {y:.1f}) scale({s})">{inner}</g>'


BODY = '<use href="#bd-body"/>'


def star(cx, cy, r, c):
    k = r * .3
    return (f'<path d="M{cx} {cy - r}L{cx + k:.1f} {cy - k:.1f}L{cx + r} {cy}L{cx + k:.1f} {cy + k:.1f}L{cx} {cy + r}'
            f'L{cx - k:.1f} {cy + k:.1f}L{cx - r} {cy}L{cx - k:.1f} {cy - k:.1f}Z" fill="{c}"/>')


def bubble(x, y, ch, c="#a3361c", w=30):
    """Speech bubble with one glyph (? or !), tail at bottom-left. Language-neutral."""
    h = w * .86
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h:.0f}" rx="{w * .4:.0f}" fill="#fff"/>'
            f'<path d="M{x + 5} {y + h - 3:.0f}l-5 9 11-5z" fill="#fff"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + h * .78:.0f}" text-anchor="middle" font-family="Fredoka, Nunito, sans-serif" '
            f'font-weight="600" font-size="{w * .66:.0f}" fill="{c}">{ch}</text>')


def heart(cx, cy, s, c=BERRY):
    return (f'<path transform="translate({cx} {cy}) scale({s})" d="M0 6C-9-1-12-8-6-11-3-12-1-10 0-8 1-10 3-12 6-11 12-8 9-1 0 6Z" fill="{c}"/>')


def check(cx, cy, r, bg=MINT_D):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{bg}"/>'
            f'<path d="M{cx - r * .45:.1f} {cy + r * .02:.1f}l{r * .3:.1f} {r * .3:.1f} {r * .6:.1f}-{r * .62:.1f}" fill="none" '
            f'stroke="#fff" stroke-width="{max(2, r * .26):.1f}" stroke-linecap="round" stroke-linejoin="round"/>')


def svg(vb, body, cls, extra=""):
    return f'<svg class="{cls}" viewBox="{vb}" aria-hidden="true" focusable="false"{extra}>{body}</svg>'


def disc(cx, cy, r, c):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}"/>'


# ---------- myth / fact pose pairs (viewBox 0 0 120 96, shown about 100px wide) ----------
def myth_pic(n, side, body):
    bg = DISC_MYTH if side == "front" else DISC_FACT
    inner = disc(60, 52, 40, bg) + body
    if side == "back":
        inner = disc(60, 52, 40, bg) + f'<g class="pop">{body}</g>'
    return svg("0 0 120 96", inner, f"pic pic-{side}")


PAPER = (f'<rect x="178" y="92" width="50" height="62" rx="7" fill="#fff" stroke="{PLUM}" stroke-width="4"/>'
         + line("M188 108h30M188 120h30M188 132h18", 4, "#cdbfc9"))
MYTHS = {
    # 1. "Our immigration status": worried, holding a paper with a big ?  ->  beaming, holding up a mint coverage card
    1: (
        buddy(54, 92, .36,
              arm("M74 124q-20 14-18 40") + arm("M166 122q18 0 22-8") + BODY + face("wide", "o", "worried", True)
              + PAPER + f'<text x="203" y="147" text-anchor="middle" font-family="Fredoka, Nunito, sans-serif" font-weight="600" font-size="30" fill="#a3361c">?</text>'
              + f'<path d="M172 54q10 14 0 21q-10-7 0-21z" fill="{SKY}"/>'),
        buddy(52, 92, .36,
              arm("M72 112q-28-18-24-54") + arm("M168 112q24-16 30-50") + BODY + face("happy", "beam")
              + f'<g transform="rotate(-8 214 40)"><rect x="176" y="14" width="76" height="52" rx="9" fill="{MINT_D}"/>'
              + f'<rect x="186" y="26" width="26" height="6" rx="3" fill="#fff" opacity=".8"/><rect x="186" y="38" width="38" height="6" rx="3" fill="#fff" opacity=".8"/>'
              + check(236, 48, 10, "#16634d") + '</g>')
        + star(14, 22, 7, MARIGOLD) + star(106, 84, 6, BERRY) + heart(20, 70, .9),
    ),
    # 2. "We both work, so we make too much": puzzled, lunchbox in hand, staring at a coin stack  ->  beaming thumbs up by the coins
    2: (
        buddy(48, 92, .36,
              arm("M74 124q-18 10-20 30") + arm("M166 124q14 10 14 26") + BODY + face("dot", "squiggle", "puzzled", True)
              + f'<rect x="28" y="150" width="44" height="34" rx="8" fill="{CORAL}"/><path d="M40 150v-8h20v8" fill="none" stroke="{PLUM}" stroke-width="5" stroke-linecap="round"/>')
        + ''.join(f'<ellipse cx="96" cy="{86 - i * 7}" rx="12" ry="4.5" fill="{MARIGOLD}" stroke="#c98a12" stroke-width="1.5"/>' for i in range(5))
        + bubble(84, 8, "?"),
        buddy(48, 92, .36,
              arm("M74 122q-22 4-26 30") + arm("M168 112q26-10 24-46") + f'<circle cx="194" cy="58" r="12" fill="{WHITE}"/><path d="M190 50v-14" stroke="{WHITE}" stroke-width="9" stroke-linecap="round"/>'
              + BODY + face("happy", "beam"))
        + ''.join(f'<ellipse cx="96" cy="{86 - i * 7}" rx="12" ry="4.5" fill="{MARIGOLD}" stroke="#c98a12" stroke-width="1.5"/>' for i in range(3))
        + check(98, 52, 10) + star(14, 24, 7, MARIGOLD) + star(108, 20, 5, BERRY),
    ),
    # 3. "Medi-Cal doesn't cover the dentist": puzzled, holding a toothbrush with a ?  ->  beaming, toothbrush up, sparkles
    3: (
        buddy(54, 92, .36,
              arm("M74 124q-20 12-20 36") + arm("M166 120q22-4 30-22") + BODY + face("dot", "squiggle", "puzzled", True)
              + f'<g transform="rotate(30 200 92)"><rect x="194" y="70" width="12" height="70" rx="6" fill="{MINT}"/><rect x="190" y="52" width="20" height="24" rx="5" fill="#fff" stroke="{SKY}" stroke-width="4"/></g>')
        + bubble(80, 6, "?"),
        buddy(50, 92, .36,
              arm("M72 120q-24-4-30-26") + arm("M168 112q22-14 26-50") + BODY + face("happy", "beam")
              + f'<g transform="rotate(-12 196 40)"><rect x="190" y="22" width="12" height="70" rx="6" fill="{MINT}"/><rect x="186" y="2" width="20" height="26" rx="5" fill="#fff" stroke="{SKY}" stroke-width="4"/></g>')
        + star(102, 20, 8, MARIGOLD) + star(110, 46, 5, BERRY) + star(14, 30, 6, MARIGOLD) + check(100, 78, 9),
    ),
    # 4. "Wait for open enrollment": worried next to a big clock  ->  beaming, pointing at a calendar where every day is open
    4: (
        buddy(44, 92, .36,
              arm("M74 124q-18 12-18 34") + arm("M166 124q12 16 8 34") + BODY + face("wide", "o", "worried", True)
              + f'<path d="M172 54q10 14 0 21q-10-7 0-21z" fill="{SKY}"/>')
        + f'<circle cx="94" cy="56" r="20" fill="#fff" stroke="{PLUM}" stroke-width="3"/>' + line("M94 56v-11M94 56l8 5", 3)
        + ''.join(f'<circle cx="{94 + 15 * dx}" cy="{56 + 15 * dy}" r="1.6" fill="{PLUM}"/>' for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)))
        + line("M80 34l-5-5M108 34l5-5", 3),
        buddy(40, 92, .36,
              arm("M72 122q-20 6-26 28") + arm("M168 116q26-4 40-14") + BODY + face("happy", "beam"))
        + f'<rect x="66" y="22" width="46" height="46" rx="8" fill="#fff" stroke="{PLUM}" stroke-width="3"/><path d="M66 30a8 8 0 0 1 8-8h30a8 8 0 0 1 8 8v4H66z" fill="{CORAL}"/>'
        + ''.join(check(74 + 10 * (i % 4), 42 + 10 * (i // 4), 3.6) for i in range(12))
        + star(12, 24, 7, MARIGOLD) + star(110, 84, 5, BERRY),
    ),
    # 5. "Baby teeth fall out": puzzled with a ?  ->  beaming, with a baby-tooth sibling
    5: (
        buddy(56, 92, .36,
              arm("M72 116q-30-6-34-40") + arm("M168 116q30-6 34-40") + BODY + face("dot", "squiggle", "puzzled", True))
        + bubble(84, 6, "?"),
        buddy(48, 92, .36,
              arm("M72 112q-30-20-26-56") + arm("M168 120q28 4 40 26") + BODY + face("happy", "beam"))
        + buddy(92, 92, .17, BODY + face("dot", "small") + line("M112 50q-6-20 10-22", 7))
        + star(14, 20, 7, MARIGOLD) + star(106, 16, 6, BERRY) + star(108, 62, 5, MARIGOLD),
    ),
    # 6. "Medi-Cal is ending because of the new rules": worried under a rain cloud  ->  beaming under an umbrella, sun out
    6: (
        buddy(48, 92, .34,
              arm("M74 124q-20 10-20 32") + arm("M166 124q20 10 20 32") + BODY + face("wide", "o", "worried", True))
        + f'<g fill="#c9bcd0"><circle cx="84" cy="20" r="10"/><circle cx="98" cy="15" r="13"/><circle cx="111" cy="21" r="9"/><rect x="76" y="20" width="42" height="11" rx="5.5"/></g>'
        + line("M86 38l-3 7M98 38l-3 7M110 38l-3 7M92 52l-3 7M104 52l-3 7", 3, SKY),
        f'<circle cx="16" cy="18" r="9" fill="{MARIGOLD}"/>'
        + buddy(54, 92, .36,
                arm("M72 120q-22 6-26 30") + arm("M168 116q20-12 24-40") + BODY + face("happy", "beam")
                + f'<path d="M192 76V-26" stroke="{PLUM}" stroke-width="6" stroke-linecap="round"/>')
        + f'<path d="M46 24q34-34 68 0q-8.5-6-17 0q-8.5-6-17 0q-8.5-6-17 0q-8.5-6-17 0z" fill="{CORAL}"/>'
        + buddy(92, 92, .16, BODY + face("happy", "small"))
        + star(110, 70, 6, MARIGOLD) + star(14, 50, 5, BERRY),
    ),
}


# ---------- spot illustrations ----------
def spot_plan():
    body = (disc(52, 54, 40, "#ffe1a6")
            + buddy(42, 92, .36, arm("M72 122q-20 6-22 28") + arm("M168 118q16 2 22-8") + BODY + face("open", "smile")
                    + f'<rect x="176" y="70" width="64" height="84" rx="9" fill="{MARIGOLD}"/><rect x="184" y="84" width="48" height="62" rx="5" fill="#fff"/>'
                    + f'<rect x="196" y="64" width="24" height="14" rx="5" fill="{PLUM}"/>'
                    + check(196, 100, 6) + line("M208 100h16", 5, "#cdbfc9") + check(196, 118, 6) + line("M208 118h16", 5, "#cdbfc9")
                    + check(196, 136, 6) + line("M208 136h12", 5, "#cdbfc9"))
            + star(92, 14, 6, BERRY))
    return svg("0 0 104 96", body, "spot spot-plan")


def spot_apply():
    def chip(x, y, inner, c):
        return f'<g transform="translate({x} {y})"><circle r="17" fill="{c}"/>{inner}</g>'
    laptop = f'<rect x="-10" y="-8" width="20" height="13" rx="2" fill="#fff" stroke="{PLUM}" stroke-width="2.5"/><path d="M-13 8h26" stroke="{PLUM}" stroke-width="3" stroke-linecap="round"/>'
    phone = f'<rect x="-6" y="-10" width="12" height="20" rx="3" fill="#fff" stroke="{PLUM}" stroke-width="2.5"/><circle cy="6" r="1.4" fill="{PLUM}"/>'
    mail = f'<rect x="-10" y="-7" width="20" height="14" rx="2" fill="#fff" stroke="{PLUM}" stroke-width="2.5"/><path d="M-9-5l9 7 9-7" fill="none" stroke="{PLUM}" stroke-width="2.5" stroke-linejoin="round"/>'
    body = (f'<rect x="0" y="0" width="200" height="140" rx="28" fill="#e2f0fa"/>'
            + f'<path d="M0 116q100-26 200 0v-0 24H0z" fill="{MINT}" opacity=".55"/>'
            + buddy(66, 128, .5, arm("M72 122q-22 6-24 30") + arm("M168 112q30-10 44-36") + BODY + face("open", "smile", "", False))
            + chip(132, 34, laptop, "#fff") + chip(168, 64, phone, "#fff") + chip(150, 104, mail, "#fff")
            + star(24, 26, 7, MARIGOLD) + star(186, 20, 5, BERRY))
    return svg("0 0 200 140", body, "spot spot-apply")


def spot_help():
    body = (disc(60, 56, 44, "#ffe1d8")
            + buddy(52, 100, .4, arm("M72 120q-22 8-22 30") + arm("M168 116q22-6 20-34")
                    + f'<rect x="178" y="54" width="22" height="38" rx="6" fill="{PLUM}"/><rect x="182" y="60" width="14" height="22" rx="2" fill="{SKY}"/>'
                    + BODY + face("open", "smile"))
            + f'<rect x="72" y="6" width="42" height="32" rx="14" fill="#fff"/><path d="M80 36l-4 9 11-6z" fill="#fff"/>' + heart(93, 23, 1.1)
            + star(14, 24, 6, MARIGOLD))
    return svg("0 0 120 104", body, "spot spot-help")


def hero_scene():
    """Parent, child, sun and hill. The tooth buddy is a separate SVG on top (.hero-buddy) so its idle bounce is
    a composited transform on an HTML box, not an SVG repaint."""
    b = (f'<rect y="60" width="540" height="350" fill="#ffeedd"/>'
         f'<circle cx="330" cy="190" r="150" fill="{MARIGOLD}"/>'
         f'<circle cx="330" cy="190" r="196" fill="none" stroke="{MARIGOLD}" stroke-width="3" stroke-dasharray="2 14" stroke-linecap="round" opacity=".7"/>'
         + line("M28 130q10-14 24 0M470 100q10-14 24 0", 6, CORAL)
         + star(84, 104, 10, BERRY) + star(512, 300, 8, BERRY)
         + '<rect x="40" y="200" width="70" height="26" rx="13" fill="#fff" opacity=".85"/><rect x="60" y="186" width="40" height="26" rx="13" fill="#fff" opacity=".85"/>'
         f'<path d="M0 352C120 316 280 330 540 360V410H0Z" fill="{MINT}"/><path d="M0 392C160 372 320 382 540 390V410H0Z" fill="#46b393"/>'
         # parent
         '<g><rect x="128" y="316" width="24" height="70" rx="12" fill="#4b3c7d"/><rect x="164" y="316" width="24" height="70" rx="12" fill="#4b3c7d"/>'
         f'<ellipse cx="140" cy="388" rx="18" ry="9" fill="{PLUM}"/><ellipse cx="178" cy="388" rx="18" ry="9" fill="{PLUM}"/>'
         f'<rect x="112" y="206" width="94" height="132" rx="46" fill="{BERRY}"/>'
         '<path d="M120 250q-22 40-6 70" fill="none" stroke="#c46f45" stroke-width="18" stroke-linecap="round"/>'
         '<path d="M198 248q30 34 52 52" fill="none" stroke="#c46f45" stroke-width="18" stroke-linecap="round"/>'
         f'<path d="M198 248q28 32 44 46" fill="none" stroke="{BERRY}" stroke-width="22" stroke-linecap="round" stroke-dasharray="30 200"/>'
         '<rect x="146" y="188" width="26" height="28" rx="10" fill="#c46f45"/><circle cx="159" cy="166" r="36" fill="#c46f45"/>'
         '<path d="M122 166c0-30 18-42 38-42s38 12 38 40c-10-14-30-20-46-18-12 2-22 8-30 20z" fill="#2b1a1f"/><circle cx="166" cy="122" r="17" fill="#2b1a1f"/>'
         '<g class="blink"><circle cx="146" cy="170" r="4.5" fill="#2b1a1f"/><circle cx="174" cy="170" r="4.5" fill="#2b1a1f"/></g>'
         '<path d="M150 184q10 9 20 0" fill="none" stroke="#2b1a1f" stroke-width="4" stroke-linecap="round"/>'
         f'<circle cx="138" cy="182" r="6" fill="{BERRY}" opacity=".35"/><circle cx="182" cy="182" r="6" fill="{BERRY}" opacity=".35"/></g>'
         # child
         f'<g><rect x="246" y="342" width="20" height="44" rx="10" fill="{PLUM}"/><rect x="274" y="342" width="20" height="44" rx="10" fill="{PLUM}"/>'
         f'<ellipse cx="256" cy="388" rx="15" ry="8" fill="{CORAL}"/><ellipse cx="284" cy="388" rx="15" ry="8" fill="{CORAL}"/>'
         f'<rect x="236" y="276" width="68" height="80" rx="32" fill="{CORAL}"/>'
         '<path d="M244 300q-8 2-10 4" fill="none" stroke="#8d5a3b" stroke-width="15" stroke-linecap="round"/>'
         '<path d="M300 300q22 6 28-18" fill="none" stroke="#8d5a3b" stroke-width="14" stroke-linecap="round"/>'
         '<circle cx="270" cy="244" r="32" fill="#8d5a3b"/>'
         '<path d="M238 244c0-26 14-38 32-38s34 12 32 34c-8-10-16-14-26-12-6-8-18-6-24 0-6 0-10 6-14 16z" fill="#1f1418"/>'
         '<g class="blink"><circle cx="258" cy="250" r="4.5" fill="#1f1418"/><circle cx="284" cy="250" r="4.5" fill="#1f1418"/></g>'
         '<path d="M260 262q11 12 22 0z" fill="#fff" stroke="#1f1418" stroke-width="3.5" stroke-linejoin="round"/>'
         f'<circle cx="250" cy="262" r="6" fill="{CORAL}" opacity=".45"/><circle cx="292" cy="262" r="6" fill="{CORAL}" opacity=".45"/></g>'
         f'<ellipse cx="432" cy="376" rx="46" ry="9" fill="{MINT_D}" opacity=".55"/>')
    scene = svg("0 60 540 350", b, "hero-scene")
    bud = buddy(432, 372, .84,
                f'<g class="wave">{arm("M168 118q34-6 42-44")}</g>' + arm("M72 122q-24 12-22 40") + BODY + face("open", "smile", "", True))
    buddy_svg = svg("370 180 170 200", bud, "hero-buddy")
    return f'<div class="hero-art" aria-hidden="true">{scene}{buddy_svg}</div>'


def age_buddies():
    """One small buddy per age group, shown with the matching 'Medi-Cal Dental, by age' text."""
    base = disc(40, 40, 34, "#ffd9e3")

    def one(group, inner, extra=""):
        return svg("0 0 80 80", base + extra + inner, "age-pic", f' data-ages="{group}"')
    return (
        one("baby", buddy(40, 72, .3, BODY + face("dot", "small") + line("M112 50q-8-22 12-24", 7)
                          + f'<circle cx="120" cy="160" r="10" fill="{SKY}"/><rect x="112" y="150" width="16" height="10" rx="4" fill="{SKY}"/>'))
        + one("kid", buddy(40, 74, .3, arm("M168 116q20-10 22-40") + BODY + face("open", "smile")
                           + f'<path d="M78 70q0-34 42-34t42 34z" fill="{CORAL}"/><path d="M150 64q22 0 30 8" stroke="{CORAL}" stroke-width="9" stroke-linecap="round"/>'))
        + one("teen", buddy(40, 74, .3, BODY + face("open", "braces")))
        + one("adult", buddy(40, 74, .3, arm("M72 116q-22-6-24-34") + BODY + face("open", "smile")))
        + one("senior", buddy(40, 74, .3, BODY + face("happy", "smile")
                              + f'<g fill="none" stroke="{PLUM}" stroke-width="4"><circle cx="105" cy="108" r="13"/><circle cx="135" cy="108" r="13"/><path d="M118 108h4"/></g>'
                              + line("M90 70q14-14 30-6q16-8 30 6", 6, "#c9bcd0")))
    )


def map_buddy():
    body = (disc(36, 42, 30, "#ffe1d8")
            + buddy(30, 70, .28, arm("M168 112q24-18 26-52") + BODY + face("open", "smile")
                    + f'<path d="M196 4c-16 0-26 12-26 25 0 18 26 40 26 40s26-22 26-40c0-13-10-25-26-25z" fill="{BERRY}"/><circle cx="196" cy="29" r="9" fill="#fff"/>'))
    return svg("0 0 72 72", body, "map-buddy")


def sdoh_spots():
    coins = svg("0 0 64 64", disc(32, 32, 28, "#ffd9cb")
                + buddy(26, 58, .24, arm("M168 120q14 10 16 30") + BODY + face("open", "smile"))
                + ''.join(f'<ellipse cx="46" cy="{52 - i * 6}" rx="10" ry="4" fill="{MARIGOLD}" stroke="#c98a12" stroke-width="1.4"/>' for i in range(4)),
                "sdoh-pic")
    clinic = svg("0 0 64 64", disc(32, 32, 28, "#d3e8f7")
                 + buddy(24, 58, .24, arm("M168 118q18-8 22-30") + BODY + face("open", "smile"))
                 + f'<rect x="38" y="24" width="22" height="30" rx="4" fill="#fff" stroke="{PLUM}" stroke-width="2"/>'
                 + f'<path d="M49 30v12M43 36h12" stroke="{BERRY}" stroke-width="3.4" stroke-linecap="round"/>',
                 "sdoh-pic")
    return coins, clinic


def note_buddy():
    body = (disc(36, 38, 32, "#ffe1a6")
            + buddy(36, 70, .3, arm("M168 116q22-10 22-40") + BODY + face("open", "smile")
                    + f'<path d="M72 54l48-20 48 20-48 20z" fill="{PLUM}"/><path d="M96 64v14q24 12 48 0V64" fill="{PLUM}"/>'
                    + f'<path d="M168 54v26" stroke="{MARIGOLD}" stroke-width="5"/><circle cx="168" cy="82" r="5" fill="{MARIGOLD}"/>'))
    return svg("0 0 72 72", body, "note-pic")


def foot_buddy():
    body = buddy(24, 46, .2, f'<g class="wave">{arm("M168 118q34-6 42-44")}</g>' + BODY + face("open", "smile"))
    return svg("0 0 52 48", body, "foot-pic")


def splash():
    b = (f'<circle class="sp-disc" cx="140" cy="122" r="94" fill="#ffe1a6"/>'
         f'<circle class="sp-ring" cx="140" cy="122" r="110" fill="none" stroke="{MARIGOLD}" stroke-width="2.5" stroke-dasharray="2 10" stroke-linecap="round"/>'
         + buddy(140, 214, .82, f'<g class="wave">{arm("M168 118q34-6 42-44")}</g>' + arm("M72 122q-24 12-22 40") + BODY + face("open", "smile", "", True), "sp-bud")
         + f'<g class="sp-spark s1">{star(236, 50, 12, BERRY)}</g><g class="sp-spark s2">{star(44, 74, 10, MARIGOLD)}</g><g class="sp-spark s3">{star(236, 180, 8, MINT_D)}</g>')
    return f'<svg class="splash-art" viewBox="0 0 280 240" focusable="false">{b}</svg>'


def brand():
    return ('<svg class="brand-mark" viewBox="62 32 116 188" aria-hidden="true" focusable="false">'
            + BODY + f'<g fill="{PLUM}"><circle cx="106" cy="110" r="8"/><circle cx="134" cy="110" r="8"/></g>'
            + line("M107 136q13 13 26 0", 7) + '</svg>')


def print_flyer():
    """Flyer: the buddy and a child tooth waving next to the headline (ink-light: small fills, white paper)."""
    body = (disc(70, 70, 60, "#ffe9c2")
            + buddy(62, 128, .5, f'<g>{arm("M168 118q34-6 42-44")}</g>' + arm("M72 122q-24 12-22 40") + BODY + face("open", "smile"))
            + buddy(112, 128, .22, arm("M72 116q-24-8-26-36") + BODY + face("happy", "smile"))
            + star(18, 20, 8, BERRY) + star(128, 26, 6, MARIGOLD))
    return svg("0 0 140 136", body, "flyer-art")


PIECES = {
    "defs": DEFS,
    "brand": brand(),
    "splash": splash(),
    "hero": hero_scene(),
    "plan": spot_plan(),
    "note": note_buddy(),
    "sdoh1": sdoh_spots()[0],
    "sdoh2": sdoh_spots()[1],
    "age": age_buddies(),
    "apply": spot_apply(),
    "help": spot_help(),
    "foot": foot_buddy(),
    "pbrand": brand(),
    "pflyer": print_flyer(),
}
PAGES = {"index.html": [k for k in PIECES if k not in ("pbrand", "pflyer")],
         "checklist.html": ["defs", "pbrand"], "es/checklist.html": ["defs", "pbrand"],
         "flyer.html": ["defs", "pbrand", "pflyer"], "es/flyer.html": ["defs", "pbrand", "pflyer"]}
for n, (front, back) in MYTHS.items():
    PIECES[f"m{n}f"] = myth_pic(n, "front", front)
    PIECES[f"m{n}b"] = myth_pic(n, "back", back)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        out = pathlib.Path(sys.argv[2])
        cells = "".join(f'<figure><figcaption>{k}</figcaption>{v}</figure>' for k, v in PIECES.items() if k not in ("defs", "splash"))
        cells += f'<figure><figcaption>splash</figcaption>{PIECES["splash"]}</figure>'
        out.write_text(f'<!doctype html><meta charset=utf-8><style>body{{background:{CREAM};font:14px sans-serif;display:flex;flex-wrap:wrap;gap:16px;padding:16px}}'
                       'figure{margin:0;background:#fff;padding:8px;border-radius:12px}figure:nth-child(n+11){background:#ffe4d9}figure svg{display:block;width:220px;height:auto;max-height:240px}'
                       '.hero-art{position:relative;width:440px}.hero-art .hero-scene{width:100%;display:block}.hero-art .hero-buddy{position:absolute;left:68.5%;top:34.3%;width:31.5%}'
                       '.age-pic{width:60px!important}</style>'
                       f'<svg width="0" height="0" style="position:absolute"><defs>{DEFS}</defs></svg>{cells}')
        print("preview", out)
        sys.exit()
    for page, keys in PAGES.items():
        path = ROOT / page
        s = path.read_text()
        for k in [k for k in keys if k.startswith("m") and k[1:2].isdigit()] + [k for k in keys if not (k.startswith("m") and k[1:2].isdigit())]:
            v = PIECES[k]
            pat = re.compile(r"<!--ART:%s-->.*?<!--/ART:%s-->" % (k, k), re.S)
            assert pat.search(s), f"missing marker {k} in {page}"
            s = pat.sub(lambda m: f"<!--ART:{k}-->{v}<!--/ART:{k}-->", s)
        path.write_text(s)
        print("wrote art into", page)
