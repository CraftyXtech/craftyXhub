import React, { createContext, useState } from "react";


const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
    console.log(localStorage.getItem('token'));
    
    const token = localStorage.getItem('token')? localStorage.getItem('token'): null;

    console.log(token);
    const isAuthenticated = !!localStorage.getItem('token');
    
    const [auth, setAuth] = useState(JSON.parse(token));

    return (
        <AuthContext.Provider value={{ auth, setAuth,isAuthenticated  }}>
            {children}
        </AuthContext.Provider>
    )
}

export default AuthContext;
