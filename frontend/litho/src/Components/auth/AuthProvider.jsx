import React, { createContext, useState, useEffect, useContext } from "react";

const AuthContext = createContext({});

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

const isTokenExpired = (token) => {
    if (!token) return true;
    
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const currentTime = Date.now() / 1000;
        return payload.exp < currentTime;
    } catch (error) {
        return true;
    }
};

export const AuthProvider = ({ children }) => {
    const [auth, setAuth] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('craftyxhub_token');
        const userInfo = localStorage.getItem('craftyxhub_user');
        
        if (token && !isTokenExpired(token)) {
            try {
                const userData = userInfo ? JSON.parse(userInfo) : null;
                setAuth({
                    accessToken: token,
                    user: userData
                });
                setUser(userData);
                setIsAuthenticated(true);
            } catch (error) {
                console.error('Error parsing user info:', error);
                localStorage.removeItem('craftyxhub_token');
                localStorage.removeItem('craftyxhub_user');
            }
        } else {
            // Token expired or doesn't exist
            localStorage.removeItem('craftyxhub_token');
            localStorage.removeItem('craftyxhub_user');
        }
        setLoading(false);
    }, []);

    const login = (token, userData) => {
        localStorage.setItem('craftyxhub_token', token);
        localStorage.setItem('craftyxhub_user', JSON.stringify(userData));
        setAuth({
            accessToken: token,
            user: userData
        });
        setUser(userData);
        setIsAuthenticated(true);
    };

    const logout = () => {
        localStorage.removeItem('craftyxhub_token');
        localStorage.removeItem('craftyxhub_user');
        setAuth(null);
        setUser(null);
        setIsAuthenticated(false);
    };

    const updateUser = (userData) => {
        localStorage.setItem('craftyxhub_user', JSON.stringify(userData));
        setAuth(prev => ({
            ...prev,
            user: userData
        }));
        setUser(userData);
    };

    return (
        <AuthContext.Provider value={{ 
            auth, 
            user,
            setAuth, 
            isAuthenticated, 
            loading,
            login,
            logout,
            updateUser
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext; 