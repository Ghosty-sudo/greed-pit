#!/usr/bin/env python3
"""Static release-hardening checks for the GREED PIT itch/browser package."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "greed-pit-0.20.13.html"
OUT = ROOT / "dist" / "itch"
HTML = OUT / "index.html"
REPORT = ROOT / "dist" / "GREED_PIT_RELEASE_QA.json"


def check(name: str, condition: bool, details: str = "") -> dict:
    if not condition:
        raise SystemExit(f"QA FAIL — {name}: {details}")
    return {"name": name, "status": "pass", "details": details}


def main() -> None:
    src = SOURCE.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    results: list[dict] = []

    def ok(name: str, condition: bool, details: str = "") -> None:
        results.append(check(name, condition, details))

    # Package / platform integrity.
    ok("itch index exists", HTML.is_file())
    ok("build metadata exists", (OUT / "build.json").is_file())
    ok("no service worker in itch package", "navigator.serviceWorker.register" not in html)
    ok("desktop controls disclosed", "PC: WASD / arrow keys to move" in html and "ESC to pause" in html)
    ok("desktop landscape allowed", "matchMedia('(pointer: coarse)').matches" in html)
    ok("window blur pauses play", "window.addEventListener('blur'" in html and "pauseGame()" in html)
    ok("visibility loss pauses play", "visibilitychange" in html and "document.hidden&&state==='playing'" in html)

    # Player path / QoL surfaces expected for this class.
    required_player_path = {
        "opening CTA": 'id="play"',
        "tutorial": 'id="tutorial"',
        "pause": 'id="pauseBtn"',
        "resume": 'id="resume"',
        "manual end run": 'id="quitRun"',
        "death/results": 'id="death"',
        "retry": 'id="again"',
        "cycle cash out": 'id="cashOut"',
        "go deeper": 'id="goDeeper"',
        "audio control": 'id="audioToggle"',
        "run recovery": 'id="continueRun"',
        "upgrade choices": 'id="cards"',
        "meta progression": 'id="badIdeasOpen"',
        "skins": 'id="skinsOpen"',
        "feedback": 'id="feedbackOpen"',
    }
    for label, marker in required_player_path.items():
        ok(f"player path: {label}", marker in html)

    # Persistence / interruption resilience.
    ok("active run checkpoint exists", "greedPitActiveRun0212" in html and "saveRunSnapshot" in html)
    ok("checkpoint write is guarded", "try{localStorage.setItem(RUN_SAVE_KEY" in html)
    ok("meta save is guarded", "try{localStorage.setItem('greedPitMeta'" in html)
    ok("checkpoint cadence is bounded", "g.t-lastRunSnapshot<5" in html)

    # Long-session performance protections that specifically address prior lag risk.
    ok("frame delta clamp exists", "Math.min(.033,(now-last)/1000" in html)
    ok("mobile DPR cap exists", "MOBILE_DPR_CAP=1.5" in html)
    ok("HUD update throttle exists", "now-hudLastMs<100" in html)
    ok("spatial broad phase exists", "buildSpatialGrid" in html and "visitSpatial" in html)
    ok("viewport culling exists", "function inView" in html)
    ok("XP orb cap exists", "g.orbs.length<300" in html)
    ok("particle cap exists", "g.particles.length<600" in html)
    ok("attack-rate cap exists", "Math.min(12" in html and "effectiveFireRate" in html)
    ok("late-session enemy cap exists", "return 180" in html and "function enemyCap()" in html)

    # Audio lifecycle / lag containment.
    ok("audio gesture priming exists", "function audioGesture()" in html and "pointerdown',audioGesture" in html)
    ok("music autoplay rejection retry exists", "audioMusicRetry" in html)
    ok("SFX pools bounded to two voices", "SFX_POOL_SIZE=2" in html)
    ok("SFX duplicate throttling retained", "audioLast" in html and "minGap" in html)
    ok("music pauses with game", "function pauseGame()" in html and "pauseMusic()" in html)
    ok("music stops on run exit/death", "stopMusic()" in html)
    ok("audio toggle persists", "meta.audio" in html and "setAudio" in html)

    # Audio asset integrity and budget.
    audio_refs = sorted(set(re.findall(r"\./assets/audio/[^'\"\s)]+\.mp3", html)))
    ok("all expected audio references discovered", len(audio_refs) == 10, f"count={len(audio_refs)} refs={audio_refs}")
    total_audio = 0
    for ref in audio_refs:
        path = OUT / ref.removeprefix("./")
        ok(f"audio asset present: {path.name}", path.is_file() and path.stat().st_size > 0)
        total_audio += path.stat().st_size
    ok("audio payload remains lightweight", total_audio < 1_500_000, f"bytes={total_audio}")
    ok("unused connection test not shipped", not (OUT / "assets/audio/sfx/connection_test.mp3").exists())

    # Basic attack surface / package hygiene.
    ok("no remote script dependencies", not re.search(r"<script[^>]+src=['\"]https?://", html, flags=re.I))
    ok("no iframe dependency", "<iframe" not in html.lower())
    ok("HTML package remains compact", HTML.stat().st_size < 200_000, f"bytes={HTML.stat().st_size}")
    ok("QA hooks present", all(x in html for x in ("function audioQa()", "function perfQa()", "ALL TESTS PASSED")))

    # Verify source still contains the known 0.20.13 performance work rather than silently drifting.
    ok("source labels performance candidate", "0.20.13 PERFORMANCE CANDIDATE" in src)
    ok("source broad phase preserved", "buildSpatialGrid" in src and "visitSpatial" in src)
    ok("source viewport culling preserved", "function inView" in src)
    ok("source HUD throttle preserved", "now-hudLastMs<100" in src)

    report = {
        "game": "GREED PIT",
        "source_version": "0.20.13",
        "distribution_build": "0.20.13-itch-pc2",
        "gate": "MACHINE-VALID-PENDING-BROWSER-DYNAMIC-QA",
        "checks_passed": len(results),
        "audio_payload_bytes": total_audio,
        "results": results,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"GREED PIT static release QA passed: {len(results)} checks")
    print(f"Audio payload: {total_audio} bytes")
    print(f"Report: {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
