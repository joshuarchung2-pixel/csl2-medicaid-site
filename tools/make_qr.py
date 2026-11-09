"""Writes img/qr-en.svg and img/qr-es.svg locally (python qrcode, no online service)."""
import pathlib, qrcode, qrcode.image.svg
ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://joshuarchung2-pixel.github.io/csl2-medicaid-site/"
for lang, url in (("en", BASE), ("es", BASE + "es/")):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2,
                       image_factory=qrcode.image.svg.SvgPathImage)
    qr.add_data(url); qr.make(fit=True)
    img = qr.make_image()
    out = ROOT / "img" / f"qr-{lang}.svg"
    img.save(str(out))
    print(out, url)
