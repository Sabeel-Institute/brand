#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["cairosvg", "pillow", "numpy"]
# ///
"""
Build a Sabeel app's icons, and write them into that app's repository.

    uv run make-app-icons.py lms         --repo ../../../lms
    uv run make-app-icons.py kanban      --repo ../../../sabeel-institute-kanban
    uv run make-app-icons.py timetracker --repo ../../../sabeel-institute-time-tracker
    uv run make-app-icons.py lms --repo <path> --check   # write nothing; compare

Every Sabeel app's icon comes from here, beside the logo it is drawn from.

THE ICONS
---------
* The LMS, the app the public installs from the stores, carries the brand's
  own icon: the logo's raspberry calligraphy alone, centred on Warm Ivory, no
  badge. The calligraphy is cut from `logo/sabeel-logo.png` above its
  wordmark each run, so no second copy of it exists.
* The staff apps carry the earlier black mark (`logo/sabeel-mark-earlier.png`,
  the lockup before 2026-09-28 with its text removed) and a Dark Raspberry
  badge saying which app: a board (Kanban), a stopwatch (the Time Tracker).

WHAT IT WRITES
--------------
`app/assets/icon.png`, `adaptive-icon.png` and `favicon.png`, and, where the
app commits its `android/` directory (all of them do), the Android resources
Gradle compiles: Expo regenerates those only during `prebuild`, and prebuild
also rewrites `build.gradle` from its template, which would drop each app's
release signing and Sentry setup. So this writes exactly what prebuild would
(`@expo/prebuild-config`, withAndroidIcons.js): a foreground at 108dp per
density, legacy square and round icons at 48dp, the two `mipmap-anydpi-v26`
XMLs and an `iconBackground` colour. A later prebuild is then a no-op on icons.
iOS takes `icon.png` through `app.json` when `ios/` is generated.

THE GEOMETRY IS MEASURED, NOT CHOSEN
------------------------------------
An adaptive icon's foreground fills the whole 108dp layer, of which only the
central 72dp is guaranteed to survive the launcher's mask: 66.67%, so on this
1024 canvas the safe radius is 341. `--check` re-proves on every run that no
ink leaves that circle and that no badge hides any calligraphy.

* The LMS: the square icon has the calligraphy across 76% of the tile, as the
  brand's `logo/sabeel-icon.png` does; the adaptive foreground has it across
  76% of the 72dp a launcher shows, so the two read alike.
* The badged icons: each bound was found by rendering candidates and counting
  pixels. A 410px badge hides no calligraphy (418 starts cutting the sweep);
  the mark sits low (at cy=643 its descender leaves the circle) to free the
  upper arc; the badge's bearing is 38 degrees (36 already hides 12px). Mark
  and badge both end up 338 from centre. The badge lands where the wordmark
  was: the lockup's text is illegible at launcher sizes, and that hole is the
  one place a badge costs the calligraphy nothing.
"""

from __future__ import annotations

import argparse
import base64
import math
import re
import sys
from io import BytesIO
from pathlib import Path

import cairosvg
import numpy as np
from PIL import Image, ImageDraw

# --- brand (the sabeel-brand skill, Option 1 palette) ------------------------
IVORY = "#F6EBDD"  # Warm Ivory: the canvas, and the only background
PLUM = "#83114F"  # Dark Raspberry: the badge
ON_PLUM = "#F9F2E9"  # ivory on plum is 8.8:1

# --- geometry (see the module docstring) --------------------------------------
CANVAS = 1024
SAFE_R = 341  # 72dp of the 108dp adaptive layer
# Badged icons
BADGE_R = 205
MARK_W = 507
MARK_CY = 637
BEARING = 38  # degrees above horizontal, from centre
RING = 14  # ivory separation between badge and mark
# The LMS
ICON_SHARE = 0.76  # the brand icon's: calligraphy width over what is seen

LOGO_DIR = Path(__file__).resolve().parent.parent / "logo"
EARLIER_MARK = LOGO_DIR / "sabeel-mark-earlier.png"
LOGO = LOGO_DIR / "sabeel-logo.png"

# Each app's badge glyph; None is the brand's own icon, with no badge.
APPS = {"lms": None, "kanban": "board", "timetracker": "stopwatch"}

# Density buckets, and the baseline sizes @expo/prebuild-config uses.
DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
LEGACY_BASE = 48
ADAPTIVE_BASE = 108

ADAPTIVE_XML = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/iconBackground"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
"""


def calligraphy() -> Image.Image:
    """The logo's calligraphy: everything above the first clear band of rows, cropped to its ink."""
    logo = Image.open(LOGO).convert("RGBA")
    rows = (np.array(logo.getchannel("A")) > 16).any(axis=1)
    inked = np.flatnonzero(rows)
    gaps = np.flatnonzero(np.diff(inked) > 20)
    if not len(gaps):
        sys.exit(f"{LOGO}: no clear band between the calligraphy and the wordmark")
    top = logo.crop((0, 0, logo.width, int(inked[gaps[0]]) + 1))
    return top.crop(top.getchannel("A").getbbox())


