import { axiosPrivate } from "@/api/axios";

export const aiWriterService = {
  generate: async ({
    template_id,
    params = {},
    prompt,
    keywords,
    tone = "professional",
    language = "en-US",
    length = "medium",
    variant_count = 1,
    creativity = 0.7,
    model = "openai",
  }) => {
    const payload = {
      template_id,
      model,
      params,
      prompt,
      keywords,
      tone,
      length,
      language,
      creativity,
      variant_count,
    };
    const { data } = await axiosPrivate.post("ai/generate", payload);
    return data?.variants ?? [];
  },
};

export default aiWriterService;
