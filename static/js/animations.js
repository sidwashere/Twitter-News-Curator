// Global Animations System
// Using GSAP and AOS for smooth, production-grade animations

document.addEventListener('DOMContentLoaded', function () {
    console.log('🎬 Animations initialized');

    // Register GSAP plugins
    gsap.registerPlugin(ScrollTrigger);

    // Initialize AOS (Animate On Scroll)
    AOS.init({
        duration: 800,
        easing: 'ease-out-cubic',
        once: false,
        offset: 120,
        delay: 100,
        disable: 'mobile' // Optionally disable on mobile for performance
    });

    // ==================== PAGE LOAD ANIMATIONS ====================

    // Fade in page header
    gsap.from('.page-header', {
        opacity: 0,
        y: -30,
        duration: 0.8,
        ease: 'power3.out',
        delay: 0.1
    });

    // Stagger in stat cards/metric cards
    gsap.from('.metric-card, .stat-card', {
        opacity: 0,
        y: 40,
        scale: 0.95,
        duration: 0.6,
        stagger: 0.1,
        ease: 'back.out(1.2)',
        delay: 0.3,
        clearProps: 'all'
    });

    // Animate stats grid
    gsap.from('.stats-grid > *', {
        opacity: 0,
        y: 30,
        duration: 0.6,
        stagger: 0.12,
        ease: 'power2.out',
        delay: 0.4,
        clearProps: 'all'
    });

    // Animate article cards
    gsap.from('.article-card', {
        opacity: 0,
        y: 40,
        duration: 0.5,
        stagger: 0.08,
        ease: 'power2.out',
        delay: 0.5,
        clearProps: 'all'
    });

    // Animate activity items
    gsap.from('.activity-item', {
        opacity: 0,
        x: -30,
        duration: 0.5,
        stagger: 0.1,
        ease: 'power2.out',
        delay: 0.6,
        clearProps: 'all'
    });

    // ==================== HOVER ANIMATIONS ====================

    // Enhanced card hover effects
    document.querySelectorAll('.glass-card, .metric-card, .article-card').forEach(card => {
        card.addEventListener('mouseenter', function () {
            gsap.to(this, {
                scale: 1.02,
                y: -4,
                duration: 0.3,
                ease: 'power2.out'
            });
        });

        card.addEventListener('mouseleave', function () {
            gsap.to(this, {
                scale: 1,
                y: 0,
                duration: 0.3,
                ease: 'power2.out'
            });
        });
    });

    // Button ripple effect on click
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');

            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';

            this.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);
        });
    });

    // ==================== SCROLL ANIMATIONS ====================

    // Parallax effect on large cards
    gsap.utils.toArray('.glass-card').forEach(card => {
        gsap.to(card, {
            y: -20,
            scrollTrigger: {
                trigger: card,
                start: 'top bottom',
                end: 'bottom top',
                scrub: 1
            }
        });
    });

    // Fade in sections as they appear
    gsap.utils.toArray('.setting-section, .section').forEach(section => {
        gsap.from(section, {
            opacity: 0,
            y: 50,
            duration: 0.8,
            scrollTrigger: {
                trigger: section,
                start: 'top 85%',
                end: 'top 50%',
                toggleActions: 'play none none reverse'
            }
        });
    });

    // ==================== FILTER CHIP ANIMATIONS ====================

    // Animate filter chips on click
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.addEventListener('click', function () {
            // Remove active from all
            document.querySelectorAll('.filter-chip').forEach(c => {
                gsap.to(c, {
                    scale: 1,
                    duration: 0.2
                });
            });

            // Animate active chip
            gsap.fromTo(this,
                { scale: 0.9 },
                {
                    scale: 1,
                    duration: 0.3,
                    ease: 'back.out(3)'
                }
            );
        });
    });

    // ==================== NAVBAR SCROLL EFFECT ====================

    // NOTE: Navbar scroll effect is now handled by navbar.js
    // This prevents conflicts with theme-specific styling

    // ==================== NUMBER COUNTER ANIMATION ====================

    // Animate numbers in metric cards
    document.querySelectorAll('.metric-value').forEach(metric => {
        const value = parseFloat(metric.textContent);

        if (!isNaN(value)) {
            ScrollTrigger.create({
                trigger: metric,
                start: 'top 80%',
                onEnter: () => {
                    gsap.from(metric, {
                        textContent: 0,
                        duration: 1.5,
                        ease: 'power1.out',
                        snap: { textContent: 1 },
                        onUpdate: function () {
                            metric.textContent = Math.ceil(this.targets()[0].textContent);
                        }
                    });
                }
            });
        }
    });

    // ==================== FORM INPUT ANIMATIONS ====================

    // Animate input focus
    document.querySelectorAll('.control-input, input, textarea').forEach(input => {
        input.addEventListener('focus', function () {
            gsap.to(this, {
                scale: 1.02,
                borderColor: 'var(--accent-primary)',
                duration: 0.3,
                ease: 'power2.out'
            });
        });

        input.addEventListener('blur', function () {
            gsap.to(this, {
                scale: 1,
                duration: 0.3,
                ease: 'power2.out'
            });
        });
    });

    // ==================== PROGRESS BAR ANIMATION ====================

    // Animate progress bars
    document.querySelectorAll('.progress-fill').forEach(bar => {
        const width = bar.style.width || '0%';
        bar.style.width = '0%';

        ScrollTrigger.create({
            trigger: bar,
            start: 'top 80%',
            onEnter: () => {
                gsap.to(bar, {
                    width: width,
                    duration: 1.5,
                    ease: 'power2.out'
                });
            }
        });
    });

    // ==================== MODAL ANIMATIONS ====================

    // Animate modals when they appear
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const observer = new MutationObserver(() => {
            if (modal.style.display === 'flex') {
                gsap.from(modal.querySelector('.modal-content'), {
                    scale: 0.8,
                    opacity: 0,
                    duration: 0.4,
                    ease: 'back.out(1.5)'
                });
            }
        });

        observer.observe(modal, {
            attributes: true,
            attributeFilter: ['style']
        });
    });

    // ==================== TOAST ANIMATION ENHANCEMENT ====================

    // Override toast function to add animations
    const originalShowToast = window.showToast;
    if (originalShowToast) {
        window.showToast = function (message, type) {
            originalShowToast(message, type);

            // Find the latest toast
            setTimeout(() => {
                const toasts = document.querySelectorAll('.toast');
                const latestToast = toasts[toasts.length - 1];

                if (latestToast) {
                    gsap.from(latestToast, {
                        x: 400,
                        opacity: 0,
                        duration: 0.5,
                        ease: 'back.out(1.5)'
                    });
                }
            }, 10);
        };
    }

    // ==================== PAGE TRANSITION ====================

    // Smooth page transitions for navigation
    document.querySelectorAll('a[href^="/"]').forEach(link => {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');

            // Skip for external links or # links
            if (!href || href === '#' || this.target === '_blank') return;

            e.preventDefault();

            // Fade out current page
            gsap.to('body', {
                opacity: 0,
                duration: 0.3,
                ease: 'power2.in',
                onComplete: () => {
                    window.location.href = href;
                }
            });
        });
    });

    // Fade in on page load
    gsap.to('body', {
        opacity: 1,
        duration: 0.4,
        ease: 'power2.out'
    });

    console.log('✨ All animations loaded successfully');
});

// ==================== RIPPLE EFFECT CSS (Dynamic Injection) ====================
const rippleStyles = document.createElement('style');
rippleStyles.textContent = `
    .ripple-effect {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        pointer-events: none;
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .btn {
        position: relative;
        overflow: hidden;
    }
`;
document.head.appendChild(rippleStyles);
