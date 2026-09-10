#!/usr/bin/env python3
"""Build GREED PIT 0.20.12 from the validated 0.20.11 audio candidate.

0.20.12 adds recoverable active-run checkpoints for real mobile lifecycle safety.
Transient combat entities are intentionally rebuilt after recovery; progression,
health, timers, upgrades, GREED, haul, cycles, and difficulty modifiers persist.
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/greed-pit-0.20.11.html"
OUTPUT = ROOT / "src/greed-pit-0.20.12.html"
SHA_FILE = ROOT / "src/greed-pit-0.20.12.sha256"
EXPECTED_0211 = "3ba734c0fec2dfb24fd13ceecbc8b4333e40a2ee25fd19047f0b382e0618a5f3"
VERSION = "0.20.12"
CHUNK_SIZE = 8000


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def r(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def patch() -> str:
    raw = SOURCE.read_bytes()
    actual = sha(raw)
    if actual != EXPECTED_0211:
        raise RuntimeError(f"Refusing 0.20.12 build: 0.20.11 SHA changed: {actual}")
    text = raw.decode("utf-8")
    text = r(text, "<title>GREED PIT 0.20.11 AUDIO CANDIDATE</title>", "<title>GREED PIT 0.20.12 MOBILE RESUME CANDIDATE</title>", "title")
    text = r(text, '<button class="cta" id="play">DROP IN</button>', '<button class="cta" id="play">DROP IN</button><button class="secondary hidden" id="continueRun">CONTINUE SAVED RUN</button>', "continue button")
    text = r(text, "Candidate 0.20.11 — verified 0.20.9 gameplay baseline plus integrated music/SFX and persistent audio controls.", "Candidate 0.20.12 — browser-validated audio build plus recoverable mobile run checkpoints.", "visible version")
    text = r(text, "build:'0.20.11'", "build:'0.20.12'", "feedback version")

    anchor = "function badIdeaCost(level){return 20+(level-1)*15}function saveMeta(){try{localStorage.setItem('greedPitMeta',JSON.stringify(meta))}catch(e){console.warn('GREED PIT save failed',e)}renderMeta()} function renderMeta(){$('#scrap').textContent=meta.scrap;if(!$('#badIdeasBox').classList.contains('hidden'))renderBadIdeas()}renderMeta();"
    resume = r"""
