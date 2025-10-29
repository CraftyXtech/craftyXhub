import React from 'react';
import { Card, CardBody } from 'reactstrap';
import { Row, Col } from 'reactstrap';
import { Icon } from '@/components/Component';

const EngagementMetrics = ({ data }) => {
  const metrics = [
    {
      title: 'Total Views',
      value: data?.totalViews || '0',
      icon: 'eye',
      change: '+15.2%',
      color: 'primary'
    },
    {
      title: 'Likes',
      value: data?.likes || '0',
      icon: 'heart',
      change: '+8.5%',
      color: 'success'
    },
    {
      title: 'Comments',
      value: data?.comments || '0',
      icon: 'chat',
      change: '+12.3%',
      color: 'info'
    },
    {
      title: 'Bookmarks',
      value: data?.bookmarks || '0',
      icon: 'bookmark',
      change: '+10.1%',
      color: 'warning'
    }
  ];

  return (
    <Card className="card-bordered h-100">
      <CardBody className="card-inner">
        <div className="card-title-group align-start mb-3">
          <div className="card-title">
            <h6 className="title">Engagement Metrics</h6>
            <p className="text-soft">User interactions with your content</p>
          </div>
        </div>
        <Row className="g-3">
          {metrics.map((metric, index) => (
            <Col key={index} sm="6">
              <div className="card-inner-sm card-bordered">
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <div className="sub-text mb-1">{metric.title}</div>
                    <div className="lead-text">{metric.value}</div>
                    <span className={`change up text-${metric.color}`}>{metric.change}</span>
                  </div>
                  <div className={`icon-wrap icon-wrap-lg bg-${metric.color}-dim`}>
                    <Icon name={metric.icon} className={`text-${metric.color} icon-lg`}></Icon>
                  </div>
                </div>
              </div>
            </Col>
          ))}
        </Row>
      </CardBody>
    </Card>
  );
};

export default EngagementMetrics;

