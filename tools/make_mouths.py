"""Writes the tap-a-tooth mouth SVGs (EN + ES) into index.html and es/index.html.
Run after make_es.py; the site itself has no build step.
Occlusal chart view: upper arch on top (front teeth at the top), lower arch below.
Five stages: no teeth yet (gums), baby teeth (20), mixed (about age 8: 4 adult front teeth,
4 first adult molars, the rest baby teeth), adult (28 + 4 wisdom teeth), no natural teeth (gum ridges)."""
import math, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# one arch, from the patient's right back tooth to the left back tooth
TEETH = {
    "primary": ["bm", "bm", "bc", "bi", "bi", "bi", "bi", "bc", "bm", "bm"],
    "mixed": ["six", "bm", "bm", "bc", "pi", "pi", "pi", "pi", "bc", "bm", "bm", "six"],
    "adult": ["wis", "m", "m", "p", "p", "c", "i", "i", "i", "i", "c", "p", "p", "m", "m", "wis"],
}
SIZE = {  # width along the arch, depth
    "six": (31, 31), "bm": (24, 25), "bc": (17, 20), "bi": (16, 17), "pi": (19, 19),
    "wis": (25, 26), "m": (27, 28), "p": (21, 23), "c": (19, 22), "i": (18, 19),
}
GROUP = {"six": "six-molar", "bm": "baby-molar", "bc": "baby-front", "bi": "baby-front", "pi": "front",
         "wis": "wisdom", "m": "back", "p": "back", "c": "front", "i": "front"}
PERM = {"six", "pi", "wis", "m", "p", "c", "i"}
MOLARISH = {"six", "m", "wis", "bm"}
ARCH = {  # rx, ry, half-span in degrees
    "primary": (104, 140, 80), "mixed": (114, 150, 82), "adult": (130, 160, 84),
    "none": (104, 140, 80), "edentulous": (124, 156, 82),
}

NAMES = {
    "en": {
        "six": "first adult molar", "bm": "baby molar", "bc": "baby canine", "bi": "baby front tooth", "pi": "adult front tooth",
        "wis": "wisdom tooth", "m": "molar", "p": "premolar", "c": "canine", "i": "front tooth",
        "upper": "Upper", "lower": "Lower", "right": "right", "left": "left",
        "gums_u": "Top gums", "gums_l": "Bottom gums",
        "ridge_u": "Top gum ridge, no teeth", "ridge_l": "Bottom gum ridge, no teeth",
        "none": "Baby's gums, no teeth yet. Use arrow keys to move between the top and bottom.",
        "primary": "Baby teeth, 20 teeth. Use arrow keys to move between teeth.",
        "mixed": "Mixed baby and adult teeth, about age 8. Use arrow keys to move between teeth.",
        "adult": "Adult teeth, 28 plus 4 wisdom teeth. Use arrow keys to move between teeth.",
        "edentulous": "A mouth with no natural teeth. Use arrow keys to move between the top and bottom.",
        "top": "Top", "bottom": "Bottom",
    },
    "es": {
        "six": "primera muela permanente", "bm": "muela de leche", "bc": "colmillo de leche", "bi": "diente de leche del frente", "pi": "diente permanente del frente",
        "wis": "muela del juicio", "m": "muela", "p": "premolar", "c": "colmillo", "i": "diente del frente",
        "upper": "De arriba", "lower": "De abajo", "right": "derecho", "left": "izquierdo",
        "gums_u": "Encías de arriba", "gums_l": "Encías de abajo",
        "ridge_u": "Encía de arriba, sin dientes", "ridge_l": "Encía de abajo, sin dientes",
        "none": "Encías de un bebé, todavía sin dientes. Use las flechas para moverse entre arriba y abajo.",
        "primary": "Dientes de leche, 20 dientes. Use las flechas para moverse entre los dientes.",
        "mixed": "Dientes de leche y permanentes, a los 8 años más o menos. Use las flechas para moverse entre los dientes.",
        "adult": "Dientes de adulto, 28 más 4 muelas del juicio. Use las flechas para moverse entre los dientes.",
        "edentulous": "Una boca sin dientes naturales. Use las flechas para moverse entre arriba y abajo.",
        "top": "Arriba", "bottom": "Abajo",
    },
}

CX, CY_U, CY_L = 180, 196, 244

def curve(rx, ry, upper, span_deg, n=2000):
    th = [math.radians(-span_deg + 2 * span_deg * k / n) for k in range(n + 1)]
    cy = CY_U if upper else CY_L
    pts = [(CX + rx * math.sin(t), cy - ry * math.cos(t) if upper else cy + ry * math.cos(t)) for t in th]
    return th, pts

