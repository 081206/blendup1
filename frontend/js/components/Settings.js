import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

const Settings = () => {
    const { t } = useTranslation();
    const [settings, setSettings] = useState({
        hideProfile: false,
        pushNotifications: true,
        twoFactorAuth: false,
        language: localStorage.getItem('language') || 'en',
        theme: localStorage.getItem('theme') || 'light'
    });
    const [blockedUsers, setBlockedUsers] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchSettings();
        fetchBlockedUsers();
    }, []);

    const fetchSettings = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/settings', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to fetch settings');
            }

            const data = await response.json();
            setSettings(data);
        } catch (err) {
            setError(err.message);
        }
    };

    const fetchBlockedUsers = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/blocked-users', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to fetch blocked users');
            }

            const data = await response.json();
            setBlockedUsers(data);
        } catch (err) {
            setError(err.message);
        }
    };

    const handleSettingChange = async (setting, value) => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/settings', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ [setting]: value }),
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to update setting');
            }

            setSettings(prev => ({ ...prev, [setting]: value }));
        } catch (err) {
            setError(err.message);
        }
    };

    const handleUnblockUser = async (userId) => {
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/blocked-users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to unblock user');
            }

            setBlockedUsers(prev => prev.filter(user => user.id !== userId));
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="settings-container">
            <h2>{t('settings')}</h2>

            {error && <div className="error-message">{error}</div>}

            <div className="settings-section">
                <h3>{t('privacy')}</h3>
                <div className="setting-item">
                    <label>
                        <input
                            type="checkbox"
                            checked={settings.hideProfile}
                            onChange={(e) => handleSettingChange('hideProfile', e.target.checked)}
                        />
                        {t('hideProfile')}
                    </label>
                </div>
            </div>

            <div className="settings-section">
                <h3>{t('notifications')}</h3>
                <div className="setting-item">
                    <label>
                        <input
                            type="checkbox"
                            checked={settings.pushNotifications}
                            onChange={(e) => handleSettingChange('pushNotifications', e.target.checked)}
                        />
                        {t('pushNotifications')}
                    </label>
                </div>
            </div>

            <div className="settings-section">
                <h3>{t('security')}</h3>
                <div className="setting-item">
                    <label>
                        <input
                            type="checkbox"
                            checked={settings.twoFactorAuth}
                            onChange={(e) => handleSettingChange('twoFactorAuth', e.target.checked)}
                        />
                        {t('twoFa')}
                    </label>
                </div>
            </div>

            <div className="settings-section">
                <h3>{t('blockedUsers')}</h3>
                {blockedUsers.length === 0 ? (
                    <p>{t('noBlockedUsers')}</p>
                ) : (
                    <div className="blocked-users-list">
                        {blockedUsers.map(user => (
                            <div key={user.id} className="blocked-user">
                                <span>{user.name}</span>
                                <button
                                    onClick={() => handleUnblockUser(user.id)}
                                    className="btn-secondary"
                                >
                                    {t('unblock')}
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Settings; 