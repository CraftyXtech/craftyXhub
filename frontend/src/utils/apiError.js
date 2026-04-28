export const getApiErrorMessage = (error, fallback = 'Something went wrong') => {
  const detail = error?.response?.data?.detail;

  if (!detail) {
    return error?.message || fallback;
  }

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.message || item?.msg || String(item))
      .filter(Boolean)
      .join(' ');
  }

  if (typeof detail === 'object') {
    const messages = [
      detail.message,
      ...(detail.critical_failures || []),
      ...(detail.warnings || []),
      ...(detail.errors || []).map((item) => item?.message || item?.msg)
    ].filter(Boolean);

    return messages.length ? messages.join(' ') : fallback;
  }

  return fallback;
};