def arch(teeth, rx, ry, upper, span_deg):
    """Place teeth along half an ellipse. theta 0 = front center."""
    th, pts = curve(rx, ry, upper, span_deg)
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + math.dist(a, b))
    gap = 3.0
    scale = (L[-1] - gap * (len(teeth) - 1)) / sum(SIZE[k][0] for k in teeth)
    out, s = [], 0.0
    for k in teeth:
        w = SIZE[k][0] * scale
        mid = s + w / 2
        i = min(range(len(L)), key=lambda j: abs(L[j] - mid))
        t = th[i]
        x, y = pts[i]
        dx = rx * math.cos(t); dy = (ry * math.sin(t)) if upper else (-ry * math.sin(t))
        out.append((k, x, y, math.degrees(math.atan2(dy, dx)), scale))
        s += w + gap
    gum = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in pts[::40] + [pts[-1]])
    return out, gum

def tooth_svg(k, x, y, ang, sc, label, idx):
    w, d = SIZE[k][0] * sc, SIZE[k][1] * sc
    deco = ""
    if k in MOLARISH:
        deco = f'<path class="groove" d="M{-w/2+9:.1f} 0H{w/2-9:.1f}M0 {-d/2+9:.1f}V{d/2-9:.1f}"/>'
    elif k == "p":
        deco = f'<path class="groove" d="M{-w/2+6:.1f} 0H{w/2-6:.1f}"/>'
    cls = "tooth" + (" perm" if k in PERM else "") + (" opt" if k == "wis" else "")
    return (f'<g class="{cls}" role="radio" aria-checked="false" tabindex="-1" data-group="{GROUP[k]}" data-i="{idx}" '
            f'aria-label="{label}" transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f})">'
            f'<rect x="{-w/2:.2f}" y="{-d/2:.2f}" width="{w:.2f}" height="{d:.2f}" rx="2"/>{deco}</g>')

def ridge_svg(rx, ry, span, upper, label, group, idx, thick=34):
    """A tappable gum ridge: a band along the arch, square ends."""
    _, outer = curve(rx + thick / 2, ry + thick / 2, upper, span, 120)
    _, inner = curve(rx - thick / 2, ry - thick / 2, upper, span, 120)
    d = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in outer + inner[::-1]) + " Z"
    return (f'<g class="tooth" role="radio" aria-checked="false" tabindex="-1" data-group="{group}" data-i="{idx}" '
            f'aria-label="{label}"><path class="ridge-hit" d="{d}"/></g>')

def mouth(kind, lang):
    N = NAMES[lang]
    rx, ry, span = ARCH[kind]
    head = (f'<svg class="mouth-svg" viewBox="0 0 360 440" role="radiogroup" aria-label="{N[kind]}">'
            f'<text aria-hidden="true" class="arch-label" x="180" y="214" text-anchor="middle">{N["top"]}</text>'
            f'<text aria-hidden="true" class="arch-label" x="180" y="238" text-anchor="middle">{N["bottom"]}</text>')
    if kind in ("none", "edentulous"):
        key, group = ("gums", "gums") if kind == "none" else ("ridge", "ridge")
        return (head + ridge_svg(rx, ry, span, True, N[key + "_u"], group, 0)
                + ridge_svg(rx, ry, span, False, N[key + "_l"], group, 1) + '</svg>')
    teeth = TEETH[kind]
    (U, gu), (Lw, gl) = arch(teeth, rx, ry, True, span), arch(teeth, rx, ry, False, span)
    parts, idx = [], 0
    for row, side in ((U, "upper"), (Lw, "lower")):
        for k, x, y, ang, sc in row:
            sidew = N["right"] if x < 180 else N["left"]  # viewer's left = patient's right
            label = f'{N[side]} {sidew} {N[k]}' if lang == "en" else f'{N[k].capitalize()} {N[side].lower()}, lado {sidew}'
            parts.append(tooth_svg(k, x, y, ang, sc, label, idx)); idx += 1
    gums = f'<g aria-hidden="true"><path class="gum" d="{gu}"/><path class="gum" d="{gl}"/></g>'
    return head + gums + "".join(parts) + '</svg>'

KINDS = ("none", "primary", "mixed", "adult", "edentulous")
for lang, path in (("en", ROOT / "index.html"), ("es", ROOT / "es" / "index.html")):
    html = path.read_text()
    for kind in KINDS:
        html, n = re.subn(rf'<!--MOUTH:{kind}-->.*?<!--/MOUTH:{kind}-->',
                          lambda m: f'<!--MOUTH:{kind}-->{mouth(kind, lang)}<!--/MOUTH:{kind}-->', html, flags=re.S)
        assert n == 1, (lang, kind)
    path.write_text(html)
    print("wrote", path)
