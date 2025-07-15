// Global Engagement Functions for KOL Opinions

// Toggle like on a KOL opinion
async function toggleLike(opinionId, buttonElement) {
    try {
        const isLiked = buttonElement.classList.contains('liked');
        const action = isLiked ? 'unlike' : 'like';
        
        const response = await fetch('/api/social/engagement/like', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                opinion_id: opinionId,
                action: action
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update button state
            buttonElement.classList.toggle('liked');
            
            // Update like count in the stats
            const card = buttonElement.closest('.kol-card');
            const likesCount = card.querySelector('[data-type="likes"]');
            if (likesCount) {
                likesCount.textContent = formatNumber(data.likes);
            }
            
            // Show feedback
            showEngagementFeedback(buttonElement, action === 'like' ? 'Liked!' : 'Unliked');
        }
    } catch (error) {
        console.error('Error toggling like:', error);
        showEngagementFeedback(buttonElement, 'Error occurred', 'error');
    }
}

// Share a KOL opinion
async function shareOpinion(opinionId) {
    try {
        const response = await fetch('/api/social/engagement/share', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                opinion_id: opinionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update share count
            const card = document.querySelector(`[data-opinion-id="${opinionId}"]`);
            const sharesCount = card.querySelector('[data-type="shares"]');
            if (sharesCount) {
                sharesCount.textContent = formatNumber(data.shares);
            }
            
            // Copy to clipboard
            const shareUrl = `${window.location.origin}/opinion/${opinionId}`;
            await navigator.clipboard.writeText(shareUrl);
            
            // Show feedback
            showEngagementFeedback(card.querySelector('.share-btn'), 'Shared! Link copied to clipboard');
        }
    } catch (error) {
        console.error('Error sharing opinion:', error);
        showEngagementFeedback(null, 'Error sharing opinion', 'error');
    }
}

// Toggle comments section
function toggleComments(opinionId) {
    const commentsSection = document.getElementById(`comments-${opinionId}`);
    if (commentsSection) {
        const isVisible = commentsSection.style.display !== 'none';
        commentsSection.style.display = isVisible ? 'none' : 'block';
        
        if (!isVisible) {
            loadComments(opinionId);
        }
    }
}

// Load comments for an opinion
async function loadComments(opinionId) {
    try {
        const response = await fetch(`/api/social/comments/${opinionId}`);
        const data = await response.json();
        
        if (data.success) {
            renderComments(opinionId, data.comments);
        }
    } catch (error) {
        console.error('Error loading comments:', error);
    }
}

