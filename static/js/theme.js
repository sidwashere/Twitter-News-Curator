// Theme Toggle Functionality
document.addEventListener('DOMContentLoaded', function () {
    // Remove preload class to enable transitions
    setTimeout(() => {
        document.body.classList.remove('preload');
    }, 100);

    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle?.querySelector('.theme-icon');
    const themeText = themeToggle?.querySelector('.theme-text');

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);

    // Theme toggle handler
    themeToggle?.addEventListener('click', function () {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeButton(newTheme);

        showToast(`Switched to ${newTheme} mode`, 'success');
    });

    function updateThemeButton(theme) {
        if (!themeIcon || !themeText) return;

        if (theme === 'light') {
            themeIcon.textContent = '☀️';
            themeText.textContent = 'Light';
        } else {
            themeIcon.textContent = '🌙';
            themeText.textContent = 'Dark';
        }
    }
});

console.log('✨ Theme toggle loaded');
