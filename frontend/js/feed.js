// Feed Page JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // API Base URL
    const API_BASE_URL = 'http://localhost:5001/api';

    // Check if user is logged in
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    console.log('Checking authentication:', { token: !!token, userId: user.id });
    
    if (!token || !user.id) {
        console.log('No token or user found, redirecting to login');
        window.location.replace('index.html');
        return;
    }

    // Verify token is valid by making a test request
    async function verifyToken() {
        try {
            const response = await fetch(`${API_BASE_URL}/user/profile`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                console.log('Token verification failed:', response.status);
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.replace('index.html');
                return false;
            }
            return true;
        } catch (error) {
            console.error('Token verification error:', error);
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.replace('index.html');
            return false;
        }
    }

    // Initialize the page
    async function initializePage() {
        const isValid = await verifyToken();
        if (!isValid) return;

        // DOM Elements
        const postContent = document.getElementById('post-content');
        const postImageInput = document.getElementById('post-image');
        const postSubmit = document.getElementById('post-submit');
        const postsFeed = document.getElementById('posts-feed');
        const imagePreview = document.getElementById('image-preview');
        const currentUserAvatar = document.getElementById('current-user-avatar');
        const logoutBtn = document.getElementById('logout-btn');

        // Load current user's profile picture
        async function loadCurrentUser() {
            try {
                const response = await fetch(`${API_BASE_URL}/user/profile`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.profile_picture) {
                        currentUserAvatar.src = data.profile_picture;
                    }
                } else {
                    const error = await response.json();
                    console.error('Profile error:', error.message);
                    if (response.status === 401) {
                        localStorage.removeItem('token');
                        localStorage.removeItem('user');
                        window.location.replace('index.html');
                    }
                }
            } catch (error) {
                console.error('Error loading user profile:', error);
            }
        }

        // Load posts
        async function loadPosts() {
            try {
                postsFeed.innerHTML = '<div class="loading-posts"><i class="fas fa-spinner fa-spin"></i> Loading posts...</div>';
                
                const response = await fetch(`${API_BASE_URL}/posts`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    const error = await response.json();
                    if (response.status === 401) {
                        localStorage.removeItem('token');
                        localStorage.removeItem('user');
                        window.location.replace('index.html');
                        return;
                    }
                    throw new Error(error.message || 'Failed to load posts');
                }

                const posts = await response.json();
                
                if (posts.length === 0) {
                    postsFeed.innerHTML = '<div class="no-posts">No posts yet. Be the first to post something!</div>';
                    return;
                }

                postsFeed.innerHTML = '';
                
                posts.forEach(post => {
                    const postElement = createPostElement(post);
                    postsFeed.appendChild(postElement);
                });
                
            } catch (error) {
                console.error('Error loading posts:', error);
                postsFeed.innerHTML = `<div class="error">Error loading posts: ${error.message}</div>`;
            }
        }

        // Create post element
        function createPostElement(post) {
            const postElement = document.createElement('div');
            postElement.className = 'post';
            postElement.dataset.postId = post.id;
            
            const isCurrentUserPost = post.user.id === parseInt(getJwtUserId());
            
            postElement.innerHTML = `
                <div class="post-header">
                    <img src="${post.user.profile_picture || 'https://via.placeholder.com/40'}" 
                         alt="${post.user.name}" class="user-avatar">
                    <div class="post-user-info">
                        <h4>${post.user.name}</h4>
                        <span class="post-time">${formatPostTime(post.created_at)}</span>
                    </div>
                    ${isCurrentUserPost ? `
                        <button class="btn-icon delete-post" data-post-id="${post.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : ''}
                </div>
                <div class="post-content">${post.content}</div>
                ${post.image_path ? `
                    <div class="post-image">
                        <img src="${post.image_path}" alt="Post image">
                    </div>
                ` : ''}
                <div class="post-actions">
                    <button class="btn-icon">
                        <i class="far fa-heart"></i>
                        <span>Like</span>
                    </button>
                    <button class="btn-icon">
                        <i class="far fa-comment"></i>
                        <span>Comment</span>
                    </button>
                    <button class="btn-icon">
                        <i class="far fa-share-square"></i>
                        <span>Share</span>
                    </button>
                </div>
            `;

            // Add delete post handler
            const deleteBtn = postElement.querySelector('.delete-post');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    deletePost(post.id, postElement);
                });
            }

            return postElement;
        }

        // Format post time
        function formatPostTime(timestamp) {
            const date = new Date(timestamp);
            const now = new Date();
            const diffInSeconds = Math.floor((now - date) / 1000);
            
            if (diffInSeconds < 60) return 'Just now';
            if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
            if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
            if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
            
            return date.toLocaleDateString();
        }

        // Get user ID from stored user data
        function getJwtUserId() {
            return user.id;
        }

        // Handle post submission
        postSubmit.addEventListener('click', async () => {
            const content = postContent.value.trim();
            const imageFile = postImageInput.files[0];
            
            if (!content && !imageFile) {
                alert('Please add some content or an image to your post');
                return;
            }
            
            try {
                const formData = new FormData();
                if (content) formData.append('content', content);
                if (imageFile) formData.append('image', imageFile);
                
                const response = await fetch(`${API_BASE_URL}/posts`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Failed to create post');
                }
                
                // Clear form
                postContent.value = '';
                postImageInput.value = '';
                imagePreview.innerHTML = '';
                imagePreview.style.display = 'none';
                
                // Reload posts
                loadPosts();
                
            } catch (error) {
                console.error('Error creating post:', error);
                alert(`Error: ${error.message}`);
            }
        });

        // Handle image preview
        postImageInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            if (!file.type.startsWith('image/')) {
                alert('Please select an image file');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = (event) => {
                imagePreview.innerHTML = `
                    <div class="preview-image">
                        <img src="${event.target.result}" alt="Preview">
                        <button class="remove-image" id="remove-image">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `;
                imagePreview.style.display = 'block';
                
                // Add remove image handler
                document.getElementById('remove-image').addEventListener('click', () => {
                    postImageInput.value = '';
                    imagePreview.innerHTML = '';
                    imagePreview.style.display = 'none';
                });
            };
            reader.readAsDataURL(file);
        });

        // Delete post
        async function deletePost(postId, postElement) {
            if (!confirm('Are you sure you want to delete this post?')) return;
            
            try {
                const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Failed to delete post');
                }
                
                postElement.remove();
            } catch (error) {
                console.error('Error deleting post:', error);
                alert(`Error: ${error.message}`);
            }
        }

        // Logout handler
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.replace('index.html');
            });
        }

        // Initialize
        loadCurrentUser();
        loadPosts();
    }

    // Start initialization
    initializePage();
});
