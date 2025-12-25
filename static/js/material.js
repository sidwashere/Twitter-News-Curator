// Twitter News Curator - Material UI JavaScript Enhancements
// Ripple effects, interactions, and Material-style behaviors

// Ripple Effect on Buttons
function createRipple(event) {
    const button = event.currentTarget;

    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;

    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
    circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
    circle.classList.add('ripple-effect');

    const ripple = button.getElementsByClassName('ripple-effect')[0];
    if (ripple) {
        ripple.remove();
    }

    button.appendChild(circle);
}

// Add ripple to all buttons
document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.btn, .filter-chip, .generate-tweet-btn');
    buttons.forEach(button => {
        button.addEventListener('click', createRipple);
    });
});

// Smooth scroll with offset for navbar
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const navHeight = document.querySelector('.navbar').offsetHeight;
            const targetPosition = target.offsetTop - navHeight - 20;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Intersection Observer for Scroll Animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function (entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
        }
    });
}, observerOptions);

// Observe elements for scroll animations
document.querySelectorAll('.stat-card, .article-card, .setting-section').forEach(el => {
    observer.observe(el);
});

// Enhanced Slider Value Display
document.querySelectorAll('.control-slider').forEach(slider => {
    slider.addEventListener('input', function () {
        const value = this.value;
        const min = this.min || 0;
        const max = this.max || 100;
        const percentage = ((value - min) / (max - min)) * 100;

        // Update background gradient
        this.style.background = `linear-gradient(to right, 
            var(--accent-primary) 0%, 
            var(--accent-primary) ${percentage}%, 
            var(--bg-card) ${percentage}%, 
            var(--bg-card) 100%)`;
    });

    // Trigger initial update
    slider.dispatchEvent(new Event('input'));
});

// Material-style Input Focus
document.querySelectorAll('.control-input, .control-select, textarea').forEach(input => {
    input.addEventListener('focus', function () {
        this.parentElement.classList.add('input-focused');
    });

    input.addEventListener('blur', function () {
        this.parentElement.classList.remove('input-focused');
    });
});

// Topic Filter Functionality
document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', function () {
        const topic = this.dataset.topic;

        // Update active state
        document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        this.classList.add('active');

        // Filter articles
        const articles = document.querySelectorAll('.article-card');
        articles.forEach(article => {
            if (topic === 'all') {
                article.classList.remove('hidden');
                return;
            }

            const title = article.querySelector('.article-title').textContent.toLowerCase();
            const summary = article.querySelector('.article-summary').textContent.toLowerCase();
            const content = title + ' ' + summary;

            // Simple keyword matching
            const keywords = {
                'ai': ['artificial intelligence', 'ai ', 'machine learning', 'neural', 'deep learning'],
                'ml': ['machine learning', 'ml ', 'algorithm', 'model', 'training'],
                'blockchain': ['blockchain', 'crypto', 'bitcoin', 'ethereum', 'web3'],
                'hardware': ['chip', 'processor', 'gpu', 'hardware', 'semiconductor'],
                'software': ['software', 'app', 'development', 'code', 'programming'],
                'security': ['security', 'hack', 'breach', 'vulnerability', 'cyber'],
                'startups': ['startup', 'founder', 'funding', 'venture', 'investment'],
                'research': ['research', 'study', 'paper', 'discovery', 'breakthrough']
            };

            const matchesFilter = keywords[topic]?.some(keyword => content.includes(keyword));

            if (matchesFilter) {
                article.classList.remove('hidden');
            } else {
                article.classList.add('hidden');
            }
        });
    });
});

// Enhanced Toast with Auto-dismiss
window.showToast = function (message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    // Add icon based on type
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
        </div>
    `;

    container.appendChild(toast);

    // Auto-dismiss
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);

    // Click to dismiss
    toast.addEventListener('click', () => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => toast.remove(), 300);
    });
};

// Loading State Helper
function setLoadingState(element, loading) {
    if (loading) {
        element.classList.add('loading');
        element.setAttribute('disabled', 'disabled');
    } else {
        element.classList.remove('loading');
        element.removeAttribute('disabled');
    }
}

// Make it available globally
window.setLoadingState = setLoadingState;

// Card Hover Effects with 3D Tilt (subtle)
document.querySelectorAll('.article-card, .stat-card').forEach(card => {
    card.addEventListener('mousemove', function (e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;

        this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
    });

    card.addEventListener('mouseleave', function () {
        this.style.transform = '';
    });
});

// Progress Bar Animation
function animateProgress(element, targetWidth, duration = 1000) {
    let start = null;
    const startWidth = parseFloat(element.style.width) || 0;

    function step(timestamp) {
        if (!start) start = timestamp;
        const progress = timestamp - start;
        const percentage = Math.min((progress / duration) * (targetWidth - startWidth) + startWidth, targetWidth);

        element.style.width = percentage + '%';

        if (progress < duration) {
            window.requestAnimationFrame(step);
        }
    }

    window.requestAnimationFrame(step);
}

// Make it available globally
window.animateProgress = animateProgress;

// Form Validation with Material Feedback
document.querySelectorAll('input[required], textarea[required]').forEach(input => {
    input.addEventListener('invalid', function (e) {
        e.preventDefault();
        this.classList.add('input-error');

        let errorMessage = this.validationMessage;
        const errorEl = document.createElement('span');
        errorEl.className = 'input-error-message';
        errorEl.textContent = errorMessage;

        // Remove existing error message
        const existingError = this.parentElement.querySelector('.input-error-message');
        if (existingError) {
            existingError.remove();
        }

        this.parentElement.appendChild(errorEl);
    });

    input.addEventListener('input', function () {
        this.classList.remove('input-error');
        const errorEl = this.parentElement.querySelector('.input-error-message');
        if (errorEl) {
            errorEl.remove();
        }
    });
});

// Keyboard Navigation Enhancement
document.addEventListener('keydown', function (e) {
    // Escape to close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    // Ctrl/Cmd + K for quick search (future enhancement)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // Focus on search if it exists
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
});

// Add CSS for ripple effect dynamically
const style = document.createElement('style');
style.textContent = `
    .ripple-effect {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .animate-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    .input-error {
        border-color: var(--accent-error) !important;
        box-shadow: 0 0 0 3px rgba(248, 81, 73, 0.1) !important;
    }
    
    .input-error-message {
        color: var(--accent-error);
        font-size: 0.85rem;
        margin-top: 0.25rem;
        display: block;
        animation: slideInRight 0.3s ease-out;
    }
    
    .toast {
        cursor: pointer;
        user-select: none;
    }
    
    .toast-content {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .toast-icon {
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .hidden {
        display: none !important;
    }
`;
document.head.appendChild(style);

console.log('✨ Material UI enhancements loaded');
