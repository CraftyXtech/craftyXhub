import { useLocation } from 'react-router-dom';
import { Box, Collapse } from '@mui/material';
import HeroSection from './sections/HeroSection';
import LatestPosts from './sections/LatestPosts';
import PopularPosts from './sections/PopularPosts';
import Newsletter from './Newsletter';
import Categories from './Categories';

/**
 * Homepage
 * Structure inspired by litho Magazine page
 * Hero section now includes slider + featured posts side by side
 */
export default function Home() {
  const location = useLocation();
  const showCategories = location.hash === '#categories';

  return (
    <Box>
      {/* Hero Slider + Featured Posts (side by side on desktop) */}
      <HeroSection />

      {/* Categories / Explore Topics - Only shown when searched/requested */}
      <Collapse in={showCategories}>
        <Box id="categories">
          <Categories />
        </Box>
      </Collapse>

      {/* Latest Articles - 4 col grid */}
      <LatestPosts />

      {/* Popular Articles - 3 col grid */}
      <PopularPosts />

      {/* Newsletter */}
      <Newsletter />
    </Box>
  );
}
