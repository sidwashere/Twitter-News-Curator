// Settings Page JavaScript
document.addEventListener('DOMContentLoaded', function () {
    console.log('✨ Settings page loaded');

    // Helper function to get selected topics
    function getSelectedTopics() {
        const topics = [];
        document.querySelectorAll('.topic-checkbox input:checked').forEach(checkbox => {
            const label = checkbox.nextElementSibling?.textContent.trim() || '';
            topics.push(label);
        });
        return topics;
    }

    // Save All Settings Button - PRIMARY SAVE BUTTON
    const saveAllBtn = document.getElementById('save-all-settings');

    if (saveAllBtn) {
        saveAllBtn.addEventListener('click', async function () {
            // Collect all settings from the form
            const settings = {
                ai_settings: {
                    temperature: parseFloat(document.getElementById('default-temp')?.value || 90) / 100
                },
                tweet_style: {
                    max_hashtags: parseInt(document.getElementById('max-hashtags')?.value || 1),
                    max_length: parseInt(document.getElementById('max-length')?.value || 280)
                },
                posting_schedule: {
                    times: [],
                    auto_post: document.getElementById('auto-post')?.checked || false,
                    max_per_day: parseInt(document.getElementById('max-per-day')?.value || 10)
                },
                topic_preferences: getSelectedTopics()
            };

            // Collect posting times if they exist
            const timeInputs = document.querySelectorAll('input[type="time"]');
            if (timeInputs.length > 0) {
                settings.posting_schedule.times = Array.from(timeInputs).map(input => input.value).filter(v => v);
            }

            this.disabled = true;
            this.innerHTML = '⏳ Saving...';

            try {
                const response = await fetch('/api/settings/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(settings)
                });

                const data = await response.json();

                if (response.ok) {
                    showToast('✅ All settings saved and applied successfully!', 'success');
                    this.innerHTML = '✓ Saved!';
                    setTimeout(() => {
                        this.innerHTML = '💾 Save All Settings';
                    }, 2000);
                } else {
                    showToast('❌ Error: ' + (data.error || 'Failed to save settings'), 'error');
                    this.innerHTML = '💾 Save All Settings';
                }
            } catch (error) {
                console.error('Settings save error:', error);
                showToast('❌ Network error: ' + error.message, 'error');
                this.innerHTML = '💾 Save All Settings';
            } finally {
                this.disabled = false;
            }
        });
    }

    // Show/Hide Add Feed Form
    const addFeedBtn = document.getElementById('add-feed-btn');
    const addFeedForm = document.getElementById('add-feed-form');
    const cancelFeedBtn = document.getElementById('cancel-feed-btn');

    if (addFeedBtn && addFeedForm) {
        addFeedBtn.addEventListener('click', function () {
            addFeedForm.style.display = 'block';
        });
    }

    if (cancelFeedBtn && addFeedForm) {
        cancelFeedBtn.addEventListener('click', function () {
            addFeedForm.style.display = 'none';
            document.getElementById('new-feed-url').value = '';
        });
    }

    // Save Feed Button
    const saveFeedBtn = document.getElementById('save-feed-btn');
    if (saveFeedBtn) {
        saveFeedBtn.addEventListener('click', async function () {
            const feedInput = document.getElementById('new-feed-url');
            const feedUrl = feedInput?.value.trim();

            if (!feedUrl) {
                showToast('⚠️ Please enter a feed URL', 'warning');
                return;
            }

            // Basic URL validation
            if (!feedUrl.startsWith('http://') && !feedUrl.startsWith('https://')) {
                showToast('⚠️ Please enter a valid URL starting with http:// or https://', 'warning');
                return;
            }

            this.disabled = true;
            this.innerHTML = '⏳ Adding...';

            try {
                const response = await fetch('/api/rss/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: feedUrl })
                });

                const data = await response.json();

                if (response.ok) {
                    showToast('✅ RSS feed added! Reloading...', 'success');
                    feedInput.value = '';
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast('❌ Error: ' + (data.error || 'Failed to add feed'), 'error');
                }
            } catch (error) {
                showToast('❌ Network error: ' + error.message, 'error');
            } finally {
                this.disabled = false;
                this.innerHTML = 'Save Feed';
            }
        });
    }

    // Remove RSS Feed Buttons
    document.querySelectorAll('.remove-feed-btn').forEach(btn => {
        btn.addEventListener('click', async function () {
            const feedUrl = this.dataset.url;

            if (!confirm(`Remove this feed?\n${feedUrl}`)) {
                return;
            }

            this.disabled = true;
            this.innerHTML = '⏳';

            try {
                const response = await fetch('/api/rss/remove', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: feedUrl })
                });

                const data = await response.json();

                if (response.ok) {
                    showToast('✅ Feed removed! Reloading...', 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast('❌ Error: ' + (data.error || 'Failed to remove'), 'error');
                    this.disabled = false;
                    this.innerHTML = '🗑️ Remove';
                }
            } catch (error) {
                showToast('❌ Network error: ' + error.message, 'error');
                this.disabled = false;
                this.innerHTML = '🗑️ Remove';
            }
        });
    });

    // Add Suggested Feed Buttons
    document.querySelectorAll('.add-suggested-btn').forEach(btn => {
        btn.addEventListener('click', async function () {
            const feedUrl = this.dataset.feed;

            this.disabled = true;
            this.innerHTML = '⏳';

            try {
                const response = await fetch('/api/rss/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: feedUrl })
                });

                const data = await response.json();

                if (response.ok) {
                    showToast('✅ Feed added! Reloading...', 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast('⚠️ ' + (data.error || 'Feed already exists'), 'warning');
                    this.disabled = false;
                    this.innerHTML = 'Add';
                }
            } catch (error) {
                showToast('❌ Network error: ' + error.message, 'error');
                this.disabled = false;
                this.innerHTML = 'Add';
            }
        });
    });
});
