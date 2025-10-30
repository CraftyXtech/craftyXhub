const STORAGE_KEY = 'ai_drafts';

// Migrate old data from ai_documents to ai_drafts (one-time)
const migrateOldData = () => {
  const oldData = localStorage.getItem('ai_documents');
  if (oldData && !localStorage.getItem('ai_drafts')) {
    localStorage.setItem('ai_drafts', oldData);
    console.log('✅ Migrated old documents to drafts');
  }
};

// Run migration on module load
migrateOldData();

export const aiDraftStorage = {
  getAll: () => {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error reading AI drafts:', error);
      return [];
    }
  },

  getById: (id) => {
    const drafts = aiDraftStorage.getAll();
    return drafts.find((draft) => draft.id === id);
  },

  save: (draft) => {
    try {
      const drafts = aiDraftStorage.getAll();
      const existingIndex = drafts.findIndex((d) => d.id === draft.id);

      if (existingIndex >= 0) {
        drafts[existingIndex] = {
          ...drafts[existingIndex],
          ...draft,
          updated_at: new Date().toISOString(),
        };
      } else {
        drafts.push({
          ...draft,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      }

      localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
      return draft;
    } catch (error) {
      console.error('Error saving AI draft:', error);
      throw error;
    }
  },

  update: (id, updates) => {
    try {
      const drafts = aiDraftStorage.getAll();
      const idx = drafts.findIndex((draft) => draft.id === id);
      if (idx === -1) throw new Error('Draft not found');

      drafts[idx] = {
        ...drafts[idx],
        ...updates,
        updated_at: new Date().toISOString(),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
      return drafts[idx];
    } catch (error) {
      console.error('Error updating AI draft:', error);
      throw error;
    }
  },

  delete: (id) => {
    try {
      const drafts = aiDraftStorage.getAll();
      const filtered = drafts.filter((d) => d.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
      return true;
    } catch (error) {
      console.error('Error deleting AI draft:', error);
      throw error;
    }
  },

  deleteMultiple: (ids) => {
    try {
      const drafts = aiDraftStorage.getAll();
      const filtered = drafts.filter((d) => !ids.includes(d.id));
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
      return true;
    } catch (error) {
      console.error('Error deleting AI drafts:', error);
      throw error;
    }
  },

  clear: () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
      return true;
    } catch (error) {
      console.error('Error clearing AI drafts:', error);
      throw error;
    }
  },

  export: () => {
    const drafts = aiDraftStorage.getAll();
    const dataStr = JSON.stringify(drafts, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ai-drafts-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  },

  import: (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const drafts = JSON.parse(e.target.result);
          localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
          resolve(drafts);
        } catch (err) {
          reject(err);
        }
      };
      reader.onerror = reject;
      reader.readAsText(file);
    });
  },
};





