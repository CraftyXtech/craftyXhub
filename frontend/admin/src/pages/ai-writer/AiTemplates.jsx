import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Nav, NavItem, NavLink, TabContent, TabPane } from 'reactstrap';
import Head from '@/layout/head/Head';
import Content from '@/layout/content/Content';
import { Block, BlockHead, BlockTitle, BlockDes, BlockBetween, BlockHeadContent, Row, Col } from '@/components/Component';
import TemplateCard from '@/components/ai-writer/TemplateCard';
import { AI_TEMPLATES, TEMPLATE_CATEGORIES } from '@/data/aiTemplates';
import classnames from 'classnames';

const AiTemplates = () => {
  const navigate = useNavigate();
  const [activeCategory, setActiveCategory] = useState('all');

  const filteredTemplates = activeCategory === 'all'
    ? AI_TEMPLATES
    : AI_TEMPLATES.filter(template => template.category === activeCategory);

  const handleTemplateClick = (template) => {
    navigate('/ai-writer/editor/new', { 
      state: { selectedTemplate: template } 
    });
  };

  return (
    <>
      <Head title="AI Templates" />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BlockTitle page>AI Content Templates</BlockTitle>
              <BlockDes className="text-soft">
                <p>Choose a template to generate AI-powered content</p>
              </BlockDes>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <Nav tabs className="nav-tabs-s2 mb-4">
            {TEMPLATE_CATEGORIES.map((category) => (
              <NavItem key={category.id}>
                <NavLink
                  tag="a"
                  href="#tab"
                  className={classnames({ active: activeCategory === category.id })}
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveCategory(category.id);
                  }}
                >
                  {category.name}
                </NavLink>
              </NavItem>
            ))}
          </Nav>

          <TabContent activeTab={activeCategory}>
            <TabPane tabId={activeCategory}>
              {filteredTemplates.length === 0 ? (
                <div className="text-center py-5">
                  <p className="text-soft">No templates found in this category</p>
                </div>
              ) : (
                <Row className="g-gs">
                  {filteredTemplates.map((template) => (
                    <Col key={template.id} sm="6" lg="4" xxl="3">
                      <TemplateCard
                        icon={template.icon}
                        title={template.title}
                        description={template.description}
                        color={template.color}
                        onClick={() => handleTemplateClick(template)}
                      />
                    </Col>
                  ))}
                </Row>
              )}
            </TabPane>
          </TabContent>
        </Block>
      </Content>
    </>
  );
};

export default AiTemplates;

