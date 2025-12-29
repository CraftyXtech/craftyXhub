import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Stack from '@mui/material/Stack';

// Icons
import {
  IconList,
  IconHistory,
  IconHighlight,
  IconMessage,
  IconBookmark
} from '@tabler/icons-react';

// Tab components
import YourLists from './YourLists';
import ReadingHistory from './ReadingHistory';
import Highlights from './Highlights';
import Comments from './Comments';
import BookmarksTab from './BookmarksTab';

/**
 * Tab panel wrapper
 */
function TabPanel({ children, value, index, ...props }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`collection-tabpanel-${index}`}
      aria-labelledby={`collection-tab-${index}`}
      {...props}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

/**
 * My Collection Page
 * Tabbed interface for managing saved content: Lists, History, Highlights, Comments, Bookmarks
 */
export default function Collection() {
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get('tab');
  
  // Map URL param to tab index
  const tabMap = {
    lists: 0,
    history: 1,
    highlights: 2,
    comments: 3,
    bookmarks: 4
  };
  
  const [tabValue, setTabValue] = useState(tabMap[tabParam] || 0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    // Update URL
    const tabNames = ['lists', 'history', 'highlights', 'comments', 'bookmarks'];
    setSearchParams({ tab: tabNames[newValue] });
  };

  const tabItems = [
    { label: 'Your Lists', icon: <IconList size={18} /> },
    { label: 'Reading History', icon: <IconHistory size={18} /> },
    { label: 'Highlights', icon: <IconHighlight size={18} /> },
    { label: 'Comments', icon: <IconMessage size={18} /> },
    { label: 'Bookmarks', icon: <IconBookmark size={18} /> }
  ];

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>
          My Collection
        </Typography>
      </Stack>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': {
              textTransform: 'none',
              minHeight: 48,
              fontWeight: 500
            }
          }}
        >
          {tabItems.map((item, index) => (
            <Tab
              key={index}
              label={item.label}
              icon={item.icon}
              iconPosition="start"
              sx={{ gap: 1 }}
            />
          ))}
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <TabPanel value={tabValue} index={0}>
        <YourLists />
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        <ReadingHistory />
      </TabPanel>
      <TabPanel value={tabValue} index={2}>
        <Highlights />
      </TabPanel>
      <TabPanel value={tabValue} index={3}>
        <Comments />
      </TabPanel>
      <TabPanel value={tabValue} index={4}>
        <BookmarksTab />
      </TabPanel>
    </Box>
  );
}
