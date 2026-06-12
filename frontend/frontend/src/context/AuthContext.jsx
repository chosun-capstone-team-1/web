import { createContext, useState } from 'react';
import { isLoggedIn as checkLoginStatus } from '../utils/isLoggedIn';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(checkLoginStatus());

  const login = () => {
    localStorage.setItem('access_token', 'mock_token_value');
    setIsLoggedIn(true);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setIsLoggedIn(false);
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
