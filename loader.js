(async()=>{try{
if(typeof DecompressionStream!=='function')throw new Error('This browser needs gzip stream support.');
const names=['game.01.b64','game.02.b64','game.03.b64','game.04.b64','game.05.b64','game.06.b64','game.07.b64','game.08.b64','game.09.b64','game.10.b64','game.11.b64','game.12.b64','game.13.b64'];
const parts=await Promise.all(names.map(async name=>{const r=await fetch('./'+name,{cache:'no-store'});if(!r.ok)throw new Error(name+' '+r.status);return (await r.text()).replace(/\s+/g,'')}));
const rawParts=parts.map(s=>{const raw=atob(s),u=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)u[i]=raw.charCodeAt(i);return u});
const total=rawParts.reduce((n,u)=>n+u.length,0),bytes=new Uint8Array(total);let off=0;for(const u of rawParts){bytes.set(u,off);off+=u.length}
const html=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
if(!html.includes('GREED PIT 0.20.5 PIT FIGHTS BACK'))throw new Error('Build payload verification failed.');
document.open();document.write(html);document.close();
}catch(e){const b=document.getElementById('boot');if(b)b.innerHTML='THE PIT FAILED TO OPEN<small>'+String(e.message||e)+'</small>';console.error(e)}})();
