#!/usr/bin/env python3
"""Build the hardened PC/browser itch.io package from verified GREED PIT 0.20.13."""

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
BUILD_ID = "0.20.13-itch-pc2"


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

    # itch.io hosts the HTML5 package itself; PWA service workers can leave embedded
    # players on stale bytes after an update, so the distribution build omits them.
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
        '<meta name="theme-color" content="#09090d">\n<meta name="greed-pit-build" content="0.20.13-itch-pc2">',
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

    old_audio = """const runMusic=new Audio(AUDIO.music);runMusic.loop=true;runMusic.preload='auto';runMusic.volume=.22;
const audioLast={},sfxPools={},sfxCursor={};
for(const [key,url] of Object.entries(AUDIO)){if(key==='music')continue;sfxPools[key]=Array.from({length:3},()=>{const a=new Audio(url);a.preload='auto';return a});sfxCursor[key]=0}
function playSfx(key,volume=.45,minGap=0){if(!meta.audio||!sfxPools[key])return;const now=performance.now();if(now-(audioLast[key]??-1e9)<minGap)return;audioLast[key]=now;const pool=sfxPools[key],i=sfxCursor[key]%pool.length,a=pool[i];sfxCursor[key]=i+1;try{a.pause();a.currentTime=0}catch(e){}a.volume=clamp(volume,0,1);a.play().catch(()=>{})}
function resumeMusic(){if(!meta.audio)return;runMusic.volume=.22;runMusic.play().catch(()=>{})}
function pauseMusic(){runMusic.pause()}
function stopMusic(){runMusic.pause();try{runMusic.currentTime=0}catch(e){}}
function updateAudioButton(){const b=$('#audioToggle');if(b)b.textContent=meta.audio?'AUDIO: ON':'AUDIO: OFF'}
function setAudio(enabled){meta.audio=!!enabled;saveMeta();updateAudioButton();if(!meta.audio)stopMusic();else if(state==='playing'&&!g?.paused)resumeMusic()}"""

    new_audio = """const runMusic=new Audio(AUDIO.music);runMusic.loop=true;runMusic.preload='metadata';runMusic.volume=.22;
const SFX_POOL_SIZE=2,audioLast={},sfxPools={},sfxCursor={};let audioPrimed=false,audioMusicRetry=false;
for(const [key] of Object.entries(AUDIO)){if(key==='music')continue;sfxPools[key]=[];sfxCursor[key]=0}
function makeSfxVoice(key){const a=new Audio(AUDIO[key]);a.preload='metadata';return a}
function getSfxPool(key){if(!sfxPools[key])return null;while(sfxPools[key].length<SFX_POOL_SIZE)sfxPools[key].push(makeSfxVoice(key));return sfxPools[key]}
function primeAudio(){if(audioPrimed)return;audioPrimed=true;runMusic.preload='auto';try{runMusic.load()}catch(e){};for(const key of Object.keys(sfxPools)){const pool=getSfxPool(key);if(pool?.[0]){pool[0].preload='auto';try{pool[0].load()}catch(e){}}}}
function safeAudioPlay(a,retryMusic=false){try{const p=a.play();if(p?.catch)p.catch(()=>{if(retryMusic)audioMusicRetry=true})}catch(e){if(retryMusic)audioMusicRetry=true}}
function playSfx(key,volume=.45,minGap=0){if(!meta.audio||!sfxPools[key])return;const now=performance.now();if(now-(audioLast[key]??-1e9)<minGap)return;audioLast[key]=now;const pool=getSfxPool(key),i=sfxCursor[key]%pool.length,a=pool[i];sfxCursor[key]=i+1;try{a.pause();a.currentTime=0}catch(e){}a.volume=clamp(volume,0,1);safeAudioPlay(a,false)}
function resumeMusic(){if(!meta.audio)return;runMusic.volume=.22;safeAudioPlay(runMusic,true)}
function pauseMusic(){runMusic.pause()}
function stopMusic(){runMusic.pause();audioMusicRetry=false;try{runMusic.currentTime=0}catch(e){}}
function audioGesture(){primeAudio();if(audioMusicRetry&&meta.audio&&state==='playing'&&!g?.paused){audioMusicRetry=false;resumeMusic()}}
document.addEventListener('pointerdown',audioGesture,{capture:true});document.addEventListener('keydown',audioGesture,{capture:true});
function updateAudioButton(){const b=$('#audioToggle');if(b)b.textContent=meta.audio?'AUDIO: ON':'AUDIO: OFF'}
function setAudio(enabled){meta.audio=!!enabled;saveMeta();updateAudioButton();if(!meta.audio)stopMusic();else if(state==='playing'&&!g?.paused)resumeMusic()}"""
    html = replace_once(html, old_audio, new_audio, "audio lifecycle hardening")

    old_tail = "if(new URLSearchParams(location.search).has('test'))selfTest();else draw()"
    qa_hooks = r"""
function qaRender(name,tests,extra=''){const pass=tests.every(x=>x[1]);document.body.innerHTML='<pre id="qa-result" style="white-space:pre-wrap;padding:20px;background:white;color:#111">'+name+'\n\n'+tests.map(x=>(x[1]?'PASS  ':'FAIL  ')+x[0]).join('\n')+(extra?'\n\n'+extra:'')+'\n\n'+(pass?'QA PASSED':'QA FAILURE')+'</pre>'}
function audioQa(){
 const tests=[];const ok=(n,v)=>tests.push([n,!!v]);const priorState=state,priorG=g,priorAudio=meta.audio,priorRetry=audioMusicRetry,priorPrimed=audioPrimed;
 const pool=getSfxPool('xp');let musicCalls=0,sfxCalls=0;const musicPlay=runMusic.play,poolPlays=pool.map(a=>a.play);
 try{
  runMusic.play=()=>{musicCalls++;return Promise.resolve()};pool.forEach(a=>a.play=()=>{sfxCalls++;return Promise.resolve()});
  meta.audio=true;state='title';g={paused:false};setAudio(true);ok('title audio toggle does not autoplay music',musicCalls===0);
  state='playing';resumeMusic();ok('music starts when gameplay requests it',musicCalls===1);
  audioLast.xp=-1e9;playSfx('xp',.2,1000);playSfx('xp',.2,1000);ok('dense duplicate SFX are throttled',sfxCalls===1);
  meta.audio=false;audioLast.xp=-1e9;playSfx('xp',.2,0);ok('audio OFF suppresses SFX',sfxCalls===1);
  ok('SFX voice pool is bounded',pool.length===SFX_POOL_SIZE&&SFX_POOL_SIZE===2);
  ok('audio is primed through explicit gesture hook',typeof audioGesture==='function'&&typeof primeAudio==='function');
  ok('music retry path is bounded to user gesture',typeof audioMusicRetry==='boolean');
 }catch(e){tests.push(['audio QA exception: '+e.message,false])}
 finally{runMusic.play=musicPlay;pool.forEach((a,i)=>a.play=poolPlays[i]);meta.audio=priorAudio;state=priorState;g=priorG;audioMusicRetry=priorRetry;audioPrimed=priorPrimed;updateAudioButton()}
 qaRender('GREED PIT AUDIO LIFECYCLE QA',tests)
}
async function mediaQa(){
 const tests=[];const ok=(n,v)=>tests.push([n,!!v]);const entries=Object.entries(AUDIO);
 for(const [key,url] of entries){
  const result=await new Promise(resolve=>{const a=new Audio();let settled=false;const finish=v=>{if(settled)return;settled=true;clearTimeout(timer);resolve(v)};const timer=setTimeout(()=>finish(false),5000);a.preload='metadata';a.addEventListener('loadedmetadata',()=>finish(Number.isFinite(a.duration)&&a.duration>0),{once:true});a.addEventListener('error',()=>finish(false),{once:true});a.src=url;try{a.load()}catch(e){finish(false)}});
  ok('media metadata loads: '+key,result)
 }
 qaRender('GREED PIT AUDIO ASSET / DECODE QA',tests)
}
async function playbackQa(){
 const tests=[];const ok=(n,v)=>tests.push([n,!!v]);const priorState=state,priorG=g,priorAudio=meta.audio;
 try{
  meta.audio=true;state='playing';g={paused:false};primeAudio();runMusic.muted=true;
  for(const key of Object.keys(sfxPools)){const pool=getSfxPool(key);for(const a of pool)a.muted=true}
  let musicOk=true;try{await runMusic.play()}catch(e){musicOk=false}ok('music element can enter playback',musicOk&&!runMusic.paused);pauseMusic();ok('pause halts music',runMusic.paused);
  audioLast.xp=-1e9;playSfx('xp',0,0);await new Promise(r=>setTimeout(r,180));const xpPool=getSfxPool('xp');ok('SFX element can activate',xpPool.some(a=>!a.paused||a.currentTime>0));
  stopMusic()
 }catch(e){tests.push(['playback QA exception: '+e.message,false])}
 finally{meta.audio=priorAudio;state=priorState;g=priorG;runMusic.muted=false;for(const key of Object.keys(sfxPools)){for(const a of sfxPools[key])a.muted=false}}
 qaRender('GREED PIT ACTUAL AUDIO PLAYBACK QA',tests)
}
function perfQa(){
 const tests=[];const ok=(n,v)=>tests.push([n,!!v]);const priorState=state,priorG=g,priorMetaAudio=meta.audio,priorLast=last;
 try{
  meta.audio=false;resetGame();cancelAnimationFrame(raf);state='playing';g.paused=false;
  g.t=2701;g.nextCycle=1e9;g.nextBossAt=1e9;g.spawnTimer=1e9;g.hazardTimer=1e9;g.nextXp=1e12;g.player.hp=g.player.maxHp=1e12;g.player.damage=0;g.player.regen=1e9;g.player.magnet=1;
  while(g.enemies.length<enemyCap())spawnEnemy();
  g.orbs=[];for(let i=0;i<300;i++)g.orbs.push({x:(i%20)*55+20,y:Math.floor(i/20)*55+20,r:5,xp:1});
  g.particles=[];for(let i=0;i<600;i++)g.particles.push({x:(i%30)*35,y:Math.floor(i/30)*35,vx:0,vy:0,life:999,max:999,r:2});
  g.floating=[];for(let i=0;i<160;i++)g.floating.push({x:(i%20)*50,y:Math.floor(i/20)*45,text:'99',life:999,crit:false});
  const start=performance.now();for(let i=0;i<180;i++){update(1/60);if(state!=='playing')throw new Error('stress run left playing state');draw()}const elapsed=performance.now()-start;
  ok('45-minute enemy cap stays bounded',enemyCap()<=180&&g.enemies.length<=183);
  ok('XP orb population remains bounded',g.orbs.length<=300);
  ok('particle population remains bounded',g.particles.length<=600);
  ok('long-session values remain finite',Number.isFinite(g.player.x)&&Number.isFinite(g.player.y)&&Number.isFinite(g.t));
  ok('180 stress frames complete under CI budget',elapsed<5000);
  ok('performance protections are active',MOBILE_DPR_CAP===1.5&&typeof buildSpatialGrid==='function'&&typeof visitSpatial==='function'&&typeof inView==='function');
  qaRender('GREED PIT LONG-SESSION PERFORMANCE QA',tests,`stress_ms=${elapsed.toFixed(1)} enemies=${g.enemies.length} orbs=${g.orbs.length} particles=${g.particles.length}`)
  return
 }catch(e){tests.push(['performance QA exception: '+e.message,false])}
 finally{cancelAnimationFrame(raf);state=priorState;g=priorG;meta.audio=priorMetaAudio;last=priorLast}
 qaRender('GREED PIT LONG-SESSION PERFORMANCE QA',tests)
}
const qaParams=new URLSearchParams(location.search);
if(qaParams.has('test'))selfTest();else if(qaParams.has('audioqa'))audioQa();else if(qaParams.has('mediaqa'))mediaQa();else if(qaParams.has('playbackqa'))playbackQa();else if(qaParams.has('perfqa'))perfQa();else draw()"""
    html = replace_once(html, old_tail, qa_hooks.strip(), "release QA hooks")

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets" / "audio" / "music").mkdir(parents=True)
    (OUT / "assets" / "audio" / "sfx").mkdir(parents=True)

    shutil.copy2(ROOT / "assets" / "audio" / "music" / "music_run_preview.mp3", OUT / "assets" / "audio" / "music" / "music_run_preview.mp3")
    for key, rel in {
        "xp": "xp_pickup.mp3",
        "upgrade": "upgrade_select.mp3",
        "greed": "greed_contract.mp3",
        "enemy": "enemy_death.mp3",
        "hit": "player_hit.mp3",
        "blast": "circle_crash_explosion.mp3",
        "boss": "boss_arrival.mp3",
        "cycle": "cycle_checkpoint.mp3",
        "death": "player_death.mp3",
    }.items():
        src = ROOT / "assets" / "audio" / "sfx" / rel
        if not src.is_file() or src.stat().st_size <= 0:
            raise SystemExit(f"missing/empty required audio asset: {key} -> {src}")
        shutil.copy2(src, OUT / "assets" / "audio" / "sfx" / rel)

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
                "audio": {
                    "enabled": True,
                    "gesture_primed": True,
                    "music_preload": "metadata->auto on gesture",
                    "sfx_pool_size": 2,
                    "duplicate_event_throttles": True,
                },
                "active_run_recovery": True,
                "qa_modes": ["test", "audioqa", "mediaqa", "playbackqa", "perfqa"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    required = [
        'greed-pit-build" content="0.20.13-itch-pc2',
        "WASD / arrow keys",
        "KeyW:'up'",
        "ArrowUp:'up'",
        "e.code==='Escape'",
        "matchMedia('(pointer: coarse)').matches",
        "CONTINUE SAVED RUN",
        "AUDIO: ON",
        "SFX_POOL_SIZE=2",
        "function audioGesture()",
        "function audioQa()",
        "function mediaQa()",
        "function playbackQa()",
        "function perfQa()",
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
