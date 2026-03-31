document.addEventListener('DOMContentLoaded', () => {
const dropdown = document.querySelector('.dropdown');
const dropdownTrigger = document.querySelector('.dropdown-trigger');
const dropdownMenu = document.querySelector('.dropdown-menu');
const userDropdown = document.querySelector('.user-dropdown');
const userTrigger = document.querySelector('.user-trigger');
const userMenu = document.querySelectorAll('.user-dropdown .dropdown-menu')[0];

let timeout;

// Activities dropdown logic (hover remains)
dropdown.addEventListener('mouseenter', () => {
    clearTimeout(timeout);
    dropdownMenu.style.display = 'block';
    dropdownMenu.style.opacity = '1';
    dropdownTrigger.classList.add('hovered');
});

dropdown.addEventListener('mouseleave', () => {
    timeout = setTimeout(() => {
        if (!dropdownMenu.matches(':hover')) {
            dropdownMenu.style.opacity = '0';
            setTimeout(() => {
                dropdownMenu.style.display = 'none';
                dropdownTrigger.classList.remove('hovered');
            }, 300);
        }
    }, 1000);
});

dropdownMenu.addEventListener('mouseenter', () => {
    clearTimeout(timeout);
    dropdownMenu.style.opacity = '1';
    dropdownTrigger.classList.add('hovered');
});

dropdownMenu.addEventListener('mouseleave', () => {
    timeout = setTimeout(() => {
        if (!dropdown.matches(':hover') && !dropdownMenu.matches(':hover')) {
            dropdownMenu.style.opacity = '0';
            setTimeout(() => {
                dropdownMenu.style.display = 'none';
                dropdownTrigger.classList.remove('hovered');
            }, 300);
        }
    }, 1000);
});

// User dropdown logic (click-based)
let isUserMenuOpen = false;

userTrigger.addEventListener('click', (e) => {
    e.preventDefault();
    isUserMenuOpen = !isUserMenuOpen;
    userMenu.style.display = isUserMenuOpen ? 'block' : 'none';
    userMenu.style.opacity = isUserMenuOpen ? '1' : '0';
    userTrigger.classList.toggle('hovered', isUserMenuOpen);
    if (isUserMenuOpen) {
        document.addEventListener('click', closeUserMenuOutside);
    } else {
        document.removeEventListener('click', closeUserMenuOutside);
    }
});

function closeUserMenuOutside(e) {
    if (!userDropdown.contains(e.target)) {
        isUserMenuOpen = false;
        userMenu.style.opacity = '0';
        setTimeout(() => {
            userMenu.style.display = 'none';
            userTrigger.classList.remove('hovered');
        }, 300);
        document.removeEventListener('click', closeUserMenuOutside);
    }
}
});

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
});
