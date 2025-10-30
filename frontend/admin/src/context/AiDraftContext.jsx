import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { aiDraftStorage } from '../utils/aiDraftStorage';
import { toast } from 'react-toastify';

const AiDraftContext = createContext();

export const useAiDrafts = () => {
  const context = useContext(AiDraftContext);
  if (!context) {
    throw new Error('useAiDrafts must be used within AiDraftProvider');
  }
  return context;
};

export const AiDraftProvider = ({ children }) => {
  const [drafts, setDrafts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDraft, setSelectedDraft] = useState(null);

  const loadDrafts = useCallback(() => {
    try {
      const docs = aiDraftStorage.getAll();
      setDrafts(docs);
    } catch (error) {
      console.error('Error loading drafts:', error);
      toast.error('Failed to load drafts');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDrafts();
  }, [loadDrafts]);

  const addDraft = useCallback((draft) => {
    try {
      const newDraft = {
        id: `draft_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        ...draft,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      aiDraftStorage.save(newDraft);
      setDrafts(prev => [newDraft, ...prev]);
      toast.success('Draft saved successfully');
      return newDraft;
    } catch (error) {
      console.error('Error adding draft:', error);
      toast.error('Failed to save draft');
      throw error;
    }
  }, []);

  const updateDraft = useCallback((id, updates) => {
    try {
      const updated = aiDraftStorage.update(id, updates);
      setDrafts(prev =>
        prev.map(draft => (draft.id === id ? updated : draft))
      );
      toast.success('Draft updated successfully');
      return updated;
    } catch (error) {
      console.error('Error updating draft:', error);
      toast.error('Failed to update draft');
      throw error;
    }
  }, []);

  const deleteDraft = useCallback((id) => {
    try {
      aiDraftStorage.delete(id);
      setDrafts(prev => prev.filter(draft => draft.id !== id));
      if (selectedDraft?.id === id) {
        setSelectedDraft(null);
      }
      toast.success('Draft deleted successfully');
    } catch (error) {
      console.error('Error deleting draft:', error);
      toast.error('Failed to delete draft');
      throw error;
    }
  }, [selectedDraft]);

  const deleteMultipleDrafts = useCallback((ids) => {
    try {
      aiDraftStorage.deleteMultiple(ids);
      setDrafts(prev => prev.filter(draft => !ids.includes(draft.id)));
      if (selectedDraft && ids.includes(selectedDraft.id)) {
        setSelectedDraft(null);
      }
      toast.success(`${ids.length} draft(s) deleted successfully`);
    } catch (error) {
      console.error('Error deleting drafts:', error);
      toast.error('Failed to delete drafts');
      throw error;
    }
  }, [selectedDraft]);

  const duplicateDraft = useCallback((id) => {
    try {
      const original = drafts.find(draft => draft.id === id);
      if (!original) {
        throw new Error('Draft not found');
      }

      const duplicate = {
        ...original,
        id: `draft_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: `${original.name} (Copy)`,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      aiDraftStorage.save(duplicate);
      setDrafts(prev => [duplicate, ...prev]);
      toast.success('Draft duplicated successfully');
      return duplicate;
    } catch (error) {
      console.error('Error duplicating draft:', error);
      toast.error('Failed to duplicate draft');
      throw error;
    }
  }, [drafts]);

  const getDraftById = useCallback((id) => {
    return drafts.find(draft => draft.id === id);
  }, [drafts]);

  const exportDrafts = useCallback(() => {
    try {
      aiDraftStorage.export();
      toast.success('Drafts exported successfully');
    } catch (error) {
      console.error('Error exporting drafts:', error);
      toast.error('Failed to export drafts');
    }
  }, []);

  const importDrafts = useCallback(async (file) => {
    try {
      const imported = await aiDraftStorage.import(file);
      setDrafts(imported);
      toast.success(`${imported.length} draft(s) imported successfully`);
      return imported;
    } catch (error) {
      console.error('Error importing drafts:', error);
      toast.error('Failed to import drafts');
      throw error;
    }
  }, []);

  const getStats = useCallback(() => {
    const totalDrafts = drafts.length;
    const totalWords = drafts.reduce((sum, draft) => sum + (draft.metadata?.words || 0), 0);
    const recentDrafts = drafts.filter(draft => {
      const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
      return new Date(draft.created_at) > dayAgo;
    }).length;

    const typeCount = drafts.reduce((acc, draft) => {
      const type = draft.type || 'blog_post';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {});

    return {
      totalDrafts,
      totalWords,
      recentDrafts,
      draftsByType: typeCount
    };
  }, [drafts]);

  const value = {
    drafts,
    loading,
    selectedDraft,
    setSelectedDraft,
    addDraft,
    updateDraft,
    deleteDraft,
    deleteMultipleDrafts,
    duplicateDraft,
    getDraftById,
    exportDrafts,
    importDrafts,
    getStats,
    refreshDrafts: loadDrafts
  };

  return (
    <AiDraftContext.Provider value={value}>
      {children}
    </AiDraftContext.Provider>
  );
};