const RUN_SAVE_KEY='greedPitActiveRun0212';let lastRunSnapshot=-999;
function readRunSnapshot(){try{const s=JSON.parse(localStorage.getItem(RUN_SAVE_KEY)||'null');if(!s||s.version!=='0.20.12'||!s.run?.player||!s.run?.mods||!Number.isFinite(s.run.t)||s.run.t<0)return null;return s}catch(e){return null}}
function updateContinueButton(){const b=$('#continueRun');if(!b)return;const s=readRunSnapshot();b.classList.toggle('hidden',!s);if(s)b.textContent=`CONTINUE · ${Math.floor(s.run.t/60)}:${Math.floor(s.run.t%60).toString().padStart(2,'0')} · LV ${s.run.level}`}
function clearRunSnapshot(){try{localStorage.removeItem(RUN_SAVE_KEY)}catch(e){}updateContinueButton()}
function saveRunSnapshot(force=false){if(!g||g.player?.hp<=0||(state!=='playing'&&state!=='paused'))return false;if(!force&&g.t-lastRunSnapshot<5)return false;lastRunSnapshot=g.t;const keep={worldW:g.worldW,worldH:g.worldH,t:g.t,kills:g.kills,level:g.level,xp:g.xp,nextXp:g.nextXp,hype:g.hype,hypeTime:g.hypeTime,spawnTimer:g.spawnTimer,bossSpawned:g.bossSpawned,nextBossAt:g.nextBossAt,greed:g.greed,rerolls:g.rerolls,hitNo:g.hitNo,upgradeHistory:g.upgradeHistory,cycle:g.cycle,nextCycle:g.nextCycle,runScrap:g.runScrap,multiplier:g.multiplier,contracts:g.contracts,hazardTimer:g.hazardTimer,player:g.player,mods:g.mods};try{localStorage.setItem(RUN_SAVE_KEY,JSON.stringify({version:'0.20.12',savedAt:Date.now(),run:keep}));updateContinueButton();return true}catch(e){console.warn('GREED PIT run checkpoint failed',e);return false}}
function restoreRunSnapshot(){const s=readRunSnapshot();if(!s){clearRunSnapshot();toast('NO SAVED RUN');return}const q=s.run;pointer.down=false;g={...q,worldW:Math.max(W*1.4,q.worldW||0),worldH:Math.max(H*1.4,q.worldH||0),camX:0,camY:0,spawnTimer:0,bulletTimer:0,paused:false,shake:0,pendingLevels:0,cyclePending:false,contractOffer:[],hazards:[],hazardTimer:Math.max(1,q.hazardTimer||8),enemies:[],bullets:[],orbs:[],healthDrops:[],particles:[],floating:[]};g.player={...q.player,x:clamp(q.player.x||W*.7,18,g.worldW-18),y:clamp(q.player.y||H*.7,18,g.worldH-18),moving:false};lastRunSnapshot=g.t;state='playing';ui.title.classList.add('hidden');ui.death.classList.add('hidden');ui.level.classList.add('hidden');$('#contractBox').classList.add('hidden');$('#cycleBox').classList.add('hidden');ui.hud.classList.remove('hidden');updateHud();draw();pauseGame();toast('RUN RECOVERED')}
"""
    text = r(text, anchor, anchor + resume + "\nupdateContinueButton();", "resume helpers")

    replacements = [
        ("function resetGame(){pointer.down=false;g={", "function resetGame(){clearRunSnapshot();lastRunSnapshot=0;pointer.down=false;g={", "new-run clears checkpoint"),
        ("function update(dt){\n g.t+=dt;", "function update(dt){\n g.t+=dt;saveRunSnapshot(false);", "periodic checkpoint"),
        ("function die(){playSfx('death',.78,800);stopMusic();state='dead';", "function die(){clearRunSnapshot();playSfx('death',.78,800);stopMusic();state='dead';", "death clears checkpoint"),
        ("function pauseGame(){if(state!=='playing')return;pauseMusic();state='paused';", "function pauseGame(){if(state!=='playing')return;saveRunSnapshot(true);pauseMusic();state='paused';", "pause checkpoint"),
        ("function cashOutRun(){\n stopMusic();const bank=haulValue();", "function cashOutRun(){\n clearRunSnapshot();stopMusic();const bank=haulValue();", "cashout clears checkpoint"),
        ("$('#cycleBox').classList.add('hidden');g.paused=false;state='playing';last=performance.now();toast(`CYCLE ${g.cycle}: ×${g.multiplier.toFixed(2)} HAUL`);raf=requestAnimationFrame(loop)", "$('#cycleBox').classList.add('hidden');g.paused=false;state='playing';saveRunSnapshot(true);last=performance.now();toast(`CYCLE ${g.cycle}: ×${g.multiplier.toFixed(2)} HAUL`);raf=requestAnimationFrame(loop)", "deep-cycle checkpoint"),
        ("g.paused=false;state='playing';last=performance.now();raf=requestAnimationFrame(loop)\n}", "g.paused=false;state='playing';saveRunSnapshot(true);last=performance.now();raf=requestAnimationFrame(loop)\n}", "level-choice checkpoint"),
        ("$('#audioToggle').onclick=()=>setAudio(!meta.audio);", "$('#continueRun').onclick=restoreRunSnapshot;$('#audioToggle').onclick=()=>setAudio(!meta.audio);", "continue handler"),
        ("const salvage=Math.floor(haulValue()*.20);meta.scrap+=salvage;recordRunMeta();state='title';", "const salvage=Math.floor(haulValue()*.20);clearRunSnapshot();meta.scrap+=salvage;recordRunMeta();state='title';", "manual end clears checkpoint"),
        ("ok('release sprite system exists',typeof makeSprite==='function'&&typeof updateFacing==='function'&&SPRITE_FRAMES===4);ok('audio system exists',typeof playSfx==='function'&&typeof resumeMusic==='function'&&!!AUDIO.death)", "ok('release sprite system exists',typeof makeSprite==='function'&&typeof updateFacing==='function'&&SPRITE_FRAMES===4);ok('audio system exists',typeof playSfx==='function'&&typeof resumeMusic==='function'&&!!AUDIO.death);ok('run checkpoint system exists',typeof saveRunSnapshot==='function'&&typeof restoreRunSnapshot==='function'&&!!$('#continueRun'))", "resume self-test"),
    ]
    for old, new, label in replacements:
        text = r(text, old, new, label)

    for marker in ["GREED PIT 0.20.12 MOBILE RESUME CANDIDATE", "CONTINUE SAVED RUN", "greedPitActiveRun0212", "run checkpoint system exists", "build:'0.20.12'"]:
        if marker not in text:
            raise RuntimeError(f"Missing 0.20.12 marker: {marker}")
    return text


def package(html: str) -> tuple[str, list[str]]:
    raw = html.encode("utf-8")
    digest = sha(raw)
    OUTPUT.write_bytes(raw)
    SHA_FILE.write_text(digest + "\n")
    for old in ROOT.glob("gp0212.*.b64"):
        old.unlink()
    encoded = base64.b64encode(gzip.compress(raw, compresslevel=9, mtime=0)).decode("ascii")
    names = []
    for i, off in enumerate(range(0, len(encoded), CHUNK_SIZE), 1):
        name = f"gp0212.{i:02d}.b64"
        (ROOT / name).write_text(encoded[off:off + CHUNK_SIZE])
        names.append(name)
    names_js = json.dumps(names, separators=(",", ":"))
    loader = f"""(async()=>{{try{{if(typeof DecompressionStream!=='function')throw new Error('This browser needs gzip stream support.');const names={names_js},texts=await Promise.all(names.map(async n=>{{const r=await fetch('./'+n,{{cache:'no-store'}});if(!r.ok)throw new Error(n+' '+r.status);return(await r.text()).replace(/\\s+/g,'')}})),parts=texts.map(s=>{{const raw=atob(s),a=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)a[i]=raw.charCodeAt(i);return a}}),total=parts.reduce((n,a)=>n+a.length,0),z=new Uint8Array(total);let o=0;for(const a of parts){{z.set(a,o);o+=a.length}}const h=await new Response(new Blob([z]).stream().pipeThrough(new DecompressionStream('gzip'))).text();if(!h.includes('GREED PIT 0.20.12 MOBILE RESUME CANDIDATE'))throw new Error('Build marker verification failed.');if(globalThis.crypto?.subtle){{const d=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(h)),hex=[...new Uint8Array(d)].map(x=>x.toString(16).padStart(2,'0')).join('');if(hex!=='{digest}')throw new Error('Build hash verification failed.')}}document.open();document.write(h);document.close()}}catch(e){{document.body.innerHTML='<main style=\"font-family:system-ui;padding:24px;background:#09090d;color:#f7f2df;min-height:100vh\"><h1>THE PIT FAILED TO OPEN</h1><p>'+String(e.message||e)+'</p></main>';console.error(e)}}}})()\n"""
    (ROOT / "loader-0212.js").write_text(loader)
    reconstructed = gzip.decompress(base64.b64decode("".join((ROOT / n).read_text().strip() for n in names)))
    if reconstructed != raw or sha(reconstructed) != digest:
        raise RuntimeError("0.20.12 packaged reconstruction mismatch")
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    if len(scripts) != 1:
        raise RuntimeError(f"Expected one inline script, found {len(scripts)}")
    Path("/tmp/greed-pit-0212.js").write_text(scripts[0])
    return digest, names


def main() -> None:
    html = patch()
    digest, names = package(html)
    print(f"Built 0.20.12 SHA-256: {digest}")
    print(f"Verified {len(names)} payload chunks: {', '.join(names)}")


if __name__ == "__main__":
    main()
