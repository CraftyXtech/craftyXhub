import { Card } from 'reactstrap';
import PropTypes from 'prop-types';

const AiStatCard = ({
  title,
  value,
  subtitle,
  color = 'primary',
  variant = 'bordered',
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

  const isSolid = variant === 'solid';
  const cardClass = isSolid ? `card-full ${solidColors[color]} is-dark` : 'card-bordered';

  return (
    <Card className={`${cardClass} h-100 ${className}`} style={{ borderRadius: '4px' }}>
      <div className="card-inner" style={{ padding: '1.25rem' }}>
        <div className="d-flex justify-content-between align-items-start mb-3">
          <div>
            <h6 className={`fs-13px fw-normal mb-0 ${isSolid ? 'text-white opacity-90' : 'text-soft'}`}>
              {title}
            </h6>
          </div>
          {linkText && (
            <a
              href="#link"
              onClick={(e) => {
                e.preventDefault();
                onLinkClick && onLinkClick();
              }}
              className={`fs-13px ${isSolid ? 'text-white' : 'text-primary'}`}
              style={{ textDecoration: 'none', fontWeight: '400' }}
            >
              {linkText}
            </a>
          )}
        </div>

        <div className="mb-1">
          <h2 className={`fw-bold mb-0 ${isSolid ? 'text-white' : ''}`} style={{ fontSize: '2rem', lineHeight: '1.2' }}>
            {value}
          </h2>
        </div>

        {subtitle && (
          <div className={`fs-13px ${isSolid ? 'text-white opacity-75' : 'text-soft'}`}>
            {subtitle}
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
  linkText: PropTypes.string,
  onLinkClick: PropTypes.func,
  className: PropTypes.string
};

export default AiStatCard;

