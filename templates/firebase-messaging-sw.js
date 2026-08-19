/**
 * CALSEVA Firebase Messaging Service Worker
 * Handles background push notifications when CALSEVA tab is closed or in background.
 */

importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js');

// Initialize Firebase App in Service Worker
firebase.initializeApp({
  apiKey: "AIzaSy_placeholder_key",
  authDomain: "calseva-2026.firebaseapp.com",
  projectId: "calseva-2026",
  messagingSenderId: "104417696551",
  appId: "1:104417696551:web:placeholder"
});

const messaging = firebase.messaging();

// Handle Background Push Messages
messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background push message:', payload);
  
  const notificationTitle = (payload.notification && payload.notification.title) || 'CalSEVA Alert';
  const notificationOptions = {
    body: (payload.notification && payload.notification.body) || '',
    icon: (payload.notification && payload.notification.icon) || '/caliprofile-pages/Calsevalogo.png',
    badge: '/caliprofile-pages/Calsevalogo.png',
    image: (payload.notification && payload.notification.image) || null,
    data: {
      url: (payload.data && payload.data.url) || '/home/home.html'
    }
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle Notification Clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
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
