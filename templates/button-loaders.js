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

  // Dynamic Client-side Flash Message
  function showClientFlash(message) {
    let flash = document.querySelector('.flash-message');
    if (flash) {
      flash.remove();
    }
    
    flash = document.createElement('div');
    flash.className = 'flash-message';
    flash.innerHTML = `
      <span class="material-symbols-outlined" style="font-size: 16px;">info</span>
      <span>${message}</span>
    `;
    
    const container = document.querySelector('.device-container') || document.querySelector('.device-container-signup');
    const header = document.querySelector('.header-section');
    if (container && header) {
      container.insertBefore(flash, header.nextSibling);
      
      // Trigger error shake animation immediately
      container.classList.remove('error-shake');
      void container.offsetWidth; // force reflow
      container.classList.add('error-shake');
      setTimeout(() => {
        container.classList.remove('error-shake');
      }, 400);
    }
    
    // Auto fade-out after 3.5s
    flash.style.transition = 'opacity 0.4s ease, transform 0.4s ease, margin 0.4s ease';
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateY(-20px)';
      setTimeout(() => {
        flash.remove();
      }, 400);
    }, 3500);
  }

  function isValidPassword(password) {
    if (password.length < 8) return false;
    const hasLetter = /[A-Za-z]/.test(password);
    const hasDigit = /\d/.test(password);
    const hasSpecial = /[@$!%*#?&_#@!%^&*()\-+=]/.test(password);
    return hasLetter && hasDigit && hasSpecial;
  }

  // 1. Login Validations
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      const employeeId = document.getElementById('employeeId').value.trim();
      const password = document.getElementById('password').value.trim();
      
      if (!employeeId || !password) {
        e.preventDefault();
        showClientFlash("Invalid Credentials");
        return;
      }
      if (!/^\d{5}$/.test(employeeId)) {
        e.preventDefault();
        showClientFlash("Invalid Username Please Signup");
        return;
      }
      if (!isValidPassword(password)) {
        e.preventDefault();
        showClientFlash("Invalid Password Please Signup");
        return;
      }
      
      const btn = loginForm.querySelector('.btn-login');
      if (btn) setButtonLoading(btn, 'Authenticating...');
    });
  }

  // 2. Signup Validations
  if (signupForm) {
    signupForm.addEventListener('submit', (e) => {
      const employeeId = document.getElementById('employeeId').value.trim();
      const email = document.getElementById('email').value.trim();
      const phone = document.getElementById('phone').value.trim();
      const password = document.getElementById('password').value.trim();
      
      if (!employeeId || !email || !phone || !password) {
        e.preventDefault();
        showClientFlash("Invalid Credentials");
        return;
      }
      if (!/^\d{5}$/.test(employeeId)) {
        e.preventDefault();
        showClientFlash("Employee ID must be exactly 5 digits");
        return;
      }
      if (!/^\d{10}$/.test(phone)) {
        e.preventDefault();
        showClientFlash("Phone no must be written in 10 digits");
        return;
      }
      if (!email.toLowerCase().endsWith('@gmail.com')) {
        e.preventDefault();
        showClientFlash("Email must be email format mostly as @gmail.com");
        return;
      }
      if (!isValidPassword(password)) {
        e.preventDefault();
        showClientFlash("Password must contain at least 8 alphanumeric characters and special symbols");
        return;
      }
      
      const btn = signupForm.querySelector('.btn-login');
      if (btn) setButtonLoading(btn, 'Creating Account...');
    });
  }

  // 3. Verification OTP Validations
  if (otpForm) {
    otpForm.addEventListener('submit', (e) => {
      const digit1 = document.getElementsByName('digit1')[0].value.trim();
      const digit2 = document.getElementsByName('digit2')[0].value.trim();
      const digit3 = document.getElementsByName('digit3')[0].value.trim();
      const digit4 = document.getElementsByName('digit4')[0].value.trim();
      const digit5 = document.getElementsByName('digit5')[0].value.trim();
      const digit6 = document.getElementsByName('digit6')[0].value.trim();
      
      const otp = digit1 + digit2 + digit3 + digit4 + digit5 + digit6;
      if (otp.length !== 6 || !/^\d{6}$/.test(otp)) {
        e.preventDefault();
        showClientFlash("Please enter a valid 6-digit OTP code");
        return;
      }
      
      const btn = otpForm.querySelector('.btn-submit');
      if (btn) setButtonLoading(btn, 'Verifying...');
    });
  }

  // Handle server-flashed messages (fade out after 3.5s)
  const flash = document.querySelector('.flash-message');
  if (flash) {
    flash.style.transition = 'opacity 0.4s ease, transform 0.4s ease, margin 0.4s ease';
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateY(-20px)';
      setTimeout(() => {
        flash.remove();
      }, 400);
    }, 3500);
  }
});
