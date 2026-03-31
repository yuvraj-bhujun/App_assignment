document.addEventListener('DOMContentLoaded', () => {
    const messages = document.querySelectorAll('.flash-message');

    messages.forEach(msg => {
        // Auto-hide after 4 seconds
        setTimeout(() => {
            msg.style.transition = "opacity 0.5s, transform 0.5s";
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-20px)';
            setTimeout(() => msg.remove(), 500);
        }, 4000);

        // Click to dismiss
        msg.addEventListener('click', () => {
            msg.style.transition = "opacity 0.3s, transform 0.3s";
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-20px)';
            setTimeout(() => msg.remove(), 300);
        });
    });

    const djangoAdminBtn = document.getElementById('djangoAdminBtn');
    const djangoAdminModal = document.getElementById('djangoAdminModal');
    const confirmDjangoAdmin = document.getElementById('confirmDjangoAdmin');
    const cancelDjangoAdmin = document.getElementById('cancelDjangoAdmin');

    if (djangoAdminBtn && djangoAdminModal) {
        const openModal = () => {
            djangoAdminModal.style.display = 'flex';
        };

        const closeModal = () => {
            djangoAdminModal.style.display = 'none';
        };

        djangoAdminBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal();
        });

        if (cancelDjangoAdmin) {
            cancelDjangoAdmin.addEventListener('click', (e) => {
                e.preventDefault();
                closeModal();
            });
        }

        if (confirmDjangoAdmin) {
            confirmDjangoAdmin.addEventListener('click', (e) => {
                e.preventDefault();
                const adminUrl = djangoAdminBtn.getAttribute('data-admin-url') || '/admin/';
                window.location.href = adminUrl;
            });
        }

        // Click outside modal closes it
        djangoAdminModal.addEventListener('click', (e) => {
            if (e.target === djangoAdminModal) {
                closeModal();
            }
        });
    }
});
