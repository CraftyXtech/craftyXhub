import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import Head from '@/layout/head/Head';
import Content from '@/layout/content/Content';
import { Block, BlockHead, BlockTitle, BlockDes, BlockBetween, BlockHeadContent, Row, Col, Button, Icon, DataTable, DataTableBody, DataTableHead, DataTableRow, DataTableItem } from '@/components/Component';
import AiStatCard from '@/components/ai-writer/AiStatCard';
import TemplateCard from '@/components/ai-writer/TemplateCard';
import { useAiDocuments } from '@/context/AiDocumentContext';
import { AI_TEMPLATES } from '@/data/aiTemplates';
import { textUtils } from '@/utils/textUtils';

const AiDashboard = () => {
  const navigate = useNavigate();
  const { documents, getStats } = useAiDocuments();
  const stats = getStats();

  const recentDocuments = useMemo(() => {
    return documents
      .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
      .slice(0, 5);
  }, [documents]);

  const popularTemplates = AI_TEMPLATES.slice(0, 4);

  const wordLimit = 2000;
  const draftLimit = 10;
  const toolsUsed = Object.keys(stats.documentsByType).length;
  const toolsLimit = 16;

  return (
    <>
      <Head title="AI Writer Dashboard" />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BlockTitle page>Welcome Back!</BlockTitle>
              <BlockDes className="text-soft">
                <p>AI-powered content creation at your fingertips</p>
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              <Button
                color="primary"
                onClick={() => navigate('/ai-writer/editor/generate')}
              >
                <Icon name="plus" />
                <span>Create New</span>
              </Button>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <Row className="g-gs">
            <Col sm="6" lg="4">
              <AiStatCard
                title="Drafts Available"
                value={`${stats.totalDocuments}`}
                subtitle={`${stats.totalDocuments}/${draftLimit} free drafts created`}
                color="warning"
                variant="solid"
                linkText="See All"
              />
            </Col>
            <Col sm="6" lg="4">
              <AiStatCard
                title="Documents Available"
                value={`${stats.totalDocuments}`}
                subtitle={`${stats.totalDocuments}/10 free documents created`}
                color="cyan"
                variant="solid"
                linkText="See All"
              />
            </Col>
            <Col sm="6" lg="4">
              <AiStatCard
                title="Tools Available"
                value={`${AI_TEMPLATES.length}`}
                subtitle={`${toolsUsed}/${toolsLimit} tools used to generate`}
                color="danger"
                variant="solid"
                linkText="All Tools"
              />
            </Col>
          </Row>
        </Block>

        <Block>
          <BlockHead>
            <BlockBetween className="g-3">
              <BlockHeadContent>
                <BlockTitle>Popular Templates</BlockTitle>
              </BlockHeadContent>
              <BlockHeadContent>
                <Button color="light" outline onClick={() => navigate('/ai-writer/templates')}>
                  <span>Explore All</span>
                  <Icon name="arrow-right" className="ms-1" />
                </Button>
              </BlockHeadContent>
            </BlockBetween>
          </BlockHead>
          <Row className="g-gs">
            {popularTemplates.map((template) => (
              <Col key={template.id} sm="6" lg="3">
                <TemplateCard
                  icon={template.icon}
                  title={template.title}
                  description={template.description}
                  color={template.color}
                  onClick={() => navigate('/ai-writer/editor/generate', { 
                    state: { selectedTemplate: template } 
                  })}
                />
              </Col>
            ))}
          </Row>
        </Block>

        <Block>
          <BlockHead>
            <BlockBetween className="g-3">
              <BlockHeadContent>
                <BlockTitle>Recent Documents</BlockTitle>
              </BlockHeadContent>
              <BlockHeadContent>
                <Button color="light" outline onClick={() => navigate('/ai-writer/documents')}>
                  <span>See All</span>
                  <Icon name="arrow-right" className="ms-1" />
                </Button>
              </BlockHeadContent>
            </BlockBetween>
          </BlockHead>

          {recentDocuments.length === 0 ? (
            <div className="text-center py-5 card card-bordered">
              <div className="card-inner">
                <Icon name="file-text" className="text-soft mb-2" style={{ fontSize: '3rem' }} />
                <p className="text-soft">No documents yet</p>
                <Button color="primary" onClick={() => navigate('/ai-writer/editor/generate')}>
                  <Icon name="plus" className="me-1" />
                  <span>Create Your First Document</span>
                </Button>
              </div>
            </div>
          ) : (
            <DataTable className="card card-bordered">
              <DataTableHead>
                <DataTableRow>
                  <span className="sub-text">Name</span>
                </DataTableRow>
                <DataTableRow size="sm">
                  <span className="sub-text">Type</span>
                </DataTableRow>
                <DataTableRow size="sm">
                  <span className="sub-text">Last Modified</span>
                </DataTableRow>
                <DataTableRow size="sm" className="nk-tb-col-tools text-end">
                  <span className="sub-text">Actions</span>
                </DataTableRow>
              </DataTableHead>
              <DataTableBody>
                {recentDocuments.map((doc) => (
                  <DataTableItem key={doc.id}>
                    <DataTableRow>
                      <div className="user-card">
                        <div className="user-info">
                          <span className="tb-lead">{doc.name}</span>
                          <span className="sub-text">{doc.metadata?.words || 0} words</span>
                        </div>
                      </div>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="badge badge-dim badge-sm badge-primary">
                        {doc.type || 'Blog Post'}
                      </span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span>{textUtils.timeAgo(doc.updated_at)}</span>
                    </DataTableRow>
                    <DataTableRow size="sm" className="nk-tb-col-tools text-end">
                      <Button
                        color="primary"
                        size="sm"
                        onClick={() => navigate(`/ai-writer/editor/${doc.id}`)}
                      >
                        <Icon name="edit" />
                        <span>Edit</span>
                      </Button>
                    </DataTableRow>
                  </DataTableItem>
                ))}
              </DataTableBody>
            </DataTable>
          )}
        </Block>
      </Content>
    </>
  );
};

export default AiDashboard;

