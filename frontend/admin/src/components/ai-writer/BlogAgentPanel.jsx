import React, { useState, useEffect } from 'react';
import { Card, CardBody, Form, FormGroup, Label, Input, Spinner, Badge, Alert } from 'reactstrap';
import { Button, Icon, RSelect } from '@/components/Component';
import { TONE_OPTIONS, LANGUAGE_OPTIONS, BLOG_TYPE_OPTIONS, BLOG_LENGTH_OPTIONS } from '@/data/aiTools';
import { useGetCategories } from '@/api/postService';

const MODEL_OPTIONS = [
  { value: 'gpt-5-mini', label: 'GPT-5 Mini (Recommended)' },
  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
  { value: 'gpt-4o', label: 'GPT-4o' },
  { value: 'gemini', label: 'Google Gemini (Web Search)' },
  { value: 'grok', label: 'xAI Grok' },
  { value: 'deepseek-v3', label: 'DeepSeek V3' }
];

const BlogAgentPanel = ({
  onGenerate,
  loading = false,
  generatedBlog = null,
  className = ''
}) => {
  const { categories, loading: categoriesLoading } = useGetCategories();
  
  const [formData, setFormData] = useState({
    topic: '',
    blog_type: 'how-to',
    keywords: '',
    audience: '',
    word_count: 'medium',
    tone: 'professional',
    language: 'en-US',
    model: 'gpt-5-mini',
    creativity: 0.7,
    use_web_search: true,
    save_draft: true,
    publish_post: false,
    category_id: null,
    is_published: false,
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onGenerate && formData.topic.trim()) {
      const keywords = formData.keywords
        .split(',')
        .map(k => k.trim())
        .filter(k => k);
      
      onGenerate({
        ...formData,
        keywords,
        category_id: formData.category_id || null,
      });
    }
  };

  // Category options for select
  const categoryOptions = categories.map(cat => ({
    value: cat.id,
    label: cat.parent_id ? `  └ ${cat.name}` : cat.name,
  }));

  // Check if web search is available for selected model
  const webSearchAvailable = ['gemini'].includes(formData.model);

  return (
    <Card className={`card-bordered ${className}`}>
      <CardBody className="card-inner-lg">
        {/* Header */}
        <div className="d-flex align-items-center mb-4">
          <div className="icon-circle icon-circle-lg bg-danger-dim">
            <Icon name="article" className="text-danger" />
          </div>
          <div className="ms-3">
            <h5 className="mb-0">Blog Agent</h5>
            <small className="text-soft">Generate complete, publication-ready blog posts</small>
          </div>
        </div>

        <Form onSubmit={handleSubmit}>
          {/* Topic Input */}
          <FormGroup>
            <Label className="form-label">
              Blog Topic <span className="text-danger">*</span>
            </Label>
            <Input
              type="textarea"
              rows="3"
              placeholder="E.g., How to build a successful content marketing strategy in 2024"
              value={formData.topic}
              onChange={(e) => handleInputChange('topic', e.target.value)}
              maxLength={500}
            />
            <div className="form-note d-flex justify-content-between">
              <span>Describe what you want to write about</span>
              <span>{formData.topic.length}/500</span>
            </div>
          </FormGroup>

          {/* Blog Type */}
          <FormGroup>
            <Label className="form-label">Blog Type</Label>
            <RSelect
              options={BLOG_TYPE_OPTIONS.map(opt => ({
                value: opt.value,
                label: `${opt.label} - ${opt.description}`,
              }))}
              value={{
                value: formData.blog_type,
                label: BLOG_TYPE_OPTIONS.find(o => o.value === formData.blog_type)?.label || 'How-To Guide',
              }}
              onChange={(opt) => handleInputChange('blog_type', opt.value)}
            />
          </FormGroup>

          {/* Keywords */}
          <FormGroup>
            <Label className="form-label">Target Keywords</Label>
            <Input
              type="text"
              placeholder="content marketing, SEO, blog strategy"
              value={formData.keywords}
              onChange={(e) => handleInputChange('keywords', e.target.value)}
            />
            <div className="form-note">Comma-separated SEO keywords (max 10)</div>
          </FormGroup>

          {/* Target Audience */}
          <FormGroup>
            <Label className="form-label">Target Audience</Label>
            <Input
              type="text"
              placeholder="E.g., Small business owners, marketing professionals"
              value={formData.audience}
              onChange={(e) => handleInputChange('audience', e.target.value)}
            />
          </FormGroup>

          {/* Model and Length Row */}
          <div className="row g-3">
            <div className="col-sm-6">
              <FormGroup>
                <Label className="form-label">AI Model</Label>
                <RSelect
                  options={MODEL_OPTIONS}
                  value={MODEL_OPTIONS.find(opt => opt.value === formData.model)}
                  onChange={(opt) => handleInputChange('model', opt.value)}
                />
              </FormGroup>
            </div>
            <div className="col-sm-6">
              <FormGroup>
                <Label className="form-label">Target Length</Label>
                <RSelect
                  options={BLOG_LENGTH_OPTIONS}
                  value={BLOG_LENGTH_OPTIONS.find(opt => opt.value === formData.word_count)}
                  onChange={(opt) => handleInputChange('word_count', opt.value)}
                />
              </FormGroup>
            </div>
          </div>

          {/* Tone and Language Row */}
          <div className="row g-3">
            <div className="col-sm-6">
              <FormGroup>
                <Label className="form-label">Tone</Label>
                <RSelect
                  options={TONE_OPTIONS}
                  value={TONE_OPTIONS.find(opt => opt.value === formData.tone)}
                  onChange={(opt) => handleInputChange('tone', opt.value)}
                />
              </FormGroup>
            </div>
            <div className="col-sm-6">
              <FormGroup>
                <Label className="form-label">Language</Label>
                <RSelect
                  options={LANGUAGE_OPTIONS}
                  value={LANGUAGE_OPTIONS.find(opt => opt.value === formData.language)}
                  onChange={(opt) => handleInputChange('language', opt.value)}
                />
              </FormGroup>
            </div>
          </div>

          {/* Creativity Slider */}
          <FormGroup>
            <Label className="form-label">
              Creativity Level: {formData.creativity}
            </Label>
            <Input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={formData.creativity}
              onChange={(e) => handleInputChange('creativity', parseFloat(e.target.value))}
            />
            <div className="form-note d-flex justify-content-between">
              <span>Focused</span>
              <span>Creative</span>
            </div>
          </FormGroup>

          {/* Web Search Toggle */}
          <FormGroup className="mb-3">
            <div className="custom-control custom-switch">
              <input
                type="checkbox"
                className="custom-control-input"
                id="webSearchToggle"
                checked={formData.use_web_search}
                onChange={(e) => handleInputChange('use_web_search', e.target.checked)}
                disabled={!webSearchAvailable}
              />
              <label className="custom-control-label" htmlFor="webSearchToggle">
                Enable Web Search
                {webSearchAvailable ? (
                  <Badge color="success" className="ms-2">Available</Badge>
                ) : (
                  <Badge color="secondary" className="ms-2">Use Gemini</Badge>
                )}
              </label>
            </div>
            <div className="form-note">Research current information while writing</div>
          </FormGroup>

          <hr className="my-4" />

          {/* Save/Publish Options */}
          <h6 className="mb-3">
            <Icon name="save" className="me-2" />
            Save Options
          </h6>

          <FormGroup className="mb-3">
            <div className="custom-control custom-switch">
              <input
                type="checkbox"
                className="custom-control-input"
                id="saveDraftToggle"
                checked={formData.save_draft}
                onChange={(e) => handleInputChange('save_draft', e.target.checked)}
              />
              <label className="custom-control-label" htmlFor="saveDraftToggle">
                Save as AI Draft
              </label>
            </div>
          </FormGroup>

          <FormGroup className="mb-3">
            <div className="custom-control custom-switch">
              <input
                type="checkbox"
                className="custom-control-input"
                id="publishPostToggle"
                checked={formData.publish_post}
                onChange={(e) => handleInputChange('publish_post', e.target.checked)}
              />
              <label className="custom-control-label" htmlFor="publishPostToggle">
                Create as Blog Post
              </label>
            </div>
          </FormGroup>

          {/* Category and Publish Status (shown when publish_post is true) */}
          {formData.publish_post && (
            <>
              <FormGroup>
                <Label className="form-label">Category</Label>
                <RSelect
                  options={[{ value: null, label: 'No Category' }, ...categoryOptions]}
                  value={
                    formData.category_id
                      ? categoryOptions.find(opt => opt.value === formData.category_id)
                      : { value: null, label: 'No Category' }
                  }
                  onChange={(opt) => handleInputChange('category_id', opt.value)}
                  isLoading={categoriesLoading}
                  placeholder="Select category..."
                />
              </FormGroup>

              <FormGroup className="mb-3">
                <div className="custom-control custom-switch">
                  <input
                    type="checkbox"
                    className="custom-control-input"
                    id="isPublishedToggle"
                    checked={formData.is_published}
                    onChange={(e) => handleInputChange('is_published', e.target.checked)}
                  />
                  <label className="custom-control-label" htmlFor="isPublishedToggle">
                    Publish Immediately
                    {formData.is_published && (
                      <Badge color="warning" className="ms-2">Live</Badge>
                    )}
                  </label>
                </div>
                <div className="form-note">
                  {formData.is_published
                    ? 'Post will be visible to readers immediately'
                    : 'Post will be saved as draft for review'}
                </div>
              </FormGroup>
            </>
          )}

          {/* Generate Button */}
          <Button
            type="submit"
            color="danger"
            size="lg"
            className="w-100 mt-3"
            disabled={loading || !formData.topic.trim()}
          >
            {loading ? (
              <>
                <Spinner size="sm" className="me-2" />
                <span>Generating Blog Post...</span>
              </>
            ) : (
              <>
                <Icon name="spark" className="me-2" />
                <span>Generate Blog Post</span>
              </>
            )}
          </Button>

          {/* Generation Info */}
          {loading && (
            <Alert color="info" className="mt-3 mb-0">
              <Icon name="info" className="me-2" />
              This may take 30-60 seconds depending on the length and model selected.
            </Alert>
          )}
        </Form>
      </CardBody>
    </Card>
  );
};

export default BlogAgentPanel;

