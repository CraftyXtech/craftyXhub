import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Row, Col, Button, ButtonGroup, Card } from 'react-bootstrap';
import { useNotifications } from '../../Context/NotificationContext';

const NotificationsPage = () => {
  const navigate = useNavigate();
  const { 
    notifications, 
    loading, 
    fetchNotifications, 
    markAsRead, 
    markAllAsRead,
    deleteNotification,
    unreadCount 
  } = useNotifications();
  
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  // Handle notification click - navigate to action URL
  const handleNotificationClick = async (notification) => {
    // Mark as read
    if (!notification.is_read) {
      await markAsRead(notification.uuid);
    }
    
    // Navigate to action URL (Litho uses direct URLs)
    if (notification.action_url) {
      navigate(notification.action_url);
    }
  };

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread') return !n.is_read;
    if (filter === 'read') return n.is_read;
    return true;
  });

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

  return (
    <section className="py-5 bg-light min-vh-100">
      <Container>
        <Row>
          <Col lg={8} className="mx-auto">
            <div className="d-flex justify-content-between align-items-center mb-4">
              <div>
                <h2 className="mb-2 fw-bold">Notifications</h2>
                <p className="text-muted mb-0">
                  You have {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
                </p>
              </div>
              {unreadCount > 0 && (
                <Button variant="primary" onClick={markAllAsRead}>
                  Mark All as Read
                </Button>
              )}
            </div>

            <ButtonGroup className="mb-4 w-100">
              <Button 
                variant={filter === 'all' ? 'primary' : 'outline-primary'}
                onClick={() => setFilter('all')}
              >
                All
              </Button>
              <Button 
                variant={filter === 'unread' ? 'primary' : 'outline-primary'}
                onClick={() => setFilter('unread')}
              >
                Unread ({unreadCount})
              </Button>
              <Button 
                variant={filter === 'read' ? 'primary' : 'outline-primary'}
                onClick={() => setFilter('read')}
              >
                Read
              </Button>
            </ButtonGroup>

            <Card className="shadow-sm">
              <Card.Body className="p-0">
                {loading ? (
                  <div className="text-center p-5">
                    <div className="spinner-border text-primary" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="text-muted mt-3">Loading notifications...</p>
                  </div>
                ) : filteredNotifications.length === 0 ? (
                  <div className="text-center p-5">
                    <i className="fas fa-bell text-muted" style={{ fontSize: '3rem', opacity: 0.3 }}></i>
                    <p className="text-muted mt-3">
                      {filter === 'unread' ? 'No unread notifications' : 
                       filter === 'read' ? 'No read notifications' : 
                       'No notifications yet'}
                    </p>
                  </div>
                ) : (
                  filteredNotifications.map((notification, index) => (
                    <div
                      key={notification.uuid}
                      className={`p-4 ${index !== filteredNotifications.length - 1 ? 'border-bottom' : ''} ${
                        !notification.is_read ? 'bg-light' : ''
                      }`}
                      style={{ 
                        borderLeft: !notification.is_read ? '3px solid #0d6efd' : 'none',
                        transition: 'background-color 0.2s ease',
                        cursor: notification.action_url ? 'pointer' : 'default'
                      }}
                      onClick={() => notification.action_url && handleNotificationClick(notification)}
                    >
                      <div className="d-flex align-items-start">
                        <div className="flex-shrink-0 me-3 d-flex align-items-center justify-center" style={{ width: '48px', height: '48px' }}>
                          <i 
                            className={`${getIcon(notification.notification_type)} ${getIconColor(notification.notification_type)}`}
                            style={{ fontSize: '1.5rem' }}
                          ></i>
                        </div>
                        <div className="flex-grow-1">
                          <h6 className="mb-2 fw-semibold">{notification.title}</h6>
                          <p className="mb-2">
                            {notification.sender_username && (
                              <strong className="text-primary">{notification.sender_username}</strong>
                            )}
                            {' '}{notification.message}
                          </p>
                          <small className="text-muted d-flex align-items-center">
                            <i className="far fa-clock me-1"></i>
                            {formatTimeAgo(notification.created_at)}
                          </small>
                        </div>
                        <div className="flex-shrink-0 ms-3 d-flex flex-column gap-2">
                          {!notification.is_read && (
                            <Button 
                              variant="outline-primary" 
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                markAsRead(notification.uuid);
                              }}
                            >
                              <i className="fas fa-check me-1"></i> Mark Read
                            </Button>
                          )}
                          <Button 
                            variant="outline-danger" 
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteNotification(notification.uuid);
                            }}
                          >
                            <i className="fas fa-trash me-1"></i> Delete
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </section>
  );
};

export default NotificationsPage;
