// Load user settings
async function loadSettings() {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = 'login.html';
            return;
        }

        const response = await fetch('http://localhost:5001/api/settings', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const settings = await response.json();
            
            // Apply settings
            document.getElementById('email').value = settings.email || '';
            document.getElementById('profile-visibility').checked = settings.profile_visible || true;
            document.getElementById('show-online-status').checked = settings.show_online_status || true;
            document.getElementById('show-last-seen').checked = settings.show_last_seen || true;
            document.getElementById('email-notifications').checked = settings.email_notifications || true;
            document.getElementById('match-notifications').checked = settings.match_notifications || true;
            document.getElementById('message-notifications').checked = settings.message_notifications || true;
            document.getElementById('language').value = settings.language || 'en';
        }
    } catch (error) {
        console.error('Error loading settings:', error);
        showError('Failed to load settings');
    }
}

// Save settings
async function saveSettings(settings) {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = 'login.html';
            return;
        }

        const response = await fetch('http://localhost:5001/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(settings)
        });

        if (response.ok) {
            showSuccess('Settings saved successfully');
        } else {
            const data = await response.json();
            showError(data.message || 'Failed to save settings');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showError('Failed to save settings');
    }
}

// Change password
async function changePassword(currentPassword, newPassword) {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = 'login.html';
            return;
        }

        const response = await fetch('http://localhost:5001/api/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });

        if (response.ok) {
            showSuccess('Password changed successfully');
            document.getElementById('password').value = '';
        } else {
            const data = await response.json();
            showError(data.message || 'Failed to change password');
        }
    } catch (error) {
        console.error('Error changing password:', error);
        showError('Failed to change password');
    }
}

// Delete account
async function deleteAccount() {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        return;
    }

    try {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = 'login.html';
            return;
        }

        const response = await fetch('http://localhost:5001/api/delete-account', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            localStorage.removeItem('token');
            window.location.href = 'index.html';
        } else {
            const data = await response.json();
            showError(data.message || 'Failed to delete account');
        }
    } catch (error) {
        console.error('Error deleting account:', error);
        showError('Failed to delete account');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Load settings on page load
    loadSettings();

    // Save settings when checkboxes change
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const settings = {
                profile_visible: document.getElementById('profile-visibility').checked,
                show_online_status: document.getElementById('show-online-status').checked,
                show_last_seen: document.getElementById('show-last-seen').checked,
                email_notifications: document.getElementById('email-notifications').checked,
                match_notifications: document.getElementById('match-notifications').checked,
                message_notifications: document.getElementById('message-notifications').checked,
                language: document.getElementById('language').value
            };
            saveSettings(settings);
        });
    });

    // Language change handler
    document.getElementById('language').addEventListener('change', () => {
        const settings = {
            language: document.getElementById('language').value
        };
        saveSettings(settings);
    });

    // Change password handler
    document.getElementById('change-password').addEventListener('click', () => {
        const currentPassword = prompt('Enter your current password:');
        if (!currentPassword) return;

        const newPassword = prompt('Enter your new password:');
        if (!newPassword) return;

        const confirmPassword = prompt('Confirm your new password:');
        if (newPassword !== confirmPassword) {
            showError('Passwords do not match');
            return;
        }

        changePassword(currentPassword, newPassword);
    });

    // Delete account handler
    document.getElementById('delete-account').addEventListener('click', deleteAccount);

    // Logout handler
    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = 'index.html';
    });
});

// Utility functions
function showSuccess(message) {
    alert(message); // Replace with a better UI notification
}

function showError(message) {
    alert(message); // Replace with a better UI notification
} 