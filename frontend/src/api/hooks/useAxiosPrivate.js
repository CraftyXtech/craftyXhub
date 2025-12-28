import { useEffect } from 'react';
import { axiosPrivate } from '../axios';
import { useAuth } from '../AuthProvider';
import useRefreshToken from './useRefreshToken';

/**
 * Hook that returns an axios instance with auth token attached
 * Automatically refreshes token if needed
 */
const useAxiosPrivate = () => {
  const { auth, logout } = useAuth();
  const refresh = useRefreshToken();

  useEffect(() => {
    // Request interceptor - add current token
    const requestIntercept = axiosPrivate.interceptors.request.use(
      (config) => {
        if (!config.headers['Authorization'] && auth?.accessToken) {
          config.headers['Authorization'] = `Bearer ${auth.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle 401 and try refresh
    const responseIntercept = axiosPrivate.interceptors.response.use(
      (response) => response,
      async (error) => {
        const prevRequest = error?.config;
        
        if (error?.response?.status === 401 && !prevRequest?.sent) {
          prevRequest.sent = true;
          
          try {
            const newAccessToken = await refresh();
            if (newAccessToken) {
              prevRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
              return axiosPrivate(prevRequest);
            }
          } catch (refreshError) {
            // Refresh failed, logout user
            logout();
          }
        }
        
        return Promise.reject(error);
      }
    );

    // Cleanup interceptors on unmount
    return () => {
      axiosPrivate.interceptors.request.eject(requestIntercept);
      axiosPrivate.interceptors.response.eject(responseIntercept);
    };
  }, [auth, refresh, logout]);

  return axiosPrivate;
};

export default useAxiosPrivate;
