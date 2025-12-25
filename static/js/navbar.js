// Navbar JavaScript - Isolated and Efficient
(function () {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function () {
        console.log('🧭 Navbar module loaded');

        const navbar = document.querySelector('.navbar');
        if (!navbar) {
            console.warn('Navbar element not found');
            return;
        }

        // ==================== SCROLL HANDLER ====================
        let ticking = false;
        let lastScrollPosition = 0;

        function updateNavbarOnScroll() {
            const currentScroll = window.pageYOffset;

            if (currentScroll > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }

            lastScrollPosition = currentScroll;
            ticking = false;
        }

        // Throttled scroll event using requestAnimationFrame
        window.addEventListener('scroll', function () {
            if (!ticking) {
                window.requestAnimationFrame(updateNavbarOnScroll);
                ticking = true;
            }
        }, { passive: true });

        // ==================== ACTIVE LINK HIGHLIGHTING ====================
        function updateActiveLinks() {
            const currentPath = window.location.pathname;
            const navLinks = document.querySelectorAll('.nav-link');

            navLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href === currentPath) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }

        updateActiveLinks();

        // ==================== THEME TOGGLE ANIMATION ====================
        const themeToggle = document.getElementById('theme-toggle');

        if (themeToggle) {
            themeToggle.addEventListener('click', function () {
                // Add rotation animation
                this.style.transition = 'transform 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                this.style.transform = 'rotate(360deg)';

                setTimeout(() => {
                    this.style.transform = '';
                    setTimeout(() => {
                        this.style.transition = '';
                    }, 100);
                }, 600);
            });
        }

        // ==================== RIPPLE EFFECT ====================
        const navLinks = document.querySelectorAll('.nav-link');

        navLinks.forEach(link => {
            link.addEventListener('click', function (e) {
                // Create ripple element
                const ripple = document.createElement('span');
                ripple.className = 'nav-ripple';

                // Position ripple
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;

                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';

                this.appendChild(ripple);

                // Remove after animation
                setTimeout(() => ripple.remove(), 600);
            });
        });

        // ==================== KEYBOARD SHORTCUTS ====================
        document.addEventListener('keydown', function (e) {
            // Alt + Number for quick navigation
            if (e.altKey && !e.ctrlKey && !e.shiftKey) {
                const num = parseInt(e.key);
                if (num >= 1 && num <= navLinks.length) {
                    e.preventDefault();
                    navLinks[num - 1].click();
                }
            }
        });

        console.log('✅ Navbar initialized successfully');
    });

    // ==================== INJECTED STYLES ====================
    const rippleStyles = document.createElement('style');
    rippleStyles.id = 'navbar-ripple-styles';
    rippleStyles.textContent = `
        .nav-link {
            position: relative;
            overflow: hidden;
        }
        
        .nav-ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            pointer-events: none;
            transform: scale(0);
            animation: navbar-ripple 0.6s ease-out;
        }
        
        @keyframes navbar-ripple {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
    `;

    // Add styles only once
    if (!document.getElementById('navbar-ripple-styles')) {
        document.head.appendChild(rippleStyles);
    }
})();
