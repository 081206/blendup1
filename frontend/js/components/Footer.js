import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const Footer = () => {
    const { t } = useTranslation('common');

    return (
        <footer className="footer">
            <nav className="footer-nav">
                <div className="footer-section">
                    <h3>Company</h3>
                    <ul>
                        <li><Link to="/about">About Us</Link></li>
                        <li><Link to="/careers">Careers</Link></li>
                        <li><Link to="/press">Press</Link></li>
                    </ul>
                </div>

                <div className="footer-section">
                    <h3>Legal</h3>
                    <ul>
                        <li><Link to="/terms">Terms of Service</Link></li>
                        <li><Link to="/privacy">Privacy Policy</Link></li>
                        <li><Link to="/cookies">Cookie Policy</Link></li>
                    </ul>
                </div>

                <div className="footer-section">
                    <h3>Support</h3>
                    <ul>
                        <li><Link to="/safety">Safety Tips</Link></li>
                        <li><Link to="/help">Help Center</Link></li>
                        <li><Link to="/community">Community Guidelines</Link></li>
                    </ul>
                </div>

                <div className="footer-section social-links">
                    <h3>Connect</h3>
                    <ul>
                        <li><a href="https://facebook.com" target="_blank" rel="noopener noreferrer"><i className="fab fa-facebook"></i></a></li>
                        <li><a href="https://twitter.com" target="_blank" rel="noopener noreferrer"><i className="fab fa-twitter"></i></a></li>
                        <li><a href="https://instagram.com" target="_blank" rel="noopener noreferrer"><i className="fab fa-instagram"></i></a></li>
                        <li><a href="https://linkedin.com" target="_blank" rel="noopener noreferrer"><i className="fab fa-linkedin"></i></a></li>
                    </ul>
                </div>
            </nav>
        </footer>
    );
};

export default Footer; 