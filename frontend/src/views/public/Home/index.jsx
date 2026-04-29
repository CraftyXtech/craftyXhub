import { useLocation } from 'react-router-dom';
import { Box, Collapse } from '@mui/material';
import HeroSection from './sections/HeroSection';
import LatestPosts from './sections/LatestPosts';
import CategoryCarouselSection from './sections/CategoryCarouselSection';
import PopularPosts from './sections/PopularPosts';
import ExploreTopics from './sections/ExploreTopics';
import Categories from './Categories';

/**
 * Homepage
 * Structure inspired by litho Magazine page
 * Hero section now includes slider + featured posts side by side
 * Newsletter is now embedded in the PopularPosts sidebar
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

      {/* Latest Articles + Breaking News sidebar */}
      <LatestPosts />

      {/* Business articles from the Business & Finance taxonomy */}
      <CategoryCarouselSection
        title="Business"
        parentSlug="business-and-finance"
        background="background.default"
      />

      {/* Technology articles from the Tech & Innovation taxonomy */}
      <CategoryCarouselSection
        title="Technology"
        parentSlug="tech-and-innovation"
        background="grey.50"
      />

      {/* Explore More Topics - Featured topics section */}
      <ExploreTopics />

      {/* Popular Articles + Newsletter sidebar */}
      <PopularPosts />
    </Box>
  );
}
