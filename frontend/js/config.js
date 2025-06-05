const config = {
    API_URL: process.env.API_URL || 'http://localhost:5001',
    ENV: process.env.NODE_ENV || 'development',
    UPLOAD_URL: process.env.API_URL ? `${process.env.API_URL}/uploads` : 'http://localhost:5000/uploads',
    DEFAULT_LANGUAGE: 'en',
    SUPPORTED_LANGUAGES: ['en', 'fr', 'es', 'hi'],
    MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
    ALLOWED_FILE_TYPES: ['image/jpeg', 'image/png', 'image/gif'],
    TOKEN_KEY: 'token',
    USER_KEY: 'user',
    LANGUAGE_KEY: 'language'
};

export default config; 