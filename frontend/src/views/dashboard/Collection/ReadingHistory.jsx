import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';
import Skeleton from '@mui/material/Skeleton';
import Divider from '@mui/material/Divider';

// Icons
import { IconHistory, IconTrash, IconClock } from '@tabler/icons-react';

// Hooks
import { useReadingHistory, useHistoryOperations } from '@/api/hooks/useCollection';

/**
 * Reading History Tab
 * Display posts the user has read, grouped by date
 */
export default function ReadingHistory() {
  const navigate = useNavigate();
  const { entries, total, loading, refetch } = useReadingHistory(0, 50);
  const { clear, loading: clearLoading } = useHistoryOperations();

  const handleClearHistory = async () => {
    if (window.confirm('Are you sure you want to clear your entire reading history?')) {
      try {
        await clear();
        refetch();
      } catch (err) {
        console.error('Failed to clear history:', err);
      }
    }
  };

  // Group entries by date
  const groupByDate = (entries) => {
    const groups = {};
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const weekAgo = new Date(today);
    weekAgo.setDate(weekAgo.getDate() - 7);

    entries.forEach((entry) => {
      const date = new Date(entry.read_at);
      date.setHours(0, 0, 0, 0);

      let key;
      if (date >= today) {
        key = 'Today';
      } else if (date >= yesterday) {
        key = 'Yesterday';
      } else if (date >= weekAgo) {
        key = 'This Week';
      } else {
        key = 'Earlier';
      }

      if (!groups[key]) groups[key] = [];
      groups[key].push(entry);
    });

    return groups;
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <Box>
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} variant="rectangular" height={80} sx={{ mb: 1, borderRadius: 1 }} />
        ))}
      </Box>
    );
  }

  const grouped = groupByDate(entries);
  const groupOrder = ['Today', 'Yesterday', 'This Week', 'Earlier'];

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h6">
          {total} Post{total !== 1 ? 's' : ''} Read
        </Typography>
        {entries.length > 0 && (
          <Button
            variant="outlined"
            color="error"
            size="small"
            startIcon={<IconTrash size={16} />}
            onClick={handleClearHistory}
            disabled={clearLoading}
          >
            Clear History
          </Button>
        )}
      </Stack>

      {/* Empty State */}
      {entries.length === 0 ? (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', textAlign: 'center', py: 8 }}>
          <IconHistory size={48} color="#9E9E9E" />
          <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
            No Reading History
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Posts you read will appear here so you can easily find them again.
          </Typography>
          <Button variant="contained" onClick={() => navigate('/')}>
            Explore Posts
          </Button>
        </Card>
      ) : (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
          {groupOrder.map((groupName) => {
            const groupEntries = grouped[groupName];
            if (!groupEntries || groupEntries.length === 0) return null;

            return (
              <Box key={groupName}>
                <Typography 
                  variant="subtitle2" 
                  color="text.secondary"
                  sx={{ px: 2, py: 1.5, bgcolor: 'action.hover' }}
                >
                  {groupName}
                </Typography>
                <List disablePadding>
                  {groupEntries.map((entry, idx) => (
                    <Box key={entry.uuid}>
                      <ListItem
                        sx={{ 
                          py: 2, 
                          cursor: 'pointer',
                          '&:hover': { bgcolor: 'action.selected' }
                        }}
                        onClick={() => navigate(`/blog/${entry.post.slug}`)}
                      >
                        <ListItemAvatar>
                          <Avatar
                            variant="rounded"
                            src={entry.post.featured_image}
                            sx={{ width: 56, height: 56 }}
                          >
                            {entry.post.title?.[0]}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Typography variant="body1" fontWeight={500}>
                              {entry.post.title}
                            </Typography>
                          }
                          secondary={
                            <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 0.5 }}>
                              <IconClock size={14} />
                              <Typography variant="caption" color="text.secondary">
                                {formatTime(entry.read_at)}
                              </Typography>
                              {entry.post.author_name && (
                                <>
                                  <Typography variant="caption">•</Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {entry.post.author_name}
                                  </Typography>
                                </>
                              )}
                            </Stack>
                          }
                          sx={{ ml: 1 }}
                        />
                      </ListItem>
                      {idx < groupEntries.length - 1 && <Divider />}
                    </Box>
                  ))}
                </List>
              </Box>
            );
          })}
        </Card>
      )}
    </Box>
  );
}
