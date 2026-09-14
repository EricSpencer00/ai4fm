(() => {
  const carousel = document.querySelector('.hero-carousel');

  if (!carousel) {
    return;
  }

  const slides = Array.from(
    carousel.querySelectorAll('.hero-carousel__slide'),
  );

  if (slides.length < 2) {
    return;
  }

  const prefersReducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)',
  ).matches;
  let current = 0;
  let timer = null;

  const render = () => {
    const previous = (current - 1 + slides.length) % slides.length;
    const next = (current + 1) % slides.length;

    slides.forEach((slide, index) => {
      slide.classList.toggle('is-prev', index === previous);
      slide.classList.toggle('is-active', index === current);
      slide.classList.toggle('is-next', index === next);
      slide.classList.toggle(
        'is-hidden',
        index !== previous && index !== current && index !== next,
      );
    });
  };

  const stop = () => {
    if (timer) {
      window.clearInterval(timer);
      timer = null;
    }
  };

  const start = () => {
    if (prefersReducedMotion) {
      return;
    }
    stop();
    timer = window.setInterval(() => {
      current = (current + 1) % slides.length;
      render();
    }, 6500);
  };

  render();
  carousel.addEventListener('mouseenter', stop);
  carousel.addEventListener('mouseleave', start);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      stop();
    } else {
      start();
    }
  });
  start();
})();
