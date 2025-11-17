import { useCallback, useEffect, useState } from "react";
import useAxiosPrivate from "./useAxiosPrivate";

const DEFAULT_META = {
  total: 0,
  page: 1,
  size: 10,
  pages: 0,
  has_next: false,
  has_prev: false,
};

export const useGetAdminUsers = (params = {}) => {
  const axiosPrivate = useAxiosPrivate();
  const [users, setUsers] = useState([]);
  const [meta, setMeta] = useState(DEFAULT_META);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchUsers = useCallback(
    async (overrideParams = {}) => {
      try {
        setLoading(true);
        setError(null);

        const response = await axiosPrivate.get("/admin/users", {
          params: { ...params, ...overrideParams },
        });

        const {
          users: responseUsers = [],
          total = 0,
          page = 1,
          size = 10,
          pages = 0,
          has_next = false,
          has_prev = false,
        } = response.data || {};

        setUsers(responseUsers);
        setMeta({ total, page, size, pages, has_next, has_prev });
      } catch (err) {
        setError(err.response?.data?.detail || err.message || "Failed to fetch users");
      } finally {
        setLoading(false);
      }
    },
    [axiosPrivate, params]
  );

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return {
    users,
    ...meta,
    loading,
    error,
    refetch: fetchUsers,
  };
};

export const useGetAdminUser = (userUuid, options = { enabled: true }) => {
  const axiosPrivate = useAxiosPrivate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(options?.enabled));
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userUuid || options?.enabled === false) {
      setLoading(false);
      return;
    }

    const fetchUser = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await axiosPrivate.get(`/admin/users/${userUuid}`);
        setUser(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || err.message || "Failed to fetch user");
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [axiosPrivate, userUuid, options?.enabled]);

  return {
    user,
    loading,
    error,
    setUser,
  };
};

const createMutationHook = (mutationFn) => {
  return () => {
    const axiosPrivate = useAxiosPrivate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const mutate = useCallback(
      async (...args) => {
        try {
          setLoading(true);
          setError(null);
          return await mutationFn(axiosPrivate, ...args);
        } catch (err) {
          const message = err.response?.data?.detail || err.message || "Operation failed";
          setError(message);
          throw err;
        } finally {
          setLoading(false);
        }
      },
      [axiosPrivate]
    );

    return { mutate, loading, error };
  };
};

export const useUpdateAdminUser = createMutationHook((axiosPrivate, userUuid, payload) =>
  axiosPrivate.put(`/admin/users/${userUuid}`, payload)
);

export const useChangeUserRole = createMutationHook((axiosPrivate, userUuid, role, reason) =>
  axiosPrivate.patch(`/admin/users/${userUuid}/role`, reason ? { role, reason } : { role })
);

export const useToggleAdminUserStatus = createMutationHook((axiosPrivate, userUuid, isActive) =>
  axiosPrivate.patch(`/admin/users/${userUuid}/status`, { is_active: isActive })
);

export const useDeactivateAdminUser = createMutationHook((axiosPrivate, userUuid) =>
  axiosPrivate.delete(`/admin/users/${userUuid}`)
);

export const useAdminUserStats = () => {
  const axiosPrivate = useAxiosPrivate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.get("/admin/users/stats");
      setStats(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to fetch user stats");
    } finally {
      setLoading(false);
    }
  }, [axiosPrivate]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  };
};

