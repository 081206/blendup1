import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

const Login = () => {
    const { t } = useTranslation();
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const response = await fetch('http://127.0.0.1:5000/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
                credentials: 'include'
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Login failed');
            }

            localStorage.setItem('token', data.token);
            window.location.href = '/profile';
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-box">
                <h2>{t('welcomeBack')}</h2>
                <p>{t('loginToAccount')}</p>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">{t('email')}</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">{t('password')}</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <button type="submit" className="btn-primary">
                        {t('login')}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>
                        {t('dontHaveAccount')}{' '}
                        <Link to="/signup">{t('createAccount')}</Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login; 