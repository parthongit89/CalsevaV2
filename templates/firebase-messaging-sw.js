/**
 * CALSEVA Firebase Messaging Service Worker
 * Rich Native Push Notification System (SMS / Play Store / WhatsApp Style)
 */

importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js');

// Dynamically injected Firebase Configuration
firebase.initializeApp({{ firebase_config|tojson }});

const messaging = firebase.messaging();

// Handle Rich Background Push Messages
messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received rich background push message:', payload);
  
  const notificationTitle = (payload.notification && payload.notification.title) || 'CalSEVA Alert';
  const notificationOptions = {
    body: (payload.notification && payload.notification.body) || '',
    icon: (payload.notification && payload.notification.icon) || '/caliprofile-pages/Calsevalogo.png',
    badge: '/caliprofile-pages/Calsevalogo.png',
    image: (payload.notification && payload.notification.image) || null,
    vibrate: [200, 100, 200, 100, 200],
    tag: 'calseva-rich-alert',
    renotify: true,
    requireInteraction: true,
    actions: [
      { action: 'open_app', title: '📲 Open App' },
      { action: 'dismiss_alert', title: '✖ Dismiss' }
    ],
    data: {
      url: (payload.data && payload.data.url) || '/home/home.html'
    }
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle Native Notification Click & Action Buttons
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'dismiss_alert') {
    return;
  }

  const targetUrl = (event.notification.data && event.notification.data.url) || '/home/home.html';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes(targetUrl) && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});
