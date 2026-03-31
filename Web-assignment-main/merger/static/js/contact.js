// Contact Form Enhancement
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('contactForm');
    const inputs = form.querySelectorAll('.form-control');

    // Add floating label effect
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', () => {
            if (!input.value) {
                input.parentElement.classList.remove('focused');
            }
        });
    });

    // Form submission animation
    form.addEventListener('submit', (e) => {
        const submitBtn = form.querySelector('.submit-btn');
        submitBtn.innerHTML = '<span>Sending...</span><span class="btn-icon">⏳</span>';
        submitBtn.disabled = true;
    });

    // Smooth scroll to messages
    const messages = document.querySelector('.messages');
    if (messages) {
        messages.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});
