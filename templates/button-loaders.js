document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');
  const otpForm = document.getElementById('otpForm');

  function setButtonLoading(button, text) {
    button.disabled = true;
    button.style.opacity = '0.7';
    button.style.cursor = 'not-allowed';
    button.innerHTML = `<span class="spinner-inline"></span> ${text}`;
  }

  // Inject CSS for inline spinner
  const style = document.createElement('style');
  style.textContent = `
    .spinner-inline {
      display: inline-block;
      width: 14px;
      height: 14px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: #ffffff;
      border-radius: 50%;
      margin-right: 8px;
      animation: spin-inline 0.8s linear infinite;
      vertical-align: middle;
    }
    @keyframes spin-inline {
      to { transform: rotate(360deg); }
    }
  `;
  document.head.appendChild(style);

  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      const btn = loginForm.querySelector('.btn-login');
      if (btn) setButtonLoading(btn, 'Authenticating...');
    });
  }
  if (signupForm) {
    signupForm.addEventListener('submit', (e) => {
      const btn = signupForm.querySelector('.btn-login');
      if (btn) setButtonLoading(btn, 'Creating Account...');
    });
  }
  if (otpForm) {
    otpForm.addEventListener('submit', (e) => {
      const btn = otpForm.querySelector('.btn-submit');
      if (btn) setButtonLoading(btn, 'Verifying...');
    });
  }

  // Handle flash messages automatic fade out/slide up after 3.5s
  const flash = document.querySelector('.flash-message');
  if (flash) {
    flash.style.transition = 'opacity 0.4s ease, transform 0.4s ease, margin 0.4s ease, padding 0.4s ease, height 0.4s ease';
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateY(-20px)';
      setTimeout(() => {
        flash.style.display = 'none';
      }, 400);
    }, 3500);
  }
});
