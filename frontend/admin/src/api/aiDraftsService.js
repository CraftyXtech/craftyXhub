import { axiosPrivate } from "@/api/axios";

export const aiDraftsService = {
  list: async ({ skip = 0, limit = 50 } = {}) => {
    const { data } = await axiosPrivate.get("ai/drafts", { params: { skip, limit } });
    return data;
  },
  create: async ({ name, content, tool_id = null, model_used = null, favorite = false, draft_metadata = null }) => {
    const payload = { name, content, tool_id, model_used, favorite, draft_metadata };
    const { data } = await axiosPrivate.post("ai/drafts", payload);
    return data;
  },
  update: async (uuid, updates) => {
    const { data } = await axiosPrivate.put(`ai/drafts/${uuid}`, updates);
    return data;
  },
  delete: async (uuid) => {
    await axiosPrivate.delete(`ai/drafts/${uuid}`);
    return true;
  },
};

export default aiDraftsService;
