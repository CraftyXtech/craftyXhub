import React from 'react';
import { Card, CardBody } from 'reactstrap';
import { Icon } from '@/components/Component';

const RecentActivity = ({ data }) => {
  const defaultActivities = [
    {
      id: 1,
      type: 'post',
      icon: 'file-text',
      color: 'primary',
      title: 'New post published',
      description: 'Building Scalable APIs with FastAPI',
      time: '2 hours ago'
    },
    {
      id: 2,
      type: 'comment',
      icon: 'chat',
      color: 'info',
      title: 'New comment received',
      description: 'Great article! Very helpful.',
      time: '5 hours ago'
    },
    {
      id: 3,
      type: 'report',
      icon: 'alert-circle',
      color: 'warning',
      title: 'Post reported',
      description: 'User reported inappropriate content',
      time: '1 day ago'
    },
    {
      id: 4,
      type: 'post',
      icon: 'edit',
      color: 'success',
      title: 'Post updated',
      description: 'Introduction to React Hooks',
      time: '2 days ago'
    },
    {
      id: 5,
      type: 'comment',
      icon: 'chat',
      color: 'info',
      title: 'New comment received',
      description: 'Thanks for sharing this!',
      time: '3 days ago'
    }
  ];

  const activities = data?.activities || defaultActivities;

  return (
    <Card className="card-bordered h-100">
      <CardBody className="card-inner">
        <div className="card-title-group align-start mb-3">
          <div className="card-title">
            <h6 className="title">Recent Activity</h6>
            <p className="text-soft">Latest updates and actions</p>
          </div>
        </div>
        <ul className="nk-activity">
          {activities.map((activity) => (
            <li key={activity.id} className="nk-activity-item">
              <div className={`nk-activity-media icon-wrap-lg bg-${activity.color}-dim`}>
                <Icon name={activity.icon} className={`text-${activity.color} icon-lg`}></Icon>
              </div>
              <div className="nk-activity-data">
                <div className="label">{activity.title}</div>
                <span className="sub-text">{activity.description}</span>
                <span className="time">{activity.time}</span>
              </div>
            </li>
          ))}
        </ul>
      </CardBody>
    </Card>
  );
};

export default RecentActivity;

