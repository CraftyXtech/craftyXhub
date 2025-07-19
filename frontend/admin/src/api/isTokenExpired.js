import { jwtDecode } from 'jwt-decode';

export const isTokenExpired = (token) => {
  if (!token) return true;

  try {
    const { exp } = jwtDecode(token);
    if (!exp) return true;

    const currentTime = Math.floor(Date.now() / 1000); // current time in seconds
    return exp < currentTime;
  } catch (error) {
    console.error('Invalid token:', error);
    return true;
  }
};