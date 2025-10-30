import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { Card, CardBody, Input, Spinner, UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import { Editor } from '@tinymce/tinymce-react';
import Head from '@/layout/head/Head';
import Content from '@/layout/content/Content';
import { Block, Button, Icon } from '@/components/Component';
import AiWriterPanel from '@/components/ai-writer/AiWriterPanel';
import { useAiDrafts } from '@/context/AiDraftContext';
import { mockGenerator } from '@/data/mockGenerator';
import { textUtils } from '@/utils/textUtils';
import { toast } from 'react-toastify';
import { AI_TEMPLATES } from '@/data/aiTemplates';
import { useTheme } from '@/layout/provider/Theme';
// TinyMCE imports
import 'tinymce/tinymce';
import 'tinymce/models/dom/model';
import 'tinymce/themes/silver';
import 'tinymce/icons/default';
import 'tinymce/skins/content/default/content';

const AiEditor = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { documentId } = useParams();
  const editorRef = useRef(null);
  const theme = useTheme();
  const isEditMode = !!documentId;
  
  const [documentTitle, setDocumentTitle] = useState('Untitled Draft');
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  const [content, setContent] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [variants, setVariants] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [wordCount, setWordCount] = useState(0);
  const [charCount, setCharCount] = useState(0);
  const { addDraft, updateDraft, getDraftById } = useAiDrafts();

  // Load template from route state (for new documents)
  useEffect(() => {
    if (location.state?.selectedTemplate && !isEditMode) {
      setSelectedTemplate(location.state.selectedTemplate);
    }
  }, [location.state, isEditMode]);

  // Load draft if in edit mode
  useEffect(() => {
    if (isEditMode && documentId) {
      const draft = getDraftById(documentId);
      if (draft) {
        setDocumentTitle(draft.name);
        setContent(draft.content);
        setIsFavorite(draft.favorite || false);
        if (draft.template) {
          const template = AI_TEMPLATES.find(t => t.id === draft.template);
          setSelectedTemplate(template);
        }
      }
    }
  }, [documentId, isEditMode, getDraftById]);

  // Update word and character count
  useEffect(() => {
    setWordCount(textUtils.countWords(content));
    setCharCount(textUtils.countCharacters(content));
  }, [content]);

  const handleGenerate = async (params) => {
    try {
      setGenerating(true);
      const results = await mockGenerator.generate({
        ...params,
        variants: params.variantCount || 1,
        template: selectedTemplate?.id
      });
      setVariants(results);
      toast.success('Content generated successfully!');
    } catch (error) {
      console.error('Generation error:', error);
      toast.error('Failed to generate content');
    } finally {
      setGenerating(false);
    }
  };

  const handleInsertVariant = (variant) => {
    if (editorRef.current) {
      const currentContent = editorRef.current.getContent();
      const newContent = currentContent + (currentContent ? '<br/><br/>' : '') + variant.content;
      editorRef.current.setContent(newContent);
      setContent(newContent);
      toast.success('Content inserted');
    }
  };

  const handleSave = () => {
    const currentContent = editorRef.current ? editorRef.current.getContent() : content;
    const draftData = {
      name: documentTitle,
      content: currentContent,
      type: 'blog_post',
      template: selectedTemplate?.id || null,
      favorite: isFavorite,
      metadata: {
        words: textUtils.countWords(currentContent),
        characters: textUtils.countCharacters(currentContent),
        readingTime: textUtils.estimateReadingTime(currentContent)
      }
    };

    if (isEditMode && documentId) {
      updateDraft(documentId, draftData);
      toast.success('Draft saved successfully');
    } else {
      const newDraft = addDraft(draftData);
      navigate(`/ai-writer/editor/${newDraft.id}`, { replace: true });
      toast.success('Draft saved successfully');
    }
  };

  const handleExportText = () => {
    const currentContent = editorRef.current ? editorRef.current.getContent() : content;
    const plainText = currentContent.replace(/<[^>]*>/g, '\n').replace(/\n\n+/g, '\n\n').trim();
    const blob = new Blob([plainText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${textUtils.slugify(documentTitle)}.txt`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success('Draft exported as Text');
  };

  const handleExportHTML = () => {
    const currentContent = editorRef.current ? editorRef.current.getContent() : content;
    const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${documentTitle}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.6; }
  </style>
</head>
<body>
  <h1>${documentTitle}</h1>
  ${currentContent}
</body>
</html>`;
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${textUtils.slugify(documentTitle)}.html`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success('Draft exported as HTML');
  };

  const handleTemplateChange = (template) => {
    setSelectedTemplate(template);
  };

  const handleTitleEdit = () => {
    setIsEditingTitle(true);
  };

  const handleTitleSave = () => {
    setIsEditingTitle(false);
    if (!documentTitle.trim()) {
      setDocumentTitle('Untitled Draft');
    }
  };

  const toggleFavorite = () => {
    setIsFavorite(!isFavorite);
  };

  return (
    <>
      <Head title={documentTitle} />
      <Content>
        <Block>
          {/* Title Bar */}
          <div className="editor-header mb-4">
            <div className="d-flex justify-content-between align-items-center">
              <div className="d-flex align-items-center gap-2">
                <Button size="sm" color="light" outline onClick={() => navigate('/ai-writer/documents')}>
                  <Icon name="arrow-left" />
                </Button>
                {isEditingTitle ? (
                  <Input
                    type="text"
                    value={documentTitle}
                    onChange={(e) => setDocumentTitle(e.target.value)}
                    onBlur={handleTitleSave}
                    onKeyPress={(e) => e.key === 'Enter' && handleTitleSave()}
                    autoFocus
                    className="form-control-lg"
                    style={{ fontSize: '1.5rem', fontWeight: '600', maxWidth: '500px' }}
                  />
                ) : (
                  <h3 className="mb-0" style={{ fontSize: '1.5rem', fontWeight: '600' }}>
                    {documentTitle}
                  </h3>
                )}
                <Button 
                  size="sm" 
                  className="btn-icon btn-trigger" 
                  onClick={handleTitleEdit}
                  title="Edit title"
                >
                  <Icon name="edit" />
                </Button>
                <Button 
                  size="sm" 
                  className={`btn-icon btn-trigger ${isFavorite ? 'text-warning' : ''}`}
                  onClick={toggleFavorite}
                  title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
                >
                  <Icon name={isFavorite ? 'star-fill' : 'star'} />
                </Button>
              </div>
              <div className="d-flex align-items-center gap-3">
                {/* Stats - Same row as buttons */}
                <div className="text-soft small">
                  <span className="me-3">Words: {wordCount}</span>
                  <span>Characters: {charCount}</span>
                </div>
                {/* Export and Save buttons */}
                <UncontrolledDropdown>
                  <DropdownToggle color="light" outline>
                    <Icon name="download" />
                    <span>Export</span>
                    <Icon name="chevron-down" className="dd-indc" />
                  </DropdownToggle>
                  <DropdownMenu end>
                    <DropdownItem onClick={handleExportHTML}>
                      <Icon name="file-docs" className="me-2" />
                      <span>Docs (HTML)</span>
                    </DropdownItem>
                    <DropdownItem onClick={handleExportText}>
                      <Icon name="file-text" className="me-2" />
                      <span>Text (TXT)</span>
                    </DropdownItem>
                  </DropdownMenu>
                </UncontrolledDropdown>
                <Button color="primary" onClick={handleSave}>
                  <Icon name="save" />
                  <span>Save</span>
                </Button>
              </div>
            </div>
          </div>

          {/* Editor and Panel */}
          <div className="row g-gs">
            <div className="col-lg-8">
              <Card className="card-bordered h-100">
                <CardBody className="card-inner">
                  <Editor
                    licenseKey="gpl"
                    onInit={(evt, editor) => (editorRef.current = editor)}
                    initialValue={content}
                    value={content}
                    onEditorChange={(newContent) => setContent(newContent)}
                    init={{
                      height: 'calc(100vh - 280px)',
                      min_height: 500,
                      max_height: 1200,
                      resize: true,
                      menubar: false,
                      toolbar:
                        'undo redo | blocks | bold italic forecolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat',
                      content_style: theme.skin === 'dark' ? 
                        'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #fff; background-color: #1a1a1a; }' : 
                        'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #000; background-color: #fff; }',
                      branding: false
                    }}
                  />
                </CardBody>
              </Card>
            </div>
            <div className="col-lg-4">
              <AiWriterPanel
                selectedTemplate={selectedTemplate}
                onTemplateChange={handleTemplateChange}
                onGenerate={handleGenerate}
                variants={variants}
                onInsert={handleInsertVariant}
                loading={generating}
              />
            </div>
          </div>
        </Block>
      </Content>
    </>
  );
};

export default AiEditor;