// Render comments in the comments section
function renderComments(opinionId, comments) {
    const commentsList = document.getElementById(`comments-list-${opinionId}`);
    if (!commentsList) return;
    
    commentsList.innerHTML = comments.map(comment => `
        <div class="comment-item">
            <div class="comment-avatar">
                <div class="avatar-circle" style="background: ${comment.avatar_color}">
                    ${comment.author.charAt(0)}
                </div>
            </div>
            <div class="comment-content">
                <div class="comment-header">
                    <span class="comment-author">${comment.author}</span>
                    <span class="comment-sentiment ${comment.sentiment}">
                        ${getSentimentIcon(comment.sentiment)}
                    </span>
                    <span class="comment-time">${comment.time_ago}</span>
                </div>
                <div class="comment-text">${comment.content}</div>
                <div class="comment-actions">
                    <button class="comment-like-btn ${comment.user_liked ? 'liked' : ''}" 
                            onclick="toggleCommentLike('${comment.id}', this)">
                        <i class="fas fa-heart"></i>
                        ${comment.likes}
                    </button>
                    <button class="comment-reply-btn">
                        <i class="fas fa-reply"></i>
                        Reply
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Submit a new comment
async function submitComment(opinionId) {
    const textArea = document.getElementById(`comment-text-${opinionId}`);
    const content = textArea.value.trim();
    
    if (!content) {
        showEngagementFeedback(textArea, 'Please enter a comment', 'error');
        return;
    }
    
    // Get selected sentiment
    const selectedSentiment = document.querySelector(`#comments-${opinionId} .sentiment-btn.selected`);
    const sentiment = selectedSentiment ? selectedSentiment.dataset.sentiment : 'neutral';
    
    try {
        const response = await fetch('/api/social/comments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                opinion_id: opinionId,
                content: content,
                sentiment: sentiment
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Clear the input
            textArea.value = '';
            
            // Reload comments
            loadComments(opinionId);
            
            // Update comment count
            const card = document.querySelector(`[data-opinion-id="${opinionId}"]`);
            const commentsCount = card.querySelector('[data-type="comments"]');
            if (commentsCount) {
                commentsCount.textContent = formatNumber(data.total_comments);
            }
            
            showEngagementFeedback(textArea, 'Comment posted successfully!');
        }
    } catch (error) {
        console.error('Error posting comment:', error);
        showEngagementFeedback(textArea, 'Error posting comment', 'error');
    }
}

// Toggle bookmark on an opinion
async function toggleBookmark(opinionId, buttonElement) {
    try {
        const isBookmarked = buttonElement.classList.contains('bookmarked');
        const action = isBookmarked ? 'unbookmark' : 'bookmark';
        
        const response = await fetch('/api/social/engagement/bookmark', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                opinion_id: opinionId,
                action: action
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            buttonElement.classList.toggle('bookmarked');
            showEngagementFeedback(buttonElement, action === 'bookmark' ? 'Bookmarked!' : 'Removed from bookmarks');
        }
    } catch (error) {
        console.error('Error toggling bookmark:', error);
        showEngagementFeedback(buttonElement, 'Error occurred', 'error');
    }
}

// Toggle like on a comment
async function toggleCommentLike(commentId, buttonElement) {
    try {
        const isLiked = buttonElement.classList.contains('liked');
        buttonElement.classList.toggle('liked');
        
        // Update like count (simulate for now)
        const currentLikes = parseInt(buttonElement.textContent.trim());
        const newLikes = isLiked ? currentLikes - 1 : currentLikes + 1;
        buttonElement.innerHTML = `<i class="fas fa-heart"></i> ${newLikes}`;
        
        showEngagementFeedback(buttonElement, isLiked ? 'Unliked' : 'Liked');
    } catch (error) {
        console.error('Error toggling comment like:', error);
    }
}

// Show engagement feedback
function showEngagementFeedback(element, message, type = 'success') {
    const feedback = document.createElement('div');
    feedback.className = `engagement-feedback ${type}`;
    feedback.textContent = message;
    
    if (element) {
        element.parentNode.appendChild(feedback);
        
        setTimeout(() => {
            feedback.remove();
        }, 3000);
    } else {
        // Show global notification
        document.body.appendChild(feedback);
        feedback.style.position = 'fixed';
        feedback.style.top = '20px';
        feedback.style.right = '20px';
        feedback.style.zIndex = '10000';
        
        setTimeout(() => {
            feedback.remove();
        }, 3000);
    }
}

// Utility functions
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function getSentimentIcon(sentiment) {
    const icons = {
        'bullish': '📈',
        'bearish': '📉',
        'neutral': '😐'
    };
    return icons[sentiment] || '😐';
}

// Setup sentiment selector
document.addEventListener('DOMContentLoaded', function() {
    // Handle sentiment button selection
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('sentiment-btn')) {
            const container = e.target.closest('.sentiment-selector');
            container.querySelectorAll('.sentiment-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            e.target.classList.add('selected');
        }
    });
    
    // Track clicks for engagement
    document.addEventListener('click', function(e) {
        const kolCard = e.target.closest('.kol-card');
        if (kolCard && !e.target.closest('.engagement-actions')) {
            const opinionId = kolCard.dataset.opinionId;
            if (opinionId) {
                trackClick(opinionId);
            }
        }
    });
});

// Track click engagement
async function trackClick(opinionId) {
    try {
        const response = await fetch('/api/social/engagement/click', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                opinion_id: opinionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update click count
            const card = document.querySelector(`[data-opinion-id="${opinionId}"]`);
            const clicksCount = card.querySelector('[data-type="clicks"]');
            if (clicksCount) {
                clicksCount.textContent = formatNumber(data.clicks);
            }
        }
    } catch (error) {
        console.error('Error tracking click:', error);
    }
}

