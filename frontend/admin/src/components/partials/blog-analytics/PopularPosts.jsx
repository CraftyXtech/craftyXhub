import React from 'react';
import { Card, CardBody } from 'reactstrap';
import { DataTable, DataTableBody, DataTableHead, DataTableRow, DataTableItem, Icon } from '@/components/Component';

const PopularPosts = ({ data }) => {
  const defaultPosts = [
    {
      id: 1,
      title: 'Getting Started with React Hooks',
      views: '2.5k',
      likes: 342,
      trend: 'up'
    },
    {
      id: 2,
      title: 'Advanced TypeScript Patterns',
      views: '1.8k',
      likes: 256,
      trend: 'up'
    },
    {
      id: 3,
      title: 'Building Scalable APIs with FastAPI',
      views: '1.2k',
      likes: 189,
      trend: 'up'
    },
    {
      id: 4,
      title: 'Introduction to Next.js 14',
      views: '980',
      likes: 145,
      trend: 'down'
    },
    {
      id: 5,
      title: 'CSS Grid Layout Mastery',
      views: '875',
      likes: 128,
      trend: 'up'
    }
  ];

  const posts = data?.posts || defaultPosts;

  return (
    <Card className="card-bordered h-100">
      <CardBody className="card-inner">
        <div className="card-title-group align-start mb-3">
          <div className="card-title">
            <h6 className="title">Popular Posts</h6>
            <p className="text-soft">Top performing content</p>
          </div>
        </div>
        <DataTable>
          <DataTableHead>
            <DataTableRow>
              <span className="sub-text">Post Title</span>
            </DataTableRow>
            <DataTableRow size="sm">
              <span className="sub-text">Views</span>
            </DataTableRow>
            <DataTableRow size="sm">
              <span className="sub-text">Likes</span>
            </DataTableRow>
            <DataTableRow size="sm" className="text-end">
              <span className="sub-text">Trend</span>
            </DataTableRow>
          </DataTableHead>
          <DataTableBody>
            {posts.map((post) => (
              <DataTableItem key={post.id}>
                <DataTableRow>
                  <span className="tb-lead">{post.title}</span>
                </DataTableRow>
                <DataTableRow size="sm">
                  <span className="tb-sub">{post.views}</span>
                </DataTableRow>
                <DataTableRow size="sm">
                  <span className="tb-sub">{post.likes}</span>
                </DataTableRow>
                <DataTableRow size="sm" className="text-end">
                  <Icon 
                    name={post.trend === 'up' ? 'arrow-long-up' : 'arrow-long-down'} 
                    className={`text-${post.trend === 'up' ? 'success' : 'danger'}`}
                  ></Icon>
                </DataTableRow>
              </DataTableItem>
            ))}
          </DataTableBody>
        </DataTable>
      </CardBody>
    </Card>
  );
};

export default PopularPosts;

