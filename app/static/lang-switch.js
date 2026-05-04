document.querySelectorAll('.lang-btn').forEach(btn => {
  btn.addEventListener('click', e => {
    e.preventDefault();
    document.cookie = `lang=${btn.dataset.lang};path=/;max-age=31536000;samesite=lax`;
    location.reload();
  });
});
