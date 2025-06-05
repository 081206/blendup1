import React from 'react';
import { Routes, Route } from 'react-router-dom';
import LanguageSwitcher from './components/LanguageSwitcher';
import Home from './components/Home';
import Login from './components/Login';
import Signup from './components/Signup';
import Settings from './components/Settings';
import Profile from './components/Profile';
import Footer from './components/Footer';

function App() {
  return (
    <div className="app">
      <LanguageSwitcher />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;

                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<Signup />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="/" element={<Login />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
