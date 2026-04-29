import { axiosPrivate, axiosPublic } from '../axios';

export const getPublicSettings = async () => {
  const response = await axiosPublic.get('/settings/public');
  return response.data;
};

export const getAdminSettings = async () => {
  const response = await axiosPrivate.get('/settings');
  return response.data;
};

export const updateAdminSettings = async (data) => {
  const response = await axiosPrivate.put('/settings', data);
  return response.data;
};
