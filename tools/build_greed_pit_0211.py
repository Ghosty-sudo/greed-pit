#!/usr/bin/env python3
"""Build GREED PIT 0.20.11 from the hash-verified 0.20.9 canonical source.

This script intentionally does not touch the public index/service-worker/manifest.
It produces a staged candidate that can be validated before promotion.
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/greed-pit-0.20.9.html"
OUTPUT = ROOT / "src/greed-pit-0.20.11.html"
SHA_FILE = ROOT / "src/greed-pit-0.20.11.sha256"
EXPECTED_0209 = "ed73fd1a4e4e8cf0c442d6c89ed0864a0d38aec9bb99bf91c41c30679a60302d"
CHUNK_SIZE = 8000

AUDIO_FILES = [
    "assets/audio/music/music_run_preview.mp3",
    "assets/audio/sfx/xp_pickup.mp3",
    "assets/audio/sfx/upgrade_select.mp3",
    "assets/audio/sfx/greed_contract.mp3",
    "assets/audio/sfx/enemy_death.mp3",
    "assets/audio/sfx/player_hit.mp3",
    "assets/audio/sfx/circle_crash_explosion.mp3",
    "assets/audio/sfx/boss_arrival.mp3",
    "assets/audio/sfx/cycle_checkpoint.mp3",
    "assets/audio/sfx/player_death.mp3",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one source match, found {count}")
    return text.replace(old, new, 1)


def verify_inputs() -> bytes:
    source_bytes = SOURCE.read_bytes()
    actual = sha256(source_bytes)
    if actual != EXPECTED_0209:
        raise RuntimeError(f"0.20.9 source hash changed: {actual}")
    for rel in AUDIO_FILES:
        path = ROOT / rel
        if not path.is_file() or path.stat().st_size <= 0:
            raise RuntimeError(f"Missing/empty audio input: {rel}")
    return source_bytes


def patch_source(source_bytes: bytes) -> str:
    src = source_bytes.decode("utf-8")
    src = replace_once(
        src,
        "<title>GREED PIT 0.20.9 RELEASE CANDIDATE</title>",
        "<title>GREED PIT 0.20.11 AUDIO CANDIDATE</title>",
        "document title",
    )
    src = replace_once(
        src,
        "Prototype 0.20.6 — Bad Ideas catalog, tappable build details, visible stack caps, and maxed upgrades leave the roll pool.",
        "Candidate 0.20.11 — verified 0.20.9 gameplay baseline plus integrated music/SFX and persistent audio controls.",
        "visible build label",
    )
    src = replace_once(
        src,
        '<button class="secondary" id="feedbackOpen">FEEDBACK / BUG REPORT</button>',
        '<button class="secondary" id="audioToggle">AUDIO: ON</button><button class="secondary" id="feedbackOpen">FEEDBACK / BUG REPORT</button>',
        "audio toggle button",
    )
    src = replace_once(
        src,
        "meta={scrap:meta.scrap||0,unlocked:meta.unlocked||0,best:meta.best||0,totalKills:meta.totalKills||0,totalSeconds:meta.totalSeconds||0,maxGreed:meta.maxGreed||0,maxLevel:meta.maxLevel||1,skin:meta.skin||'pit',tutorialSeen:!!meta.tutorialSeen};",
        "meta={scrap:meta.scrap||0,unlocked:meta.unlocked||0,best:meta.best||0,totalKills:meta.totalKills||0,totalSeconds:meta.totalSeconds||0,maxGreed:meta.maxGreed||0,maxLevel:meta.maxLevel||1,skin:meta.skin||'pit',tutorialSeen:!!meta.tutorialSeen,audio:meta.audio!==false};",
        "audio persistence field",
    )

    audio_engine = r"""
