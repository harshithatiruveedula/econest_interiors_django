// Mobile nav toggle ONLY
document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('siteNav');

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
  }
});
