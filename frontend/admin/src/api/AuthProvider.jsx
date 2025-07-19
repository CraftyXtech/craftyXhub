import React, { createContext, useState, useEffect, useContext } from "react";
import { isTokenExpired } from "./isTokenExpired";

const AuthContext = createContext({});

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [auth, setAuth] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        const userInfo = localStorage.getItem('userInfo');
        
        if (token && !isTokenExpired(token)) {
            try {
                const user = userInfo ? JSON.parse(userInfo) : null;
                setAuth({
                    accessToken: token,
                    user: user
                });
                setIsAuthenticated(true);
            } catch (error) {
                console.error('Error parsing user info:', error);
                localStorage.removeItem('accessToken');
                localStorage.removeItem('userInfo');
            }
        } else {
            // Token expired or doesn't exist
            localStorage.removeItem('accessToken');
            localStorage.removeItem('userInfo');
        }
        setLoading(false);
    }, []);

    const login = (token, user) => {
        localStorage.setItem('accessToken', token);
        localStorage.setItem('userInfo', JSON.stringify(user));
        setAuth({
            accessToken: token,
            user: user
        });
        setIsAuthenticated(true);
    };

    const logout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('userInfo');
        setAuth(null);
        setIsAuthenticated(false);
    };

    return (
        <AuthContext.Provider value={{ 
            auth, 
            setAuth, 
            isAuthenticated, 
            loading,
            login,
            logout
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;