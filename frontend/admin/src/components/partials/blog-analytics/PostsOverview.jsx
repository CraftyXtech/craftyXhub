import React from 'react';
import { Card, CardBody } from 'reactstrap';
import { Icon } from '@/components/Component';

const PostsOverview = ({ data }) => {
  const stats = [
    {
      title: 'Total Posts',
      value: data?.totalPosts || 0,
      icon: 'file-text',
      color: 'primary',
      change: '+12.5%',
      changeType: 'up'
    },
    {
      title: 'Published',
      value: data?.published || 0,
      icon: 'check-circle',
      color: 'success',
      change: '+8.3%',
      changeType: 'up'
    },
    {
      title: 'Drafts',
      value: data?.drafts || 0,
      icon: 'edit',
      color: 'warning',
      change: '-2.1%',
      changeType: 'down'
    },
    {
      title: 'Trending',
      value: data?.trending || 0,
      icon: 'trending-up',
      color: 'info',
      change: '+25.8%',
      changeType: 'up'
    }
  ];

  return (
    <Card className="card-bordered h-100">
      <CardBody className="card-inner">
        <div className="card-title-group align-start mb-3">
          <div className="card-title">
            <h6 className="title">Posts Overview</h6>
            <p className="text-soft">Summary of your blog posts</p>
          </div>
        </div>
        <div className="nk-tb-list">
          {stats.map((stat, index) => (
            <div key={index} className="nk-tb-item">
              <div className="nk-tb-col">
                <div className={`icon-circle icon-circle-lg bg-${stat.color}-dim text-${stat.color}`}>
                  <Icon name={stat.icon}></Icon>
                </div>
              </div>
              <div className="nk-tb-col tb-col-md">
                <span className="sub-text">{stat.title}</span>
              </div>
              <div className="nk-tb-col tb-col-end">
                <span className="lead-text">{stat.value}</span>
                <span className={`change ${stat.changeType === 'up' ? 'up' : 'down'} text-${stat.changeType === 'up' ? 'success' : 'danger'}`}>
                  <Icon name={stat.changeType === 'up' ? 'arrow-long-up' : 'arrow-long-down'}></Icon>
                  {stat.change}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
};

export default PostsOverview;

