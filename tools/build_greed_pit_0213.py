#!/usr/bin/env python3
"""Build GREED PIT 0.20.13 performance candidate from verified 0.20.12.

Performance pass keeps gameplay/progression intact while reducing per-frame mobile cost:
- spatial broad phase for projectile/enemy collision
- local spatial lookup for collector/orb targeting
- viewport culling for world rendering
- HUD updates throttled to 10 Hz
- canvas DPR capped at 1.5 on high-density mobile screens
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/greed-pit-0.20.12.html"
OUTPUT = ROOT / "src/greed-pit-0.20.13.html"
SHA_FILE = ROOT / "src/greed-pit-0.20.13.sha256"
EXPECTED_0212 = "cefac4ae0db98fb63006113ae7deac0320a6b61cb0a231ea01d3bae8c78072ef"
VERSION = "0.20.13"
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
    if actual != EXPECTED_0212:
        raise RuntimeError(f"Refusing 0.20.13 build: 0.20.12 SHA changed: {actual}")
    text = raw.decode("utf-8")

    text = r(
        text,
        "<title>GREED PIT 0.20.12 MOBILE RESUME CANDIDATE</title>",
        "<title>GREED PIT 0.20.13 PERFORMANCE CANDIDATE</title>",
        "title",
    )
    text = r(
        text,
        "Candidate 0.20.12 — browser-validated audio build plus recoverable mobile run checkpoints.",
        "Candidate 0.20.13 — mobile performance pass: spatial collision broad-phase, viewport culling, HUD throttling, and a lower high-density render cost.",
        "visible version",
    )
    text = r(text, "build:'0.20.12'", "build:'0.20.13'", "feedback version")

    text = r(
        text,
        "function resize(){DPR=Math.min(devicePixelRatio||1,2);W=innerWidth;H=innerHeight;canvas.width=W*DPR;canvas.height=H*DPR;ctx.setTransform(DPR,0,0,DPR,0,0)}",
        "const MOBILE_DPR_CAP=1.5;function resize(){DPR=Math.min(devicePixelRatio||1,MOBILE_DPR_CAP);W=innerWidth;H=innerHeight;canvas.width=Math.round(W*DPR);canvas.height=Math.round(H*DPR);ctx.setTransform(DPR,0,0,DPR,0,0)}",
        "mobile DPR cap",
    )

    segment_anchor = """function segmentCircle(x1,y1,x2,y2,cx,cy,r){
 const dx=x2-x1,dy=y2-y1,l2=dx*dx+dy*dy;
 if(!l2)return Math.hypot(cx-x1,cy-y1)<=r;
 const t=clamp(((cx-x1)*dx+(cy-y1)*dy)/l2,0,1),px=x1+t*dx,py=y1+t*dy;
 return Math.hypot(cx-px,cy-py)<=r
}
"""
    perf_helpers = r"""const PERF_CELL=96;
