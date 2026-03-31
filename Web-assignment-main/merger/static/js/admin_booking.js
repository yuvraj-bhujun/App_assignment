let currentForm = null;
let currentBookingId = null;

function showCancelDialog(bookingId, button) {
    currentForm = button.closest('form');
    currentBookingId = bookingId;
    document.getElementById('bookingIdText').textContent = bookingId;
    document.getElementById('dialogOverlay').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeDialog() {
    document.getElementById('dialogOverlay').classList.remove('active');
    document.body.style.overflow = 'auto';
    currentForm = null;
    currentBookingId = null;
}

function confirmCancel() {
    if (currentForm && currentBookingId) {
        // Find the table row for this booking
        const row = document.querySelector(`tr[data-booking-id="${currentBookingId}"]`);
        
        // Submit the form
        currentForm.submit();
        
        // If you want to hide the cancel button immediately (before page reload)
        // Uncomment the following lines:
        /*
        if (row) {
            const cancelCell = row.querySelector('.cancel-cell');
            if (cancelCell) {
                cancelCell.innerHTML = '<span style="color: #ccc;">—</span>';
            }
            
            // Update status badge
            const statusBadge = row.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.textContent = 'Cancelled';
                statusBadge.className = 'status-badge cancelled';
            }
        }
        */
    }
    closeDialog();
}

// Close dialog with ESC key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeDialog();
});