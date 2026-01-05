import { useState, useEffect, useCallback } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Avatar,
  Stack,
  Card,
  CardContent,
  Divider,
  Alert,
  Skeleton,
  CircularProgress
} from '@mui/material';
import { IconHeart, IconMessageCircle, IconCornerDownRight, IconLock } from '@tabler/icons-react';
import { useAuth } from '@/api/AuthProvider';
import { getComments, createComment, toggleCommentLike } from '@/api';

// Single Comment Component
function Comment({ comment, isReply = false, isAuthenticated = false, onReplySubmit }) {
  const [liked, setLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(comment.likes_count || 0);
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [isSubmittingReply, setIsSubmittingReply] = useState(false);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const handleLike = async () => {
    if (!isAuthenticated) return;
    
    // Optimistic update
    const wasLiked = liked;
    setLiked(!wasLiked);
    setLikesCount(prev => wasLiked ? prev - 1 : prev + 1);
    
    try {
      const result = await toggleCommentLike(comment.uuid);
      setLiked(result.liked);
      setLikesCount(result.likes_count);
    } catch (err) {
      console.error('Failed to toggle comment like:', err);
      // Rollback on error
      setLiked(wasLiked);
      setLikesCount(prev => wasLiked ? prev + 1 : prev - 1);
    }
  };

  const handleReply = () => {
    if (!isAuthenticated) return;
    setShowReplyForm(!showReplyForm);
  };

  const handleReplySubmit = async () => {
    if (!replyText.trim() || !isAuthenticated || !onReplySubmit) return;
    
    setIsSubmittingReply(true);
    try {
      await onReplySubmit(replyText, comment.uuid || comment.id);
      setReplyText('');
      setShowReplyForm(false);
    } catch (err) {
      console.error('Failed to submit reply:', err);
    } finally {
      setIsSubmittingReply(false);
    }
  };

  return (
    <Box sx={{ pl: isReply ? 6 : 0, mt: isReply ? 2 : 0 }}>
      <Stack direction="row" spacing={2}>
        <Avatar
          src={comment.author?.avatar}
          sx={{ 
            width: isReply ? 32 : 40, 
            height: isReply ? 32 : 40, 
            bgcolor: 'primary.main' 
          }}
        >
          {comment.author?.full_name?.[0] || comment.author?.name?.[0] || 'U'}
        </Avatar>
        <Box sx={{ flex: 1 }}>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 0.5 }}>
            <Typography variant="subtitle2" fontWeight={600}>
              {comment.author?.full_name || comment.author?.name || 'Anonymous'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              · {formatDate(comment.created_at)}
            </Typography>
          </Stack>
          
          <Typography variant="body2" sx={{ mb: 1.5, lineHeight: 1.7 }}>
            {comment.content}
          </Typography>
          
          <Stack direction="row" spacing={2} alignItems="center">
            <Button
              size="small"
              startIcon={<IconHeart size={16} fill={liked ? 'currentColor' : 'none'} />}
              onClick={handleLike}
              disabled={!isAuthenticated}
              sx={{ 
                color: liked ? 'error.main' : 'text.secondary',
                minWidth: 'auto',
                px: 1
              }}
            >
              {likesCount}
            </Button>
            {!isReply && isAuthenticated && (
              <Button
                size="small"
                startIcon={<IconCornerDownRight size={16} />}
                onClick={handleReply}
                sx={{ color: 'text.secondary', minWidth: 'auto', px: 1 }}
              >
                Reply
              </Button>
            )}
          </Stack>
          
          {/* Reply Form */}
          {showReplyForm && isAuthenticated && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                size="small"
                placeholder="Write a reply..."
                multiline
                rows={2}
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                sx={{ mb: 1 }}
              />
              <Stack direction="row" spacing={1}>
                <Button 
                  variant="contained" 
                  size="small" 
                  disabled={!replyText.trim() || isSubmittingReply}
                  onClick={handleReplySubmit}
                >
                  {isSubmittingReply ? 'Posting...' : 'Post Reply'}
                </Button>
                <Button 
                  size="small" 
                  onClick={() => { setShowReplyForm(false); setReplyText(''); }}
                >
                  Cancel
                </Button>
              </Stack>
            </Box>
          )}
          
          {/* Nested Replies */}
          {comment.replies?.map((reply) => (
            <Comment 
              key={reply.uuid || reply.id} 
              comment={reply} 
              isReply 
              isAuthenticated={isAuthenticated}
              onReplySubmit={onReplySubmit}
            />
          ))}
        </Box>
      </Stack>
    </Box>
  );
}

