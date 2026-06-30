const CACHE_NAME = 'calseva-pwa-cache-v2';
const ASSETS_TO_CACHE = [
  '/cal-login/cal-login.html',
  '/cal-signup/cal-signup.html',
  '/caliverify/caliverify.html',
  '/home/home.html',
  '/cali-report/cali-report.html',
  '/cali-reports-data/cali-reports-data.html',
  '/caliprofile/caliprofile.html',
  '/cali-unit-convert/cali-unit-convert.html',
  '/cali-mv-chart/cali-mv-chart.html',
  '/cali-rtd-chart/cali-rtd-chart.html',
  '/notifications/notifications.html',
  '/schedule-work/schedule-work.html',
  '/tutorial/tutorial.html',
  '/material-symbols-outlined.woff2',
  '/caliprofile-pages/Calsevalogo.png',
  '/_cal-loder.mp4',
  '/cali-mv-chart/page2.png',
  '/cali-mv-chart/page3.png',
  '/cali-mv-chart/page4.png',
  '/cali-mv-chart/page5.png',
  '/cali-rtd-chart/page1.png',
  '/cali-rtd-chart/page2.png',
  '/cali-rtd-chart/page3.png'
];

// Install Event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('Service Worker: Caching files...');
      return cache.addAll(ASSETS_TO_CACHE);
    }).then(() => self.skipWaiting())
  );
});

// Activate Event (cleans up older caches)
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('Service Worker: Clearing old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event (Cache First, Network Fallback strategy)
self.addEventListener('fetch', (event) => {
  // Only intercept GET requests
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Skip API routes / database operations (always go to network)
  if (url.pathname.startsWith('/api') || 
      url.pathname.startsWith('/cal-login/auth') || 
      url.pathname.startsWith('/cal-signup/register') ||
      url.pathname.startsWith('/verify-otp') ||
      url.pathname.startsWith('/resend-otp') ||
      url.pathname.startsWith('/get-reports') ||
      url.pathname.startsWith('/save-report') ||
      url.pathname.startsWith('/delete-report')) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Return cached asset, fetch fresh copy in background to update cache
        fetch(event.request).then((networkResponse) => {
          if (networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, networkResponse);
            });
          }
        }).catch(() => {});
        return cachedResponse;
      }
      return fetch(event.request);
    })
  );
});
