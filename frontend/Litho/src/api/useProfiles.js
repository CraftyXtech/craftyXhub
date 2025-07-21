import { useState, useEffect, useCallback } from 'react';
import { getProfile, createProfile, updateProfile, deleteProfile } from './profilesService';

// Hook to get a profile by user UUID (public read)
export const useProfile = (userUuid) => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchProfile = useCallback(async () => {
        if (!userUuid) {
            setProfile(null);
            setLoading(false);
            return;
        }

        try {
            setLoading(true);
            const data = await getProfile(userUuid);
            setProfile(data);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            setProfile(null);
        } finally {
            setLoading(false);
        }
    }, [userUuid]);

    useEffect(() => {
        fetchProfile();
    }, [fetchProfile]);

    return { profile, loading, error, refetch: fetchProfile };
};

// Hook to create a profile (authenticated)
export const useCreateProfile = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const createProfileHandler = useCallback(async (profileData) => {
        try {
            setLoading(true);
            setError(null);
            setSuccess(false);
            
            const result = await createProfile(profileData);
            setSuccess(true);
            return result;
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return { createProfile: createProfileHandler, loading, error, success };
};

// Hook to update a profile (authenticated)
export const useUpdateProfile = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const updateProfileHandler = useCallback(async (userUuid, profileData) => {
        try {
            setLoading(true);
            setError(null);
            setSuccess(false);
            
            const result = await updateProfile(userUuid, profileData);
            setSuccess(true);
            return result;
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return { updateProfile: updateProfileHandler, loading, error, success };
};

// Hook to delete a profile (authenticated)
export const useDeleteProfile = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const deleteProfileHandler = useCallback(async (userUuid) => {
        try {
            setLoading(true);
            setError(null);
            setSuccess(false);
            
            const result = await deleteProfile(userUuid);
            setSuccess(true);
            return result;
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return { deleteProfile: deleteProfileHandler, loading, error, success };
}; 