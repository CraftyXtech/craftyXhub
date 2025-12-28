import { memo } from 'react';
import PropTypes from 'prop-types';

// MUI
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Chip from '@mui/material/Chip';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import IconButton from '@mui/material/IconButton';
import Divider from '@mui/material/Divider';
import CircularProgress from '@mui/material/CircularProgress';

// Icons
import { IconX, IconClock } from '@tabler/icons-react';

const DRAWER_WIDTH = 360;

/**
 * PostSettingsSidebar - Slide-out settings panel
 * 
 * @param {object} props
 * @param {boolean} props.isOpen - Whether drawer is open
 * @param {function} props.onClose - Close handler
 * @param {string} props.excerpt - Manual excerpt
 * @param {string} props.autoExcerpt - Auto-generated excerpt
 * @param {boolean} props.useAutoExcerpt - Use auto-generated excerpt
 * @param {function} props.onExcerptModeChange - Toggle auto excerpt
 * @param {function} props.onExcerptChange - Manual excerpt change
 * @param {array} props.categories - Available categories
 * @param {string|number} props.categoryId - Selected category ID
 * @param {function} props.onCategoryChange - Category change handler
 * @param {array} props.tags - Available tags
 * @param {array} props.selectedTags - Selected tag IDs
 * @param {function} props.onTagToggle - Tag toggle handler
 * @param {string} props.metaTitle - SEO title
 * @param {string} props.metaDescription - SEO description
 * @param {number} props.readingTime - Reading time in minutes
 * @param {function} props.onMetaChange - Meta change handler
 * @param {boolean} props.categoriesLoading - Loading categories
 * @param {boolean} props.tagsLoading - Loading tags
 */
const PostSettingsSidebar = ({
  isOpen,
  onClose,
  excerpt = '',
  autoExcerpt = '',
  useAutoExcerpt = true,
  onExcerptModeChange,
  onExcerptChange,
  categories = [],
  categoryId,
  onCategoryChange,
  tags = [],
  selectedTags = [],
  onTagToggle,
  metaTitle = '',
  metaDescription = '',
  readingTime = 1,
  onMetaChange,
  categoriesLoading = false,
  tagsLoading = false,
}) => {
  return (
    <Drawer
      anchor="right"
      open={isOpen}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
        },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Typography variant="h6" fontWeight={600}>
          Post Settings
        </Typography>
        <IconButton onClick={onClose} size="small">
          <IconX size={20} />
        </IconButton>
      </Box>

      {/* Content */}
      <Box sx={{ p: 2, overflowY: 'auto', flex: 1 }}>
        <Stack spacing={3}>
          {/* Excerpt */}
          <Box>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle2" fontWeight={600}>
                Excerpt
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    size="small"
                    checked={useAutoExcerpt}
                    onChange={(e) => onExcerptModeChange?.(e.target.checked)}
                  />
                }
                label={<Typography variant="caption">Auto</Typography>}
                labelPlacement="start"
              />
            </Stack>
            <TextField
              multiline
              rows={3}
              fullWidth
              size="small"
              placeholder={useAutoExcerpt ? 'Auto-generated from content' : 'Write a custom excerpt...'}
              value={useAutoExcerpt ? autoExcerpt : excerpt}
              onChange={(e) => onExcerptChange?.(e.target.value)}
              disabled={useAutoExcerpt}
              InputProps={{
                sx: { fontSize: '0.875rem' }
              }}
            />
          </Box>

          <Divider />

          {/* Category */}
          <Box>
            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
              Category
            </Typography>
            <FormControl fullWidth size="small">
              <InputLabel>Select Category</InputLabel>
              <Select
                value={categoryId || ''}
                onChange={(e) => onCategoryChange?.(e.target.value)}
                label="Select Category"
                disabled={categoriesLoading}
              >
                <MenuItem value="">
                  <em>No category</em>
                </MenuItem>
                {categories.map((cat) => (
                  <MenuItem key={cat.id} value={cat.id}>
                    {cat.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            {categoriesLoading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 1 }}>
                <CircularProgress size={20} />
              </Box>
            )}
          </Box>

          {/* Tags */}
          <Box>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle2" fontWeight={600}>
                Tags
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {selectedTags.length}/5
              </Typography>
            </Stack>
            {tagsLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                <CircularProgress size={24} />
              </Box>
            ) : (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {tags.map((tag) => {
                  const isSelected = selectedTags.includes(tag.id);
                  const isDisabled = !isSelected && selectedTags.length >= 5;
                  return (
                    <Chip
                      key={tag.id}
                      label={tag.name}
                      size="small"
                      clickable={!isDisabled}
                      color={isSelected ? 'primary' : 'default'}
                      variant={isSelected ? 'filled' : 'outlined'}
                      disabled={isDisabled}
                      onClick={() => !isDisabled && onTagToggle?.(tag.id)}
                      sx={{ fontSize: '0.75rem' }}
                    />
                  );
                })}
              </Box>
            )}
          </Box>

          <Divider />

          {/* Reading Time */}
          <Box>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
              <IconClock size={16} />
              <Typography variant="subtitle2" fontWeight={600}>
                Reading Time
              </Typography>
            </Stack>
            <TextField
              type="number"
              size="small"
              fullWidth
              value={readingTime}
              onChange={(e) => onMetaChange?.({ readingTime: parseInt(e.target.value) || 1 })}
              InputProps={{
                inputProps: { min: 1 },
                endAdornment: <Typography variant="caption" color="text.secondary">min</Typography>
              }}
            />
          </Box>

          <Divider />

          {/* SEO Settings */}
          <Box>
            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
              SEO
            </Typography>
            <Stack spacing={2}>
              <TextField
                label="Meta Title"
                size="small"
                fullWidth
                value={metaTitle}
                onChange={(e) => onMetaChange?.({ metaTitle: e.target.value })}
                placeholder="SEO title (optional)"
                helperText={`${metaTitle.length}/60 characters`}
              />
              <TextField
                label="Meta Description"
                size="small"
                fullWidth
                multiline
                rows={2}
                value={metaDescription}
                onChange={(e) => onMetaChange?.({ metaDescription: e.target.value })}
                placeholder="SEO description (optional)"
                helperText={`${metaDescription.length}/160 characters`}
              />
            </Stack>
          </Box>
        </Stack>
      </Box>

      {/* Footer hint */}
      <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary">
          Press <strong>Esc</strong> or <strong>⌘,</strong> to close
        </Typography>
      </Box>
    </Drawer>
  );
};

PostSettingsSidebar.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  excerpt: PropTypes.string,
  autoExcerpt: PropTypes.string,
  useAutoExcerpt: PropTypes.bool,
  onExcerptModeChange: PropTypes.func,
  onExcerptChange: PropTypes.func,
  categories: PropTypes.array,
  categoryId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onCategoryChange: PropTypes.func,
  tags: PropTypes.array,
  selectedTags: PropTypes.array,
  onTagToggle: PropTypes.func,
  metaTitle: PropTypes.string,
  metaDescription: PropTypes.string,
  readingTime: PropTypes.number,
  onMetaChange: PropTypes.func,
  categoriesLoading: PropTypes.bool,
  tagsLoading: PropTypes.bool,
};

export default memo(PostSettingsSidebar);
