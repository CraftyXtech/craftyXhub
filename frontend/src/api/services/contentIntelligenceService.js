import { axiosPrivate } from '../axios';

const BASE = '/content-intelligence';

export const createContentSource = async (payload) => {
  const response = await axiosPrivate.post(`${BASE}/sources`, payload);
  return response.data;
};

export const getContentSources = async () => {
  const response = await axiosPrivate.get(`${BASE}/sources`);
  return response.data;
};

export const importSearchConsoleRows = async (rows) => {
  const response = await axiosPrivate.post(`${BASE}/imports/search-console`, rows);
  return response.data;
};

export const importTrendingRows = async (rows) => {
  const response = await axiosPrivate.post(`${BASE}/imports/trending`, rows);
  return response.data;
};

export const generateTopicBriefs = async (options = {}) => {
  const response = await axiosPrivate.post(`${BASE}/briefs/generate`, {
    limit: 10,
    include_rss: true,
    include_imports: true,
    include_site_search: true,
    include_content_gaps: true,
    ...options,
  }, {
    timeout: 60000,
  });
  return response.data;
};

export const getTopicBriefs = async ({ status = 'pending', limit = 50 } = {}) => {
  const response = await axiosPrivate.get(`${BASE}/briefs`, {
    params: { status, limit },
  });
  return response.data;
};

export const updateTopicBriefStatus = async (briefUuid, status) => {
  const response = await axiosPrivate.put(`${BASE}/briefs/${briefUuid}/status`, { status });
  return response.data;
};

export const getPostIntelligenceStatuses = async (postUuids) => {
  if (!postUuids?.length) return {};
  const response = await axiosPrivate.get(`${BASE}/posts/statuses`, {
    params: { post_uuids: postUuids.join(',') },
  });
  return response.data?.statuses || {};
};

export const runPostQualityReview = async (postUuid) => {
  const response = await axiosPrivate.post(`${BASE}/posts/${postUuid}/quality-review`, null, {
    timeout: 120000,
  });
  return response.data;
};

export const getLatestPostQualityReview = async (postUuid) => {
  const response = await axiosPrivate.get(`${BASE}/posts/${postUuid}/quality-review`);
  return response.data;
};

export const approvePostQualityOverride = async (postUuid, overrideReason) => {
  const response = await axiosPrivate.put(`${BASE}/posts/${postUuid}/quality-review/override`, {
    override_reason: overrideReason,
  });
  return response.data;
};

export const generateDistributionAssets = async (postUuid) => {
  const response = await axiosPrivate.post(`${BASE}/posts/${postUuid}/distribution`, null, {
    timeout: 120000,
  });
  return response.data;
};

export const getDistributionAssets = async (postUuid) => {
  const response = await axiosPrivate.get(`${BASE}/posts/${postUuid}/distribution`);
  return response.data;
};

export const updateDistributionAssetStatus = async (assetUuid, status) => {
  const response = await axiosPrivate.put(`${BASE}/distribution/${assetUuid}/status`, { status });
  return response.data;
};
