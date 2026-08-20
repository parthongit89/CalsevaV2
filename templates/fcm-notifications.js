/**
 * CALSEVA Firebase Cloud Messaging (FCM) Client Integration
 * Rich Android System / SMS / Play Store Notification Style
 */

(function() {
  const firebaseConfig = window.calsevaFirebaseConfig || {};
  const vapidKey = firebaseConfig.vapidKey || 'BG9hLohg7jKRV_NC6NxVLCYr2J136Qldq8PQFMJ1ogwBuQBEs70EwJzINX3hrInBXtK_K_jcLEAj05mwKCLzRC4';

  if (!('Notification' in window)) {
    console.log('[CalSEVA FCM] Web notifications are not supported by this browser.');
    return;
  }

  async function sendTokenToBackend(token) {
    if (!token) return null;
    try {
      const response = await fetch('/api/register-fcm-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fcm_token: token,
          device_info: `${navigator.platform || 'Web'} - ${navigator.userAgent.split(' ')[0]}`
        })
      });
      const data = await response.json();
      if (data.success) {
        console.log('[CalSEVA FCM] Token registered with backend successfully.');
      } else {
        console.warn('[CalSEVA FCM] Backend token note:', data.error);
      }
      return data;
    } catch (err) {
      console.error('[CalSEVA FCM] Failed to send token to backend:', err);
      return null;
    }
  }

  async function obtainAndSendToken(messaging, isManual = false) {
    if (!('serviceWorker' in navigator)) {
      if (isManual) alert('❌ Service Workers are not supported on this browser.');
      return;
    }

    try {
      // 1. Register service worker and wait until it is fully active
      await navigator.serviceWorker.register('/firebase-messaging-sw.js');
      const registration = await navigator.serviceWorker.ready;
      if (isManual) console.log('[CalSEVA FCM] Service Worker active & ready:', registration);

      // 2. Request FCM Token from Google Cloud Messaging
      let token = null;
      try {
        token = await messaging.getToken({
          vapidKey: vapidKey,
          serviceWorkerRegistration: registration
        });
      } catch (fcmErr) {
        console.warn('[CalSEVA FCM] VAPID getToken failed, trying fallback scope:', fcmErr);
        try {
          token = await messaging.getToken();
        } catch (fcmErr2) {
          console.error('[CalSEVA FCM] Fallback getToken failed:', fcmErr2);
          throw fcmErr;
        }
      }

      if (token) {
        // Log FCM Token prominently in Browser Console (F12) for "Test on Device"
        console.log('%c🔥 CALSEVA DEVICE FCM REGISTRATION TOKEN 🔥', 'background: #3A606E; color: #FFFFFF; font-size: 14px; font-weight: bold; padding: 4px 10px; border-radius: 6px;');
        console.log('%cCopy this token for Firebase Console "Test on device":', 'color: #2E7D32; font-weight: bold;');
        console.log(token);
        console.log('========================================================================================');

        const res = await sendTokenToBackend(token);
        if (isManual) {
          if (res && res.success) {
            alert('🎉 SUCCESS! Device registered in database.\n\n🔥 YOUR FCM TOKEN:\n' + token);
            if (typeof loadStats === 'function') loadStats();
          } else {
            alert('⚠️ Token obtained but backend response: ' + (res ? res.error : 'Unknown'));
          }
        }
      } else {
        if (isManual) alert('⚠️ Google returned empty FCM token. Please check FIREBASE_API_KEY in Render.');
      }
    } catch (err) {
      console.error('[CalSEVA FCM] Token error:', err);
      if (isManual) {
        alert('❌ Google FCM Token Error:\n' + (err.message || err) + '\n\nPlease check VAPID Key or FIREBASE_API_KEY!');
      }
    }
  }

  function initFCM() {
    if (typeof firebase === 'undefined' || !firebase.messaging) {
      setTimeout(initFCM, 1000);
      return;
    }

    let targetProjectId = firebaseConfig.projectId || "calseva-2026";
    if (!targetProjectId || targetProjectId.includes("gen-lang-client")) {
      targetProjectId = "calseva-2026";
    }

    if (!firebase.apps.length) {
      const configToUse = {
        apiKey: firebaseConfig.apiKey || "AIzaSy_calseva_public_web_key",
        authDomain: firebaseConfig.authDomain || "calseva-2026.firebaseapp.com",
        projectId: targetProjectId,
        messagingSenderId: firebaseConfig.messagingSenderId || "104417696551",
        appId: firebaseConfig.appId || "1:104417696551:web:calseva"
      };
      firebase.initializeApp(configToUse);
    } else {
      const app = firebase.apps[0];
      app.options.projectId = targetProjectId;
      if (!app.options.messagingSenderId) {
        app.options.messagingSenderId = firebaseConfig.messagingSenderId || "104417696551";
      }
    }

    try {
      const messaging = firebase.messaging();
      window.calsevaMessaging = messaging;

      if (Notification.permission === 'granted') {
        obtainAndSendToken(messaging, false);
      } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then((permission) => {
          if (permission === 'granted') {
            obtainAndSendToken(messaging, false);
          }
        });
      }

      messaging.onMessage((payload) => {
        console.log('[CalSEVA FCM] Foreground Message received:', payload);
        const notification = payload.notification || {};
        const title = notification.title || 'CalSEVA Alert';
        const body = notification.body || '';
        const icon = notification.icon || '/caliprofile-pages/Calsevalogo.png';
        const image = notification.image || null;
        const clickUrl = (payload.data && payload.data.url) || '/home/home.html';

        if (navigator.serviceWorker && navigator.serviceWorker.ready) {
          navigator.serviceWorker.ready.then((registration) => {
            registration.showNotification(title, {
              body: body,
              icon: icon,
              badge: icon,
              image: image,
              vibrate: [200, 100, 200],
              data: { url: clickUrl }
            });
          }).catch(() => {});
        }

        showRichSystemToast(title, body, icon, image, clickUrl);
      });

    } catch (fcmErr) {
      console.error('[CalSEVA FCM] Initialization error:', fcmErr);
    }
  }

  // Global manual trigger to force-sync FCM Token with full visual step alerts
  window.syncFcmDeviceToken = function() {
    if (typeof firebase === 'undefined' || !firebase.messaging) {
      alert('⚙️ Initializing Firebase Messaging SDK... Please tap again in 2 seconds.');
      initFCM();
      return;
    }

    const messaging = firebase.messaging();
    Notification.requestPermission().then((perm) => {
      if (perm === 'granted') {
        obtainAndSendToken(messaging, true);
      } else {
        alert('❌ Notification permission is DENIED or BLOCKED in Chrome settings.\n\nPlease tap Lock Icon (🔒) in Chrome address bar -> Site settings -> Notifications -> Allow.');
      }
    });
  };

  // Display Android Native System Card (SMS / Play Store / Samsung Style)
  function showRichSystemToast(title, body, icon, image, url) {
    const existing = document.getElementById('calsevaRichToast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'calsevaRichToast';
    
    let imageMarkup = '';
    if (image) {
      imageMarkup = `<img src="${image}" style="width: 50px; height: 50px; border-radius: 10px; object-fit: cover; margin-left: 10px;">`;
    }

    toast.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
        <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
          <img src="${icon}" alt="App Icon" style="width: 40px; height: 40px; border-radius: 12px; object-fit: cover; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
          <div style="flex: 1; text-align: left; overflow: hidden;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
              <h4 style="margin: 0; font-size: 14px; font-weight: 700; color: #FFFFFF; letter-spacing: -0.2px;">${title}</h4>
              <span style="font-size: 11px; color: rgba(255,255,255,0.6); margin-left: 8px;">Just now</span>
            </div>
            <p style="margin: 3px 0 0 0; font-size: 13px; color: rgba(255,255,255,0.85); line-height: 1.35; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${body}</p>
          </div>
        </div>
        ${imageMarkup}
        <button id="closeRichToast" style="background: none; border: none; color: rgba(255,255,255,0.7); font-size: 18px; cursor: pointer; padding: 0 0 0 10px; line-height: 1;">&times;</button>
      </div>
    `;

    Object.assign(toast.style, {
      position: 'fixed',
      top: '16px',
      left: '50%',
      transform: 'translateX(-50%)',
      zIndex: '999999',
      backgroundColor: 'rgba(30, 46, 53, 0.96)',
      backdropFilter: 'blur(16px)',
      webkitBackdropFilter: 'blur(16px)',
      color: '#FFFFFF',
      borderRadius: '24px',
      padding: '14px 18px',
      boxShadow: '0 12px 36px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.12)',
      width: 'calc(100% - 32px)',
      maxWidth: '420px',
      fontFamily: "'Outfit', 'Commissioner', sans-serif",
      cursor: 'pointer',
      transition: 'all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
    });

    toast.addEventListener('click', (e) => {
      if (e.target.id === 'closeRichToast') {
        e.stopPropagation();
        toast.remove();
      } else {
        window.location.href = url;
      }
    });

    document.body.appendChild(toast);

    setTimeout(() => {
      if (toast.parentNode) toast.remove();
    }, 7000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFCM);
  } else {
    initFCM();
  }
})();
