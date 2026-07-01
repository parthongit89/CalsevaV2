(function() {
  const isDark = localStorage.getItem('calseva_dark_mode') === 'true';
  
  const style = document.createElement('style');
  style.id = 'calsevaGlobalThemeStyle';
  style.textContent = `
    :root.dark-mode {
      --color-bg-card: #1F2023 !important;
      --color-card-inner: #2A2B2E !important;
      --color-text-dark: #E8EAED !important;
      --color-text-light: #9AA0A6 !important;
      --color-border: rgba(255, 255, 255, 0.08) !important;
      --color-bg-body: #1E2E35 !important;
    }
    :root.dark-mode #deviceContainer {
      background-color: #1F2023 !important;
    }
  `;
  document.head.appendChild(style);
  
  if (isDark) {
    document.documentElement.classList.add('dark-mode');
  }
})();
