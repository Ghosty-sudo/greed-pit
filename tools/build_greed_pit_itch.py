#!/usr/bin/env python3
"""Build a PC-friendly itch.io HTML5 package from verified GREED PIT 0.20.13."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/greed-pit-0.20.13.html"
OUT = ROOT / "dist" / "itch"
EXPECTED_SHA = "652b45741d3329191e4fc02cca156615ead4343ad615d1dfe36215b67c644aba"
BUILD_ID = "0.20.13-itch-pc1"


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
        raise SystemExit(f"Refusing itch build: canonical 0.20.13 SHA changed: {actual}")

    html = SOURCE.read_text(encoding="utf-8")

    # itch.io hosts the HTML5 package itself; the PWA manifest/service worker are unnecessary
    # and can create stale-cache behavior inside an embedded game frame.
    html, manifest_count = re.subn(r'\n?<link rel="manifest" href="\./manifest\.webmanifest">', "", html, count=1)
    if manifest_count != 1:
        raise SystemExit(f"Expected one web-manifest link, found {manifest_count}")

    sw = "if('serviceWorker' in navigator)navigator.serviceWorker.register('./sw.js').catch(e=>console.warn('GREED PIT service worker registration failed',e));"
    if html.count(sw) != 1:
        raise SystemExit(f"Expected one service-worker registration, found {html.count(sw)}")
    html = html.replace(sw, "// itch.io build intentionally omits PWA service-worker registration.", 1)

    html = replace_once(
        html,
        '<meta name="theme-color" content="#09090d">',
        '<meta name="theme-color" content="#09090d">\n<meta name="greed-pit-build" content="0.20.13-itch-pc1">',
        "itch build marker",
    )

    html = replace_once(
        html,
        '<title>GREED PIT 0.20.13 PERFORMANCE CANDIDATE</title>',
        '<title>GREED PIT — PC / Browser</title>',
        "page title",
    )

    html = replace_once(
        html,
        '<p class="sub">Fight through 5-minute Cycles. Take upgrades, make GREED contracts, then CASH OUT your haul—or GO DEEPER and risk it for a bigger multiplier.</p>',
        '<p class="sub">Fight through 5-minute Cycles. Take upgrades, make GREED contracts, then CASH OUT your haul—or GO DEEPER and risk it for a bigger multiplier.<br><br><b style="color:#f7f2df">PC: WASD / arrow keys to move · ESC to pause · mouse for menus. Touch: drag to move.</b></p>',
        "desktop control hint",
    )

    html = replace_once(
        html,
        "DRAG anywhere to move. Your idiot attacks automatically. Kill enemies, grab XP, level up, and survive as long as possible.",
        "WASD / ARROW KEYS or DRAG anywhere to move. Your idiot attacks automatically. Kill enemies, grab XP, level up, and survive as long as possible.",
        "tutorial control copy",
    )

    pointer_block = """let pointer={down:false,id:null,x:0,y:0,ox:0,oy:0};
canvas.addEventListener('pointerdown',e=>{
 if(pointer.down)return;
 pointer.down=true;pointer.id=e.pointerId;pointer.ox=pointer.x=e.clientX;pointer.oy=pointer.y=e.clientY;
 canvas.setPointerCapture?.(e.pointerId)
});
canvas.addEventListener('pointermove',e=>{if(pointer.down&&e.pointerId===pointer.id){pointer.x=e.clientX;pointer.y=e.clientY}});
function releasePointer(e){if(e.pointerId===pointer.id){pointer.down=false;pointer.id=null}}
canvas.addEventListener('pointerup',releasePointer);canvas.addEventListener('pointercancel',releasePointer);"""

    keyboard_block = pointer_block + """
