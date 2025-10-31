import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Nav, NavItem, NavLink, TabContent, TabPane } from 'reactstrap';
import Head from '@/layout/head/Head';
import Content from '@/layout/content/Content';
import { Block, BlockHead, BlockTitle, BlockDes, BlockBetween, BlockHeadContent, Row, Col } from '@/components/Component';
import ToolCard from '@/components/ai-writer/ToolCard';
import { AI_TOOLS, TOOL_CATEGORIES } from '@/data/aiTools';
import classnames from 'classnames';

const AiTools = () => {
  const navigate = useNavigate();
  const [activeCategory, setActiveCategory] = useState('all');

  const filteredTools = activeCategory === 'all'
    ? AI_TOOLS
    : AI_TOOLS.filter(tool => tool.category === activeCategory);

  const handleToolClick = (tool) => {
    navigate('/ai-writer/editor/new', { 
      state: { selectedTool: tool } 
    });
  };

  return (
    <>
      <Head title="AI Tools" />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BlockTitle page>AI Content Tools</BlockTitle>
              <BlockDes className="text-soft">
                <p>Choose a tool to generate AI-powered content</p>
              </BlockDes>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <Nav tabs className="nav-tabs-s2 mb-4">
            {TOOL_CATEGORIES.map((category) => (
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
              {filteredTools.length === 0 ? (
                <div className="text-center py-5">
                  <p className="text-soft">No tools found in this category</p>
                </div>
              ) : (
                <Row className="g-gs">
                  {filteredTools.map((tool) => (
                    <Col key={tool.id} sm="6" lg="4" xxl="3">
                      <ToolCard
                        icon={tool.icon}
                        title={tool.title}
                        description={tool.description}
                        color={tool.color}
                        onClick={() => handleToolClick(tool)}
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

export default AiTools;

