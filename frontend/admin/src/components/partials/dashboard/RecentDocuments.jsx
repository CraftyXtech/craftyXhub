import React from 'react';
import { Button, Icon, DataTable, DataTableBody, DataTableHead, DataTableRow, DataTableItem, BlockHead, BlockBetween, BlockHeadContent, BlockTitle } from '@/components/Component';

const mockRecentDocuments = [
  { id: 'r1', name: 'The Impact of Artificial Intelligence on the Future of Work', type: 'Document', category: 'Blog Content', updated_at: '2023-02-15T14:31:00Z' },
  { id: 'r2', name: 'How to Boost Your Online Presence with Social Media Marketing', type: 'Social Media', category: 'Marketing', updated_at: '2023-02-15T14:31:00Z' },
  { id: 'r3', name: 'Top 10 Tips for Effective Time Management in the Workplace', type: 'Blog Content', category: 'Productivity', updated_at: '2023-02-15T14:31:00Z' },
  { id: 'r4', name: 'Transforming Healthcare with Big Data: Exploring the Opportunities', type: 'Website Copy & SEO', category: 'SEO', updated_at: '2023-02-15T14:31:00Z' },
  { id: 'r5', name: 'YouTube Tags Strategy for 2024: Complete Guide', type: 'Video', category: 'SEO', updated_at: '2023-02-15T14:31:00Z' },
];

const TypeBadge = ({ type }) => {
  const map = {
    'Document': 'primary',
    'Social Media': 'info',
    'Blog Content': 'purple',
    'Website Copy & SEO': 'warning',
    'Video': 'success',
  };
  const color = map[type] || 'gray';
  return <span className={`badge badge-dim badge-sm badge-${color}`}>{type}</span>;
};

const RecentDocuments = ({ onSeeAll }) => {
  return (
    <div className="card card-bordered">
      <div className="card-inner">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <BlockHead size="sm" className="m-0">
            <BlockBetween>
              <BlockHeadContent>
                <BlockTitle tag="h6">Recent Documents</BlockTitle>
              </BlockHeadContent>
            </BlockBetween>
          </BlockHead>
          <Button size="sm" color="light" outline onClick={onSeeAll}>
            <span>See All</span>
            <Icon name="arrow-right" className="ms-1" />
          </Button>
        </div>

        <DataTable>
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
            {mockRecentDocuments.map((doc) => (
              <DataTableItem key={doc.id}>
                <DataTableRow>
                  <div className="user-card">
                    <div className="user-info">
                      <span className="tb-lead">{doc.name}</span>
                      <span className="sub-text">{doc.category}</span>
                    </div>
                  </div>
                </DataTableRow>
                <DataTableRow size="sm">
                  <TypeBadge type={doc.type} />
                </DataTableRow>
                <DataTableRow size="sm">
                  <span>Feb 15,2023 02:31 PM</span>
                </DataTableRow>
                <DataTableRow size="sm" className="nk-tb-col-tools text-end">
                  <Button color="primary" size="sm" outline>
                    <Icon name="eye" />
                    <span className="ms-1">View</span>
                  </Button>
                </DataTableRow>
              </DataTableItem>
            ))}
          </DataTableBody>
        </DataTable>
      </div>
    </div>
  );
};

export default RecentDocuments;
