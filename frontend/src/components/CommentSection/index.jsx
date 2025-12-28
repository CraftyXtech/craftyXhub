import { useState } from 'react';
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
  IconButton
} from '@mui/material';
import { IconHeart, IconMessageCircle, IconCornerDownRight } from '@tabler/icons-react';

// Sample comments data
const sampleComments = [
  {
    id: 1,
    author: {
      name: 'John Smith',
      avatar: '',
      username: 'johnsmith'
    },
    content: 'This is a fantastic article! I learned so much about design thinking. The five stages breakdown was particularly helpful.',
    created_at: '2024-12-26T14:30:00Z',
    likes: 12,
    replies: [
      {
        id: 2,
        author: {
          name: 'Emma Wilson',
          avatar: '',
          username: 'emmawilson'
        },
        content: 'Thank you John! Glad you found it helpful. Let me know if you have any questions.',
        created_at: '2024-12-26T15:00:00Z',
        likes: 5
      }
    ]
  },
  {
    id: 3,
    author: {
      name: 'Sarah Johnson',
      avatar: '',
      username: 'sarahj'
    },
    content: 'I have been applying these principles in my work and the results are amazing. Design thinking really changes how you approach problems.',
    created_at: '2024-12-25T10:15:00Z',
    likes: 8,
    replies: []
  }
];

// Single Comment Component
function Comment({ comment, isReply = false }) {
  const [liked, setLiked] = useState(false);
  const [showReplyForm, setShowReplyForm] = useState(false);

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
          {comment.author?.name?.[0] || 'U'}
        </Avatar>
        <Box sx={{ flex: 1 }}>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 0.5 }}>
            <Typography variant="subtitle2" fontWeight={600}>
              {comment.author?.name || 'Anonymous'}
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
              onClick={() => setLiked(!liked)}
              sx={{ 
                color: liked ? 'error.main' : 'text.secondary',
                minWidth: 'auto',
                px: 1
              }}
            >
              {(comment.likes || 0) + (liked ? 1 : 0)}
            </Button>
            {!isReply && (
              <Button
                size="small"
                startIcon={<IconCornerDownRight size={16} />}
                onClick={() => setShowReplyForm(!showReplyForm)}
                sx={{ color: 'text.secondary', minWidth: 'auto', px: 1 }}
              >
                Reply
              </Button>
            )}
          </Stack>
          
          {/* Reply Form */}
          {showReplyForm && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                size="small"
                placeholder="Write a reply..."
                multiline
                rows={2}
                sx={{ mb: 1 }}
              />
              <Stack direction="row" spacing={1}>
                <Button variant="contained" size="small">
                  Post Reply
                </Button>
                <Button 
                  size="small" 
                  onClick={() => setShowReplyForm(false)}
                >
                  Cancel
                </Button>
              </Stack>
            </Box>
          )}
          
          {/* Nested Replies */}
          {comment.replies?.map((reply) => (
            <Comment key={reply.id} comment={reply} isReply />
          ))}
        </Box>
      </Stack>
    </Box>
  );
}

// Main Comment Section Component
export default function CommentSection({ postUuid, comments = sampleComments }) {
  const [newComment, setNewComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    
    setIsSubmitting(true);
    // TODO: Implement actual API call
    console.log('Submitting comment:', newComment);
    
    setTimeout(() => {
      setNewComment('');
      setIsSubmitting(false);
    }, 500);
  };

  return (
    <Box sx={{ py: { xs: 6, md: 8 }, bgcolor: 'background.paper' }}>
      <Container maxWidth="lg">
        <Box sx={{ maxWidth: 800 }}>
          {/* Header */}
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 4 }}>
            <IconMessageCircle size={24} />
            <Typography variant="h5" fontWeight={600}>
              Comments ({comments.length})
            </Typography>
          </Stack>
          
          {/* Comment Form */}
          <Card variant="outlined" sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="subtitle2" sx={{ mb: 2 }}>
                Leave a Comment
              </Typography>
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
                >
                  {isSubmitting ? 'Posting...' : 'Post Comment'}
                </Button>
              </form>
            </CardContent>
          </Card>
          
          {/* Comments List */}
          <Stack spacing={3} divider={<Divider />}>
            {comments.map((comment) => (
              <Comment key={comment.id} comment={comment} />
            ))}
          </Stack>
          
          {comments.length === 0 && (
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