const AUDIO={
 music:'./assets/audio/music/music_run_preview.mp3',
 xp:'./assets/audio/sfx/xp_pickup.mp3',upgrade:'./assets/audio/sfx/upgrade_select.mp3',greed:'./assets/audio/sfx/greed_contract.mp3',enemy:'./assets/audio/sfx/enemy_death.mp3',hit:'./assets/audio/sfx/player_hit.mp3',blast:'./assets/audio/sfx/circle_crash_explosion.mp3',boss:'./assets/audio/sfx/boss_arrival.mp3',cycle:'./assets/audio/sfx/cycle_checkpoint.mp3',death:'./assets/audio/sfx/player_death.mp3'
};
const runMusic=new Audio(AUDIO.music);runMusic.loop=true;runMusic.preload='auto';runMusic.volume=.22;
const audioLast={},sfxPools={},sfxCursor={};
for(const [key,url] of Object.entries(AUDIO)){if(key==='music')continue;sfxPools[key]=Array.from({length:3},()=>{const a=new Audio(url);a.preload='auto';return a});sfxCursor[key]=0}
function playSfx(key,volume=.45,minGap=0){if(!meta.audio||!sfxPools[key])return;const now=performance.now();if(now-(audioLast[key]??-1e9)<minGap)return;audioLast[key]=now;const pool=sfxPools[key],i=sfxCursor[key]%pool.length,a=pool[i];sfxCursor[key]=i+1;try{a.pause();a.currentTime=0}catch(e){}a.volume=clamp(volume,0,1);a.play().catch(()=>{})}
function resumeMusic(){if(!meta.audio)return;runMusic.volume=.22;runMusic.play().catch(()=>{})}
function pauseMusic(){runMusic.pause()}
function stopMusic(){runMusic.pause();try{runMusic.currentTime=0}catch(e){}}
function updateAudioButton(){const b=$('#audioToggle');if(b)b.textContent=meta.audio?'AUDIO: ON':'AUDIO: OFF'}
function setAudio(enabled){meta.audio=!!enabled;saveMeta();updateAudioButton();if(!meta.audio)stopMusic();else if(state==='playing'&&!g?.paused)resumeMusic()}
"""
    resize_old = "function resize(){DPR=Math.min(devicePixelRatio||1,2);W=innerWidth;H=innerHeight;canvas.width=W*DPR;canvas.height=H*DPR;ctx.setTransform(DPR,0,0,DPR,0,0)}addEventListener('resize',resize);resize();"
    resize_new = audio_engine + "\n" + resize_old + "updateAudioButton();"
    src = replace_once(src, resize_old, resize_new, "audio engine insertion")

    replacements = [
        ("toast(u.curse?'TERRIBLE CHOICE 👍':'UPGRADE ACQUIRED');finishLevelChoice()", "playSfx('upgrade',.52,80);toast(u.curse?'TERRIBLE CHOICE 👍':'UPGRADE ACQUIRED');finishLevelChoice()", "upgrade SFX"),
        ("g.greed++;g.rerolls++;c.apply(g.player,g.mods);g.contracts.push(c.name);", "g.greed++;g.rerolls++;c.apply(g.player,g.mods);g.contracts.push(c.name);playSfx('greed',.65,120);", "GREED SFX"),
        ("function killEnemy(e){g.kills++;", "function killEnemy(e){g.kills++;playSfx('enemy',e.boss?.72:e.elite?.46:.28,95);", "enemy-death SFX"),
        ("h.detonated=true;g.shake=Math.max(g.shake,10);", "h.detonated=true;g.shake=Math.max(g.shake,10);playSfx('blast',.58,180);", "hazard SFX"),
        ("if(hitPlayer){g.player.hp-=e.damage*dt*1.75;g.shake=Math.max(g.shake,3)}", "if(hitPlayer){g.player.hp-=e.damage*dt*1.75;g.shake=Math.max(g.shake,3);playSfx('hit',.34,420)}", "player-hit SFX"),
        ("if(d<g.player.r+o.r+5){o.dead=1;gainXp(o.xp)}", "if(d<g.player.r+o.r+5){o.dead=1;playSfx('xp',.20,70);gainXp(o.xp)}", "XP SFX"),
        ("if(g.t>=g.nextBossAt){g.bossSpawned++;if(g.enemies.length<enemyCap()+3)spawnEnemy(true);g.nextBossAt=g.t+bossEvery;toast('TAX COLLECTOR INBOUND')}", "if(g.t>=g.nextBossAt){g.bossSpawned++;if(g.enemies.length<enemyCap()+3)spawnEnemy(true);g.nextBossAt=g.t+bossEvery;playSfx('boss',.72,1200);toast('TAX COLLECTOR INBOUND')}", "boss SFX"),
        ("function completeCycle(){\n g.cyclePending=true;", "function completeCycle(){\n playSfx('cycle',.70,800);g.cyclePending=true;", "cycle SFX"),
        ("function die(){state='dead';", "function die(){playSfx('death',.78,800);stopMusic();state='dead';", "death SFX"),
        ("function cashOutRun(){\n const bank=haulValue();", "function cashOutRun(){\n stopMusic();const bank=haulValue();", "cash-out music stop"),
        ("function pauseGame(){if(state!=='playing')return;state='paused';", "function pauseGame(){if(state!=='playing')return;pauseMusic();state='paused';", "pause music"),
        ("function resumeGame(){if(state!=='paused')return;$('#pause').classList.add('hidden');g.paused=false;state='playing';", "function resumeGame(){if(state!=='paused')return;$('#pause').classList.add('hidden');g.paused=false;state='playing';resumeMusic();", "resume music"),
        ("state='playing';ui.title.classList.add('hidden');ui.death.classList.add('hidden');ui.level.classList.add('hidden');$('#abilityBox').classList.add('hidden');ui.hud.classList.remove('hidden');last=performance.now();cancelAnimationFrame(raf);raf=requestAnimationFrame(loop)}", "state='playing';ui.title.classList.add('hidden');ui.death.classList.add('hidden');ui.level.classList.add('hidden');$('#abilityBox').classList.add('hidden');ui.hud.classList.remove('hidden');resumeMusic();last=performance.now();cancelAnimationFrame(raf);raf=requestAnimationFrame(loop)}", "run-start music"),
        ("$('#feedbackOpen').onclick=showFeedback;", "$('#audioToggle').onclick=()=>setAudio(!meta.audio);$('#feedbackOpen').onclick=showFeedback;", "audio toggle handler"),
        ("state='title';cancelAnimationFrame(raf);\n $('#pause').classList.add('hidden');", "state='title';cancelAnimationFrame(raf);stopMusic();\n $('#pause').classList.add('hidden');", "quit-run music stop"),
        ("$('#home').onclick=()=>{state='title';", "$('#home').onclick=()=>{stopMusic();state='title';", "home music stop"),
        ("build:'0.20.9'", "build:'0.20.11'", "feedback build number"),
        ("ok('release sprite system exists',typeof makeSprite==='function'&&typeof updateFacing==='function'&&SPRITE_FRAMES===4)", "ok('release sprite system exists',typeof makeSprite==='function'&&typeof updateFacing==='function'&&SPRITE_FRAMES===4);ok('audio system exists',typeof playSfx==='function'&&typeof resumeMusic==='function'&&!!AUDIO.death)", "audio self-test"),
    ]
    for old, new, label in replacements:
        src = replace_once(src, old, new, label)

    required = [
        "GREED PIT 0.20.11 AUDIO CANDIDATE",
        "AUDIO: ON",
        "music_run_preview.mp3",
        "player_death.mp3",
        "build:'0.20.11'",
        "ok('audio system exists'",
    ]
    for marker in required:
        if marker not in src:
            raise RuntimeError(f"Missing integration marker after patch: {marker}")
    return src


def package_candidate(html: str) -> tuple[str, list[str]]:
    html_bytes = html.encode("utf-8")
    digest = sha256(html_bytes)
    OUTPUT.write_bytes(html_bytes)
    SHA_FILE.write_text(digest + "\n")

    for old in ROOT.glob("gp0211.*.b64"):
        old.unlink()

    compressed = gzip.compress(html_bytes, compresslevel=9, mtime=0)
    encoded = base64.b64encode(compressed).decode("ascii")
    chunk_names: list[str] = []
    for index, offset in enumerate(range(0, len(encoded), CHUNK_SIZE), start=1):
        name = f"gp0211.{index:02d}.b64"
        (ROOT / name).write_text(encoded[offset : offset + CHUNK_SIZE])
        chunk_names.append(name)

    names_js = json.dumps(chunk_names, separators=(",", ":"))
    loader = f"""(async()=>{{try{{if(typeof DecompressionStream!=='function')throw new Error('This browser needs gzip stream support.');const names={names_js},texts=await Promise.all(names.map(async n=>{{const r=await fetch('./'+n,{{cache:'no-store'}});if(!r.ok)throw new Error(n+' '+r.status);return(await r.text()).replace(/\\s+/g,'')}})),parts=texts.map(s=>{{const raw=atob(s),a=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)a[i]=raw.charCodeAt(i);return a}}),total=parts.reduce((n,a)=>n+a.length,0),z=new Uint8Array(total);let o=0;for(const a of parts){{z.set(a,o);o+=a.length}}const h=await new Response(new Blob([z]).stream().pipeThrough(new DecompressionStream('gzip'))).text();if(!h.includes('GREED PIT 0.20.11 AUDIO CANDIDATE'))throw new Error('Build marker verification failed.');if(globalThis.crypto?.subtle){{const d=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(h)),hex=[...new Uint8Array(d)].map(x=>x.toString(16).padStart(2,'0')).join('');if(hex!=='{digest}')throw new Error('Build hash verification failed.')}}document.open();document.write(h);document.close()}}catch(e){{document.body.innerHTML='<main style=\"font-family:system-ui;padding:24px;background:#09090d;color:#f7f2df;min-height:100vh\"><h1>THE PIT FAILED TO OPEN</h1><p>'+String(e.message||e)+'</p></main>';console.error(e)}}}})()\n"""
    (ROOT / "loader-0211.js").write_text(loader)

    manifest = {
        "name": "GREED PIT",
        "short_name": "GREED PIT",
        "start_url": "./",
        "display": "standalone",
        "background_color": "#09090d",
        "theme_color": "#09090d",
        "orientation": "portrait",
        "description": "GREED PIT 0.20.11 — verified release-candidate baseline with integrated music and sound effects.",
    }
    (ROOT / "manifest-0211.webmanifest").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    sw = """const CACHE='greed-pit-0.20.11';
