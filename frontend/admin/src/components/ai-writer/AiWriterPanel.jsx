import React, { useState } from 'react';
import { Card, CardBody, Nav, NavItem, NavLink, TabContent, TabPane, Form, FormGroup, Label, Input, Spinner } from 'reactstrap';
import { Button, Icon, RSelect } from '@/components/Component';
import { TONE_OPTIONS, LANGUAGE_OPTIONS, LENGTH_OPTIONS, AI_TOOLS } from '@/data/aiTools';
import { textUtils } from '@/utils/textUtils';
import classnames from 'classnames';

const AiWriterPanel = ({
  selectedTool,
  onToolChange,
  onGenerate,
  variants = [],
  onInsert,
  loading = false,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState('1');
  const [expandedVariants, setExpandedVariants] = useState({});
  const [formData, setFormData] = useState({
    prompt: '',
    keywords: '',
    tone: 'professional',
    language: 'en-US',
    length: 'medium',
    model: 'gpt-5-mini',
    creativity: 0.7,
    variantCount: 1
  });

  const toggleTab = (tab) => {
    if (activeTab !== tab) setActiveTab(tab);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onGenerate && formData.prompt.trim()) {
      const keywords = formData.keywords.split(',').map(k => k.trim()).filter(k => k);
      onGenerate({
        prompt: formData.prompt,
        keywords,
        tone: formData.tone,
        language: formData.language,
        length: formData.length,
        model: formData.model,
        creativity: formData.creativity,
        variant_count: formData.variantCount,
        tool_id: selectedTool?.id
      });
    }
  };

  const toggleVariant = (index) => {
    setExpandedVariants(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const handleCopyVariant = (variant) => {
    const plainText = variant.content.replace(/<[^>]*>/g, '');
    navigator.clipboard.writeText(plainText);
  };

  return (
    <Card className={`card-bordered ${className}`}>
      <CardBody className="card-inner-lg">
        <Nav tabs className="nav-tabs-card">
          <NavItem>
            <NavLink
              tag="a"
              href="#tab"
              className={classnames({ active: activeTab === '1' })}
              onClick={(ev) => {
                ev.preventDefault();
                toggleTab('1');
              }}
            >
              <Icon name="spark" />
              <span>AI Writer</span>
            </NavLink>
          </NavItem>
          <NavItem>
            <NavLink
              tag="a"
              href="#tab"
              className={classnames({ active: activeTab === '2' })}
              onClick={(ev) => {
                ev.preventDefault();
                toggleTab('2');
              }}
            >
              <Icon name="clock" />
              <span>History</span>
            </NavLink>
          </NavItem>
        </Nav>

        <TabContent activeTab={activeTab}>
          <TabPane tabId="1">
            <Form onSubmit={handleSubmit} className="mt-3">
              {/* Model Selector */}
              <FormGroup>
                <Label>AI Model</Label>
                <RSelect
                  options={[
                    { value: 'gpt-5-mini', label: 'GPT-5 Mini (Recommended)' },
                    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
                    { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
                    { value: 'gpt-4o', label: 'GPT-4o' },
                    { value: 'gemini', label: 'Google Gemini' },
                    { value: 'grok', label: 'xAI Grok' },
                    { value: 'deepseek-v3', label: 'DeepSeek V3' }
                  ]}
                  value={{ 
                    value: formData.model, 
                    label: formData.model === 'gpt-5-mini' ? 'GPT-5 Mini (Recommended)' :
                           formData.model === 'gpt-3.5-turbo' ? 'GPT-3.5 Turbo' :
                           formData.model === 'gpt-4o-mini' ? 'GPT-4o Mini' :
                           formData.model === 'gpt-4o' ? 'GPT-4o' :
                           formData.model === 'gemini' ? 'Google Gemini' :
                           formData.model === 'grok' ? 'xAI Grok' :
                           formData.model === 'deepseek-v3' ? 'DeepSeek V3' :
                           'OpenAI'
                  }}
                  onChange={(opt) => handleInputChange('model', opt.value)}
                />
              </FormGroup>

              {/* Tool Selector */}
              <FormGroup>
                <Label>Select Tool</Label>
                <RSelect
                  options={AI_TOOLS.map(t => ({
                    value: t.id,
                    label: t.title
                  }))}
                  value={selectedTool ? {
                    value: selectedTool.id,
                    label: selectedTool.title
                  } : null}
                  onChange={(opt) => {
                    const tool = AI_TOOLS.find(t => t.id === opt.value);
                    onToolChange && onToolChange(tool);
                  }}
                  placeholder="Choose a tool..."
                />
              </FormGroup>

              {selectedTool && (
                <div className="mb-3 p-2 bg-light rounded">
                  <div className="d-flex align-items-center">
                    <Icon name={selectedTool.icon} className={`text-${selectedTool.color} me-2`}></Icon>
                    <div className="flex-grow-1">
                      <small className="text-soft">{selectedTool.description}</small>
                    </div>
                  </div>
                </div>
              )}

              <FormGroup>
                <Label>What do you want to generate?</Label>
                <Input
                  type="textarea"
                  rows="4"
                  placeholder="E.g., Write a blog post about the importance of digital marketing..."
                  value={formData.prompt}
                  onChange={(e) => handleInputChange('prompt', e.target.value)}
                  maxLength={500}
                />
                <div className="form-note text-right">{formData.prompt.length}/500 Characters</div>
              </FormGroup>

              <FormGroup>
                <Label>Primary Keywords</Label>
                <Input
                  type="text"
                  placeholder="marketing, SEO, content strategy"
                  value={formData.keywords}
                  onChange={(e) => handleInputChange('keywords', e.target.value)}
                />
                <div className="form-note">Separated with a comma (max 10)</div>
              </FormGroup>

              <div className="row g-3">
                <div className="col-sm-6">
                  <FormGroup>
                    <Label>Select Language</Label>
                    <RSelect
                      options={LANGUAGE_OPTIONS}
                      value={LANGUAGE_OPTIONS.find(opt => opt.value === formData.language)}
                      onChange={(opt) => handleInputChange('language', opt.value)}
                    />
                  </FormGroup>
                </div>
                <div className="col-sm-6">
                  <FormGroup>
                    <Label>Select Tone</Label>
                    <RSelect
                      options={TONE_OPTIONS}
                      value={TONE_OPTIONS.find(opt => opt.value === formData.tone)}
                      onChange={(opt) => handleInputChange('tone', opt.value)}
                    />
                  </FormGroup>
                </div>
              </div>

              <div className="row g-3">
                <div className="col-sm-6">
                  <FormGroup>
                    <Label>Length</Label>
                    <RSelect
                      options={LENGTH_OPTIONS}
                      value={LENGTH_OPTIONS.find(opt => opt.value === formData.length)}
                      onChange={(opt) => handleInputChange('length', opt.value)}
                    />
                  </FormGroup>
                </div>
                <div className="col-sm-6">
                  <FormGroup>
                    <Label>Variants</Label>
                    <Input
                      type="number"
                      min="1"
                      max="3"
                      value={formData.variantCount}
                      onChange={(e) => handleInputChange('variantCount', parseInt(e.target.value) || 1)}
                    />
                  </FormGroup>
                </div>
              </div>

              <FormGroup>
                <Label>Creativity ({formData.creativity})</Label>
                <Input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={formData.creativity}
                  onChange={(e) => handleInputChange('creativity', parseFloat(e.target.value))}
                />
                <div className="form-note">Higher values = more creative, lower = more focused</div>
              </FormGroup>

              <Button
                type="submit"
                color="primary"
                size="lg"
                className="w-100 mt-2"
                disabled={loading || !formData.prompt.trim()}
              >
                {loading ? (
                  <>
                    <Spinner size="sm" className="me-2" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Icon name="spark" className="me-2"></Icon>
                    <span>Generate Content</span>
                  </>
                )}
              </Button>
            </Form>
          </TabPane>

          <TabPane tabId="2">
            <div className="mt-3">
              {/* History Header */}
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h6 className="mb-0">Generation History</h6>
                <small className="text-soft">
                  {variants.length} {variants.length === 1 ? 'variant' : 'variants'}
                </small>
              </div>

              {variants.length === 0 ? (
                <div className="text-center py-5">
                  <Icon name="file-text" className="text-soft mb-2" style={{ fontSize: '3rem' }}></Icon>
                  <p className="text-soft">No variants generated yet</p>
                  <small className="text-soft">Switch to AI Writer tab and generate content</small>
                </div>
              ) : (
                <div className="history-list">
                  {variants.map((variant, index) => {
                    const isExpanded = expandedVariants[index];
                    const previewText = variant.content.replace(/<[^>]*>/g, '');
                    const displayText = isExpanded ? previewText : previewText.substring(0, 150) + (previewText.length > 150 ? '...' : '');
                    
                    return (
                      <Card key={index} className="card-bordered mb-3">
                        <CardBody className="card-inner-sm">
                          {/* Header with badge and actions */}
                          <div className="d-flex justify-content-between align-items-start mb-2">
                            <span className="badge badge-primary badge-sm">
                              <Icon name="spark" className="me-1" style={{ fontSize: '10px' }}></Icon>
                              {selectedTool?.title || 'AI Generated'}
                            </span>
                            <div className="d-flex gap-1">
                              <Button 
                                size="sm" 
                                className="btn-icon btn-trigger"
                                onClick={() => toggleVariant(index)}
                                title={isExpanded ? 'Collapse' : 'Expand'}
                              >
                                <Icon name={isExpanded ? 'chevron-up' : 'chevron-down'} />
                              </Button>
                              <Button 
                                size="sm" 
                                className="btn-icon btn-trigger"
                                onClick={() => handleCopyVariant(variant)}
                                title="Copy to clipboard"
                              >
                                <Icon name="copy" />
                              </Button>
                            </div>
                          </div>

                          {/* Content preview */}
                          <p className="mb-2" style={{ fontSize: '13px', lineHeight: '1.5' }}>
                            {displayText}
                          </p>

                          {/* Footer with meta info */}
                          <div className="d-flex justify-content-between align-items-center text-soft small">
                            <span>{new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                            <span>{variant.metadata?.words || textUtils.countWords(variant.content)} Words</span>
                          </div>

                          {/* Insert button (visible when expanded) */}
                          {isExpanded && (
                            <div className="mt-2 pt-2 border-top">
                              <Button
                                color="primary"
                                size="sm"
                                className="w-100"
                                onClick={() => onInsert && onInsert(variant)}
                              >
                                <Icon name="plus" className="me-1"></Icon>
                                Insert into Editor
                              </Button>
                            </div>
                          )}
                        </CardBody>
                      </Card>
                    );
                  })}
                </div>
              )}
            </div>
          </TabPane>
        </TabContent>
      </CardBody>
    </Card>
  );
};

export default AiWriterPanel;
