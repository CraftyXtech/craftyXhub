import { useState, useEffect } from 'react';

// MUI
import Box from '@mui/material/Box';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Checkbox from '@mui/material/Checkbox';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Tooltip from '@mui/material/Tooltip';

// Icons
import {
  IconBookmark,
  IconBookmarkFilled,
  IconPlus,
  IconList
} from '@tabler/icons-react';

// API
import { bookmarkPost } from '@/api/services/postService';
import { 
  getReadingLists, 
  getReadingList,
  createReadingList, 
  addPostToList, 
  removePostFromList 
} from '@/api/services/collectionService';

/**
 * SaveToListMenu Component
 * Dropdown menu for saving posts to bookmarks or custom reading lists
 * 
 * @param {string} postUuid - UUID of the post to save
 * @param {boolean} isBookmarked - Whether the post is currently bookmarked
 * @param {function} onBookmarkChange - Callback when bookmark status changes
 * @param {string} size - Icon button size ('small', 'medium')
 */
export default function SaveToListMenu({ 
  postUuid, 
  isBookmarked = false, 
  onBookmarkChange,
  size = 'medium' 
}) {
  const [anchorEl, setAnchorEl] = useState(null);
  const [lists, setLists] = useState([]);
  const [postInLists, setPostInLists] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [bookmarked, setBookmarked] = useState(isBookmarked);
  
  // Create list dialog
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newListName, setNewListName] = useState('');
  const [creating, setCreating] = useState(false);

  const open = Boolean(anchorEl);

  // Fetch lists when menu opens
  useEffect(() => {
    if (open) {
      fetchLists();
    }
  }, [open]);

  // Sync with prop
  useEffect(() => {
    setBookmarked(isBookmarked);
  }, [isBookmarked]);

  const fetchLists = async () => {
    try {
      setLoading(true);
      const data = await getReadingLists();
      setLists(data.lists || []);
      
      // Check which lists contain this post
      const inLists = new Set();
      for (const list of data.lists || []) {
        try {
          const listDetail = await getReadingList(list.uuid);
          const hasPost = listDetail.items?.some(item => item.post?.uuid === postUuid);
          if (hasPost) {
            inLists.add(list.uuid);
          }
        } catch (e) {
          // Skip if error
        }
      }
      setPostInLists(inLists);
    } catch (err) {
      console.error('Failed to fetch lists:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClick = (event) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleBookmarkToggle = async () => {
    try {
      await bookmarkPost(postUuid);
      setBookmarked(!bookmarked);
      onBookmarkChange?.(!bookmarked);
    } catch (err) {
      console.error('Failed to toggle bookmark:', err);
    }
  };

  const handleListToggle = async (listUuid) => {
    try {
      if (postInLists.has(listUuid)) {
        await removePostFromList(listUuid, postUuid);
        setPostInLists(prev => {
          const next = new Set(prev);
          next.delete(listUuid);
          return next;
        });
      } else {
        await addPostToList(listUuid, postUuid);
        setPostInLists(prev => new Set([...prev, listUuid]));
      }
    } catch (err) {
      console.error('Failed to toggle list item:', err);
    }
  };

  const handleCreateList = async () => {
    if (!newListName.trim()) return;
    
    try {
      setCreating(true);
      const newList = await createReadingList({ name: newListName.trim() });
      await addPostToList(newList.uuid, postUuid);
      
      setLists(prev => [newList, ...prev]);
      setPostInLists(prev => new Set([...prev, newList.uuid]));
      setCreateDialogOpen(false);
      setNewListName('');
    } catch (err) {
      console.error('Failed to create list:', err);
    } finally {
      setCreating(false);
    }
  };

  const iconSize = size === 'small' ? 18 : 22;
  const savedCount = postInLists.size + (bookmarked ? 1 : 0);

  return (
    <>
      <Tooltip title={savedCount > 0 ? `Saved to ${savedCount} place(s)` : 'Save'}>
        <IconButton
          onClick={handleClick}
          size={size}
          sx={{
            color: savedCount > 0 ? '#f39F5A' : 'inherit',
            '&:hover': { color: '#f39F5A' }
          }}
        >
          {savedCount > 0 ? (
            <IconBookmarkFilled size={iconSize} />
          ) : (
            <IconBookmark size={iconSize} />
          )}
        </IconButton>
      </Tooltip>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        onClick={(e) => e.stopPropagation()}
        PaperProps={{
          sx: { minWidth: 240, maxHeight: 400 }
        }}
      >
        {/* Quick Bookmark */}
        <MenuItem onClick={handleBookmarkToggle}>
          <ListItemIcon>
            <Checkbox
              checked={bookmarked}
              size="small"
              sx={{ p: 0 }}
            />
          </ListItemIcon>
          <ListItemText 
            primary="Quick Bookmark"
            secondary="Save to Bookmarks tab"
            primaryTypographyProps={{ variant: 'body2' }}
            secondaryTypographyProps={{ variant: 'caption' }}
          />
        </MenuItem>

        <Divider sx={{ my: 1 }} />

        {/* Reading Lists */}
        <Typography 
          variant="caption" 
          color="text.secondary" 
          sx={{ px: 2, py: 0.5, display: 'block' }}
        >
          Your Lists
        </Typography>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
            <CircularProgress size={24} />
          </Box>
        ) : lists.length === 0 ? (
          <MenuItem disabled>
            <ListItemText 
              primary="No lists yet"
              primaryTypographyProps={{ variant: 'body2', color: 'text.secondary' }}
            />
          </MenuItem>
        ) : (
          lists.map((list) => (
            <MenuItem key={list.uuid} onClick={() => handleListToggle(list.uuid)}>
              <ListItemIcon>
                <Checkbox
                  checked={postInLists.has(list.uuid)}
                  size="small"
                  sx={{ p: 0 }}
                />
              </ListItemIcon>
              <ListItemText 
                primary={list.name}
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </MenuItem>
          ))
        )}

        <Divider sx={{ my: 1 }} />

        {/* Create New List */}
        <MenuItem onClick={() => setCreateDialogOpen(true)}>
          <ListItemIcon>
            <IconPlus size={18} />
          </ListItemIcon>
          <ListItemText 
            primary="Create new list"
            primaryTypographyProps={{ variant: 'body2' }}
          />
        </MenuItem>
      </Menu>

      {/* Create List Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Create New List</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="List Name"
            value={newListName}
            onChange={(e) => setNewListName(e.target.value)}
            sx={{ mt: 1 }}
            onKeyPress={(e) => e.key === 'Enter' && handleCreateList()}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleCreateList}
            disabled={!newListName.trim() || creating}
          >
            {creating ? 'Creating...' : 'Create & Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
