/**
 * CALSEVA Firebase Cloud Messaging (FCM) Client Integration
 * Handles FCM registration, token retrieval, backend synchronization, and foreground push alerts.
 */

(function() {
  // Read Firebase & VAPID configuration injected from server
  const firebaseConfig = window.calsevaFirebaseConfig || {};
  const vapidKey = firebaseConfig.vapidKey || 'BG9hLohg7jKRV_NC6NxVLCYr2J136Qldq8PQFMJ1ogwBuQBEs70EwJzINX3hrInBXtK_K_jcLEAj05mwKCLzRC4';

  if (!('Notification' in window)) {
    console.log('[CalSEVA FCM] Web notifications are not supported by this browser.');
    return;
  }

  // Helper to send FCM token to CalSEVA backend
  async function sendTokenToBackend(token) {
    if (!token) return;
    try {
      const response = await fetch('/api/register-fcm-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          fcm_token: token,
          device_info: `${navigator.platform || 'Web'} - ${navigator.userAgent.split(' ')[0]}`
        })
      });
      const data = await response.json();
      if (data.success) {
        console.log('[CalSEVA FCM] Token registered with backend successfully.');
      } else {
        console.warn('[CalSEVA FCM] Backend token registration note:', data.error || data.message);
      }
    } catch (err) {
      console.error('[CalSEVA FCM] Failed to send token to backend:', err);
    }
  }

  // Initialize FCM Messaging
  function initFCM() {
    if (typeof firebase === 'undefined' || !firebase.messaging) {
      console.warn('[CalSEVA FCM] Firebase SDK compat script not found. Retrying in 1s...');
      setTimeout(initFCM, 1000);
      return;
    }

    // Ensure Firebase app is initialized
    if (!firebase.apps.length) {
      if (firebaseConfig.apiKey) {
        firebase.initializeApp(firebaseConfig);
      } else {
        console.warn('[CalSEVA FCM] Firebase config missing apiKey.');
        return;
      }
    }

    try {
      const messaging = firebase.messaging();

      // Request Notification Permission
      Notification.requestPermission().then((permission) => {
        if (permission === 'granted') {
          console.log('[CalSEVA FCM] Notification permission granted.');

          // Register service worker explicitly for FCM
          navigator.serviceWorker.register('/firebase-messaging-sw.js')
            .then((registration) => {
              return messaging.getToken({
                vapidKey: vapidKey,
                serviceWorkerRegistration: registration
              });
            })
            .then((token) => {
              if (token) {
                console.log('[CalSEVA FCM] Obtained FCM Token successfully.');
                sendTokenToBackend(token);
              } else {
                console.warn('[CalSEVA FCM] No registration token available. Request permission to generate one.');
              }
            })
            .catch((err) => {
              console.error('[CalSEVA FCM] Error retrieving FCM token:', err);
            });

        } else {
          console.log('[CalSEVA FCM] Notification permission denied by user.');
        }
      });

      // Handle Foreground Push Messages
      messaging.onMessage((payload) => {
        console.log('[CalSEVA FCM] Foreground Message received:', payload);
        const notification = payload.notification || {};
        const title = notification.title || 'CalSEVA Alert';
        const body = notification.body || '';
        const icon = notification.icon || '/caliprofile-pages/Calsevalogo.png';
        const clickUrl = (payload.data && payload.data.url) || '/home/home.html';

        showForegroundToast(title, body, icon, clickUrl);
      });

    } catch (fcmErr) {
      console.error('[CalSEVA FCM] Initialization error:', fcmErr);
    }
  }

  // Display custom floating Toast UI for foreground notifications
  function showForegroundToast(title, body, icon, url) {
    const existing = document.getElementById('calsevaFcmToast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'calsevaFcmToast';
    toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: 12px;">
        <img src="${icon}" alt="Notification Icon" style="width: 36px; height: 36px; border-radius: 8px; object-fit: contain;">
        <div style="flex: 1; text-align: left;">
          <h4 style="margin: 0; font-size: 14px; font-weight: 700; color: #FFFFFF;">${title}</h4>
          <p style="margin: 3px 0 0 0; font-size: 12px; color: rgba(255, 255, 255, 0.85);">${body}</p>
        </div>
        <button id="closeFcmToast" style="background: none; border: none; color: #FFFFFF; font-size: 18px; cursor: pointer; padding: 0 4px;">&times;</button>
      </div>
    `;

    Object.assign(toast.style, {
      position: 'fixed',
      top: '20px',
      right: '20px',
      zIndex: '999999',
      backgroundColor: '#1E2E35',
      color: '#FFFFFF',
      borderRadius: '12px',
      padding: '14px 18px',
      boxShadow: '0 8px 24px rgba(0,0,0,0.3)',
      border: '1px solid rgba(255,255,255,0.15)',
      maxWidth: '360px',
      fontFamily: "'Outfit', 'Commissioner', sans-serif",
      cursor: 'pointer',
      transition: 'all 0.3s ease'
    });

    toast.addEventListener('click', (e) => {
      if (e.target.id === 'closeFcmToast') {
        e.stopPropagation();
        toast.remove();
      } else {
        window.location.href = url;
      }
    });

    document.body.appendChild(toast);

    setTimeout(() => {
      if (toast.parentNode) toast.remove();
    }, 6000);
  }

  // Start initialization when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFCM);
  } else {
    initFCM();
  }
})();
