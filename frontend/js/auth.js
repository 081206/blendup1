// Authentication utility functions

/**
 * Check if user is authenticated and redirect to login if not
 */
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
    }
}

/**
 * Redirect to dashboard if user is already logged in
 */
function redirectIfLoggedIn() {
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = 'dashboard.html';
    }
}

/**
 * Logout user by clearing token and redirecting to login
 */
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

/**
 * Add logout button to navigation
 */
function addLogoutButton() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
}

/**
 * Verify token validity with the server
 */
async function verifyToken() {
    const token = localStorage.getItem('token');
    if (!token) return false;

    try {
        const response = await fetch('http://localhost:5001/api/verify-token', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        return response.ok;
    } catch (error) {
        console.error('Error verifying token:', error);
        return false;
    }
}

/**
 * Initialize authentication checks
 */
async function initAuth() {
    // Check if we're on the index page
    if (window.location.pathname.endsWith('index.html') || window.location.pathname.endsWith('/')) {
        redirectIfLoggedIn();
    } else {
        // For all other pages, check authentication
        const isValid = await verifyToken();
        if (!isValid) {
            logout();
        }
    }
}

// Add logout button functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    addLogoutButton();
    initAuth();
}); 