import { useContext, useDebugValue } from "react";
import AuthContext from "./AuthProvider";

const useAuth = () => {
    const { auth, isAuthenticated } = useContext(AuthContext);
    useDebugValue(auth, auth => auth?.username ? "Logged In" : "Logged Out")
    return useContext(AuthContext);
}

export default useAuth;