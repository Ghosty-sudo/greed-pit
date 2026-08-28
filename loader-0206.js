(async()=>{try{
if(typeof DecompressionStream!=='function')throw new Error('This browser needs gzip stream support.');
const names=["gp0206.01.b64", "gp0206.02.b64", "gp0206.03.b64", "gp0206.04.b64", "gp0206.05.b64"];
const parts=await Promise.all(names.map(async name=>{const r=await fetch('./'+name,{cache:'no-store'});if(!r.ok)throw new Error(name+' '+r.status);return (await r.text()).replace(/\s+/g,'')}));
const rawParts=parts.map(s=>{const raw=atob(s),u=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)u[i]=raw.charCodeAt(i);return u});
const total=rawParts.reduce((n,u)=>n+u.length,0),bytes=new Uint8Array(total);let off=0;for(const u of rawParts){bytes.set(u,off);off+=u.length}
const html=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
if(!html.includes('GREED PIT 0.20.6 KNOW YOUR PROBLEMS'))throw new Error('Build payload verification failed.');
document.open();document.write(html);document.close();
}catch(e){document.body.innerHTML='<main style="font-family:system-ui;padding:24px;background:#09090d;color:#f7f2df;min-height:100vh"><h1>THE PIT FAILED TO OPEN</h1><p>'+String(e.message||e)+'</p></main>';console.error(e)}})();