def data_uri(img: Image.Image) -> str:
    buf = BytesIO()
    img.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def badge_glyph(kind: str, cx: float, cy: float, r: float) -> str:
    """The per-app glyph, drawn in a -100..100 space then placed on the badge."""
    g = (
        f'<g transform="translate({cx},{cy}) scale({r / 100.0})" fill="none" '
        f'stroke="{ON_PLUM}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round">'
    )
    if kind == "stopwatch":
        g += (
            '<circle cx="0" cy="8" r="46"/>'
            '<path d="M-16 -46 h32"/>'  # crown bar
            '<path d="M0 -46 v10"/>'  # stem
            '<path d="M0 8 v-24 M0 8 h20"/>'  # hands
        )
    elif kind == "board":
        # Three columns at different fills: a board, still legible as bars at 48dp.
        g += (
            f'<g fill="{ON_PLUM}" stroke="none">'
            '<rect x="-54" y="-42" width="30" height="84" rx="9"/>'
            '<rect x="-15" y="-42" width="30" height="58" rx="9"/>'
            '<rect x="24" y="-42" width="30" height="36" rx="9"/>'
            "</g>"
        )
    else:
        raise ValueError(f"unknown glyph {kind!r}")
    return g + "</g>"


def icon_svg(mark: Image.Image, kind: str | None, *, background: bool = True, badge: bool = True) -> str:
    """background=False yields the adaptive foreground layer (transparent)."""
    if kind is None:
        w = ICON_SHARE * (CANVAS if background else 2 * SAFE_R)
        cy = CANVAS / 2
    else:
        w, cy = MARK_W, MARK_CY
    h = w * mark.height / mark.width
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{CANVAS}" height="{CANVAS}" viewBox="0 0 {CANVAS} {CANVAS}">'
    ]
    if background:
        parts.append(f'<rect width="{CANVAS}" height="{CANVAS}" fill="{IVORY}"/>')
    parts.append(
        f'<image x="{(CANVAS - w) / 2}" y="{cy - h / 2}" '
        f'width="{w}" height="{h}" xlink:href="{data_uri(mark)}"/>'
    )
    if kind is not None and badge:
        # Tangent to the safe circle: a bigger badge walks inward along the same
        # bearing, which is the only direction with room.
        t = math.radians(BEARING)
        d = SAFE_R - BADGE_R - 4
        bx, by = CANVAS / 2 + d * math.cos(t), CANVAS / 2 - d * math.sin(t)
        # The ring keeps the badge legible where it passes near a stroke; it is
        # drawn even on the transparent layer, so the mark never touches it.
        parts.append(f'<circle cx="{bx}" cy="{by}" r="{BADGE_R + RING}" fill="{IVORY}"/>')
        parts.append(f'<circle cx="{bx}" cy="{by}" r="{BADGE_R}" fill="{PLUM}"/>')
        parts.append(badge_glyph(kind, bx, by, BADGE_R))
    parts.append("</svg>")
    return "".join(parts)


def render(svg: str, size: int = CANVAS) -> Image.Image:
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(BytesIO(png)).convert("RGBA")


def on_ivory(img: Image.Image) -> np.ndarray:
    return np.array(Image.alpha_composite(Image.new("RGBA", img.size, IVORY), img).convert("RGB")).astype(int)


def geometry(mark: Image.Image, kind: str | None) -> tuple[float, int]:
    """(farthest ink from centre on the adaptive foreground, calligraphy pixels a badge hides)."""
    ivory = np.array([246, 235, 221])
    yy, xx = np.mgrid[0:CANVAS, 0:CANVAS]
    radius = np.sqrt((xx - CANVAS / 2) ** 2 + (yy - CANVAS / 2) ** 2)
    full = on_ivory(render(icon_svg(mark, kind, background=False)))
    ink = np.abs(full - ivory).sum(axis=2) > 40
    if kind is None:
        return float(radius[ink].max()), 0
    bare = on_ivory(render(icon_svg(mark, kind, background=False, badge=False)))
    dark = (np.abs(bare - ivory).sum(axis=2) > 40) & (bare.sum(axis=2) < 300)
    still = ink & (full.sum(axis=2) < 300)
    return float(radius[ink].max()), int((dark & ~still).sum())


def circle_crop(img: Image.Image) -> Image.Image:
    out = img.copy()
    mask = Image.new("L", out.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, out.size[0] - 1, out.size[1] - 1), fill=255)
    out.putalpha(mask)
    return out


