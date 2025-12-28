import { Box } from '@mui/material';
import HeroSection from './sections/HeroSection';
import LatestPosts from './sections/LatestPosts';
import PopularPosts from './sections/PopularPosts';
import Newsletter from './Newsletter';

/**
 * Homepage
 * Structure inspired by litho Magazine page
 * Hero section now includes slider + featured posts side by side
 */
export default function Home() {
  return (
    <Box>
      {/* Hero Slider + Featured Posts (side by side on desktop) */}
      <HeroSection />

      {/* Latest Articles - 4 col grid */}
      <LatestPosts />

      {/* Popular Articles - 3 col grid */}
      <PopularPosts />

      {/* Newsletter */}
      <Newsletter />
    </Box>
  );
}
