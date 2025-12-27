import { Box } from '@mui/material';
import Hero from './Hero';
import FeaturedPosts from './FeaturedPosts';
import Categories from './Categories';
import Newsletter from './Newsletter';

export default function Home() {
  return (
    <Box>
      <Hero />
      <FeaturedPosts />
      <Categories />
      <Newsletter />
    </Box>
  );
}
