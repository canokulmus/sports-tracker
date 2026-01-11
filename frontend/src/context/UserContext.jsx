import { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

const UserContext = createContext(null);

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const restoreSession = async () => {
      const storedUser = localStorage.getItem('sports_tracker_user');
      if (storedUser) {
        try {
          const parsedUser = JSON.parse(storedUser);
          await authApi.login(parsedUser.username);
          setUser(parsedUser);
        } catch (error) {
          console.error('Failed to restore user session:', error);
          localStorage.removeItem('sports_tracker_user');
        }
      }
      setIsLoading(false);
    };
    restoreSession();
  }, []);

  const login = (username) => {
    const userData = { username };
    setUser(userData);
    localStorage.setItem('sports_tracker_user', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('sports_tracker_user');
  };

  return (
    <UserContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}
