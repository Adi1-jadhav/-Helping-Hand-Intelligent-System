// ✅ Show a toast message on successful form submission
function showToast(message, type = 'success') {
  const toastEl = document.createElement('div');
  toastEl.className = `alert alert-${type} alert-dismissible fade show`;
  toastEl.role = 'alert';
  toastEl.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  document.body.prepend(toastEl);
  setTimeout(() => toastEl.remove(), 4000);
}

// ✅ Confirm before submitting donation
document.addEventListener('DOMContentLoaded', () => {
  const donationForm = document.querySelector('form[action*="donate"]');
  if (donationForm) {
    donationForm.addEventListener('submit', (e) => {
      if (!confirm('Are you sure you want to donate this item?')) {
        e.preventDefault();
      }
    });
  }

  // ✅ Highlight selected category if result is shown
  const predictionEl = document.querySelector('.prediction-result');
  if (predictionEl) {
    predictionEl.style.transition = 'transform 0.4s ease';
    predictionEl.style.transform = 'scale(1.2)';
    setTimeout(() => {
      predictionEl.style.transform = 'scale(1)';
    }, 1200);
  }

  // ✅ Feedback form validation
  const feedbackForm = document.querySelector('form[action*="feedback"]');
  if (feedbackForm) {
    feedbackForm.addEventListener('submit', (e) => {
      const feedbackText = feedbackForm.querySelector('textarea[name="feedback"]');
      if (feedbackText.value.trim().length < 10) {
        e.preventDefault();
        showToast('Please enter at least 10 characters of feedback.', 'warning');
      }
    });
  }
});
