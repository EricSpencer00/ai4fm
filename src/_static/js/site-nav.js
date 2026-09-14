(() => {
  const header = document.querySelector('.site-header');
  const toggle = header?.querySelector('.nav-toggle');

  if (!header || !toggle) {
    return;
  }

  const navigation = document.getElementById(toggle.getAttribute('aria-controls'));
  const label = toggle.querySelector('.nav-toggle-label');

  if (!navigation || !label) {
    return;
  }

  const close = () => {
    header.classList.remove('nav-open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation');
    label.textContent = 'Menu';
  };

  toggle.addEventListener('click', () => {
    const isOpen = header.classList.toggle('nav-open');
    toggle.setAttribute('aria-expanded', String(isOpen));
    toggle.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
    label.textContent = isOpen ? 'Close' : 'Menu';
  });

  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) {
      close();
    }
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 720) {
      close();
    }
  });
})();
