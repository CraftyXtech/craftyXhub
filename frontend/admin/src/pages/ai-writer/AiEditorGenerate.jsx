import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { Card, CardBody, Input, Spinner } from 'reactstrap';
import { Editor } from '@tinymce/tinymce-react';
import Head from '@/layout/head/Head';
import Content from '@/layout/content/Content';
import { Block, BlockHead, BlockBetween, BlockHeadContent, Row, Col, Button, Icon } from '@/components/Component';
import AiWriterPanel from '@/components/ai-writer/AiWriterPanel';
import { useAiDocuments } from '@/context/AiDocumentContext';
import { mockGenerator } from '@/data/mockGenerator';
import { textUtils } from '@/utils/textUtils';
import { toast } from 'react-toastify';

const AiEditorGenerate = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { documentId } = useParams();
  const editorRef = useRef(null);
  const [documentTitle, setDocumentTitle] = useState('Untitled Document');
  const [content, setContent] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState(location.state?.selectedTemplate || null);
  const [variants, setVariants] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [wordCount, setWordCount] = useState(0);
  const [charCount, setCharCount] = useState(0);
  const { addDocument, updateDocument, getDocumentById } = useAiDocuments();

  useEffect(() => {
    if (documentId) {
      const doc = getDocumentById(documentId);
      if (doc) {
        setDocumentTitle(doc.name);
        setContent(doc.content);
      }
    }
  }, [documentId, getDocumentById]);

  useEffect(() => {
    setWordCount(textUtils.countWords(content));
    setCharCount(textUtils.countCharacters(content));
  }, [content]);

  const handleGenerate = async (params) => {
    try {
      setGenerating(true);
      const results = await mockGenerator.generate({
        ...params,
        variants: params.variantCount || 1
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
    const docData = {
      name: documentTitle,
      content: currentContent,
      type: 'blog_post',
      template: selectedTemplate?.id || null,
      metadata: {
        words: textUtils.countWords(currentContent),
        characters: textUtils.countCharacters(currentContent),
        readingTime: textUtils.estimateReadingTime(currentContent)
      }
    };

    if (documentId) {
      updateDocument(documentId, docData);
    } else {
      const newDoc = addDocument(docData);
      navigate(`/ai-writer/editor/${newDoc.id}`, { replace: true });
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
                    apiKey="no-api-key"
                    onInit={(evt, editor) => (editorRef.current = editor)}
                    initialValue={content}
                    value={content}
                    onEditorChange={(newContent) => setContent(newContent)}
                    init={{
                      height: 600,
                      menubar: false,
                      plugins: [
                        'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                        'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                        'insertdatetime', 'media', 'table', 'code', 'help', 'wordcount'
                      ],
                      toolbar:
                        'undo redo | blocks | bold italic forecolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help',
                      content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size:14px }'
                    }}
                  />
                </CardBody>
              </Card>
            </Col>
            <Col lg="4">
              <AiWriterPanel
                selectedTemplate={selectedTemplate}
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

