import { useEffect, useRef, useCallback, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { googleLogin, getCurrentUser } from '@/api';
import { useAuth } from '@/api/AuthProvider';
import { TOKEN_KEY } from '@/api/axios';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;
const GSI_SCRIPT_URL = 'https://accounts.google.com/gsi/client';

/**
 * Hook to handle Google Sign-In using Google Identity Services SDK.
 * No redirects — uses popup/One Tap on the client side.
 *
 * @returns {object} { googleButtonRef, loading, error }
 *   - googleButtonRef: attach to a <div> to render the official Google button
 *   - loading: true while processing the Google credential
 *   - error: error message if login failed
 */
export default function useGoogleSignIn() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const googleButtonRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const initializedRef = useRef(false);

  const from = location.state?.from?.pathname || '/dashboard';

  // Handle the credential response from Google
  const handleCredentialResponse = useCallback(
    async (response) => {
      setLoading(true);
      setError('');

      try {
        // Send the Google ID token to our backend
        const result = await googleLogin(response.credential);
        const token = result.access_token;

        // Store token so axiosPrivate can use it
        localStorage.setItem(TOKEN_KEY, token);

        // Fetch user data
        const userData = await getCurrentUser();

        // Store auth data in context
        login(token, userData);

        // Navigate to dashboard
        navigate(from, { replace: true });
      } catch (err) {
        console.error('Google login error:', err);
        localStorage.removeItem(TOKEN_KEY);

        if (err.response?.data?.detail) {
          setError(err.response.data.detail);
        } else {
          setError('Google sign-in failed. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    },
    [login, navigate, from]
  );

  // Load the Google Identity Services SDK and initialize
  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) {
      console.warn('VITE_GOOGLE_CLIENT_ID is not set — Google Sign-In disabled');
      return;
    }

    if (initializedRef.current) return;

    const initializeGSI = () => {
      if (!window.google?.accounts?.id) return;

      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: true,
      });

      // Render the Google button if ref is attached
      if (googleButtonRef.current) {
        window.google.accounts.id.renderButton(googleButtonRef.current, {
          type: 'standard',
          theme: 'outline',
          size: 'large',
          text: 'signin_with',
          shape: 'rectangular',
          width: googleButtonRef.current.offsetWidth || 300,
        });
      }

      initializedRef.current = true;
    };

    // Check if the script is already loaded
    if (window.google?.accounts?.id) {
      initializeGSI();
      return;
    }

    // Load the GIS script
    const existingScript = document.querySelector(
      `script[src="${GSI_SCRIPT_URL}"]`
    );

    if (existingScript) {
      existingScript.addEventListener('load', initializeGSI);
      return;
    }

    const script = document.createElement('script');
    script.src = GSI_SCRIPT_URL;
    script.async = true;
    script.defer = true;
    script.onload = initializeGSI;
    script.onerror = () => {
      console.error('Failed to load Google Identity Services SDK');
      setError('Failed to load Google Sign-In. Please try again later.');
    };
    document.head.appendChild(script);

    return () => {
      initializedRef.current = false;
    };
  }, [handleCredentialResponse]);

  return { googleButtonRef, loading, error };
}
