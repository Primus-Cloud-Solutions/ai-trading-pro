// Enhanced Engagement System for KOL Opinions
class EngagementManager {
    constructor() {
        this.userEngagements = new Map();
        this.init();
    }

    init() {
        // Load user engagements from localStorage
        const saved = localStorage.getItem('userEngagements');
        if (saved) {
            this.userEngagements = new Map(JSON.parse(saved));
        }
    }

    saveEngagements() {
        localStorage.setItem('userEngagements', JSON.stringify([...this.userEngagements]));
    }

    // Format numbers for display
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    // Toggle like functionality
    async toggleLike(opinionId, buttonElement) {
        const isLiked = buttonElement.classList.contains('liked');
        const countElement = buttonElement.closest('.kol-card').querySelector('[data-type="likes"]');
        let currentCount = parseInt(countElement.textContent.replace(/[KM]/g, '')) || 0;

        try {
            const response = await fetch('/api/social/engagement/like', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    opinion_id: opinionId,
                    action: isLiked ? 'unlike' : 'like'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Update UI
                if (isLiked) {
                    buttonElement.classList.remove('liked');
                    currentCount = Math.max(0, currentCount - 1);
                } else {
                    buttonElement.classList.add('liked');
                    currentCount += 1;
                }
                
                countElement.textContent = this.formatNumber(currentCount);
                
                // Save engagement state
                this.userEngagements.set(opinionId + '_liked', !isLiked);
                this.saveEngagements();

                // Add animation
                buttonElement.style.transform = 'scale(1.2)';
                setTimeout(() => {
                    buttonElement.style.transform = 'scale(1)';
                }, 200);
            }
        } catch (error) {
            console.error('Error toggling like:', error);
        }
    }

