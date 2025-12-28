import { useState, useCallback } from 'react';
import { followUser, unfollowUser, getFollowers, getFollowing } from '../services/userService';

/**
 * Hook for managing follow/unfollow actions
 * @param {string} userUuid - UUID of the target user
 * @param {boolean} initialFollowState - Initial follow state
 * @returns {object} { isFollowing, isLoading, toggle, error }
 */
export const useFollow = (userUuid, initialFollowState = false) => {
  const [isFollowing, setIsFollowing] = useState(initialFollowState);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const toggle = useCallback(async () => {
    if (!userUuid) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      if (isFollowing) {
        await unfollowUser(userUuid);
        setIsFollowing(false);
      } else {
        await followUser(userUuid);
        setIsFollowing(true);
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to update follow status');
      // Revert optimistic update would go here if implemented
    } finally {
      setIsLoading(false);
    }
  }, [userUuid, isFollowing]);

  return { isFollowing, isLoading, toggle, error, setIsFollowing };
};

/**
 * Hook for fetching user followers
 * @param {string} userUuid - UUID of the user
 * @returns {object} { followers, total, isLoading, error, refetch }
 */
export const useFollowers = (userUuid) => {
  const [data, setData] = useState({ followers: [], total: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async (params = {}) => {
    if (!userUuid) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await getFollowers(userUuid, params);
      setData(result);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load followers');
    } finally {
      setIsLoading(false);
    }
  }, [userUuid]);

  return { ...data, isLoading, error, refetch: fetchData };
};

/**
 * Hook for fetching users that a user is following
 * @param {string} userUuid - UUID of the user
 * @returns {object} { following, total, isLoading, error, refetch }
 */
export const useFollowing = (userUuid) => {
  const [data, setData] = useState({ following: [], total: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async (params = {}) => {
    if (!userUuid) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await getFollowing(userUuid, params);
      setData(result);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load following');
    } finally {
      setIsLoading(false);
    }
  }, [userUuid]);

  return { ...data, isLoading, error, refetch: fetchData };
};