// Comment Skeleton for loading state
function CommentSkeleton() {
  return (
    <Box>
      <Stack direction="row" spacing={2}>
        <Skeleton variant="circular" width={40} height={40} />
        <Box sx={{ flex: 1 }}>
          <Skeleton variant="text" width={150} />
          <Skeleton variant="text" width="100%" />
          <Skeleton variant="text" width="80%" />
        </Box>
      </Stack>
    </Box>
  );
}

// Main Comment Section Component
export default function CommentSection({ postSlug }) {
  const { isAuthenticated, user } = useAuth();
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newComment, setNewComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  // Fetch comments from API
  const fetchComments = useCallback(async () => {
    if (!postSlug) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await getComments(postSlug, { limit: 50 });
      setComments(response.comments || []);
    } catch (err) {
      console.error('Failed to fetch comments:', err);
      setError('Failed to load comments');
      setComments([]);
    } finally {
      setLoading(false);
    }
  }, [postSlug]);

  useEffect(() => {
    fetchComments();
  }, [fetchComments]);

  // Submit new comment
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim() || !isAuthenticated || !postSlug) return;
    
    setIsSubmitting(true);
    setSubmitError(null);
    
    try {
      await createComment(postSlug, { content: newComment.trim() });
      setNewComment('');
      // Refresh comments to show the new one
      await fetchComments();
    } catch (err) {
      console.error('Failed to submit comment:', err);
      setSubmitError(err.response?.data?.detail || 'Failed to post comment. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle reply submission
  const handleReplySubmit = async (content, parentId) => {
    if (!content.trim() || !isAuthenticated || !postSlug) return;
    
    try {
      await createComment(postSlug, { 
        content: content.trim(),
        parent_id: parentId 
      });
      // Refresh comments to show the new reply
      await fetchComments();
    } catch (err) {
      console.error('Failed to submit reply:', err);
      throw err;
    }
  };

  return (
    <Box sx={{ py: { xs: 6, md: 8 }, bgcolor: 'background.paper' }}>
      <Container maxWidth="lg">
        <Box sx={{ maxWidth: 800 }}>
          {/* Header */}
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 4 }}>
            <IconMessageCircle size={24} />
            <Typography variant="h5" fontWeight={600}>
              Comments {!loading && `(${comments.length})`}
            </Typography>
          </Stack>
          
          {/* Comment Form - Only show for authenticated users */}
          {isAuthenticated ? (
            <Card variant="outlined" sx={{ mb: 4 }}>
              <CardContent>
                <Stack direction="row" spacing={2} alignItems="flex-start">
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    {user?.full_name?.[0] || user?.username?.[0] || 'U'}
                  </Avatar>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1.5 }}>
                      Commenting as <strong>{user?.full_name || user?.username}</strong>
                    </Typography>
                    {submitError && (
                      <Alert severity="error" sx={{ mb: 2 }} onClose={() => setSubmitError(null)}>
                        {submitError}
                      </Alert>
                    )}
                    <form onSubmit={handleSubmit}>
                      <TextField
                        fullWidth
                        placeholder="Share your thoughts..."
                        multiline
                        rows={3}
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        sx={{ mb: 2 }}
                      />
                      <Button 
                        type="submit" 
                        variant="contained" 
                        disabled={!newComment.trim() || isSubmitting}
                        startIcon={isSubmitting ? <CircularProgress size={16} color="inherit" /> : null}
                      >
                        {isSubmitting ? 'Posting...' : 'Post Comment'}
                      </Button>
                    </form>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          ) : (
            <Alert 
              severity="info" 
              icon={<IconLock size={20} />}
              sx={{ mb: 4 }}
              action={
                <Button 
                  component={RouterLink} 
                  to="/auth/login" 
                  color="inherit" 
                  size="small"
                  variant="outlined"
                >
                  Sign In
                </Button>
              }
            >
              <Typography variant="body2">
                <strong>Join the conversation!</strong> Sign in to leave a comment.
              </Typography>
            </Alert>
          )}
          
          {/* Loading State */}
          {loading && (
            <Stack spacing={3}>
              <CommentSkeleton />
              <CommentSkeleton />
              <CommentSkeleton />
            </Stack>
          )}

          {/* Error State */}
          {error && !loading && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
              <Button size="small" onClick={fetchComments} sx={{ ml: 2 }}>
                Retry
              </Button>
            </Alert>
          )}
          
          {/* Comments List */}
          {!loading && !error && (
            <Stack spacing={3} divider={<Divider />}>
              {comments.map((comment) => (
                <Comment 
                  key={comment.uuid || comment.id} 
                  comment={comment} 
                  isAuthenticated={isAuthenticated}
                  onReplySubmit={handleReplySubmit}
                />
              ))}
            </Stack>
          )}
          
          {!loading && !error && comments.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography color="text.secondary">
                No comments yet. Be the first to share your thoughts!
              </Typography>
            </Box>
          )}
        </Box>
      </Container>
    </Box>
  );
}
