import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActionArea from '@mui/material/CardActionArea';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Skeleton from '@mui/material/Skeleton';
import Chip from '@mui/material/Chip';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';

// Icons
import {
  IconPlus,
  IconList,
  IconLock,
  IconWorld,
  IconTrash,
  IconEdit
} from '@tabler/icons-react';

// Hooks
import { useReadingLists, useListOperations } from '@/api/hooks/useCollection';

/**
 * Your Lists Tab
 * Display and manage user's custom reading lists
 */
export default function YourLists() {
  const navigate = useNavigate();
  const { lists, loading, refetch } = useReadingLists();
  const { create, remove, loading: opLoading } = useListOperations();
  
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newList, setNewList] = useState({ name: '', description: '', is_public: false });

  const handleCreateList = async () => {
    try {
      await create(newList);
      setDialogOpen(false);
      setNewList({ name: '', description: '', is_public: false });
      refetch();
    } catch (err) {
      console.error('Failed to create list:', err);
    }
  };

  const handleDeleteList = async (e, uuid) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this list?')) {
      try {
        await remove(uuid);
        refetch();
      } catch (err) {
        console.error('Failed to delete list:', err);
      }
    }
  };

  // Loading skeleton
  if (loading) {
    return (
      <Grid container spacing={3}>
        {[1, 2, 3].map((i) => (
          <Grid item xs={12} sm={6} md={4} key={i}>
            <Skeleton variant="rounded" height={160} />
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <Box>
      {/* Header with Create button */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h6">
          {lists.length} List{lists.length !== 1 ? 's' : ''}
        </Typography>
        <Button
          variant="contained"
          startIcon={<IconPlus size={18} />}
          onClick={() => setDialogOpen(true)}
        >
          New List
        </Button>
      </Stack>

      {/* Lists Grid */}
      {lists.length === 0 ? (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', textAlign: 'center', py: 8 }}>
          <IconList size={48} color="#9E9E9E" />
          <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
            No Lists Yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Create reading lists to organize and save posts for later.
          </Typography>
          <Button
            variant="contained"
            startIcon={<IconPlus size={18} />}
            onClick={() => setDialogOpen(true)}
          >
            Create Your First List
          </Button>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {lists.map((list) => (
            <Grid item xs={12} sm={6} md={4} key={list.uuid}>
              <Card 
                elevation={0} 
                sx={{ 
                  border: '1px solid', 
                  borderColor: 'divider',
                  height: '100%',
                  '&:hover': { borderColor: 'primary.main' }
                }}
              >
                <CardActionArea 
                  onClick={() => navigate(`/dashboard/collection/list/${list.uuid}`)}
                  sx={{ height: '100%' }}
                >
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                      <Box>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Typography variant="h6" noWrap>
                            {list.name}
                          </Typography>
                          {list.is_public ? (
                            <IconWorld size={16} color="#4CAF50" />
                          ) : (
                            <IconLock size={16} color="#9E9E9E" />
                          )}
                        </Stack>
                        {list.description && (
                          <Typography 
                            variant="body2" 
                            color="text.secondary"
                            sx={{ 
                              mt: 1,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical'
                            }}
                          >
                            {list.description}
                          </Typography>
                        )}
                      </Box>
                      <IconButton 
                        size="small" 
                        onClick={(e) => handleDeleteList(e, list.uuid)}
                        sx={{ color: 'error.main' }}
                      >
                        <IconTrash size={18} />
                      </IconButton>
                    </Stack>
                    <Chip 
                      label={`${list.item_count} post${list.item_count !== 1 ? 's' : ''}`}
                      size="small"
                      sx={{ mt: 2 }}
                    />
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create List Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New List</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="List Name"
            value={newList.name}
            onChange={(e) => setNewList({ ...newList, name: e.target.value })}
            sx={{ mt: 2, mb: 2 }}
          />
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Description (optional)"
            value={newList.description}
            onChange={(e) => setNewList({ ...newList, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={
              <Switch
                checked={newList.is_public}
                onChange={(e) => setNewList({ ...newList, is_public: e.target.checked })}
              />
            }
            label="Make this list public"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleCreateList}
            disabled={!newList.name.trim() || opLoading}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
