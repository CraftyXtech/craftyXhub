import { axiosPublic } from '../axios';

export const subscribeToNewsletter = async ({ email, source = 'homepage' }) => {
  const response = await axiosPublic.post('/newsletter/subscribe', {
    email,
    source,
  });
  return response.data;
};
