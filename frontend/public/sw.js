const CACHE_NAME = "tablewise-v1";

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(['/', '/manifest.webmanifest'])));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            )
        )
    );
});

self.addEventListener("fetch", (event) => {
    const request = event.request;

    // Never cache non-GET requests
    if (request.method !== "GET") {
        event.respondWith(fetch(request));
        return;
    }

    // Never cache API/auth traffic
    if (request.url.includes("/api/")) {
        event.respondWith(fetch(request));
        return;
    }

    // Cache-first/static strategy
    event.respondWith(
        caches.match(request).then((cached) => {
            return (
                cached ||
                fetch(request).then((response) => {
                    const cloned = response.clone();

                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(request, cloned);
                    });

                    return response;
                })
            );
        })
    );
});
