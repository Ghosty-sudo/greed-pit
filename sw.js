const CACHE='greed-pit-0.20.2';
const CORE=['./','./index.html','./manifest.webmanifest'];
self.addEventListener('install',event=>{
  event.waitUntil(
    caches.open(CACHE)
      .then(cache=>cache.addAll(CORE))
      .then(()=>self.skipWaiting())
  );
});
self.addEventListener('activate',event=>{
  event.waitUntil(
    caches.keys()
      .then(keys=>Promise.all(
        keys
          .filter(key=>key.startsWith('greed-pit-')&&key!==CACHE)
          .map(key=>caches.delete(key))
      ))
      .then(()=>self.clients.claim())
  );
});
self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET') return;
  event.respondWith(
    fetch(event.request)
      .then(response=>{
        if(response&&response.ok&&event.request.url.startsWith(self.location.origin)){
          const copy=response.clone();
          caches.open(CACHE).then(cache=>cache.put(event.request,copy));
        }
        return response;
      })
      .catch(()=>
        caches.match(event.request).then(cached=>{
          if(cached) return cached;
          if(event.request.mode==='navigate') return caches.match('./index.html');
          return Response.error();
        })
      )
  );
});