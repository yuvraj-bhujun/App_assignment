// Review button handler
document.querySelectorAll('.btn-review').forEach(button => {
  button.addEventListener('click', () => {
    const bookingId = button.closest('tr').querySelector('.booking-id').textContent;
    window.location.href = `review.html?booking_id=${bookingId}`;
  });
});

// Cancel booking modal logic
(function () {
  const modal = document.getElementById('confirmModal');
  const confirmYes = document.getElementById('confirmYes');
  const confirmNo = document.getElementById('confirmNo');
  const overlay = modal.querySelector('.confirm-modal__overlay');

  let targetRow = null; // row to cancel
  let bookingId = null; // booking ID to cancel

  // Open modal when any .btn-cancel INSIDE THE TABLE is clicked
  document.querySelectorAll('.bookings-table .btn-cancel').forEach(btn => {
    btn.addEventListener('click', (e) => {
      console.log('Cancel button clicked');
      // find the row containing the clicked button
      targetRow = btn.closest('tr');
      // Extract booking ID from the row
      const bookingIdText = targetRow.querySelector('.booking-id').textContent.trim();
      bookingId = bookingIdText.replace('B_', ''); // Remove 'B_' prefix
      console.log('Booking ID:', bookingId);
      // show modal
      modal.setAttribute('aria-hidden', 'false');
    });
  });

  // Close helper
  function closeModal() {
    modal.setAttribute('aria-hidden', 'true');
    targetRow = null;
    bookingId = null;
  }

  // No / overlay close
  confirmNo.addEventListener('click', closeModal);
  overlay.addEventListener('click', closeModal);

  // ESC closes modal
  window.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape' && modal.getAttribute('aria-hidden') === 'false') {
      closeModal();
    }
  });

  // Yes -> perform cancellation via backend
  confirmYes.addEventListener('click', () => {
    console.log('Yes button clicked');
    console.log('Target row:', targetRow);
    console.log('Booking ID:', bookingId);

    if (!targetRow || !bookingId) {
      console.error('No target row or booking ID');
      closeModal();
      return;
    }

    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
      getCookie('csrftoken');

    console.log('CSRF Token:', csrfToken);

    const url = `/grandblue/user/booking/cancel/${bookingId}/`;
    console.log('Fetch URL:', url);

    // Make POST request to cancel booking
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      credentials: 'same-origin'
    })
      .then(response => {
        console.log('Response status:', response.status);
        console.log('Response OK:', response.ok);

        if (response.ok) {
          console.log('Booking cancelled successfully');
          // Update UI: status badge
          const statusCell = targetRow.querySelector('td:nth-child(4)');
          if (statusCell) {
            statusCell.innerHTML = '<span class="status-badge status-cancelled">Cancelled</span>';
          }

          // Update UI: remove actions (replace with dash)
          const actionCell = targetRow.querySelector('td:nth-child(5)');
          if (actionCell) {
            actionCell.innerHTML = '<span class="no-action">-</span>';
          }

          // Update data attribute for filtering
          targetRow.setAttribute('data-status', 'cancelled');

          // Close modal
          closeModal();

          // Reload page to show success message
          setTimeout(() => {
            window.location.reload();
          }, 500);
        } else {
          console.error('Failed to cancel booking. Status:', response.status);
          response.text().then(text => console.error('Response text:', text));
          alert('Failed to cancel booking. Please try again.');
          closeModal();
        }
      })
      .catch(err => {
        console.error('Error cancelling booking:', err);
        alert('Network error. Please try again.');
        closeModal();
      });
  });

  // Helper function to get CSRF token from cookies
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
})();
