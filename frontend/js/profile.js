// Profile Page JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
        console.log('No token found, redirecting to login...');
        window.location.href = 'index.html';
        return;
    }

    console.log('Token found:', token);  // Debug log

    // DOM Elements
    const profileForm = document.getElementById('profile-form');
    const settingsForm = document.getElementById('settings-form');
    const profilePictureInput = document.getElementById('profile-picture-upload');
    const logoutBtn = document.getElementById('logout-btn');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const downloadDataBtn = document.getElementById('download-data-btn');
    const deleteAccountBtn = document.getElementById('delete-account-btn');

    // Tab switching functionality
    tabButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const tabId = e.target.getAttribute('data-tab');
            
            // Update active tab button
            tabButtons.forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            
            // Show active tab content
            tabPanes.forEach(pane => pane.classList.remove('active'));
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });

    // Show notification function
    const showNotification = (message, type = 'info') => {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 5000);
    };

    // Load user profile data
    const loadProfile = async () => {
        try {
            console.log('Loading profile...');
            const response = await fetch('http://localhost:5001/api/user/profile', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            console.log('Profile response status:', response.status);  // Debug log

            if (response.status === 401) {
                console.log('Unauthorized, redirecting to login...');
                localStorage.removeItem('token');
                window.location.href = 'index.html';
                return;
            }
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to load profile');
            }

            const data = await response.json();
            console.log('Profile data:', data);  // Debug log
            
            // Update profile fields
            document.getElementById('profile-name').textContent = data.name || 'Your Name';
            document.getElementById('bio').value = data.bio || '';
            document.getElementById('gender').value = data.gender || '';
            document.getElementById('birth_date').value = data.birth_date || '';
            document.getElementById('location').value = data.location || '';
            
            if (data.profile_picture) {
                document.getElementById('profile-picture').src = data.profile_picture;
            }
            
        } catch (error) {
            console.error('Error loading profile:', error);
            showNotification(`Error: ${error.message}`, 'error');
        }
    };

    // Load user settings
    const loadSettings = async () => {
        try {
            console.log('Loading settings...');
            const response = await fetch('http://localhost:5001/api/user/settings', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            console.log('Settings response status:', response.status);  // Debug log

            if (response.status === 401) {
                console.log('Unauthorized, redirecting to login...');
                localStorage.removeItem('token');
                window.location.href = 'index.html';
                return;
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to load settings');
            }

            const settings = await response.json();
            console.log('Settings data:', settings);  // Debug log
            
            // Update settings checkboxes
            const profileVisible = document.getElementById('profile-visible');
            const showOnlineStatus = document.getElementById('show-online-status');
            const matchNotifications = document.getElementById('match-notifications');
            const messageNotifications = document.getElementById('message-notifications');

            if (profileVisible) profileVisible.checked = settings.profile_visible !== false;
            if (showOnlineStatus) showOnlineStatus.checked = settings.show_online_status !== false;
            if (matchNotifications) matchNotifications.checked = settings.match_notifications !== false;
            if (messageNotifications) messageNotifications.checked = settings.message_notifications !== false;
        } catch (error) {
            console.error('Error loading settings:', error);
            showNotification(`Error: ${error.message}`, 'error');
        }
    };

    // Save profile data
    const saveProfile = async (profileData) => {
        try {
            const response = await fetch('http://localhost:5001/api/user/profile', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profileData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to save profile');
            }

            showNotification('Profile updated successfully', 'success');
            return true;
        } catch (error) {
            console.error('Error saving profile:', error);
            showNotification(`Error: ${error.message}`, 'error');
            return false;
        }
    };

    // Save settings
    const saveSettings = async (settings) => {
        try {
            const response = await fetch('http://localhost:5001/api/user/settings', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to save settings');
            }

            showNotification('Settings updated successfully', 'success');
            return true;
        } catch (error) {
            console.error('Error saving settings:', error);
            showNotification(`Error: ${error.message}`, 'error');
            return false;
        }
    };

    // Handle profile form submission
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('profile-name').textContent,
                bio: document.getElementById('bio').value,
                gender: document.getElementById('gender').value,
                birth_date: document.getElementById('birth_date').value,
                location: document.getElementById('location').value
            };

            await saveProfile(formData);
        });
    }

    // Handle settings form submission
    if (settingsForm) {
        settingsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const settings = {
                profile_visible: document.getElementById('profile-visible').checked,
                show_online_status: document.getElementById('show-online-status').checked,
                match_notifications: document.getElementById('match-notifications').checked,
                message_notifications: document.getElementById('message-notifications').checked
            };

            await saveSettings(settings);
        });
    }

    // Handle profile picture upload
    if (profilePictureInput) {
        profilePictureInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            if (!file.type.match('image.*')) {
                showNotification('Please select a valid image file', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('http://localhost:5001/api/user/profile-picture', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.message || 'Failed to upload profile picture');
                }

                const result = await response.json();
                // Update the profile picture with the new URL
                const profilePicture = document.getElementById('profile-picture');
                if (profilePicture) {
                    profilePicture.src = `/uploads/${result.filename}?t=${new Date().getTime()}`; // Add timestamp to prevent caching
                }
                showNotification('Profile picture updated successfully', 'success');
            } catch (error) {
                console.error('Error uploading profile picture:', error);
                showNotification(error.message, 'error');
            }
        });
    }

    // Handle logout
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('token');
            window.location.href = 'index.html';
        });
    }

    // Download user data
    const downloadUserData = async () => {
        try {
            const response = await fetch('http://localhost:5001/api/user/data', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to download data');
            }

            const data = await response.json();
            
            // Create a blob and download link
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `blendup_user_${data.id}_data.json`;
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(() => {
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }, 0);
            
            showNotification('Your data has been downloaded', 'success');
        } catch (error) {
            console.error('Error downloading user data:', error);
            showNotification(error.message || 'Failed to download data', 'error');
        }
    };

    // Delete user account
    const deleteAccount = async () => {
        if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch('http://localhost:5001/api/user/delete', {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to delete account');
            }

            // Clear local storage and redirect
            localStorage.clear();
            showNotification('Your account has been successfully deleted', 'success');
            
            // Redirect after a short delay
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
            
        } catch (error) {
            console.error('Error deleting account:', error);
            showNotification(error.message || 'Failed to delete account', 'error');
        }
    };

    // Add event listeners for account actions
    if (downloadDataBtn) {
        downloadDataBtn.addEventListener('click', downloadUserData);
    }

    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', deleteAccount);
    }

    // Load initial data
    loadProfile();
    loadSettings();
});
