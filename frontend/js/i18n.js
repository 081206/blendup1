import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translations
import common_en from '../lang/common.json';
import common_es from '../lang/es.json';
import common_fr from '../lang/fr.json';
import common_ta from '../lang/ta.json';

const resources = {
  en: {
    common: common_en
  },
  es: {
    common: common_es
  },
  fr: {
    common: common_fr
  },
  ta: {
    common: common_ta
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    
    interpolation: {
      escapeValue: false
    },

    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage']
    }
  });

export default i18n; 