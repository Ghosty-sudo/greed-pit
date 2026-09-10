#!/usr/bin/env python3
"""Prepare the verified GREED PIT 0.20.13 web build for Capacitor native packaging."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/greed-pit-0.20.13.html"
WWW = ROOT / "www"
EXPECTED_SHA = "652b45741d3329191e4fc02cca156615ead4343ad615d1dfe36215b67c644aba"
VERSION = "0.20.13"
PRIVACY_URL = "https://ghosty-sudo.github.io/greed-pit/privacy.html"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    actual = digest(SOURCE)
    if actual != EXPECTED_SHA:
        raise SystemExit(f"Refusing native build: canonical 0.20.13 SHA changed: {actual}")

    html = SOURCE.read_text(encoding="utf-8")
    if "<head>" not in html or "</head>" not in html:
        raise SystemExit("Native web bundle requires a real <head> for Capacitor injection")

    # Native Capacitor packaging does not use the browser/PWA manifest or service worker.
    html, manifest_count = re.subn(r'\n?<link rel="manifest" href="\./manifest\.webmanifest">', "", html, count=1)
    if manifest_count != 1:
        raise SystemExit(f"Expected one web-manifest link, found {manifest_count}")

    sw = "if('serviceWorker' in navigator)navigator.serviceWorker.register('./sw.js').catch(e=>console.warn('GREED PIT service worker registration failed',e));"
    if html.count(sw) != 1:
        raise SystemExit(f"Expected one service-worker registration, found {html.count(sw)}")
    html = html.replace(sw, "// Native Capacitor build intentionally omits PWA service-worker registration.", 1)

    html = replace_once(
        html,
        '<meta name="theme-color" content="#09090d">',
        '<meta name="theme-color" content="#09090d">\n<meta name="greed-pit-build" content="0.20.13-native-candidate">',
        "native build marker",
    )

    # App Review expects the privacy policy to be easily accessible from inside the app.
    html = replace_once(
        html,
        '<button class="secondary" id="feedbackOpen">FEEDBACK / BUG REPORT</button>',
        '<button class="secondary" id="feedbackOpen">FEEDBACK / BUG REPORT</button><button class="secondary" id="privacyOpen">PRIVACY</button>',
        "privacy title button",
    )
    privacy_screen = f'''<section id="privacyBox" class="screen hidden"><div class="tag">PRIVACY</div><h1 style="font-size:38px">YOUR RUN.<br>YOUR DEVICE.</h1><div class="panel"><p class="sub" style="margin:0;color:#c8c4cf">GREED PIT currently uses no account, ads, analytics, location, contacts, camera, microphone, or cross-app tracking. Game progress, settings, run recovery, and saved feedback stay on this device unless you choose to copy or share them.</p><p style="margin:16px 0 0;font-size:12px"><a href="{PRIVACY_URL}" target="_blank" rel="noopener noreferrer" style="color:#70efae">FULL PRIVACY POLICY</a></p></div><button class="secondary" id="privacyClose">BACK</button></section>\n'''
    html = replace_once(
        html,
        '<section id="rotateNotice"',
        privacy_screen + '<section id="rotateNotice"',
        "privacy screen",
    )
    html = replace_once(
        html,
        "$('#continueRun').onclick=restoreRunSnapshot;$('#audioToggle').onclick=()=>setAudio(!meta.audio);",
        "$('#continueRun').onclick=restoreRunSnapshot;$('#privacyOpen').onclick=()=>{ui.title.classList.add('hidden');$('#privacyBox').classList.remove('hidden')};$('#privacyClose').onclick=()=>{$('#privacyBox').classList.add('hidden');ui.title.classList.remove('hidden')};$('#audioToggle').onclick=()=>setAudio(!meta.audio);",
        "privacy handlers",
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
                "performance_candidate": True,
                "active_run_recovery": True,
                "audio": True,
                "service_worker": False,
                "privacy_policy": PRIVACY_URL,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    native_html = WWW / "index.html"
    required = [
        "GREED PIT 0.20.13 PERFORMANCE CANDIDATE",
        "AUDIO: ON",
        "CONTINUE SAVED RUN",
        "greedPitActiveRun0212",
        'id="privacyOpen"',
        'id="privacyBox"',
        PRIVACY_URL,
    ]
    missing = [marker for marker in required if marker not in html]
    if missing:
        raise SystemExit(f"Native bundle lost required UI/build markers: {missing}")
    if "navigator.serviceWorker.register" in html:
        raise SystemExit("Native bundle still registers a service worker")

    print(f"Prepared {native_html.relative_to(ROOT)} from verified source {EXPECTED_SHA}")
    print(f"Native HTML SHA-256: {digest(native_html)}")


if __name__ == "__main__":
    main()