const CORE=['./','./index.html','./loader-0211.js','./manifest.webmanifest'];
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).catch(()=>{}))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);if(u.origin!==location.origin)return;e.respondWith(fetch(e.request,{cache:'no-store'}).then(r=>{const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy)).catch(()=>{});return r}).catch(()=>caches.match(e.request).then(r=>r||caches.match('./index.html'))))});
"""
    (ROOT / "sw-0211.js").write_text(sw)

    reconstructed = gzip.decompress(base64.b64decode("".join((ROOT / n).read_text().strip() for n in chunk_names)))
    if reconstructed != html_bytes:
        raise RuntimeError("Packaged 0.20.11 candidate did not reconstruct byte-for-byte")
    if sha256(reconstructed) != digest:
        raise RuntimeError("Packaged 0.20.11 hash verification failed")

    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    if len(scripts) != 1:
        raise RuntimeError(f"Expected one inline game script, found {len(scripts)}")
    Path("/tmp/greed-pit-0211.js").write_text(scripts[0])
    return digest, chunk_names


def main() -> None:
    source_bytes = verify_inputs()
    candidate = patch_source(source_bytes)
    digest, chunks = package_candidate(candidate)
    print(f"Verified 0.20.9 source: {EXPECTED_0209}")
    print(f"Built 0.20.11 canonical source: {digest}")
    print(f"Packaged and byte-verified {len(chunks)} payload chunks: {', '.join(chunks)}")
    print("Wrote /tmp/greed-pit-0211.js for node --check")


if __name__ == "__main__":
    main()
