import React from 'react';
import { useTranslation } from 'react-i18next';

const LanguageSwitcher = () => {
    const { i18n } = useTranslation();

    const changeLanguage = (lng) => {
        i18n.changeLanguage(lng);
    };

    return (
        <div className="language-switcher">
            <button
                className={`lang-btn ${i18n.language === 'en' ? 'active' : ''}`}
                onClick={() => changeLanguage('en')}
            >
                EN
            </button>
            <button
                className={`lang-btn ${i18n.language === 'es' ? 'active' : ''}`}
                onClick={() => changeLanguage('es')}
            >
                ES
            </button>
            <button
                className={`lang-btn ${i18n.language === 'fr' ? 'active' : ''}`}
                onClick={() => changeLanguage('fr')}
            >
                FR
            </button>
            <button
                className={`lang-btn ${i18n.language === 'ta' ? 'active' : ''}`}
                onClick={() => changeLanguage('ta')}
            >
                TA
            </button>
        </div>
    );
};

export default LanguageSwitcher; 