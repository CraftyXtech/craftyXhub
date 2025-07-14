import { Navigate } from 'react-router-dom';
import useAuth from '../api/useAuth';
import { isTokenExpired } from '../api/isTokenExpired';

const PrivateRoute = ({ children }) => {
    const { auth, isAuthenticated } = useAuth();

    if (!auth?.accessToken || isTokenExpired(auth?.accessToken)) {
        return <Navigate to="/login" replace />;
    }

    if (auth?.otpRequired == "1") {
        return <Navigate to="/otp" replace />;
    }

    return isAuthenticated ? children : <Navigate to="/login" replace />;
};

export default PrivateRoute;