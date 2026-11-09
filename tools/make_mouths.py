"""Writes the tap-a-tooth mouth SVGs (EN + ES) into index.html and es/index.html.
Run once after editing; the site itself has no build step.
Occlusal chart view: upper arch on top (front teeth at the top), lower arch below."""
import math, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (group, width along the arch, depth, kind) from the patient's right molar to left molar
KID = ["six", "bm", "bm", "bc", "bi", "bi", "bi", "bi", "bc", "bm", "bm", "six"]
ADULT = ["wis", "m", "m", "p", "p", "c", "i", "i", "i", "i", "c", "p", "p", "m", "m", "wis"]
SIZE = {  # width, depth
    "six": (31, 31), "bm": (24, 25), "bc": (17, 20), "bi": (16, 17),
    "wis": (25, 26), "m": (27, 28), "p": (21, 23), "c": (19, 22), "i": (18, 19),
}
GROUP = {"six": "six-molar", "bm": "baby-molar", "bc": "baby-front", "bi": "baby-front",
         "wis": "wisdom", "m": "back", "p": "back", "c": "front", "i": "front"}

NAMES = {
    "en": {
        "six": "first adult molar", "bm": "baby molar", "bc": "baby canine", "bi": "baby front tooth",
        "wis": "wisdom tooth", "m": "molar", "p": "premolar", "c": "canine", "i": "front tooth",
        "upper": "Upper", "lower": "Lower", "right": "right", "left": "left",
        "kid": "Kid's teeth, about age 7. Use arrow keys to move between teeth.",
        "adult": "Adult teeth. Use arrow keys to move between teeth.",
        "top": "Top teeth", "bottom": "Bottom teeth",
    },
    "es": {
        "six": "primera muela permanente", "bm": "muela de leche", "bc": "colmillo de leche", "bi": "diente de leche del frente",
        "wis": "muela del juicio", "m": "muela", "p": "premolar", "c": "colmillo", "i": "diente del frente",
        "upper": "De arriba", "lower": "De abajo", "right": "derecho", "left": "izquierdo",
        "kid": "Dientes de un niño de unos 7 años. Use las flechas para moverse entre los dientes.",
        "adult": "Dientes de un adulto. Use las flechas para moverse entre los dientes.",
        "top": "Dientes de arriba", "bottom": "Dientes de abajo",
    },
}

def arch(teeth, cx, cy, rx, ry, upper, span_deg):
    """Place teeth along half-ellipse. theta 0 = front center."""
    # sample arc length
    n = 2000
    th = [math.radians(-span_deg + 2 * span_deg * k / n) for k in range(n + 1)]
    def pt(t):
        x = cx + rx * math.sin(t)
        y = cy - ry * math.cos(t) if upper else cy + ry * math.cos(t)
        return x, y
    pts = [pt(t) for t in th]
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + math.dist(a, b))
    total = L[-1]
    gap = 3.0
    scale = (total - gap * (len(teeth) - 1)) / sum(SIZE[k][0] for k in teeth)
    widths = [SIZE[k][0] * scale for k in teeth]
    out, s = [], 0.0
    for k, w in zip(teeth, widths):
        mid = s + w / 2
        i = min(range(len(L)), key=lambda j: abs(L[j] - mid))
        t = th[i]
        x, y = pts[i]
        # tangent angle
        dx = rx * math.cos(t); dy = (ry * math.sin(t)) if upper else (-ry * math.sin(t))
        ang = math.degrees(math.atan2(dy, dx))
        out.append((k, x, y, ang, scale))
        s += w + gap
    gum = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in pts[::40] + [pts[-1]])
    return out, gum

def tooth_svg(k, x, y, ang, sc, label, gid, idx):
    w, d = SIZE[k][0] * sc, SIZE[k][1] * sc
    r = 10 if k in ("six", "m", "wis", "bm") else 8
    deco = ""
    if k in ("six", "m", "wis", "bm"):
        deco = f'<path class="groove" d="M{-w/2+9:.1f} 0H{w/2-9:.1f}M0 {-d/2+9:.1f}V{d/2-9:.1f}"/>'
    elif k == "p":
        deco = f'<path class="groove" d="M{-w/2+6:.1f} 0H{w/2-6:.1f}"/>'
    return (f'<g class="tooth" role="radio" aria-checked="false" tabindex="-1" data-group="{gid}" data-i="{idx}" '
            f'aria-label="{label}" transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f})">'
            f'<rect x="{-w/2}" y="{-d/2}" width="{w}" height="{d}" rx="{r}"/>{deco}</g>')

def mouth(kind, lang):
    N = NAMES[lang]
    teeth = KID if kind == "kid" else ADULT
    if kind == "kid":
        (U, gu), (Lw, gl) = arch(teeth, 180, 196, 112, 150, True, 82), arch(teeth, 180, 244, 112, 150, False, 82)
    else:
        (U, gu), (Lw, gl) = arch(teeth, 180, 196, 130, 160, True, 84), arch(teeth, 180, 244, 130, 160, False, 84)
    gums = f'<path class="gum" d="{gu}"/><path class="gum" d="{gl}"/>'
    parts, idx = [], 0
    for row, side in ((U, "upper"), (Lw, "lower")):
        seq = row if side == "upper" else row  # lower drawn patient's right (viewer left) to left too
        for j, (k, x, y, ang, sc) in enumerate(seq):
            right = (x < 180)  # viewer's left = patient's right
            sidew = N["right"] if right else N["left"]
            if lang == "en":
                label = f'{N[side]} {sidew} {N[k]}'
            else:
                label = f'{N[k].capitalize()} {N[side].lower()}, lado {sidew}'
            parts.append(tooth_svg(k, x, y, ang, sc, label, GROUP[k], idx)); idx += 1
    # lower row: reorder focus so arrows go upper R->L then lower L->R (a loop)
    h = 440
    return (f'<svg class="mouth-svg" viewBox="0 0 360 {h}" role="radiogroup" aria-label="{N[kind]}">'
            f'<text aria-hidden="true" class="arch-label" x="180" y="214" text-anchor="middle">{N["top"]}</text>'
            f'<text aria-hidden="true" class="arch-label" x="180" y="238" text-anchor="middle">{N["bottom"]}</text>'
            + '<g aria-hidden="true">' + gums + '</g>' + "".join(parts) + '</svg>')

for lang, path in (("en", ROOT / "index.html"), ("es", ROOT / "es" / "index.html")):
    if not path.exists() or "<!--MOUTH:kid-->" not in path.read_text():
        print("skip", path); continue
    html = path.read_text()
    for kind in ("kid", "adult"):
        svg = mouth(kind, lang)
        html, n = re.subn(rf'<!--MOUTH:{kind}-->.*?<!--/MOUTH:{kind}-->',
                          f'<!--MOUTH:{kind}-->{svg}<!--/MOUTH:{kind}-->', html, flags=re.S)
        assert n == 1, (lang, kind)
    path.write_text(html)
    print("wrote", path)
