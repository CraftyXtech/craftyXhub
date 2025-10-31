import React from 'react';
import { Card, CardBody } from 'reactstrap';
import { Icon, Button } from '@/components/Component';

const ToolCard = ({
  icon,
  title,
  description,
  color = 'primary',
  badge,
  onClick,
  className = ''
}) => {
  const iconColorClasses = {
    primary: 'bg-primary-dim text-primary',
    info: 'bg-info-dim text-info',
    success: 'bg-success-dim text-success',
    warning: 'bg-warning-dim text-warning',
    danger: 'bg-danger-dim text-danger'
  };

  return (
    <Card className={`card-bordered h-100 ${className}`} style={{ cursor: 'pointer' }} onClick={onClick}>
      <CardBody className="card-inner">
        <div className="project-head">
          <div className="d-flex justify-content-center">
            <div className={`icon-circle icon-circle-lg ${iconColorClasses[color]}`}>
              <Icon name={icon}></Icon>
            </div>
          </div>
          {badge && (
            <div className="project-action">
              <span className={`badge badge-sm badge-dot badge-${color}`}>{badge}</span>
            </div>
          )}
        </div>
        <div className="project-info mt-3 text-center">
          <h6 className="title">{title}</h6>
          <span className="sub-text">{description}</span>
        </div>
        <div className="project-meta mt-3 d-flex justify-content-center">
          <Button color="primary" size="sm" className="btn-dim" onClick={(e) => {
            e.stopPropagation();
            if (onClick) onClick();
          }}>
            <Icon name="spark" className="me-1"></Icon>
            <span>Use Tool</span>
          </Button>
        </div>
      </CardBody>
    </Card>
  );
};

export default ToolCard;

