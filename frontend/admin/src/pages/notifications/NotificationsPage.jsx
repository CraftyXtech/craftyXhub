import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Content from "@/layout/content/Content";
import Head from "@/layout/head/Head";
import {
  Block,
  BlockHead,
  BlockHeadContent,
  BlockTitle,
  BlockDes,
  BlockBetween,
  Button,
  Icon,
} from "@/components/Component";
import { Card, Spinner, ButtonGroup } from "reactstrap";
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

const NotificationsPage = () => {
  const navigate = useNavigate();
  const { 
    notifications, 
    loading, 
    stats,
    fetchNotifications, 
    markAsRead, 
    markAllAsRead,
    deleteNotification 
  } = useNotifications();
  
  const [filter, setFilter] = useState('all'); // all, unread, read

  useEffect(() => {
    fetchNotifications(filter === 'unread');
  }, [filter, fetchNotifications]);

  // Handle notification click - navigate to action URL
  const handleNotificationClick = async (notification) => {
    // Mark as read (optimistic)
    if (!notification.is_read) {
      await markAsRead(notification.uuid);
    }
    
    // Navigate to action URL (convert Litho format to Admin format if needed)
    if (notification.action_url) {
      let url = notification.action_url;
      
      // Convert Litho post format (/posts/{uuid}) to Admin format (/posts-detail?id={uuid})
      if (url.includes('/posts/')) {
        const match = url.match(/\/posts\/([a-f0-9-]+)(#comment-(\d+))?/);
        if (match) {
          const uuid = match[1];
          const commentId = match[3];
          url = commentId 
            ? `/posts-detail?id=${uuid}&comment=${commentId}`
            : `/posts-detail?id=${uuid}`;
        }
      }
      
      // Convert author links to user details
      if (url.includes('/blogs/author/')) {
        const uuid = url.split('/blogs/author/')[1];
        url = `/user-details-regular/${uuid}`;
      }
      
      navigate(url);
    }
  };

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread') return !n.is_read;
    if (filter === 'read') return n.is_read;
    return true;
  });

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
    return styleMap[type] || "text-muted";
  };

  return (
    <>
      <Head title="Notifications" />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BlockTitle page>Notifications</BlockTitle>
              <BlockDes className="text-soft">
                You have {stats.unread} unread notification{stats.unread !== 1 ? 's' : ''}
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              {stats.unread > 0 && (
                <Button color="primary" onClick={markAllAsRead}>
                  <Icon name="check-circle" />
                  <span>Mark All Read</span>
                </Button>
              )}
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <Card className="card-bordered">
            <div className="card-inner">
              <ButtonGroup className="mb-3">
                <Button 
                  color={filter === 'all' ? 'primary' : 'light'}
                  onClick={() => setFilter('all')}
                >
                  All ({stats.total})
                </Button>
                <Button 
                  color={filter === 'unread' ? 'primary' : 'light'}
                  onClick={() => setFilter('unread')}
                >
                  Unread ({stats.unread})
                </Button>
                <Button 
                  color={filter === 'read' ? 'primary' : 'light'}
                  onClick={() => setFilter('read')}
                >
                  Read ({stats.read})
                </Button>
              </ButtonGroup>

              {loading ? (
                <div className="text-center p-5">
                  <Spinner color="primary" />
                  <p className="text-muted mt-3">Loading notifications...</p>
                </div>
              ) : filteredNotifications.length === 0 ? (
                <div className="text-center p-5">
                  <Icon name="bell" style={{ fontSize: '3rem', opacity: 0.3 }} />
                  <p className="text-muted mt-3 mb-0">
                    {filter === 'unread' ? 'No unread notifications' : 
                     filter === 'read' ? 'No read notifications' : 
                     'No notifications yet'}
                  </p>
                </div>
              ) : (
                <div className="nk-notification-list">
                  {filteredNotifications.map((notification) => (
                    <div 
                      key={notification.uuid}
                      className={`nk-notification-item p-3 border-bottom ${!notification.is_read ? 'is-unread' : ''} ${notification.action_url ? 'cursor-pointer' : ''}`}
                      onClick={() => notification.action_url && handleNotificationClick(notification)}
                      style={{ cursor: notification.action_url ? 'pointer' : 'default' }}
                    >
                      <div className="d-flex align-items-start">
                        <div className="flex-shrink-0 me-3">
                          <Icon 
                            name={getIcon(notification.notification_type)} 
                            className={getIconStyle(notification.notification_type)}
                            style={{ fontSize: '1.5rem' }}
                          />
                        </div>
                        <div className="flex-grow-1">
                          <h6 className="title mb-1">{notification.title}</h6>
                          <p className="text mb-2">
                            {notification.sender_username && (
                              <strong className="text-primary">{notification.sender_username} </strong>
                            )}
                            {notification.message}
                          </p>
                          <span className="time text-muted">
                            <Icon name="clock" className="me-1" style={{ fontSize: '0.875rem' }} />
                            {formatTimeAgo(notification.created_at)}
                          </span>
                        </div>
                        <div className="flex-shrink-0 ms-3 d-flex gap-2">
                          {!notification.is_read && (
                            <Button 
                              size="sm" 
                              color="light"
                              className="btn-icon"
                              onClick={() => markAsRead(notification.uuid)}
                              title="Mark as read"
                            >
                              <Icon name="check" />
                            </Button>
                          )}
                          <Button 
                            size="sm" 
                            color="light"
                            className="btn-icon"
                            onClick={() => deleteNotification(notification.uuid)}
                            title="Delete notification"
                          >
                            <Icon name="trash" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>
        </Block>
      </Content>
    </>
  );
};

export default NotificationsPage;
