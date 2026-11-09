"""Writes the clickable California county map (EN + ES) into index.html and es/index.html,
between <!--MAP--> and <!--/MAP-->. Run after make_es.py (and make_mouths.py); no build step.
Geometry: tools/data/ca-counties.json (US Census 2023 cartographic boundary file, 1:5m, public domain;
projected to California Albers and simplified, see the "source" field). No map library, no CDN.
Los Angeles, Riverside and San Bernardino keep their own results; every other county is "other"."""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "tools" / "data" / "ca-counties.json").read_text())
KEY = {"06037": "la", "06065": "riv", "06071": "sb"}
W = 400  # viewBox width

TEXT = {
    "en": {
        "label": "{name} County", "idle": "Pick your county on the map.",
        "map": "Map of California's 58 counties. Pick yours.", "list": "Or choose from a list",
        "names": {},
    },
    "es": {
        "label": "Condado de {name}", "idle": "Elija su condado en el mapa.",
        "map": "Mapa de los 58 condados de California. Elija el suyo.", "list": "O elija de una lista",
        "names": {"Los Angeles": "Los Ángeles"},
    },
}

xs = [p[0] for c in DATA["counties"] for poly in c["polygons"] for ring in poly for p in ring]
ys = [p[1] for c in DATA["counties"] for poly in c["polygons"] for ring in poly for p in ring]
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
PAD = 2
K = (W - 2 * PAD) / (x1 - x0)
H = round((y1 - y0) * K + 2 * PAD)


def fmt(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def path_d(polys):
    out = []
    for poly in polys:
        for ring in poly:
            pts = [(PAD + (x - x0) * K, PAD + (y1 - y) * K) for x, y in ring]
            if pts[0] == pts[-1]:
                pts = pts[:-1]
            out.append("M" + " ".join(f"{fmt(x)} {fmt(y)}" for x, y in pts) + "Z")
    return "".join(out)


def block(lang):
    t = TEXT[lang]
    paths, opts = [], []
    for c in DATA["counties"]:
        name = t["names"].get(c["name"], c["name"])
        label = t["label"].format(name=name)
        key = KEY.get(c["geoid"], "other")
        paths.append(f'<path id="cty-{c["geoid"]}" class="cty" d="{path_d(c["polygons"])}" data-county="{key}" '
                     f'data-name="{name}" tabindex="0" role="button" aria-label="{label}"/>')
        opts.append(f'<button type="button" class="county-opt" data-county="{key}" data-name="{name}">{name}</button>')
    return (
        f'\n        <div class="county-map" data-label="{t["label"]}">'
        f'\n          <p class="map-label" aria-hidden="true" data-idle="{t["idle"]}">{t["idle"]}</p>'
        f'\n          <div class="map-box">'
        f'\n            <svg class="ca-map" viewBox="0 0 {W} {H}" role="group" aria-label="{t["map"]}">'
        f'\n              <g class="ctys">' + "".join(paths) + '</g>'
        f'\n              <path class="hl hl-hover" d=""/><path class="hl hl-sel" d=""/>'
        f'\n            </svg>'
        f'\n            <div class="map-tip" aria-hidden="true" hidden></div>'
        f'\n          </div>'
        f'\n          <details class="county-list">'
        f'\n            <summary>{t["list"]}</summary>'
        f'\n            <div class="county-opts">' + "".join(opts) + '</div>'
        f'\n          </details>'
        f'\n        </div>\n        '
    )


for lang, path in (("en", ROOT / "index.html"), ("es", ROOT / "es" / "index.html")):
    html = path.read_text()
    html, n = re.subn(r"<!--MAP-->.*?<!--/MAP-->", lambda m: f"<!--MAP-->{block(lang)}<!--/MAP-->", html, flags=re.S)
    assert n == 1, f"MAP marker not found once in {path} ({n})"
    path.write_text(html)
    print("wrote map into", path.relative_to(ROOT), f"(viewBox {W}x{H})")
