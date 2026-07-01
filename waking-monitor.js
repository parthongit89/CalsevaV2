(function() {
  // Create waking overlay element
  const overlay = document.createElement('div');
  overlay.id = 'serverWakingOverlay';
  overlay.innerHTML = `
    <div class="waking-content">
      <div class="waking-spinner"></div>
      <h3>Connecting to the server</h3>
      <p>Please wait, waking up cloud database...</p>
    </div>
  `;
  
  // Style overlay
  const style = document.createElement('style');
  style.textContent = `
    #serverWakingOverlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(30, 46, 53, 0.85);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      z-index: 999999;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-family: 'Outfit', 'Inter', sans-serif;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.4s ease;
    }
    #serverWakingOverlay.show {
      opacity: 1;
      pointer-events: auto;
    }
    .waking-content {
      text-align: center;
      padding: 30px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      max-width: 320px;
    }
    .waking-spinner {
      width: 40px;
      height: 40px;
      border: 3px solid rgba(255, 255, 255, 0.1);
      border-top-color: #3A606E;
      border-radius: 50%;
      margin: 0 auto 20px auto;
      animation: spin-waking 1s linear infinite;
    }
    #serverWakingOverlay h3 {
      font-size: 18px;
      margin: 0 0 8px 0;
      font-weight: 600;
      letter-spacing: 0.5px;
    }
    #serverWakingOverlay p {
      font-size: 13px;
      color: rgba(255, 255, 255, 0.7);
      margin: 0;
    }
    @keyframes spin-waking {
      to { transform: rotate(360deg); }
    }
  `;
  document.head.appendChild(style);
  if (document.body) {
    document.body.appendChild(overlay);
  } else {
    document.addEventListener('DOMContentLoaded', () => {
      document.body.appendChild(overlay);
    });
  }

  let isServerConnected = false;
  let showTimer = setTimeout(() => {
    if (!isServerConnected) {
      overlay.classList.add('show');
    }
  }, 800); // Wait 800ms before showing overlay

  function checkServer() {
    fetch('/ping')
      .then(res => {
        if (res.ok) {
          isServerConnected = true;
          clearTimeout(showTimer);
          overlay.classList.remove('show');
        } else {
          setTimeout(checkServer, 2000);
        }
      })
      .catch(() => {
        setTimeout(checkServer, 2000);
      });
  }

  // Start ping check
  checkServer();
})();
