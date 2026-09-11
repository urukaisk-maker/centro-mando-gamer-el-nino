const CACHE = "el-nino-v2";
const ASSETS = [
  "/01_EL_NINO_LAUNCHER/index.html",
  "/01_EL_NINO_LAUNCHER/manifest.json",
  "/01_EL_NINO_LAUNCHER/icono-512.png"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
});

self.addEventListener("fetch", e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});
