import { Navigate } from 'react-router-dom';
import useAuth from '../api/useAuth';
import { hasRole } from '../utils/roleUtils';

const RoleRoute = ({ children, allowedRoles }) => {
    const { auth } = useAuth();
    const userRole = auth?.user?.role;

    if (!userRole) {
        return <Navigate to="/login" replace />;
    }

    if (!hasRole(userRole, allowedRoles)) {
        return (
            <div className="nk-content">
                <div className="container-fluid">
                    <div className="nk-content-inner">
                        <div className="nk-content-body">
                            <div className="nk-block-head nk-block-head-sm">
                                <div className="nk-block-between">
                                    <div className="nk-block-head-content">
                                        <h3 className="nk-block-title page-title">Access Denied</h3>
                                        <div className="nk-block-des text-soft">
                                            <p>You don't have permission to access this page.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return children;
};

export default RoleRoute;

