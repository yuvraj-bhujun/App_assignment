document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('darkModeToggle');
    const html = document.documentElement;
    const iconMoon = document.getElementById('icon-moon');
    const iconSun = document.getElementById('icon-sun');

    // Check localStorage for preference
    const currentMode = localStorage.getItem('darkMode');

    function setIcon(isDark) {
        if (!iconMoon || !iconSun) return;
        if (isDark) {
            iconMoon.style.display = 'none';
            iconSun.style.display = 'inline';
        } else {
            iconMoon.style.display = 'inline';
            iconSun.style.display = 'none';
        }
    }

    if (currentMode === 'enabled') {
        html.classList.add('dark-mode');
        setIcon(true);
    } else {
        setIcon(false);
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const isDark = !html.classList.contains('dark-mode');
            html.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
            setIcon(isDark);
        });
    }
});
