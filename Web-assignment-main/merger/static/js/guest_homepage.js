// guest_homepage.js
// Handles guest user interactions like booking button clicks

document.addEventListener('DOMContentLoaded', function() {
    // Get modal element
    const modal = document.getElementById('loginModal');
    const closeBtn = document.querySelector('.close');
    
    // Get all book activity buttons
    const bookButtons = document.querySelectorAll('.book-activity-btn');
    
    // Add click event listeners to all book buttons
    bookButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            openLoginModal();
        });
    });
    
    // Close modal when X is clicked
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            closeLoginModal();
        });
    }
    
    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeLoginModal();
        }
    });
});

// Open login modal
function openLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

// Close login modal
function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.style.display = 'none';
    }
}