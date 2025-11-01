import axios from './axios';

export const generate = async (tool_id, model, params, options = {}, axiosPrivate) => {
  const api = axiosPrivate || axios;
  const response = await api.post('ai/generate', {
    tool_id,
    model,
    params,
    tone: options.tone || 'professional',
    length: options.length || 'medium',
    language: options.language || 'en-US',
    creativity: options.creativity || 0.7,
    variant_count: options.variant_count || 1,
    stream: options.stream || false
  });
  return response.data;
};

export const saveDraft = async (draft, axiosPrivate) => {
  const api = axiosPrivate || axios;
  const response = await api.post('ai/drafts', draft);
  return response.data;
};

export const getDrafts = async (skip = 0, limit = 50, axiosPrivate) => {
  const api = axiosPrivate || axios;
  const response = await api.get(`ai/drafts?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const getDraftById = async (id, axiosPrivate) => {
  const api = axiosPrivate || axios;
  const response = await api.get(`ai/drafts/${id}`);
  return response.data;
};

export const updateDraft = async (id, updates, axiosPrivate) => {
  const api = axiosPrivate || axios;
  const response = await api.put(`ai/drafts/${id}`, updates);
  return response.data;
};

export const deleteDraft = async (id, axiosPrivate) => {
  const api = axiosPrivate || axios;
  await api.delete(`ai/drafts/${id}`);
};

export const getFavoriteDrafts = async (skip = 0, limit = 50, axiosPrivate) => {
  const api = axiosPrivate || axios;
  const response = await api.get(`ai/drafts/favorites?skip=${skip}&limit=${limit}`);
  return response.data;
};

