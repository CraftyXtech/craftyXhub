import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import Head from '@/layout/head/Head';
import Content from '@/layout/content/Content';
import { Block, BlockHead, BlockTitle, BlockDes, BlockBetween, BlockHeadContent, Row, Col, Button, Icon, DataTable, DataTableBody, DataTableHead, DataTableRow, DataTableItem } from '@/components/Component';
import AiStatCard from '@/components/ai-writer/AiStatCard';
import TemplateCard from '@/components/ai-writer/TemplateCard';
import { useAiDrafts } from '@/context/AiDraftContext';
import { AI_TEMPLATES } from '@/data/aiTemplates';
import { textUtils } from '@/utils/textUtils';

const AiDashboard = () => {
  const navigate = useNavigate();
  const { drafts, getStats } = useAiDrafts();
  const stats = getStats();

  const recentDrafts = useMemo(() => {
    return drafts
      .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
      .slice(0, 5);
  }, [drafts]);

  const popularTemplates = AI_TEMPLATES.slice(0, 4);

  const wordLimit = 2000;
  const draftLimit = 10;
  const toolsUsed = Object.keys(stats.draftsByType || {}).length;
  const toolsLimit = 16;

  return (
    <>
      <Head title="Content Generator Dashboard" />
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
                onClick={() => navigate('/ai-writer/editor/new')}
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
                title="Content Drafts"
                value={`${stats.totalDrafts}`}
                subtitle={`${stats.totalDrafts} drafts created`}
                color="warning"
                variant="solid"
                icon="file-text"
                linkText="View All"
                onLinkClick={() => navigate('/ai-writer/documents')}
              />
            </Col>
            <Col sm="6" lg="4">
              <AiStatCard
                title="Words Generated"
                value={`${stats.totalWords}`}
                subtitle="Total words created with AI"
                color="cyan"
                variant="solid"
                icon="edit"
                linkText="View Drafts"
                onLinkClick={() => navigate('/ai-writer/documents')}
              />
            </Col>
            <Col sm="6" lg="4">
              <AiStatCard
                title="Tools Available"
                value={`${AI_TEMPLATES.length}`}
                subtitle={`${toolsUsed}/${toolsLimit} tools used to generate`}
                color="danger"
                variant="solid"
                icon="spark"
                linkText="All Tools"
                onLinkClick={() => navigate('/ai-writer/templates')}
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
                <BlockTitle>Recent Drafts</BlockTitle>
              </BlockHeadContent>
              <BlockHeadContent>
                <Button color="light" outline onClick={() => navigate('/ai-writer/documents')}>
                  <span>View All</span>
                  <Icon name="arrow-right" className="ms-1" />
                </Button>
              </BlockHeadContent>
            </BlockBetween>
          </BlockHead>

          {recentDrafts.length === 0 ? (
            <div className="text-center py-5 card card-bordered">
              <div className="card-inner">
                <Icon name="file-text" className="text-soft mb-2" style={{ fontSize: '3rem' }} />
                <p className="text-soft">No drafts yet</p>
                <Button color="primary" onClick={() => navigate('/ai-writer/editor/new')}>
                  <Icon name="plus" className="me-1" />
                  <span>Generate Your First Draft</span>
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
                {recentDrafts.map((draft) => (
                  <DataTableItem key={draft.id}>
                    <DataTableRow>
                      <div className="user-card">
                        <div className="user-info">
                          <span className="tb-lead">{draft.name}</span>
                          <span className="sub-text">{draft.metadata?.words || 0} words</span>
                        </div>
                      </div>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="badge badge-dim badge-sm badge-primary">
                        {draft.type || 'Blog Post'}
                      </span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="sub-text">{textUtils.timeAgo(draft.updated_at)}</span>
                    </DataTableRow>
                    <DataTableRow size="sm" className="nk-tb-col-tools">
                      <ul className="nk-tb-actions gx-1">
                        <li>
                          <Button
                            className="btn-icon btn-trigger"
                            size="sm"
                            color="primary"
                            onClick={() => navigate(`/ai-writer/editor/${draft.id}`)}
                            title="Edit Draft"
                          >
                            <Icon name="edit" />
                          </Button>
                        </li>
                      </ul>
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

