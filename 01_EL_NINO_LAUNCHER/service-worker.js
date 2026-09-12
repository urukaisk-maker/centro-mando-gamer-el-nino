// Service Worker - El Nino
// NO cachea el HTML para que los cambios se vean al instante.
// Solo cachea iconos y manifest, que no cambian.

const CACHE = "el-nino-v3";
const ASSETS = [
    "/01_EL_NINO_LAUNCHER/manifest.json",
    "/01_EL_NINO_LAUNCHER/icono-192.png",
    "/01_EL_NINO_LAUNCHER/icono-512.png"
];

self.addEventListener("install", function(e){
    e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(ASSETS); }));
    self.skipWaiting();
});

self.addEventListener("activate", function(e){
    e.waitUntil(caches.keys().then(function(keys){
        return Promise.all(keys.filter(function(k){ return k !== CACHE; }).map(function(k){ return caches.delete(k); }));
    }));
    self.clients.claim();
});

self.addEventListener("fetch", function(e){
    var url = e.request.url;
    if (url.indexOf("icono-") !== -1 || url.indexOf("manifest.json") !== -1) {
        e.respondWith(caches.match(e.request).then(function(r){ return r || fetch(e.request); }));
    }
});



