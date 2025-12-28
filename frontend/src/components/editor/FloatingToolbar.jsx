import { memo } from 'react';
import PropTypes from 'prop-types';

// MUI
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';

// Icons
import {
  IconSettings,
  IconSend,
  IconCheck,
  IconAlertCircle,
  IconCloudUpload,
} from '@tabler/icons-react';

/**
 * FloatingToolbar - Minimal header for distraction-free writing
 * 
 * @param {object} props
 * @param {function} props.onPublish - Publish button handler
 * @param {function} props.onOpenSettings - Settings button handler
 * @param {'idle'|'saving'|'saved'|'error'} props.saveStatus - Current save status
 * @param {number} props.lastSaved - Timestamp of last save
 * @param {boolean} props.isPublishing - Publishing in progress
 * @param {number} props.wordCount - Current word count
 * @param {number} props.readingTime - Estimated reading time
 */
const FloatingToolbar = ({
  onPublish,
  onOpenSettings,
  saveStatus = 'idle',
  lastSaved,
  isPublishing = false,
  wordCount = 0,
  readingTime = 1,
}) => {
  // Format last saved time
  const formatLastSaved = () => {
    if (!lastSaved) return null;
    
    const diff = Date.now() - lastSaved;
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    return `${Math.floor(diff / 3600000)}h ago`;
  };

  // Save status indicator
  const renderSaveStatus = () => {
    switch (saveStatus) {
      case 'saving':
        return (
          <Stack direction="row" alignItems="center" spacing={0.5}>
            <CircularProgress size={14} />
            <Typography variant="caption" color="text.secondary">
              Saving...
            </Typography>
          </Stack>
        );
      case 'saved':
        return (
          <Stack direction="row" alignItems="center" spacing={0.5}>
            <IconCheck size={14} stroke={2} />
            <Typography variant="caption" color="text.secondary">
              Saved {formatLastSaved()}
            </Typography>
          </Stack>
        );
      case 'error':
        return (
          <Stack direction="row" alignItems="center" spacing={0.5} sx={{ color: 'error.main' }}>
            <IconAlertCircle size={14} stroke={2} />
            <Typography variant="caption" color="error">
              Save failed
            </Typography>
          </Stack>
        );
      default:
        return (
          <Stack direction="row" alignItems="center" spacing={0.5}>
            <IconCloudUpload size={14} stroke={2} />
            <Typography variant="caption" color="text.secondary">
              Draft
            </Typography>
          </Stack>
        );
    }
  };

  return (
    <Box
      sx={{
        position: 'sticky',
        top: 0,
        zIndex: 100,
        bgcolor: 'background.paper',
        borderBottom: '1px solid',
        borderColor: 'divider',
        px: 3,
        py: 1.5,
      }}
    >
      <Stack direction="row" alignItems="center" justifyContent="space-between">
        {/* Left: Save Status */}
        <Box sx={{ minWidth: 120 }}>
          {renderSaveStatus()}
        </Box>

        {/* Center: Stats */}
        <Stack direction="row" spacing={2} alignItems="center">
          <Chip
            label={`${wordCount} words`}
            size="small"
            variant="outlined"
            sx={{ fontSize: '0.75rem' }}
          />
          <Chip
            label={`${readingTime} min read`}
            size="small"
            variant="outlined"
            sx={{ fontSize: '0.75rem' }}
          />
        </Stack>

        {/* Right: Actions */}
        <Stack direction="row" spacing={1} alignItems="center">
          <IconButton
            size="small"
            onClick={onOpenSettings}
            sx={{ color: 'text.secondary' }}
            title="Post settings (⌘,)"
          >
            <IconSettings size={20} />
          </IconButton>
          
          <Button
            variant="contained"
            size="small"
            startIcon={isPublishing ? <CircularProgress size={16} color="inherit" /> : <IconSend size={16} />}
            onClick={onPublish}
            disabled={isPublishing}
            sx={{ minWidth: 100 }}
          >
            {isPublishing ? 'Publishing...' : 'Publish'}
          </Button>
        </Stack>
      </Stack>
    </Box>
  );
};

FloatingToolbar.propTypes = {
  onPublish: PropTypes.func.isRequired,
  onOpenSettings: PropTypes.func.isRequired,
  saveStatus: PropTypes.oneOf(['idle', 'saving', 'saved', 'error']),
  lastSaved: PropTypes.number,
  isPublishing: PropTypes.bool,
  wordCount: PropTypes.number,
  readingTime: PropTypes.number,
};

export default memo(FloatingToolbar);
