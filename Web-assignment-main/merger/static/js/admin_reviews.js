let currentForm = null; // holds the form that will be submitted on confirm

(function () {
  function openDialog(form, reviewInfo) {
    currentForm = form;
    const overlay = document.getElementById('dialogOverlay');
    const title = overlay.querySelector('.dialog-title');
    const message = overlay.querySelector('.dialog-message');

    // Change the text for review deletion
    title.textContent = "Delete Review";
    message.innerHTML = `Are you sure you want to delete the review from <strong>${reviewInfo}</strong>? This action cannot be undone.`;

    overlay.classList.add('active');
  }

  function closeDialog() {
    const overlay = document.getElementById('dialogOverlay');
    overlay.classList.remove('active');
    currentForm = null;
  }

  function confirmDelete() {
    if (currentForm) currentForm.submit();
    closeDialog();
  }

  document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-btn');

    // handle delete button clicks
    deleteButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const form = btn.closest('form');
        const row = btn.closest('tr');
        const customer = row.querySelector('.customer-name')?.textContent.trim() || 'this customer';
        openDialog(form, customer);
      });
    });

    // global functions for dialog buttons
    window.closeDialog = closeDialog;
    window.confirmDelete = confirmDelete;
  });
})();
