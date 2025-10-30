import React, { createContext, useState, useEffect, useContext } from 'react';
import * as aiService from '../api/aiService';
import useAxiosPrivate from '../api/useAxiosPrivate';

const AiDraftContext = createContext();

export const AiDraftProvider = ({ children }) => {
  const axiosPrivate = useAxiosPrivate();
  const [drafts, setDrafts] = useState([]);
  const [localDrafts, setLocalDrafts] = useState([]);
  const [syncing, setSyncing] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    setIsAuthenticated(!!token);
  }, []);

  useEffect(() => {
    const local = JSON.parse(localStorage.getItem('ai-drafts') || '[]');
    setLocalDrafts(local);
    if (!isAuthenticated) {
      setDrafts(local);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      syncFromServer();
    }
  }, [isAuthenticated]);

  const syncFromServer = async () => {
    if (!isAuthenticated) return;
    
    setSyncing(true);
    try {
      const response = await aiService.getDrafts(0, 100, axiosPrivate);
      const serverDrafts = response.drafts || [];
      setDrafts(serverDrafts);
      
      const merged = mergeDrafts(serverDrafts, localDrafts);
      localStorage.setItem('ai-drafts', JSON.stringify(merged));
    } catch (error) {
      console.error('Sync failed:', error);
      setDrafts(localDrafts);
    } finally {
      setSyncing(false);
    }
  };

  const mergeDrafts = (serverDrafts, localDrafts) => {
    const serverMap = new Map(serverDrafts.map(d => [d.uuid, d]));
    const merged = [...serverDrafts];

    localDrafts.forEach(localDraft => {
      if (!serverMap.has(localDraft.uuid)) {
        merged.push(localDraft);
      }
    });

    return merged;
  };

  const autosave = (draft) => {
    const updated = [...localDrafts];
    const index = updated.findIndex(d => d.uuid === draft.uuid || d.id === draft.id);
    
    if (index >= 0) {
      updated[index] = draft;
    } else {
      updated.push(draft);
    }
    
    setLocalDrafts(updated);
    localStorage.setItem('ai-drafts', JSON.stringify(updated));
    
    if (!isAuthenticated) {
      setDrafts(updated);
    }
  };

  const saveDraft = async (draft) => {
    autosave(draft);

    if (isAuthenticated) {
      try {
        const saved = await aiService.saveDraft(draft, axiosPrivate);
        setDrafts(prev => {
          const filtered = prev.filter(d => d.id !== saved.id && d.uuid !== saved.uuid);
          return [...filtered, saved];
        });
        return saved;
      } catch (error) {
        console.error('Save to server failed:', error);
        throw error;
      }
    }
    
    return draft;
  };

  const updateDraft = async (id, updates) => {
    if (isAuthenticated) {
      try {
        const updated = await aiService.updateDraft(id, updates, axiosPrivate);
        setDrafts(prev => prev.map(d => d.id === id ? updated : d));
        
        const localUpdated = localDrafts.map(d => d.id === id ? updated : d);
        setLocalDrafts(localUpdated);
        localStorage.setItem('ai-drafts', JSON.stringify(localUpdated));
        
        return updated;
      } catch (error) {
        console.error('Update failed:', error);
        throw error;
      }
    } else {
      const localUpdated = localDrafts.map(d => 
        d.id === id || d.uuid === id ? { ...d, ...updates } : d
      );
      setLocalDrafts(localUpdated);
      setDrafts(localUpdated);
      localStorage.setItem('ai-drafts', JSON.stringify(localUpdated));
      return localUpdated.find(d => d.id === id || d.uuid === id);
    }
  };

  const deleteDraft = async (id) => {
    if (isAuthenticated) {
      try {
        await aiService.deleteDraft(id, axiosPrivate);
        setDrafts(prev => prev.filter(d => d.id !== id));
        
        const localFiltered = localDrafts.filter(d => d.id !== id && d.uuid !== id);
        setLocalDrafts(localFiltered);
        localStorage.setItem('ai-drafts', JSON.stringify(localFiltered));
      } catch (error) {
        console.error('Delete failed:', error);
        throw error;
      }
    } else {
      const localFiltered = localDrafts.filter(d => d.id !== id && d.uuid !== id);
      setLocalDrafts(localFiltered);
      setDrafts(localFiltered);
      localStorage.setItem('ai-drafts', JSON.stringify(localFiltered));
    }
  };

  const getDraftById = (id) => {
    return drafts.find(d => d.id === parseInt(id) || d.uuid === id);
  };

  const getStats = () => {
    const totalWords = drafts.reduce((sum, draft) => {
      const metadata = typeof draft.metadata === 'string' ? JSON.parse(draft.metadata) : draft.metadata;
      return sum + (metadata?.words || 0);
    }, 0);

    const draftsByType = {};
    drafts.forEach(draft => {
      const type = draft.template_id || 'other';
      draftsByType[type] = (draftsByType[type] || 0) + 1;
    });

    return {
      totalDrafts: drafts.length,
      totalWords,
      draftsByType
    };
  };

  const duplicateDraft = async (id) => {
    const draft = getDraftById(id);
    if (!draft) return;

    const duplicated = {
      ...draft,
      id: undefined,
      uuid: undefined,
      name: `${draft.name} (Copy)`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    return await saveDraft(duplicated);
  };

  const exportDrafts = () => {
    const dataStr = JSON.stringify(drafts, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ai-drafts-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <AiDraftContext.Provider
      value={{
        drafts,
        autosave,
        saveDraft,
        updateDraft,
        deleteDraft,
        getDraftById,
        getStats,
        duplicateDraft,
        exportDrafts,
        syncFromServer,
        syncing,
        isAuthenticated
      }}
    >
      {children}
    </AiDraftContext.Provider>
  );
};

export const useAiDrafts = () => {
  const context = useContext(AiDraftContext);
  if (!context) {
    throw new Error('useAiDrafts must be used within an AiDraftProvider');
  }
  return context;
};

