// static/js/countdown.js

(function() {
  // Ensure finishTime is defined (in seconds since epoch)
  if (typeof window.finishTime === 'undefined') {
    console.error('finishTime is not defined.');
    return;
  }

  // Grab countdown element; exit if not present
  const countdownEl = document.getElementById('countdown');
  if (!countdownEl) return;

  // Convert finishTime from seconds to milliseconds
  const targetTime = window.finishTime * 1000;

  function updateCountdown() {
    const now = Date.now();
    const distance = targetTime - now;

    if (distance <= 0) {
      countdownEl.textContent = '00:00:00';
      clearInterval(intervalId);
      return;
    }

    // Compute days, hours, minutes, seconds
    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance / (1000 * 60 * 60)) % 24);
    const minutes = Math.floor((distance / (1000 * 60)) % 60);
    const seconds = Math.floor((distance / 1000) % 60);

    // Pad H/M/S to 2 digits
    const hh = String(hours).padStart(2, '0');
    const mm = String(minutes).padStart(2, '0');
    const ss = String(seconds).padStart(2, '0');

    // If there are full days left, show “x Days ” prefix
    const dayPrefix = days > 0 ? `${days} Day${days > 1 ? 's' : ''} ` : '';

    countdownEl.textContent = `${dayPrefix}${hh}:${mm}:${ss}`;
  }

  // Initial call + interval setup
  updateCountdown();
  const intervalId = setInterval(updateCountdown, 1000);
})();
