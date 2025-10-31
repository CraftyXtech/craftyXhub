import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { Card, CardBody, Input, Spinner } from 'reactstrap';
import { Editor } from '@tinymce/tinymce-react';
import Head from '@/layout/head/Head';
import Content from '@/layout/content/Content';
import { Block, BlockHead, BlockBetween, BlockHeadContent, Row, Col, Button, Icon } from '@/components/Component';
import AiWriterPanel from '@/components/ai-writer/AiWriterPanel';
import { useAiDrafts } from '@/context/AiDraftContext';
import { aiWriterService } from '@/api/aiWriterService';
import { textUtils } from '@/utils/textUtils';
import { toast } from 'react-toastify';
import { useTheme } from '@/layout/provider/Theme';
// TinyMCE imports
import 'tinymce/tinymce';
import 'tinymce/models/dom/model';
import 'tinymce/themes/silver';
import 'tinymce/icons/default';
import 'tinymce/skins/content/default/content';

const AiEditorGenerate = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { documentId } = useParams();
  const editorRef = useRef(null);
  const theme = useTheme();
  const [documentTitle, setDocumentTitle] = useState('Untitled Draft');
  const [content, setContent] = useState('');
  const [selectedTool, setSelectedTool] = useState(location.state?.selectedTool || null);
  const [variants, setVariants] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [wordCount, setWordCount] = useState(0);
  const [charCount, setCharCount] = useState(0);
  const { addDraft, updateDraft, getDraftById } = useAiDrafts();

  useEffect(() => {
    if (documentId) {
      const draft = getDraftById(documentId);
      if (draft) {
        setDocumentTitle(draft.name);
        setContent(draft.content);
      }
    }
  }, [documentId, getDraftById]);

  useEffect(() => {
    setWordCount(textUtils.countWords(content));
    setCharCount(textUtils.countCharacters(content));
  }, [content]);

  const handleGenerate = async (params) => {
    try {
      setGenerating(true);
      const results = await aiWriterService.generate({
        tool_id: params.tool_id || selectedTool?.id,
        params: {},
        prompt: params.prompt,
        keywords: params.keywords,
        tone: params.tone,
        language: params.language,
        length: params.length,
        variant_count: params.variant_count || 1,
        creativity: params.creativity ?? 0.7,
        model: params.model || 'gpt-5-mini',
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
      tool_id: selectedTool?.id || null,
      draft_metadata: {
        words: textUtils.countWords(currentContent),
        characters: textUtils.countCharacters(currentContent),
        readingTime: textUtils.estimateReadingTime(currentContent)
      }
    };

    if (documentId) {
      updateDraft(documentId, draftData);
    } else {
      const newDraft = addDraft(draftData);
      navigate(`/ai-writer/editor/${newDraft.id}`, { replace: true });
    }
  };

  const handleExport = () => {
    const currentContent = editorRef.current ? editorRef.current.getContent() : content;
    const blob = new Blob([currentContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${textUtils.slugify(documentTitle)}.html`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success('Document exported');
  };

  return (
    <>
      <Head title="AI Content Generator" />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <div className="d-flex align-items-center gap-2">
                <Button size="sm" color="light" outline onClick={() => navigate('/ai-writer/documents')}>
                  <Icon name="arrow-left" />
                </Button>
                <div>
                  <Input
                    type="text"
                    value={documentTitle}
                    onChange={(e) => setDocumentTitle(e.target.value)}
                    className="form-control-lg border-0 px-0"
                    style={{ fontSize: '1.25rem', fontWeight: '500' }}
                    placeholder="Untitled Document"
                  />
                  <div className="text-soft small">
                    Words: {wordCount} | Characters: {charCount}
                  </div>
                </div>
              </div>
            </BlockHeadContent>
            <BlockHeadContent>
              <ul className="nk-block-tools g-3">
                <li>
                  <Button color="light" outline onClick={handleExport}>
                    <Icon name="download" />
                    <span>Export</span>
                  </Button>
                </li>
                <li>
                  <Button color="primary" onClick={handleSave}>
                    <Icon name="save" />
                    <span>Save</span>
                  </Button>
                </li>
              </ul>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <Row className="g-gs">
            <Col lg="8">
              <Card className="card-bordered h-100">
                <CardBody className="card-inner">
                  <Editor
                    licenseKey="gpl"
                    onInit={(evt, editor) => (editorRef.current = editor)}
                    initialValue={content}
                    value={content}
                    onEditorChange={(newContent) => setContent(newContent)}
                    init={{
                      height: 600,
                      menubar: false,
                      toolbar:
                        'undo redo | blocks | bold italic forecolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat',
                      content_style: theme.skin === 'dark' ? 
                        'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; color: #fff; background-color: #1a1a1a; }' : 
                        'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; color: #000; background-color: #fff; }',
                      branding: false
                    }}
                  />
                </CardBody>
              </Card>
            </Col>
            <Col lg="4">
              <AiWriterPanel
                selectedTool={selectedTool}
                onGenerate={handleGenerate}
                variants={variants}
                onInsert={handleInsertVariant}
                loading={generating}
              />
            </Col>
          </Row>
        </Block>
      </Content>
    </>
  );
};

export default AiEditorGenerate;

