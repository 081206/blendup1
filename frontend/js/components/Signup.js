import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

const Signup = () => {
    const { t } = useTranslation('common');
    const [formData, setFormData] = useState({
        fullName: '',
        email: '',
        password: '',
        confirmPassword: '',
        agreeToTerms: false
    });
    const [errors, setErrors] = useState({});

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({});

        if (formData.password !== formData.confirmPassword) {
            setErrors({ confirmPassword: 'Passwords do not match' });
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:5000/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: formData.fullName,
                    email: formData.email,
                    password: formData.password
                }),
                credentials: 'include'
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Registration failed');
            }

            localStorage.setItem('token', data.token);
            window.location.href = '/profile';
        } catch (err) {
            setErrors({ submit: err.message });
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-header">
                <h2 className="auth-title">{t('createAccount')}</h2>
                <p className="auth-subtitle">{t('joinBlendup')}</p>
            </div>
            
            <div className="auth-box">
                {Object.keys(errors).map(key => (
                    <div key={key} className="error-message">{errors[key]}</div>
                ))}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label htmlFor="fullName">{t('fullName')}</label>
                        <input
                            type="text"
                            id="fullName"
                            name="fullName"
                            value={formData.fullName}
                            onChange={handleChange}
                            required
                            placeholder={t('enterFullName')}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">{t('email')}</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            placeholder={t('enterEmail')}
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
                            placeholder={t('enterPassword')}
                            minLength="8"
                        />
                        <small>{t('passwordRequirements')}</small>
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirmPassword">{t('confirmPassword')}</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            required
                            placeholder={t('confirmPassword')}
                        />
                    </div>

                    <div className="form-group checkbox">
                        <input
                            type="checkbox"
                            id="agreeToTerms"
                            name="agreeToTerms"
                            checked={formData.agreeToTerms}
                            onChange={handleChange}
                            required
                        />
                        <label htmlFor="agreeToTerms">
                            <span className="terms-text">
                                {t('termsAgreement')}
                            </span>
                        </label>
                    </div>

                    <button type="submit" className="btn-primary">
                        <span className="btn-text">{t('signup')}</span>
                    </button>
                </form>

                <div className="auth-footer">
                    <p>
                        {t('alreadyHaveAccount')} <Link to="/login" className="login-link">{t('login')}</Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Signup; 