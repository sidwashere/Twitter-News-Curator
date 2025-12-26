// Articles Page Enhanced JavaScript
document.addEventListener('DOMContentLoaded', function () {
    // Fetch Articles Button
    const fetchBtn = document.getElementById('fetch-articles-btn');

    if (fetchBtn) {
        fetchBtn.addEventListener('click', async function () {
            // Get selected sources
            const selectedSources = [];
            document.querySelectorAll('.source-checkbox:checked').forEach(cb => {
                selectedSources.push(cb.value);
            });

            if (selectedSources.length === 0) {
                showToast('Please select at least one source', 'warning');
                return;
            }

            this.disabled = true;
            this.innerHTML = '⏳ Fetching...';

            try {
                const response = await fetch('/api/fetch-articles', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sources: selectedSources,
                        limit: 30
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    showToast(`Fetched ${data.count} articles! Reloading...`, 'success');

                    // Update last fetch time
                    const now = new Date().toLocaleTimeString();
                    document.getElementById('last-fetch').textContent = `Last fetched: ${now}`;

                    // Reload page to show new articles
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast('Error: ' + (data.error || 'Failed to fetch'), 'error');
                }
            } catch (error) {
                showToast('Network error: ' + error.message, 'error');
            } finally {
                this.disabled = false;
                this.innerHTML = '🔄 Fetch Latest Articles';
            }
        });
    }

    // Generate Tweet Buttons
    document.querySelectorAll('.generate-tweet-btn').forEach(btn => {
        btn.addEventListener('click', async function () {
            const articleUrl = this.dataset.articleUrl;

            // Show progress modal
            const modal = document.getElementById('progress-modal');
            if (modal) {
                modal.style.display = 'flex';

                // Animate thinking steps
                const steps = modal.querySelectorAll('.thinking-step');
                steps.forEach((step, index) => {
                    setTimeout(() => {
                        step.classList.add('active');
                    }, index * 800);
                });

                // Animate progress bar
                const progressFill = modal.querySelector('.progress-fill');
                if (progressFill) {
                    progressFill.style.width = '0%';
                    setTimeout(() => {
                        progressFill.style.width = '100%';
                    }, 100);
                }
            }

            try {
                const response = await fetch('/api/generate-tweet', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ article_url: articleUrl })
                });

                const data = await response.json();

                if (response.ok) {
                    showToast('Tweet generated! Redirecting to draft...', 'success');

                    // Redirect to draft page after short delay
                    setTimeout(() => {
                        window.location.href = '/draft';
                    }, 1000);
                } else {
                    if (modal) modal.style.display = 'none';
                    showToast('Error: ' + (data.error || 'Failed to generate tweet'), 'error');
                }
            } catch (error) {
                if (modal) modal.style.display = 'none';
                showToast('Network error: ' + error.message, 'error');
            }
        });
    });

    // Source checkbox styling
    document.querySelectorAll('.source-chip').forEach(chip => {
        chip.addEventListener('click', function (e) {
            if (e.target.tagName !== 'INPUT') {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
            }

            // Update chip styling
            if (this.querySelector('input[type="checkbox"]').checked) {
                this.style.background = 'var(--accent-primary)';
                this.style.color = 'white';
                this.style.borderColor = 'var(--accent-primary)';
            } else {
                this.style.background = 'var(--bg-tertiary)';
                this.style.color = 'var(--text-primary)';
                this.style.borderColor = 'var(--border-color)';
            }
        });

        // Initial styling
        if (chip.querySelector('input[type="checkbox"]').checked) {
            chip.style.background = 'var(--accent-primary)';
            chip.style.color = 'white';
            chip.style.borderColor = 'var(--accent-primary)';
        }
    });

    // Update article count when filtering
    const originalFilterChipHandler = document.querySelectorAll('.filter-chip');
    originalFilterChipHandler.forEach(chip => {
        chip.addEventListener('click', function () {
            setTimeout(() => {
                const visibleArticles = document.querySelectorAll('.article-card:not(.hidden)').length;
                document.getElementById('articles-count').textContent = `Showing ${visibleArticles} articles`;
            }, 100);
        });
    });
});

console.log('✨ Articles page enhanced controls loaded');

