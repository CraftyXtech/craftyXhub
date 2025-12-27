import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardBody, Badge, Alert, Collapse } from 'reactstrap';
import Head from '@/layout/head/Head';
import Content from '@/layout/content/Content';
import { Block, BlockHead, BlockBetween, BlockHeadContent, BlockTitle, BlockDes, Row, Col, Button, Icon } from '@/components/Component';
import BlogAgentPanel from '@/components/ai-writer/BlogAgentPanel';
import { aiWriterService } from '@/api/aiWriterService';
import { processContent } from '@/utils/markdown';
import { toast } from 'react-toastify';

const BlogAgent = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [generatedBlog, setGeneratedBlog] = useState(null);
  const [expandedSections, setExpandedSections] = useState({});
  const [showSeoDetails, setShowSeoDetails] = useState(false);

  const handleGenerate = async (params) => {
    try {
      setLoading(true);
      setGeneratedBlog(null);
      
      const result = await aiWriterService.generateBlog(params);
      setGeneratedBlog(result);
      
      // Show success message with actions taken
      let message = 'Blog post generated successfully!';
      if (result.draft_id) {
        message += ' Saved as draft.';
      }
      if (result.post_id) {
        message += ' Created as post.';
      }
      toast.success(message);
      
      // Expand all sections by default
      const expanded = {};
      result.blog_post?.sections?.forEach((_, idx) => {
        expanded[idx] = true;
      });
      setExpandedSections(expanded);
      
    } catch (error) {
      console.error('Blog generation error:', error);
      toast.error(error.response?.data?.detail || 'Failed to generate blog post');
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (index) => {
    setExpandedSections(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const handleCopyContent = () => {
    if (!generatedBlog?.blog_post) return;
    
    const { blog_post } = generatedBlog;
    let markdown = `# ${blog_post.title}\n\n`;
    markdown += `*${blog_post.summary}*\n\n`;
    
    blog_post.sections.forEach(section => {
      markdown += `## ${section.heading}\n\n`;
      markdown += `${section.body_markdown}\n\n`;
    });
    
    navigator.clipboard.writeText(markdown);
    toast.success('Content copied to clipboard!');
  };

  const handleEditInEditor = () => {
    if (generatedBlog?.draft_id) {
      navigate(`/ai-writer/editor/${generatedBlog.draft_id}`);
    } else {
      // Create new editor with content
      const { blog_post } = generatedBlog;
      let content = `<h1>${blog_post.title}</h1>`;
      content += `<p class="lead">${blog_post.summary}</p>`;
      
      blog_post.sections.forEach(section => {
        content += `<h2>${section.heading}</h2>`;
        content += `<div>${section.body_markdown}</div>`;
      });
      
      navigate('/ai-writer/editor/new', {
        state: {
          initialContent: content,
          initialTitle: blog_post.title,
        }
      });
    }
  };

  const handleViewPost = () => {
    if (generatedBlog?.post_id) {
      navigate(`/posts/edit/${generatedBlog.post_id}`);
    }
  };

  return (
    <>
      <Head title="Blog Agent" />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BlockTitle page tag="h3">
                <Icon name="article" className="me-2 text-danger" />
                Blog Agent
              </BlockTitle>
              <BlockDes className="text-soft">
                <p>Generate complete, publication-ready blog posts with AI</p>
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              <Button color="light" outline onClick={() => navigate('/ai-writer')}>
                <Icon name="arrow-left" />
                <span>Back to Dashboard</span>
              </Button>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <Row className="g-gs">
            {/* Left Column - Generated Blog Preview */}
            <Col lg="8">
              {!generatedBlog ? (
                <Card className="card-bordered h-100">
                  <CardBody className="card-inner text-center py-5">
                    <div className="icon-circle icon-circle-xxl bg-danger-dim mx-auto mb-4">
                      <Icon name="article" className="text-danger" style={{ fontSize: '3rem' }} />
                    </div>
                    <h4>Ready to Generate</h4>
                    <p className="text-soft mb-4">
                      Configure your blog settings in the panel on the right and click "Generate Blog Post"
                      to create a complete, SEO-optimized article.
                    </p>
                    <div className="d-flex flex-wrap justify-content-center gap-2">
                      <Badge color="primary" pill>Structured Sections</Badge>
                      <Badge color="success" pill>SEO Optimized</Badge>
                      <Badge color="info" pill>Auto Tags</Badge>
                      <Badge color="warning" pill>Web Research</Badge>
                    </div>
                  </CardBody>
                </Card>
              ) : (
                <div className="blog-preview">
                  {/* Blog Header */}
                  <Card className="card-bordered mb-3">
                    <CardBody className="card-inner">
                      <div className="d-flex justify-content-between align-items-start mb-3">
                        <div className="flex-grow-1">
                          <h3 className="mb-2">{generatedBlog.blog_post.title}</h3>
                          <p className="text-soft lead mb-3">{generatedBlog.blog_post.summary}</p>
                          <div className="d-flex flex-wrap gap-2">
                            {generatedBlog.blog_post.tags.map((tag, idx) => (
                              <Badge key={idx} color="primary" pill>{tag}</Badge>
                            ))}
                          </div>
                        </div>
                        <div className="ms-3">
                          <div className="d-flex gap-2">
                            <Button size="sm" color="light" outline onClick={handleCopyContent}>
                              <Icon name="copy" />
                            </Button>
                            <Button size="sm" color="primary" onClick={handleEditInEditor}>
                              <Icon name="edit" />
                            </Button>
                          </div>
                        </div>
                      </div>

                      {/* Generation Stats */}
                      <div className="d-flex flex-wrap gap-3 text-soft small">
                        <span>
                          <Icon name="clock" className="me-1" />
                          {generatedBlog.generation_time}s
                        </span>
                        <span>
                          <Icon name="cpu" className="me-1" />
                          {generatedBlog.model_used}
                        </span>
                        {generatedBlog.web_search_used && (
                          <span className="text-success">
                            <Icon name="globe" className="me-1" />
                            Web Search Used
                          </span>
                        )}
                        {generatedBlog.draft_id && (
                          <span className="text-info">
                            <Icon name="file-text" className="me-1" />
                            Draft Saved
                          </span>
                        )}
                        {generatedBlog.post_id && (
                          <span className="text-success">
                            <Icon name="check-circle" className="me-1" />
                            Post Created
                          </span>
                        )}
                      </div>
                    </CardBody>
                  </Card>

                  {/* SEO Details */}
                  <Card className="card-bordered mb-3">
                    <CardBody className="card-inner py-2">
                      <div 
                        className="d-flex justify-content-between align-items-center cursor-pointer"
                        onClick={() => setShowSeoDetails(!showSeoDetails)}
                        style={{ cursor: 'pointer' }}
                      >
                        <h6 className="mb-0">
                          <Icon name="search" className="me-2" />
                          SEO Details
                        </h6>
                        <Icon name={showSeoDetails ? 'chevron-up' : 'chevron-down'} />
                      </div>
                      <Collapse isOpen={showSeoDetails}>
                        <div className="mt-3 pt-3 border-top">
                          <div className="mb-3">
                            <label className="form-label small text-soft">SEO Title</label>
                            <div className="bg-light p-2 rounded">
                              {generatedBlog.blog_post.seo_title}
                              <small className="text-soft ms-2">
                                ({generatedBlog.blog_post.seo_title.length} chars)
                              </small>
                            </div>
                          </div>
                          <div className="mb-3">
                            <label className="form-label small text-soft">Meta Description</label>
                            <div className="bg-light p-2 rounded">
                              {generatedBlog.blog_post.seo_description}
                              <small className="text-soft ms-2">
                                ({generatedBlog.blog_post.seo_description.length} chars)
                              </small>
                            </div>
                          </div>
                          <div className="mb-3">
                            <label className="form-label small text-soft">URL Slug</label>
                            <div className="bg-light p-2 rounded font-monospace">
                              /{generatedBlog.blog_post.slug}
                            </div>
                          </div>
                          {generatedBlog.blog_post.hero_image_prompt && (
                            <div>
                              <label className="form-label small text-soft">Hero Image Prompt</label>
                              <div className="bg-light p-2 rounded text-soft">
                                {generatedBlog.blog_post.hero_image_prompt}
                              </div>
                            </div>
                          )}
                        </div>
                      </Collapse>
                    </CardBody>
                  </Card>

                  {/* Content Sections */}
                  <h6 className="mb-3">
                    <Icon name="list" className="me-2" />
                    Content Sections ({generatedBlog.blog_post.sections.length})
                  </h6>
                  
                  {generatedBlog.blog_post.sections.map((section, index) => (
                    <Card key={index} className="card-bordered mb-3">
                      <CardBody className="card-inner py-3">
                        <div 
                          className="d-flex justify-content-between align-items-center"
                          onClick={() => toggleSection(index)}
                          style={{ cursor: 'pointer' }}
                        >
                          <h5 className="mb-0">
                            <span className="badge badge-dim badge-primary me-2">{index + 1}</span>
                            {section.heading}
                          </h5>
                          <Icon name={expandedSections[index] ? 'chevron-up' : 'chevron-down'} />
                        </div>
                        <Collapse isOpen={expandedSections[index]}>
                          <div className="mt-3 pt-3 border-top">
                            <div 
                              className="blog-content"
                              style={{ 
                                lineHeight: '1.7',
                                fontSize: '14px'
                              }}
                              dangerouslySetInnerHTML={{ __html: processContent(section.body_markdown) }}
                            />
                          </div>
                        </Collapse>
                      </CardBody>
                    </Card>
                  ))}

                  {/* Action Buttons */}
                  <Card className="card-bordered">
                    <CardBody className="card-inner">
                      <div className="d-flex flex-wrap gap-2">
                        <Button color="primary" onClick={handleEditInEditor}>
                          <Icon name="edit" className="me-2" />
                          Edit in Editor
                        </Button>
                        <Button color="light" outline onClick={handleCopyContent}>
                          <Icon name="copy" className="me-2" />
                          Copy Markdown
                        </Button>
                        {generatedBlog.post_id && (
                          <Button color="success" onClick={handleViewPost}>
                            <Icon name="eye" className="me-2" />
                            View Post
                          </Button>
                        )}
                        <Button 
                          color="light" 
                          outline 
                          onClick={() => setGeneratedBlog(null)}
                        >
                          <Icon name="reload" className="me-2" />
                          Generate New
                        </Button>
                      </div>
                    </CardBody>
                  </Card>
                </div>
              )}
            </Col>

            {/* Right Column - Configuration Panel */}
            <Col lg="4">
              <BlogAgentPanel
                onGenerate={handleGenerate}
                loading={loading}
                generatedBlog={generatedBlog}
              />
            </Col>
          </Row>
        </Block>
      </Content>
    </>
  );
};

export default BlogAgent;







