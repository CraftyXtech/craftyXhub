import React from "react";
import { DropdownToggle, DropdownMenu, UncontrolledDropdown, Badge, Spinner } from "reactstrap";
import { useNavigate } from "react-router-dom";
import Icon from "@/components/icon/Icon";
import { useNotifications } from "@/context/NotificationContext";

// Helper function to format time ago
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
  const weeks = Math.floor(days / 7);
  if (weeks < 4) return `${weeks}w ago`;
  return date.toLocaleDateString();
};

const NotificationItem = ({ notification, onMarkRead }) => {
  const getIcon = (type) => {
    const iconMap = {
      post_like: "heart-fill",
      post_comment: "chat-fill",
      comment_reply: "reply-fill",
      new_follower: "user-add-fill",
      new_post_from_following: "file-text",
      post_published: "check-circle",
      post_flagged: "alert-circle",
      post_unflagged: "check-circle",
      post_reported: "flag",
      post_bookmark: "bookmark-fill",
      welcome: "gift",
      email_verified: "check-circle-fill",
    };
    return iconMap[type] || "bell-fill";
  };

  const getIconStyle = (type) => {
    const styleMap = {
      post_like: "bg-danger-dim",
      post_comment: "bg-info-dim",
      comment_reply: "bg-primary-dim",
      new_follower: "bg-success-dim",
      new_post_from_following: "bg-warning-dim",
      post_published: "bg-success-dim",
      post_flagged: "bg-warning-dim",
      post_unflagged: "bg-success-dim",
      post_reported: "bg-danger-dim",
      post_bookmark: "bg-primary-dim",
      welcome: "bg-info-dim",
      email_verified: "bg-success-dim",
    };
    return styleMap[type] || "bg-light";
  };

  const handleClick = () => {
    if (!notification.is_read) {
      onMarkRead(notification.uuid);
    }
  };

  return (
    <div 
      className={`nk-notification-item ${!notification.is_read ? 'is-unread' : ''}`}
      onClick={handleClick}
      style={{ cursor: notification.is_read ? 'default' : 'pointer' }}
    >
      <div className="nk-notification-icon">
        <Icon 
          name={getIcon(notification.notification_type)} 
          className={`icon-circle ${getIconStyle(notification.notification_type)}`} 
        />
      </div>
      <div className="nk-notification-content">
        <div className="nk-notification-text">
          {notification.sender_username && <strong>{notification.sender_username} </strong>}
          {notification.message}
        </div>
        <div className="nk-notification-time">{formatTimeAgo(notification.created_at)}</div>
      </div>
    </div>
  );
};

const Notification = () => {
  const navigate = useNavigate();
  const { 
    notifications, 
    unreadCount, 
    loading, 
    markAsRead, 
    markAllAsRead 
  } = useNotifications();

  const handleMarkAllRead = async (e) => {
    e.preventDefault();
    await markAllAsRead();
  };

  const handleViewAll = (e) => {
    e.preventDefault();
    navigate('/notifications');
  };

  return (
    <UncontrolledDropdown className="user-dropdown">
      <DropdownToggle tag="a" className="dropdown-toggle nk-quick-nav-icon">
        <div className={`icon-status ${unreadCount > 0 ? 'icon-status-info' : ''}`}>
          <Icon name="bell" />
          {unreadCount > 0 && (
            <Badge 
              color="danger" 
              className="badge-sm badge-pill position-absolute top-0 start-100 translate-middle"
              style={{ fontSize: '0.65rem', padding: '0.25rem 0.5rem' }}
            >
              {unreadCount > 9 ? '9+' : unreadCount}
            </Badge>
          )}
        </div>
      </DropdownToggle>
      <DropdownMenu end className="dropdown-menu-xl dropdown-menu-s1">
        <div className="dropdown-head">
          <span className="sub-title nk-dropdown-title">
            Notifications {unreadCount > 0 && `(${unreadCount})`}
          </span>
          {unreadCount > 0 && (
            <a href="#markasread" onClick={handleMarkAllRead}>
              Mark All as Read
            </a>
          )}
        </div>
        <div className="dropdown-body">
          {loading ? (
            <div className="text-center p-4">
              <Spinner size="sm" color="primary" />
            </div>
          ) : notifications.length === 0 ? (
            <div className="text-center p-4 text-muted">
              <Icon name="bell" className="mb-2" style={{ fontSize: '2rem', opacity: 0.3 }} />
              <p className="mb-0">No notifications yet</p>
            </div>
          ) : (
            <div className="nk-notification">
              {notifications.slice(0, 5).map((notification) => (
                <NotificationItem
                  key={notification.uuid}
                  notification={notification}
                  onMarkRead={markAsRead}
                />
              ))}
            </div>
          )}
        </div>
        <div className="dropdown-foot center">
          <a href="#viewall" onClick={handleViewAll}>
            View All Notifications
          </a>
        </div>
      </DropdownMenu>
    </UncontrolledDropdown>
  );
};

export default Notification;
