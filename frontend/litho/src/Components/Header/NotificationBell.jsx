import React, { useState } from 'react';
import { Dropdown } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useNotifications } from '../../Context/NotificationContext';

const NotificationBell = () => {
  const navigate = useNavigate();
  const { notifications, unreadCount, loading, markAsRead, markAllAsRead } = useNotifications();
  const [show, setShow] = useState(false);

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  const getIcon = (type) => {
    const iconMap = {
      post_like: "fas fa-heart",
      post_comment: "fas fa-comment",
      comment_reply: "fas fa-reply",
      new_follower: "fas fa-user-plus",
      new_post_from_following: "fas fa-file-alt",
      post_published: "fas fa-check-circle",
      post_flagged: "fas fa-exclamation-circle",
      post_unflagged: "fas fa-check-circle",
      post_reported: "fas fa-flag",
      post_bookmark: "fas fa-bookmark",
      welcome: "fas fa-gift",
      email_verified: "fas fa-envelope-circle-check",
    };
    return iconMap[type] || "fas fa-bell";
  };

  const getIconColor = (type) => {
    const colorMap = {
      post_like: "text-danger",
      post_comment: "text-info",
      comment_reply: "text-primary",
      new_follower: "text-success",
      new_post_from_following: "text-warning",
      post_published: "text-success",
      post_flagged: "text-warning",
      post_unflagged: "text-success",
      post_reported: "text-danger",
      post_bookmark: "text-primary",
      welcome: "text-info",
      email_verified: "text-success",
    };
    return colorMap[type] || "text-dark";
  };

  const handleNotificationClick = async (notification) => {
    // Mark as read
    if (!notification.is_read) {
      await markAsRead(notification.uuid);
    }
    setShow(false);
    
    // Navigate to the action URL if present
    if (notification.action_url) {
      navigate(notification.action_url);
    }
  };

  return (
    <Dropdown show={show} onToggle={(isOpen) => setShow(isOpen)} align="end">
      <Dropdown.Toggle 
        as="a"
        className="position-relative text-decoration-none d-inline-flex align-items-center justify-center"
        style={{ 
          width: '40px', 
          height: '40px',
          cursor: 'pointer',
          color: '#232323',
          transition: 'all 0.3s ease'
        }}
      >
        <i className="fas fa-bell" style={{ fontSize: '1.25rem' }}></i>
        {unreadCount > 0 && (
          <span 
            className="position-absolute badge rounded-pill bg-danger"
            style={{ 
              top: '0',
              right: '0',
              fontSize: '0.65rem',
              padding: '0.2rem 0.4rem',
              minWidth: '18px',
              lineHeight: '1'
            }}
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </Dropdown.Toggle>

      <Dropdown.Menu className="shadow-lg border-0" style={{ width: '360px', maxHeight: '500px', overflowY: 'auto' }}>
        <div className="d-flex justify-content-between align-items-center p-3 border-bottom bg-light">
          <h6 className="mb-0 fw-bold">Notifications {unreadCount > 0 && `(${unreadCount})`}</h6>
          {unreadCount > 0 && (
            <button 
              className="btn btn-sm btn-link text-decoration-none p-0 fw-semibold"
              onClick={(e) => { e.preventDefault(); markAllAsRead(); }}
              style={{ fontSize: '0.8rem' }}
            >
              Mark all read
            </button>
          )}
        </div>

        <div className="notification-list" style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {loading ? (
            <div className="text-center p-4">
              <div className="spinner-border spinner-border-sm text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          ) : notifications.length === 0 ? (
            <div className="text-center p-4 text-muted">
              <p className="mb-0">No notifications yet</p>
            </div>
          ) : (
            notifications.slice(0, 8).map((notification) => (
              <div
                key={notification.uuid}
                className={`notification-item p-3 border-bottom ${!notification.is_read ? 'bg-light' : ''}`}
                style={{ cursor: 'pointer', transition: 'background-color 0.2s' }}
                onClick={() => handleNotificationClick(notification)}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f8f9fa'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = notification.is_read ? '#fff' : '#f8f9fa'}
              >
                <div className="d-flex align-items-start">
                  <div className="flex-shrink-0 me-3 d-flex align-items-center justify-center" style={{ width: '32px', height: '32px' }}>
                    <i 
                      className={`${getIcon(notification.notification_type)} ${getIconColor(notification.notification_type)}`}
                      style={{ fontSize: '1.2rem' }}
                    ></i>
                  </div>
                  <div className="flex-grow-1">
                    <p className="mb-1 small fw-semibold">
                      {notification.title}
                    </p>
                    <p className="mb-1 small text-muted">
                      {notification.sender_username && (
                        <strong className="text-dark">{notification.sender_username}</strong>
                      )}
                      {' '}{notification.message}
                    </p>
                    <small className="text-muted d-flex align-items-center">
                      <i className="far fa-clock me-1" style={{ fontSize: '0.75rem' }}></i>
                      {formatTimeAgo(notification.created_at)}
                    </small>
                  </div>
                  {!notification.is_read && (
                    <div className="flex-shrink-0 ms-2">
                      <span className="badge bg-primary rounded-pill" style={{ fontSize: '0.6rem' }}>
                        New
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="text-center p-2 border-top">
          <Link to="/notifications" className="btn btn-sm btn-link text-decoration-none">
            View All Notifications
          </Link>
        </div>
      </Dropdown.Menu>
    </Dropdown>
  );
};

export default NotificationBell;
