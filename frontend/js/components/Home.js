import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const Home = () => {
    const { t } = useTranslation('common');

    return (
        <div className="home-page">
            <section className="hero-section">
                <div className="hero-content">
                    <h1>Welcome to Blendup</h1>
                    <p className="hero-subtitle">Sign in to connect with amazing people</p>
                    <div className="cta-buttons">
                        <Link to="/login" className="btn-primary">Sign In</Link>
                    </div>
                </div>
                <div className="hero-image">
                    <img src="/images/hero-image.png" alt="Blendup" />
                </div>
            </section>

            <section className="features-section">
                <h2>Why Choose Blendup?</h2>
                <div className="features-grid">
                    <div className="feature-card">
                        <i className="fas fa-users"></i>
                        <h3>Connect</h3>
                        <p>Find and connect with people who share your interests</p>
                    </div>
                    <div className="feature-card">
                        <i className="fas fa-shield-alt"></i>
                        <h3>Safe & Secure</h3>
                        <p>Your privacy and security are our top priorities</p>
                    </div>
                    <div className="feature-card">
                        <i className="fas fa-globe"></i>
                        <h3>Global Community</h3>
                        <p>Join a diverse community from around the world</p>
                    </div>
                </div>
            </section>

            <section className="success-stories">
                <h2>Success Stories</h2>
                <div className="stories-grid">
                    <div className="story-card">
                        <img src="/images/story1.jpg" alt="Success Story" />
                        <h3>Sarah & John</h3>
                        <p>"We found each other on Blendup and it changed our lives forever."</p>
                    </div>
                    <div className="story-card">
                        <img src="/images/story2.jpg" alt="Success Story" />
                        <h3>Mike & Lisa</h3>
                        <p>"Blendup helped us connect despite being miles apart."</p>
                    </div>
                    <div className="story-card">
                        <img src="/images/story3.jpg" alt="Success Story" />
                        <h3>David & Emma</h3>
                        <p>"The perfect platform to find meaningful connections."</p>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Home; 