def outputs(master: Image.Image, foreground: Image.Image, res: Path | None) -> dict[str, Image.Image]:
    """Every file this writes, by path relative to the app's root."""
    out = {
        "app/assets/icon.png": master.convert("RGB"),
        "app/assets/adaptive-icon.png": foreground,
        "app/assets/favicon.png": master.convert("RGB").resize((196, 196), Image.LANCZOS),
    }
    if res is None:
        return out
    for folder, scale in DENSITIES.items():
        d = f"app/android/app/src/main/res/mipmap-{folder}"
        legacy, adaptive = round(LEGACY_BASE * scale), round(ADAPTIVE_BASE * scale)
        out[f"{d}/ic_launcher.webp"] = master.convert("RGB").resize((legacy, legacy), Image.LANCZOS)
        out[f"{d}/ic_launcher_round.webp"] = circle_crop(master.resize((legacy, legacy), Image.LANCZOS))
        out[f"{d}/ic_launcher_foreground.webp"] = foreground.resize((adaptive, adaptive), Image.LANCZOS)
    return out


def differs(a: Image.Image, b: Image.Image) -> bool:
    """
    More than rounding between two renders of the same icon: colour weighed by
    its alpha (a transparent pixel's colour is not stored the same way by every
    encoder), and a pixel counted as changed past 8 levels, as resampling the
    same artwork never reaches on more than a stray pixel or two.
    """
    if a.size != b.size:
        return True

    def weighed(img: Image.Image) -> np.ndarray:
        px = np.array(img.convert("RGBA")).astype(int)
        return np.dstack([px[..., :3] * px[..., 3:] // 255, px[..., 3]])

    changed = (np.abs(weighed(a) - weighed(b)).max(axis=2) > 8).sum()
    return bool(changed > a.size[0] * a.size[1] // 10000)


def ensure_icon_background(colors_xml: Path) -> None:
    """Add the adaptive background colour without reformatting the file."""
    text = colors_xml.read_text() if colors_xml.exists() else "<resources>\n</resources>\n"
    if 'name="iconBackground"' in text:
        text = re.sub(r'(<color name="iconBackground">)[^<]*(</color>)', rf"\g<1>{IVORY}\g<2>", text)
    else:
        text = text.replace("</resources>", f'  <color name="iconBackground">{IVORY}</color>\n</resources>')
    colors_xml.parent.mkdir(parents=True, exist_ok=True)
    colors_xml.write_text(text)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("app", choices=sorted(APPS), help="which app's icon to build")
    ap.add_argument("--repo", required=True, help="the app repository's root")
    ap.add_argument("--check", action="store_true",
                    help="prove the geometry and compare the app's committed icons; write nothing")
    args = ap.parse_args()

    kind = APPS[args.app]
    repo = Path(args.repo).resolve()
    if not (repo / "app" / "app.json").is_file():
        ap.error(f"{repo} is not a Sabeel app repository (no app/app.json)")
    mark = calligraphy() if kind is None else Image.open(EARLIER_MARK).convert("RGBA")

    max_r, hidden = geometry(mark, kind)
    print(f"{args.app}: " + ("calligraphy alone" if kind is None else f"{kind} badge, {2 * BADGE_R}px"))
    print(f"  farthest ink   {max_r:6.1f} of {SAFE_R} safe")
    print(f"  calligraphy hidden {hidden:>4} px")
    if max_r > SAFE_R:
        print(f"FAIL: ink reaches {max_r:.1f}, outside the {SAFE_R}px safe circle", file=sys.stderr)
        return 1
    if hidden:
        print(f"FAIL: the badge hides {hidden}px of calligraphy", file=sys.stderr)
        return 1

    res = repo / "app" / "android" / "app" / "src" / "main" / "res"
    files = outputs(render(icon_svg(mark, kind)), render(icon_svg(mark, kind, background=False)),
                    res if res.is_dir() else None)

    if args.check:
        stale = [p for p, img in files.items() if not (repo / p).is_file() or differs(Image.open(repo / p), img)]
        for p in stale:
            print(f"  differs: {p}", file=sys.stderr)
        if stale:
            print(f"FAIL: {len(stale)} of {len(files)} icon files are not what this makes", file=sys.stderr)
            return 1
        print(f"  all {len(files)} icon files match")
        return 0

    for p, img in files.items():
        (repo / p).parent.mkdir(parents=True, exist_ok=True)
        img.save(repo / p, lossless=True) if p.endswith(".webp") else img.save(repo / p)
    if res.is_dir():
        anydpi = res / "mipmap-anydpi-v26"
        anydpi.mkdir(parents=True, exist_ok=True)
        (anydpi / "ic_launcher.xml").write_text(ADAPTIVE_XML)
        (anydpi / "ic_launcher_round.xml").write_text(ADAPTIVE_XML)
        ensure_icon_background(res / "values" / "colors.xml")
    print(f"  wrote {len(files)} files under {repo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
