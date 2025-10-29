import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { aiDocumentStorage } from '../utils/aiDocumentStorage';
import { toast } from 'react-toastify';

const AiDocumentContext = createContext();

export const useAiDocuments = () => {
  const context = useContext(AiDocumentContext);
  if (!context) {
    throw new Error('useAiDocuments must be used within AiDocumentProvider');
  }
  return context;
};

export const AiDocumentProvider = ({ children }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDocument, setSelectedDocument] = useState(null);

  const loadDocuments = useCallback(() => {
    try {
      const docs = aiDocumentStorage.getAll();
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading documents:', error);
      toast.error('Failed to load documents');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const addDocument = useCallback((document) => {
    try {
      const newDoc = {
        id: `doc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        ...document,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      aiDocumentStorage.save(newDoc);
      setDocuments(prev => [newDoc, ...prev]);
      toast.success('Document created successfully');
      return newDoc;
    } catch (error) {
      console.error('Error adding document:', error);
      toast.error('Failed to create document');
      throw error;
    }
  }, []);

  const updateDocument = useCallback((id, updates) => {
    try {
      const updated = aiDocumentStorage.update(id, updates);
      setDocuments(prev =>
        prev.map(doc => (doc.id === id ? updated : doc))
      );
      toast.success('Document updated successfully');
      return updated;
    } catch (error) {
      console.error('Error updating document:', error);
      toast.error('Failed to update document');
      throw error;
    }
  }, []);

  const deleteDocument = useCallback((id) => {
    try {
      aiDocumentStorage.delete(id);
      setDocuments(prev => prev.filter(doc => doc.id !== id));
      if (selectedDocument?.id === id) {
        setSelectedDocument(null);
      }
      toast.success('Document deleted successfully');
    } catch (error) {
      console.error('Error deleting document:', error);
      toast.error('Failed to delete document');
      throw error;
    }
  }, [selectedDocument]);

  const deleteMultipleDocuments = useCallback((ids) => {
    try {
      aiDocumentStorage.deleteMultiple(ids);
      setDocuments(prev => prev.filter(doc => !ids.includes(doc.id)));
      if (selectedDocument && ids.includes(selectedDocument.id)) {
        setSelectedDocument(null);
      }
      toast.success(`${ids.length} document(s) deleted successfully`);
    } catch (error) {
      console.error('Error deleting documents:', error);
      toast.error('Failed to delete documents');
      throw error;
    }
  }, [selectedDocument]);

  const duplicateDocument = useCallback((id) => {
    try {
      const original = documents.find(doc => doc.id === id);
      if (!original) {
        throw new Error('Document not found');
      }

      const duplicate = {
        ...original,
        id: `doc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: `${original.name} (Copy)`,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      aiDocumentStorage.save(duplicate);
      setDocuments(prev => [duplicate, ...prev]);
      toast.success('Document duplicated successfully');
      return duplicate;
    } catch (error) {
      console.error('Error duplicating document:', error);
      toast.error('Failed to duplicate document');
      throw error;
    }
  }, [documents]);

  const getDocumentById = useCallback((id) => {
    return documents.find(doc => doc.id === id);
  }, [documents]);

  const exportDocuments = useCallback(() => {
    try {
      aiDocumentStorage.export();
      toast.success('Documents exported successfully');
    } catch (error) {
      console.error('Error exporting documents:', error);
      toast.error('Failed to export documents');
    }
  }, []);

  const importDocuments = useCallback(async (file) => {
    try {
      const imported = await aiDocumentStorage.import(file);
      setDocuments(imported);
      toast.success(`${imported.length} document(s) imported successfully`);
      return imported;
    } catch (error) {
      console.error('Error importing documents:', error);
      toast.error('Failed to import documents');
      throw error;
    }
  }, []);

  const getStats = useCallback(() => {
    const totalDocs = documents.length;
    const totalWords = documents.reduce((sum, doc) => sum + (doc.metadata?.words || 0), 0);
    const recentDocs = documents.filter(doc => {
      const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
      return new Date(doc.created_at) > dayAgo;
    }).length;

    const typeCount = documents.reduce((acc, doc) => {
      const type = doc.type || 'blog_post';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {});

    return {
      totalDocuments: totalDocs,
      totalWords,
      recentDocuments: recentDocs,
      documentsByType: typeCount
    };
  }, [documents]);

  const value = {
    documents,
    loading,
    selectedDocument,
    setSelectedDocument,
    addDocument,
    updateDocument,
    deleteDocument,
    deleteMultipleDocuments,
    duplicateDocument,
    getDocumentById,
    exportDocuments,
    importDocuments,
    getStats,
    refreshDocuments: loadDocuments
  };

  return (
    <AiDocumentContext.Provider value={value}>
      {children}
    </AiDocumentContext.Provider>
  );
};