function perfKey(gx,gy){return ((gx&65535)<<16)|(gy&65535)}
function buildSpatialGrid(items){
 const grid=new Map();
 for(const item of items){if(item.dead)continue;const gx=Math.floor(item.x/PERF_CELL),gy=Math.floor(item.y/PERF_CELL),k=perfKey(gx,gy),bucket=grid.get(k);if(bucket)bucket.push(item);else grid.set(k,[item])}
 return grid
}
function visitSpatial(grid,minX,minY,maxX,maxY,fn){
 if(!grid)return true;
 const gx0=Math.floor(minX/PERF_CELL),gy0=Math.floor(minY/PERF_CELL),gx1=Math.floor(maxX/PERF_CELL),gy1=Math.floor(maxY/PERF_CELL);
 for(let gx=gx0;gx<=gx1;gx++)for(let gy=gy0;gy<=gy1;gy++){const bucket=grid.get(perfKey(gx,gy));if(!bucket)continue;for(const item of bucket)if(fn(item)===false)return false}
 return true
}
function nearestOrbTarget(e,grid,r=170){
 let best=null,best2=r*r;
 visitSpatial(grid,e.x-r,e.y-r,e.x+r,e.y+r,o=>{if(o.dead)return;const dx=o.x-e.x,dy=o.y-e.y,d2=dx*dx+dy*dy;if(d2<best2){best2=d2;best=o}});
 return best
}
function inView(o,pad=64){return o.x>=g.camX-pad&&o.x<=g.camX+W+pad&&o.y>=g.camY-pad&&o.y<=g.camY+H+pad}
"""
    text = r(text, segment_anchor, segment_anchor + perf_helpers, "performance helpers")

    old_shoot = """function shoot(){
 if(!g.enemies.length)return false;
 let target=g.enemies.reduce((a,b)=>dist(g.player,a)<dist(g.player,b)?a:b),base=Math.atan2(target.y-g.player.y,target.x-g.player.x);
"""
    new_shoot = """function shoot(){
 if(!g.enemies.length)return false;
 let target=null,best2=Infinity;for(const e of g.enemies){if(e.hp<=0||e.dead)continue;const dx=e.x-g.player.x,dy=e.y-g.player.y,d2=dx*dx+dy*dy;if(d2<best2){best2=d2;target=e}}if(!target)return false;
 let base=Math.atan2(target.y-g.player.y,target.x-g.player.x);
"""
    text = r(text, old_shoot, new_shoot, "nearest-target optimization")

    attack_anchor = """ const attack=attackSchedule(g.bulletTimer,dt,effectiveFireRate(),g.enemies.length>0);g.bulletTimer=attack.timer;for(let i=0;i<attack.shots;i++)shoot()
 for(const b of g.bullets){b.px=b.x;b.py=b.y;b.x+=b.vx*dt;b.y+=b.vy*dt;b.life-=dt}
 for(const e of g.enemies){
"""
    attack_new = """ const attack=attackSchedule(g.bulletTimer,dt,effectiveFireRate(),g.enemies.length>0);g.bulletTimer=attack.timer;for(let i=0;i<attack.shots;i++)shoot()
 for(const b of g.bullets){b.px=b.x;b.py=b.y;b.x+=b.vx*dt;b.y+=b.vy*dt;b.life-=dt}
 const orbGrid=g.orbs.length?buildSpatialGrid(g.orbs):null;
 for(const e of g.enemies){
"""
    text = r(text, attack_anchor, attack_new, "orb spatial grid")

    collector_old = """ if(e.role==='collector'&&g.orbs.length){
   let o=g.orbs.reduce((a,b)=>dist(e,a)<dist(e,b)?a:b),od=dist(e,o);
   if(od<170){
"""
    collector_new = """ if(e.role==='collector'&&g.orbs.length){
   const o=nearestOrbTarget(e,orbGrid,170);
   if(o){const od=Math.hypot(e.x-o.x,e.y-o.y);
"""
    text = r(text, collector_old, collector_new, "collector local orb lookup")

    collision_old = """ for(const b of g.bullets){for(const e of g.enemies){if(e.hp>0&&!b.seen.has(e)&&segmentCircle(b.px-e.px,b.py-e.py,b.x-e.x,b.y-e.y,0,0,b.r+e.r)){b.seen.add(e);damageEnemy(e,b);if(b.hits>b.pierce){b.life=0;break}}}}
"""
    collision_new = """ const enemyGrid=buildSpatialGrid(g.enemies);
 for(const b of g.bullets){
   const pad=52,minX=Math.min(b.px,b.x)-pad,minY=Math.min(b.py,b.y)-pad,maxX=Math.max(b.px,b.x)+pad,maxY=Math.max(b.py,b.y)+pad;
   visitSpatial(enemyGrid,minX,minY,maxX,maxY,e=>{if(e.hp<=0||b.seen.has(e))return;if(segmentCircle(b.px-e.px,b.py-e.py,b.x-e.x,b.y-e.y,0,0,b.r+e.r)){b.seen.add(e);damageEnemy(e,b);if(b.hits>b.pierce){b.life=0;return false}}})
 }
"""
    text = r(text, collision_old, collision_new, "spatial collision broad phase")

    text = r(
        text,
        "function updateHud(){let m=Math.floor(g.t/60),s=Math.floor(g.t%60).toString().padStart(2,'0');",
        "let hudLastMs=-1e9;function updateHud(force=false){const now=performance.now();if(!force&&now-hudLastMs<100)return;hudLastMs=now;let m=Math.floor(g.t/60),s=Math.floor(g.t%60).toString().padStart(2,'0');",
        "HUD throttle",
    )

    text = r(
        text,
        "ctx.strokeStyle='rgba(255,255,255,.12)';ctx.lineWidth=3;ctx.strokeRect(1,1,g.worldW-2,g.worldH-2);\n for(const h of g.hazards){",
        "ctx.strokeStyle='rgba(255,255,255,.12)';ctx.lineWidth=3;ctx.strokeRect(1,1,g.worldW-2,g.worldH-2);\n for(const h of g.hazards){if(!inView(h,h.r+20))continue;",
        "hazard viewport culling",
    )
    text = r(
        text,
        " for(const h of g.healthDrops){const pulse=1+.08*Math.sin(g.t*7+h.x*.03);",
        " for(const h of g.healthDrops){if(!inView(h,30))continue;const pulse=1+.08*Math.sin(g.t*7+h.x*.03);",
        "health viewport culling",
    )
    text = r(
        text,
        " for(const o of g.orbs){const col=o.xp>1?'#ffe66a':'#81f7b7';",
        " for(const o of g.orbs){if(!inView(o,20))continue;const col=o.xp>1?'#ffe66a':'#81f7b7';",
        "orb viewport culling",
    )
    text = r(
        text,
        "}for(const b of g.bullets){const col=g.hypeTime?'#ffdf3d':'#f3efe1';",
        "}for(const b of g.bullets){if(!inView(b,18))continue;const col=g.hypeTime?'#ffdf3d':'#f3efe1';",
        "bullet viewport culling",
    )
    text = r(
        text,
        " for(const e of g.enemies){drawEnemyVisual(e)}",
        " for(const e of g.enemies){if(inView(e,e.boss?80:60))drawEnemyVisual(e)}",
        "enemy viewport culling",
    )
    text = r(
        text,
        " for(const p of g.particles){ctx.globalAlpha=p.life/p.max;",
        " for(const p of g.particles){if(!inView(p,20))continue;ctx.globalAlpha=p.life/p.max;",
        "particle viewport culling",
    )
    text = r(
        text,
        "for(const f of g.floating){ctx.globalAlpha=clamp(f.life/.42,0,1);",
        "for(const f of g.floating){if(!inView(f,30))continue;ctx.globalAlpha=clamp(f.life/.42,0,1);",
        "floating text viewport culling",
    )

    self_test_old = "ok('run checkpoint system exists',typeof saveRunSnapshot==='function'&&typeof restoreRunSnapshot==='function'&&!!$('#continueRun'))"
    self_test_new = self_test_old + ";ok('mobile DPR cap active',MOBILE_DPR_CAP===1.5);ok('spatial broad phase prunes distant entities',(()=>{const items=Array.from({length:180},(_,i)=>({x:i*120,y:(i%3)*120})),grid=buildSpatialGrid(items);let seen=0;visitSpatial(grid,-20,-20,120,120,()=>{seen++});return seen<10})());ok('viewport culling exists',typeof inView==='function'&&typeof visitSpatial==='function')"
    text = r(text, self_test_old, self_test_new, "performance self-tests")

    for marker in [
        "GREED PIT 0.20.13 PERFORMANCE CANDIDATE",
        "MOBILE_DPR_CAP=1.5",
        "const enemyGrid=buildSpatialGrid(g.enemies)",
        "spatial broad phase prunes distant entities",
        "build:'0.20.13'",
    ]:
        if marker not in text:
            raise RuntimeError(f"Missing 0.20.13 marker: {marker}")
    return text


def package(html: str) -> tuple[str, list[str]]:
    raw = html.encode("utf-8")
    digest = sha(raw)
    OUTPUT.write_bytes(raw)
    SHA_FILE.write_text(digest + "\n")
    for old in ROOT.glob("gp0213.*.b64"):
        old.unlink()
    encoded = base64.b64encode(gzip.compress(raw, compresslevel=9, mtime=0)).decode("ascii")
    names = []
    for i, off in enumerate(range(0, len(encoded), CHUNK_SIZE), 1):
        name = f"gp0213.{i:02d}.b64"
        (ROOT / name).write_text(encoded[off:off + CHUNK_SIZE])
        names.append(name)
    names_js = json.dumps(names, separators=(",", ":"))
    loader = f"""(async()=>{{try{{if(typeof DecompressionStream!=='function')throw new Error('This browser needs gzip stream support.');const names={names_js},texts=await Promise.all(names.map(async n=>{{const r=await fetch('./'+n,{{cache:'no-store'}});if(!r.ok)throw new Error(n+' '+r.status);return(await r.text()).replace(/\\s+/g,'')}})),parts=texts.map(s=>{{const raw=atob(s),a=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)a[i]=raw.charCodeAt(i);return a}}),total=parts.reduce((n,a)=>n+a.length,0),z=new Uint8Array(total);let o=0;for(const a of parts){{z.set(a,o);o+=a.length}}const h=await new Response(new Blob([z]).stream().pipeThrough(new DecompressionStream('gzip'))).text();if(!h.includes('GREED PIT 0.20.13 PERFORMANCE CANDIDATE'))throw new Error('Build marker verification failed.');if(globalThis.crypto?.subtle){{const d=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(h)),hex=[...new Uint8Array(d)].map(x=>x.toString(16).padStart(2,'0')).join('');if(hex!=='{digest}')throw new Error('Build hash verification failed.')}}document.open();document.write(h);document.close()}}catch(e){{document.body.innerHTML='<main style=\"font-family:system-ui;padding:24px;background:#09090d;color:#f7f2df;min-height:100vh\"><h1>THE PIT FAILED TO OPEN</h1><p>'+String(e.message||e)+'</p></main>';console.error(e)}}}})()\n"""
    (ROOT / "loader-0213.js").write_text(loader)
    reconstructed = gzip.decompress(base64.b64decode("".join((ROOT / n).read_text().strip() for n in names)))
    if reconstructed != raw or sha(reconstructed) != digest:
        raise RuntimeError("0.20.13 packaged reconstruction mismatch")
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    if len(scripts) != 1:
        raise RuntimeError(f"Expected one inline script, found {len(scripts)}")
    Path("/tmp/greed-pit-0213.js").write_text(scripts[0])
    return digest, names


def main() -> None:
    html = patch()
    digest, names = package(html)
    print(f"Built 0.20.13 SHA-256: {digest}")
    print(f"Verified {len(names)} payload chunks: {', '.join(names)}")


if __name__ == "__main__":
    main()