const keys={up:false,down:false,left:false,right:false};
function clearMoveKeys(){keys.up=keys.down=keys.left=keys.right=false}
function moveKeyFor(code){return({KeyW:'up',ArrowUp:'up',KeyS:'down',ArrowDown:'down',KeyA:'left',ArrowLeft:'left',KeyD:'right',ArrowRight:'right'})[code]||null}
function typingTarget(target){return !!(target&&(target.isContentEditable||['INPUT','TEXTAREA','SELECT'].includes(target.tagName)))}
document.addEventListener('keydown',e=>{
 if(typingTarget(e.target))return;
 const key=moveKeyFor(e.code);
 if(key){keys[key]=true;if(state==='playing')e.preventDefault();return}
 if(e.code==='Escape'){
   clearMoveKeys();
   if(state==='playing')pauseGame();else if(state==='paused')resumeGame();
   e.preventDefault()
 }
});
document.addEventListener('keyup',e=>{const key=moveKeyFor(e.code);if(key){keys[key]=false;if(state==='playing')e.preventDefault()}});
window.addEventListener('blur',()=>{clearMoveKeys();if(state==='playing')pauseGame()});"""
    html = replace_once(html, pointer_block, keyboard_block, "desktop keyboard controls")

    old_move = "g.player.moving=false;if(pointer.down){let dx=pointer.x-pointer.ox,dy=pointer.y-pointer.oy,l=Math.hypot(dx,dy);if(l>8){dx/=l;dy/=l;let raw=g.player.speed*(g.hypeTime?1.24:1),sp=Math.min(700,raw);g.player.x+=dx*sp*dt;g.player.y+=dy*sp*dt;g.player.lastDirX=dx;g.player.lastDirY=dy;g.player.moving=true;updateFacing(g.player,dx,dy,dt)}}g.player.faceBlend"
    new_move = "g.player.moving=false;let mdx=(keys.right?1:0)-(keys.left?1:0),mdy=(keys.down?1:0)-(keys.up?1:0);if(!mdx&&!mdy&&pointer.down){mdx=pointer.x-pointer.ox;mdy=pointer.y-pointer.oy;if(Math.hypot(mdx,mdy)<=8){mdx=0;mdy=0}}if(mdx||mdy){let ml=Math.hypot(mdx,mdy)||1;mdx/=ml;mdy/=ml;let raw=g.player.speed*(g.hypeTime?1.24:1),sp=Math.min(700,raw);g.player.x+=mdx*sp*dt;g.player.y+=mdy*sp*dt;g.player.lastDirX=mdx;g.player.lastDirY=mdy;g.player.moving=true;updateFacing(g.player,mdx,mdy,dt)}g.player.faceBlend"
    html = replace_once(html, old_move, new_move, "keyboard movement integration")

    html = replace_once(
        html,
        "const landscape=innerWidth>innerHeight;",
        "const landscape=innerWidth>innerHeight&&matchMedia('(pointer: coarse)').matches;",
        "desktop landscape behavior",
    )

    html = replace_once(
        html,
        "function pauseGame(){if(state!=='playing')return;saveRunSnapshot(true);pauseMusic();state='paused';g.paused=true;cancelAnimationFrame(raf);pointer.down=false;renderBuilds();",
        "function pauseGame(){if(state!=='playing')return;saveRunSnapshot(true);pauseMusic();state='paused';g.paused=true;cancelAnimationFrame(raf);pointer.down=false;clearMoveKeys();renderBuilds();",
        "clear keyboard state on pause",
    )

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copytree(ROOT / "assets" / "audio", OUT / "assets" / "audio")
    (OUT / "index.html").write_text(html, encoding="utf-8")
    (OUT / "build.json").write_text(
        json.dumps(
            {
                "game_version": "0.20.13",
                "distribution_build": BUILD_ID,
                "source_sha256": EXPECTED_SHA,
                "platform": "itch.io HTML5 / desktop browser + touch",
                "pc_controls": ["WASD", "arrow keys", "Escape pause", "mouse menus", "mouse drag movement"],
                "touch_controls": ["drag movement", "touch menus"],
                "desktop_landscape": True,
                "service_worker": False,
                "audio": True,
                "active_run_recovery": True,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    required = [
        'greed-pit-build" content="0.20.13-itch-pc1',
        "WASD / arrow keys",
        "KeyW:'up'",
        "ArrowUp:'up'",
        "e.code==='Escape'",
        "matchMedia('(pointer: coarse)').matches",
        "CONTINUE SAVED RUN",
        "AUDIO: ON",
    ]
    missing = [marker for marker in required if marker not in html]
    if missing:
        raise SystemExit(f"itch package lost required PC/browser markers: {missing}")
    if "navigator.serviceWorker.register" in html:
        raise SystemExit("itch package still registers a service worker")

    print(f"Prepared {OUT.relative_to(ROOT)}/ from verified source {EXPECTED_SHA}")
    print(f"itch HTML SHA-256: {digest(OUT / 'index.html')}")


if __name__ == "__main__":
    main()
