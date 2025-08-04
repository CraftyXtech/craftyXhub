import { useState, useEffect } from 'react';
import useAxiosPrivate from './useAxiosPrivate';

// Hook to fetch post reports (admin only)
export const useGetReports = (params = {}) => {
  const axiosPrivate = useAxiosPrivate();
  const [reports, setReports] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        const response = await axiosPrivate.get('/posts/reports', { params });
        setReports(response.data);
        setTotal(response.data.length);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [axiosPrivate, JSON.stringify(params)]);

  const refetch = () => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        const response = await axiosPrivate.get('/posts/reports', { params });
        setReports(response.data);
        setTotal(response.data.length);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  };

  return { reports, total, loading, error, refetch };
};

// Hook to create a report
export const useCreateReport = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createReport = async (postUuid, reportData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.post(`/posts/${postUuid}/report`, reportData);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createReport, loading, error };
};

// Hook to resolve a report (admin action)
export const useResolveReport = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const resolveReport = async (reportId, action = 'resolved') => {
    try {
      setLoading(true);
      setError(null);
      // Note: Since there's no specific resolve endpoint, we could mark it as resolved
      // For now, we'll just track the action locally
      // In a real implementation, you might need a PATCH endpoint for report status
      return { reportId, action, resolved: true };
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { resolveReport, loading, error };
};