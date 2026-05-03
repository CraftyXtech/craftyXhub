const toIdString = (value) => (value === null || value === undefined || value === '' ? '' : String(value));

const flattenCategories = (categories = []) => {
  const byId = new Map();

  const visit = (category, parentId = null) => {
    if (!category?.id) return;
    const normalized = {
      ...category,
      id: category.id,
      parent_id: category.parent_id ?? parentId ?? null,
      subcategories: Array.isArray(category.subcategories) ? category.subcategories : [],
    };
    byId.set(normalized.id, normalized);
    normalized.subcategories.forEach((sub) => visit(sub, normalized.id));
  };

  categories.forEach((category) => visit(category));
  return byId;
};

const lineageForCategory = (categoryId, categoriesById) => {
  const lineage = new Set();
  let currentId = toIdString(categoryId);

  while (currentId && !lineage.has(currentId)) {
    lineage.add(currentId);
    const current = categoriesById.get(Number(currentId)) || categoriesById.get(currentId);
    currentId = toIdString(current?.parent_id);
  }

  return lineage;
};

export const getAllowedTagsForCategory = (categoryId, categories = [], tags = []) => {
  const normalizedCategoryId = toIdString(categoryId);
  if (!normalizedCategoryId) {
    return tags;
  }

  const categoriesById = flattenCategories(categories);
  const selectedLineage = lineageForCategory(normalizedCategoryId, categoriesById);
  if (!selectedLineage.size) {
    return [];
  }

  return tags.filter((tag) => {
    const tagCategoryId = toIdString(tag?.category_id);
    if (!tagCategoryId) {
      return true;
    }
    const tagLineage = lineageForCategory(tagCategoryId, categoriesById);
    return tagLineage.has(normalizedCategoryId) || selectedLineage.has(tagCategoryId);
  });
};

export const filterTagIdsForCategory = (tagIds = [], categoryId, categories = [], tags = []) => {
  if (!Array.isArray(tagIds) || tagIds.length === 0) {
    return [];
  }

  const allowedTagIds = new Set(
    getAllowedTagsForCategory(categoryId, categories, tags).map((tag) => tag.id)
  );
  return tagIds.filter((tagId) => allowedTagIds.has(tagId));
};
