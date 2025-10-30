import { Card } from 'reactstrap';
import PropTypes from 'prop-types';
import { Icon } from '@/components/Component';

const AiStatCard = ({
  title,
  value,
  subtitle,
  color = 'primary',
  variant = 'bordered',
  icon = 'file-text',
  linkText,
  onLinkClick,
  className = ''
}) => {
  const solidColors = {
    primary: 'bg-primary',
    info: 'bg-info', 
    success: 'bg-success',
    warning: 'bg-warning',
    danger: 'bg-danger',
    cyan: 'bg-info'
  };

  const iconColorClasses = {
    primary: 'bg-primary-dim text-primary',
    info: 'bg-info-dim text-info',
    success: 'bg-success-dim text-success',
    warning: 'bg-warning-dim text-warning',
    danger: 'bg-danger-dim text-danger',
    cyan: 'bg-info-dim text-info'
  };

  // For solid cards, use semi-transparent black background with white icons for better contrast
  const solidIconStyle = {
    backgroundColor: 'rgba(0, 0, 0, 0.15)',
    color: 'white'
  };

  const isSolid = variant === 'solid';
  const cardClass = isSolid ? `card-full ${solidColors[color]} is-dark` : 'card-bordered';

  return (
    <Card className={`${cardClass} h-100 ${className}`}>
      <div className="card-inner">
        <div className="card-title-group align-start mb-2">
          <div className="card-title">
            <h6 className={`title ${isSolid ? 'text-white' : ''}`}>{title}</h6>
          </div>
          <div className="card-tools">
            <div 
              className={`icon-circle ${isSolid ? '' : iconColorClasses[color]}`} 
              style={{ 
                height: '40px', 
                width: '40px', 
                fontSize: '18px',
                ...(isSolid ? solidIconStyle : {})
              }}
            >
              <Icon name={icon} />
            </div>
          </div>
        </div>

        <div className="card-amount">
          <span className={`amount ${isSolid ? 'text-white' : ''}`} style={{ fontSize: '1.75rem' }}>
            {value}
          </span>
        </div>

        {subtitle && (
          <div className="card-info mt-2">
            <span className={`sub-text ${isSolid ? 'text-white' : ''}`} style={{ opacity: isSolid ? 0.8 : 1 }}>
              {subtitle}
            </span>
          </div>
        )}

        {linkText && (
          <div className="card-note mt-2">
            <a
              href="#link"
              onClick={(e) => {
                e.preventDefault();
                onLinkClick && onLinkClick();
              }}
              className={`link ${isSolid ? 'text-white' : ''}`}
            >
              <span>{linkText}</span>
            </a>
          </div>
        )}
      </div>
    </Card>
  );
};

AiStatCard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  subtitle: PropTypes.string,
  color: PropTypes.oneOf(['primary', 'info', 'success', 'warning', 'danger', 'cyan']),
  variant: PropTypes.oneOf(['bordered', 'solid']),
  icon: PropTypes.string,
  linkText: PropTypes.string,
  onLinkClick: PropTypes.func,
  className: PropTypes.string
};

export default AiStatCard;

