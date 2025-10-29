const STORAGE_KEY = 'ai_documents';

export const aiDocumentStorage = {
  getAll: () => {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error reading AI documents:', error);
      return [];
    }
  },

  getById: (id) => {
    const documents = aiDocumentStorage.getAll();
    return documents.find((doc) => doc.id === id);
  },

  save: (document) => {
    try {
      const documents = aiDocumentStorage.getAll();
      const existingIndex = documents.findIndex((doc) => doc.id === document.id);

      if (existingIndex >= 0) {
        documents[existingIndex] = {
          ...documents[existingIndex],
          ...document,
          updated_at: new Date().toISOString(),
        };
      } else {
        documents.push({
          ...document,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      }

      localStorage.setItem(STORAGE_KEY, JSON.stringify(documents));
      return document;
    } catch (error) {
      console.error('Error saving AI document:', error);
      throw error;
    }
  },

  update: (id, updates) => {
    try {
      const documents = aiDocumentStorage.getAll();
      const idx = documents.findIndex((doc) => doc.id === id);
      if (idx === -1) throw new Error('Document not found');

      documents[idx] = {
        ...documents[idx],
        ...updates,
        updated_at: new Date().toISOString(),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(documents));
      return documents[idx];
    } catch (error) {
      console.error('Error updating AI document:', error);
      throw error;
    }
  },

  delete: (id) => {
    try {
      const documents = aiDocumentStorage.getAll();
      const filtered = documents.filter((d) => d.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
      return true;
    } catch (error) {
      console.error('Error deleting AI document:', error);
      throw error;
    }
  },

  deleteMultiple: (ids) => {
    try {
      const documents = aiDocumentStorage.getAll();
      const filtered = documents.filter((d) => !ids.includes(d.id));
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
      return true;
    } catch (error) {
      console.error('Error deleting AI documents:', error);
      throw error;
    }
  },

  clear: () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
      return true;
    } catch (error) {
      console.error('Error clearing AI documents:', error);
      throw error;
    }
  },

  export: () => {
    const documents = aiDocumentStorage.getAll();
    const dataStr = JSON.stringify(documents, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ai-documents-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  },

  import: (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const documents = JSON.parse(e.target.result);
          localStorage.setItem(STORAGE_KEY, JSON.stringify(documents));
          resolve(documents);
        } catch (err) {
          reject(err);
        }
      };
      reader.onerror = reject;
      reader.readAsText(file);
    });
  },
};



