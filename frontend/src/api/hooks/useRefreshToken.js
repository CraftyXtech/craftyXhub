import { axiosPublic } from '../axios';
import { useAuth } from '../AuthProvider';

/**
 * Hook to refresh authentication token
 * Note: If backend doesn't support refresh tokens, this will just return null
 * and trigger a logout on 401
 */
const useRefreshToken = () => {
  const { auth, login, logout } = useAuth();

  const refresh = async () => {
    try {
      // Attempt to refresh token using existing token
      // Adjust endpoint based on your backend API
      const response = await axiosPublic.post('/auth/refresh', {}, {
        headers: {
          'Authorization': `Bearer ${auth?.accessToken}`
        }
      });

      const { access_token, user } = response.data;
      
      if (access_token) {
        login(access_token, user || auth?.user);
        return access_token;
      }
      
      return null;
    } catch (error) {
      console.error('Token refresh failed:', error);
      // If refresh fails, logout the user
      logout();
      return null;
    }
  };

  return refresh;
};

export default useRefreshToken;
