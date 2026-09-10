#!/usr/bin/env python3
"""Prepare the verified GREED PIT web build for Capacitor native packaging."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/greed-pit-0.20.11.html"
WWW = ROOT / "www"
EXPECTED_SHA = "3ba734c0fec2dfb24fd13ceecbc8b4333e40a2ee25fd19047f0b382e0618a5f3"
VERSION = "0.20.11"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    actual = digest(SOURCE)
    if actual != EXPECTED_SHA:
        raise SystemExit(f"Refusing native build: canonical 0.20.11 SHA changed: {actual}")

    html = SOURCE.read_text(encoding="utf-8")
    if "<head>" not in html or "</head>" not in html:
        raise SystemExit("Native web bundle requires a real <head> for Capacitor injection")

    # The native app does not use the browser/PWA service worker or web manifest.
    html, manifest_count = re.subn(r'\n?<link rel="manifest" href="\./manifest\.webmanifest">', "", html, count=1)
    if manifest_count != 1:
        raise SystemExit(f"Expected one web-manifest link, found {manifest_count}")

    sw = "if('serviceWorker' in navigator)navigator.serviceWorker.register('./sw.js').catch(e=>console.warn('GREED PIT service worker registration failed',e));"
    if html.count(sw) != 1:
        raise SystemExit(f"Expected one service-worker registration, found {html.count(sw)}")
    html = html.replace(sw, "// Native Capacitor build intentionally omits PWA service-worker registration.", 1)

    # Mark this as a packaged native candidate without changing gameplay semantics.
    html = html.replace(
        '<meta name="theme-color" content="#09090d">',
        '<meta name="theme-color" content="#09090d">\n<meta name="greed-pit-build" content="0.20.11-native-candidate">',
        1,
    )

    if WWW.exists():
        shutil.rmtree(WWW)
    (WWW / "assets").mkdir(parents=True)
    shutil.copytree(ROOT / "assets" / "audio", WWW / "assets" / "audio")
    (WWW / "index.html").write_text(html, encoding="utf-8")
    (WWW / "build.json").write_text(
        json.dumps(
            {
                "game_version": VERSION,
                "source_sha256": EXPECTED_SHA,
                "native_candidate": True,
                "service_worker": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    native_html = WWW / "index.html"
    if "AUDIO: ON" not in html or "GREED PIT 0.20.11 AUDIO CANDIDATE" not in html:
        raise SystemExit("Native bundle lost required 0.20.11 UI/build markers")
    if "navigator.serviceWorker.register" in html:
        raise SystemExit("Native bundle still registers a service worker")

    print(f"Prepared {native_html.relative_to(ROOT)} from verified source {EXPECTED_SHA}")
    print(f"Native HTML SHA-256: {digest(native_html)}")


if __name__ == "__main__":
    main()
