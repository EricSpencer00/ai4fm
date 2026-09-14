(() => {
  const carousel = document.querySelector('.hero-carousel.splide');

  if (!carousel || !window.Splide) {
    return;
  }

  const prefersReducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)',
  ).matches;

  new window.Splide(carousel, {
    type: 'fade',
    rewind: true,
    autoplay: !prefersReducedMotion,
    interval: 6500,
    speed: prefersReducedMotion ? 0 : 700,
    rewindSpeed: prefersReducedMotion ? 0 : 700,
    arrows: false,
    pagination: false,
    keyboard: false,
    drag: false,
    live: false,
  }).mount();
})();