    // Share functionality
    async shareOpinion(opinionId) {
        const countElement = document.querySelector(`[data-opinion-id="${opinionId}"] [data-type="shares"]`);
        let currentCount = parseInt(countElement.textContent.replace(/[KM]/g, '')) || 0;

        try {
            // Update share count
            const response = await fetch('/api/social/engagement/share', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    opinion_id: opinionId
                })
            });

            const data = await response.json();
            
            if (data.success) {
                currentCount += 1;
                countElement.textContent = this.formatNumber(currentCount);
            }

            // Show share options
            this.showShareModal(opinionId, data.opinion);
        } catch (error) {
            console.error('Error sharing opinion:', error);
        }
    }

    // Show share modal
    showShareModal(opinionId, opinion) {
        const modal = document.createElement('div');
        modal.className = 'share-modal';
        modal.innerHTML = `
            <div class="share-modal-content">
                <div class="share-header">
                    <h3>Share Opinion</h3>
                    <button class="close-btn" onclick="this.closest('.share-modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="share-options">
                    <button class="share-option" onclick="engagementManager.shareToTwitter('${opinionId}')">
                        <i class="fab fa-twitter"></i>
                        Twitter
                    </button>
                    <button class="share-option" onclick="engagementManager.shareToTelegram('${opinionId}')">
                        <i class="fab fa-telegram"></i>
                        Telegram
                    </button>
                    <button class="share-option" onclick="engagementManager.copyLink('${opinionId}')">
                        <i class="fas fa-link"></i>
                        Copy Link
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    // Share to Twitter
    shareToTwitter(opinionId) {
        const url = `${window.location.origin}/?opinion=${opinionId}`;
        const text = "Check out this trading insight from AI Trading Pro!";
        window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
    }

    // Share to Telegram
    shareToTelegram(opinionId) {
        const url = `${window.location.origin}/?opinion=${opinionId}`;
        const text = "Check out this trading insight from AI Trading Pro!";
        window.open(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`, '_blank');
    }

    // Copy link
    async copyLink(opinionId) {
        const url = `${window.location.origin}/?opinion=${opinionId}`;
        try {
            await navigator.clipboard.writeText(url);
            this.showToast('Link copied to clipboard!', 'success');
        } catch (error) {
            console.error('Error copying link:', error);
            this.showToast('Failed to copy link', 'error');
        }
    }

    // Toggle comments section
    toggleComments(opinionId) {
        const commentsSection = document.getElementById(`comments-${opinionId}`);
        const isVisible = commentsSection.style.display !== 'none';
        
        if (isVisible) {
            commentsSection.style.display = 'none';
        } else {
            commentsSection.style.display = 'block';
            this.loadComments(opinionId);
        }
    }

    // Load comments for an opinion
    async loadComments(opinionId) {
        const commentsList = document.getElementById(`comments-list-${opinionId}`);
        
        try {
            const response = await fetch(`/api/social/comments/${opinionId}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderComments(commentsList, data.comments);
            }
        } catch (error) {
            console.error('Error loading comments:', error);
        }
    }

    // Render comments
    renderComments(container, comments) {
        container.innerHTML = comments.map(comment => `
            <div class="comment-item">
                <div class="comment-avatar">
                    <div class="avatar-circle" style="background: ${comment.avatar_color}">
                        ${comment.author.charAt(0).toUpperCase()}
                    </div>
                </div>
                <div class="comment-content">
                    <div class="comment-header">
                        <span class="comment-author">${comment.author}</span>
                        <span class="comment-sentiment ${comment.sentiment}">
                            ${this.getSentimentIcon(comment.sentiment)} ${comment.sentiment}
                        </span>
                        <span class="comment-time">${comment.time_ago}</span>
                    </div>
                    <p class="comment-text">${comment.content}</p>
                    <div class="comment-actions">
                        <button class="comment-like-btn ${comment.user_liked ? 'liked' : ''}" 
                                onclick="engagementManager.toggleCommentLike('${comment.id}', this)">
                            <i class="fas fa-heart"></i>
                            ${comment.likes}
                        </button>
                        <button class="comment-reply-btn" onclick="engagementManager.replyToComment('${comment.id}')">
                            <i class="fas fa-reply"></i>
                            Reply
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Submit comment
    async submitComment(opinionId) {
        const textArea = document.getElementById(`comment-text-${opinionId}`);
        const content = textArea.value.trim();
        
        if (!content) {
            this.showToast('Please enter a comment', 'error');
            return;
        }

        // Get selected sentiment
        const selectedSentiment = document.querySelector(`#comments-${opinionId} .sentiment-btn.selected`);
        const sentiment = selectedSentiment ? selectedSentiment.dataset.sentiment : 'neutral';

        try {
            const response = await fetch('/api/social/comments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    opinion_id: opinionId,
                    content: content,
                    sentiment: sentiment
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Clear the text area
                textArea.value = '';
                
                // Remove sentiment selection
                document.querySelectorAll(`#comments-${opinionId} .sentiment-btn`).forEach(btn => {
                    btn.classList.remove('selected');
                });
                
                // Reload comments
                this.loadComments(opinionId);
                
                // Update comment count
                const countElement = document.querySelector(`[data-opinion-id="${opinionId}"] [data-type="comments"]`);
                if (countElement) {
                    let currentCount = parseInt(countElement.textContent.replace(/[KM]/g, '')) || 0;
                    countElement.textContent = this.formatNumber(currentCount + 1);
                }
                
                this.showToast('Comment posted successfully!', 'success');
            } else {
                this.showToast(data.message || 'Failed to post comment', 'error');
            }
        } catch (error) {
            console.error('Error submitting comment:', error);
            this.showToast('Network error. Please try again.', 'error');
        }
    }

    // Toggle bookmark
    async toggleBookmark(opinionId, buttonElement) {
        const isBookmarked = buttonElement.classList.contains('bookmarked');
        
        try {
            const response = await fetch('/api/social/engagement/bookmark', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    opinion_id: opinionId,
                    action: isBookmarked ? 'unbookmark' : 'bookmark'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                if (isBookmarked) {
                    buttonElement.classList.remove('bookmarked');
                } else {
                    buttonElement.classList.add('bookmarked');
                }
                
                // Save engagement state
                this.userEngagements.set(opinionId + '_bookmarked', !isBookmarked);
                this.saveEngagements();
                
                this.showToast(
                    isBookmarked ? 'Removed from bookmarks' : 'Added to bookmarks', 
                    'success'
                );
            }
        } catch (error) {
            console.error('Error toggling bookmark:', error);
        }
    }

    // Get sentiment icon
    getSentimentIcon(sentiment) {
        const icons = {
            'bullish': '📈',
            'bearish': '📉',
            'neutral': '😐'
        };
        return icons[sentiment] || '😐';
    }

    // Show toast notification
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'exclamation' : 'info'}-circle"></i>
            ${message}
        `;
        
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Hide toast
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Track click engagement
    async trackClick(opinionId, element) {
        const countElement = element.closest('.kol-card').querySelector('[data-type="clicks"]');
        let currentCount = parseInt(countElement.textContent.replace(/[KM]/g, '')) || 0;
        
        try {
            const response = await fetch('/api/social/engagement/click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    opinion_id: opinionId
                })
            });

            const data = await response.json();
            
            if (data.success) {
                currentCount += 1;
                countElement.textContent = this.formatNumber(currentCount);
            }
        } catch (error) {
            console.error('Error tracking click:', error);
        }
    }
}

// Initialize engagement manager
const engagementManager = new EngagementManager();

// Global functions for onclick handlers
window.toggleLike = (opinionId, element) => engagementManager.toggleLike(opinionId, element);
window.shareOpinion = (opinionId) => engagementManager.shareOpinion(opinionId);
window.toggleComments = (opinionId) => engagementManager.toggleComments(opinionId);
window.submitComment = (opinionId) => engagementManager.submitComment(opinionId);
window.toggleBookmark = (opinionId, element) => engagementManager.toggleBookmark(opinionId, element);

// Add sentiment selection functionality
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('sentiment-btn')) {
        // Remove selection from siblings
        e.target.parentNode.querySelectorAll('.sentiment-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        // Add selection to clicked button
        e.target.classList.add('selected');
    }
});

// Add CSS for engagement features
const engagementStyles = `
<style>
.engagement-section {
    border-top: 1px solid rgba(76, 175, 80, 0.2);
    padding-top: 15px;
    margin-top: 15px;
}

.engagement-stats {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #b0bec5;
    font-size: 14px;
}

.stat-item i {
    color: #4CAF50;
}

.engagement-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.action-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 8px 12px;
    background: rgba(76, 175, 80, 0.1);
    border: 1px solid rgba(76, 175, 80, 0.3);
    border-radius: 20px;
    color: #4CAF50;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.action-btn:hover {
    background: rgba(76, 175, 80, 0.2);
    transform: translateY(-1px);
}

.action-btn.liked,
.action-btn.bookmarked {
    background: rgba(76, 175, 80, 0.3);
    color: #ffffff;
}

.comment-section {
    border-top: 1px solid rgba(76, 175, 80, 0.2);
    padding-top: 15px;
    margin-top: 15px;
}

.comment-input-area {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.comment-input-wrapper {
    flex: 1;
}

.comment-input {
    width: 100%;
    min-height: 80px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(76, 175, 80, 0.3);
    border-radius: 10px;
    color: #ffffff;
    resize: vertical;
    font-family: inherit;
}

.comment-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
}

.sentiment-selector {
    display: flex;
    gap: 5px;
}

.sentiment-btn {
    padding: 5px 10px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(76, 175, 80, 0.3);
    border-radius: 15px;
    color: #b0bec5;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.sentiment-btn:hover,
.sentiment-btn.selected {
    background: rgba(76, 175, 80, 0.3);
    color: #ffffff;
}

.submit-comment-btn {
    padding: 8px 16px;
    background: linear-gradient(135deg, #4CAF50, #66BB6A);
    border: none;
    border-radius: 20px;
    color: white;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.submit-comment-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
}

.comment-item {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
}

.comment-content {
    flex: 1;
}

.comment-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 5px;
    font-size: 12px;
}

.comment-author {
    font-weight: 600;
    color: #4CAF50;
}

.comment-sentiment {
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 10px;
}

.comment-sentiment.bullish {
    background: rgba(76, 175, 80, 0.2);
    color: #4CAF50;
}

.comment-sentiment.bearish {
    background: rgba(244, 67, 54, 0.2);
    color: #f44336;
}

.comment-sentiment.neutral {
    background: rgba(158, 158, 158, 0.2);
    color: #9e9e9e;
}

.comment-time {
    color: #78909c;
}

.comment-text {
    color: #e0e0e0;
    margin-bottom: 8px;
    line-height: 1.4;
}

.comment-actions {
    display: flex;
    gap: 15px;
}

.comment-like-btn,
.comment-reply-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    background: none;
    border: none;
    color: #78909c;
    font-size: 11px;
    cursor: pointer;
    transition: color 0.3s ease;
}

.comment-like-btn:hover,
.comment-reply-btn:hover {
    color: #4CAF50;
}

.comment-like-btn.liked {
    color: #f44336;
}

.share-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.share-modal-content {
    background: rgba(26, 35, 50, 0.95);
    border: 1px solid rgba(76, 175, 80, 0.3);
    border-radius: 15px;
    padding: 25px;
    min-width: 300px;
}

.share-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.share-header h3 {
    color: #4CAF50;
    margin: 0;
}

.close-btn {
    background: none;
    border: none;
    color: #78909c;
    font-size: 18px;
    cursor: pointer;
}

.share-options {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.share-option {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(76, 175, 80, 0.3);
    border-radius: 8px;
    color: #e0e0e0;
    cursor: pointer;
    transition: all 0.3s ease;
}

.share-option:hover {
    background: rgba(76, 175, 80, 0.2);
    color: #ffffff;
}

.toast {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 1001;
    transform: translateX(100%);
    transition: transform 0.3s ease;
}

.toast.show {
    transform: translateX(0);
}

.toast-success {
    background: linear-gradient(135deg, #4CAF50, #66BB6A);
}

.toast-error {
    background: linear-gradient(135deg, #f44336, #ef5350);
}

.toast-info {
    background: linear-gradient(135deg, #2196F3, #42A5F5);
}

.avatar-circle {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
    color: white;
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', engagementStyles);

