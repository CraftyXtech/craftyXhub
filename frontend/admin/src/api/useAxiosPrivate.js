import { axiosPrivate } from "../api/axios";
import { useEffect } from "react";
import useAuth from "./useAuth";
import { useNavigate } from "react-router-dom";

const useAxiosPrivate = () => {
    const { auth, logout } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        const requestIntercept = axiosPrivate.interceptors.request.use(
            config => {
                if (!config.headers['Authorization'] && auth?.accessToken) {
                    config.headers['Authorization'] = `Bearer ${auth.accessToken}`;
                }
                return config;
            }, 
            (error) => Promise.reject(error)
        );

        const responseIntercept = axiosPrivate.interceptors.response.use(
            response => response,
            async (error) => {
                if (error?.response?.status === 401) {
                    // Token expired or invalid
                    logout();
                    navigate('/auth-login');
                }
                return Promise.reject(error);
            }
        );

        return () => {
            axiosPrivate.interceptors.request.eject(requestIntercept);
            axiosPrivate.interceptors.response.eject(responseIntercept);
        };
    }, [auth, logout, navigate]);

    return axiosPrivate;
};

export default useAxiosPrivate;