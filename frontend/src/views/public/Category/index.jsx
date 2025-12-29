import { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Typography,
  Skeleton,
  Alert,
  Button,
  Tabs,
  Tab
} from '@mui/material';
import { motion } from 'framer-motion';
import PostCard from '@/components/PostCard';
import Sidebar from '@/components/Blog/Sidebar';
import Pagination from '@/components/Pagination';
import Breadcrumb from '@/components/Breadcrumb';
import { getCategoryBySlug } from '@/api/services/categoryService';
import { axiosPublic } from '@/api/axios';

const MotionBox = motion.create(Box);

/**
 * Category Page
 * - Main category: Shows subcategory tabs + posts from all or selected subcategory
 * - Subcategory: Shows posts directly with parent breadcrumb
 */
export default function Category() {
  const { slug } = useParams();
  const [page, setPage] = useState(1);
  const postsPerPage = 6;

  // Category state
  const [category, setCategory] = useState(null);
  const [categoryLoading, setCategoryLoading] = useState(true);
  const [categoryError, setCategoryError] = useState(null);

  // Posts state
  const [posts, setPosts] = useState([]);
  const [postsLoading, setPostsLoading] = useState(true);
  const [postsError, setPostsError] = useState(null);
  const [totalPosts, setTotalPosts] = useState(0);

  // Subcategory filter for main categories
  const [selectedSubcategory, setSelectedSubcategory] = useState('all');

  // Determine if this is a main category (has subcategories, no parent)
  const isMainCategory = category && !category.isSubcategory && category.subcategories?.length > 0;

  // Fetch category by slug
  useEffect(() => {
    const fetchCategory = async () => {
      if (!slug) return;
      
      try {
        setCategoryLoading(true);
        setCategoryError(null);
        const data = await getCategoryBySlug(slug);
        setCategory(data);
        setSelectedSubcategory('all'); // Reset filter
      } catch (err) {
        console.error('Failed to fetch category:', err);
        setCategoryError(err.status === 404 ? 'Category not found' : err.message);
        setCategory(null);
      } finally {
        setCategoryLoading(false);
      }
    };

    fetchCategory();
    setPage(1);
  }, [slug]);

  // Get category IDs to query
  const categoryIdsToQuery = useMemo(() => {
    if (!category) return [];
    
    if (isMainCategory) {
      if (selectedSubcategory === 'all') {
        // Query all subcategory IDs
        return category.subcategories.map(sub => sub.id);
      } else {
        // Query selected subcategory
        return [parseInt(selectedSubcategory)];
      }
    }
    
    // Subcategory: just query its ID
    return [category.id];
  }, [category, isMainCategory, selectedSubcategory]);

  // Fetch posts by category IDs
  const fetchPosts = useCallback(async () => {
    if (categoryIdsToQuery.length === 0) return;
    
    try {
      setPostsLoading(true);
      setPostsError(null);
      
      // For multiple categories, make parallel requests and merge
      if (categoryIdsToQuery.length > 1) {
        const requests = categoryIdsToQuery.map(catId =>
          axiosPublic.get('/posts/', {
            params: {
              category_id: catId,
              page: 1,
              page_size: 100, // Get more to merge
              status: 'published'
            }
          })
        );
        
        const responses = await Promise.all(requests);
        const allPosts = responses.flatMap(r => r.data.posts || []);
        
        // Sort by date and paginate
        allPosts.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
        
        const startIdx = (page - 1) * postsPerPage;
        const paginatedPosts = allPosts.slice(startIdx, startIdx + postsPerPage);
        
        setPosts(paginatedPosts);
        setTotalPosts(allPosts.length);
      } else {
        // Single category query
        const response = await axiosPublic.get('/posts/', {
          params: {
            category_id: categoryIdsToQuery[0],
            page,
            page_size: postsPerPage,
            status: 'published'
          }
        });
        
        setPosts(response.data.posts || []);
        setTotalPosts(response.data.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch posts:', err);
      setPostsError(err.response?.data?.detail || err.message);
      setPosts([]);
    } finally {
      setPostsLoading(false);
    }
  }, [categoryIdsToQuery, page, postsPerPage]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  const totalPages = Math.ceil(totalPosts / postsPerPage);

  const handlePageChange = (event, value) => {
    setPage(value);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSubcategoryChange = (event, newValue) => {
    setSelectedSubcategory(newValue);
    setPage(1);
  };

  // Build breadcrumb based on whether it's a subcategory
  const breadcrumbItems = category?.parent
    ? [
        { label: category.parent.name, to: `/category/${category.parent.slug}` },
        { label: category.name }
      ]
    : [
        { label: category?.name || slug }
      ];

  // Error state for category not found
  if (categoryError) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom>
          {categoryError === 'Category not found' ? 'Category Not Found' : 'Error Loading Category'}
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 4 }}>
          {categoryError === 'Category not found' 
            ? 'The category you are looking for does not exist or may have been removed.'
            : categoryError
          }
        </Typography>
        <Button
          component={RouterLink}
          to="/"
          variant="contained"
          color="primary"
        >
          Back to Home
        </Button>
      </Container>
    );
  }

  return (
    <Box>
      {/* Category Header */}
      <Box
        sx={{
          bgcolor: 'grey.50',
          py: { xs: 6, md: 8 },
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Container maxWidth="lg">
          <Breadcrumb items={breadcrumbItems} />
          
          <MotionBox
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {categoryLoading ? (
              <>
                <Skeleton variant="text" width={300} height={60} />
                <Skeleton variant="text" width={500} height={24} />
              </>
            ) : (
              <>
                <Typography
                  variant="h2"
                  sx={{ fontWeight: 700, mb: 2 }}
                >
                  {category?.name}
                </Typography>
                {category?.description && (
                  <Typography
                    variant="body1"
                    color="text.secondary"
                    sx={{ maxWidth: 600 }}
                  >
                    {category.description}
                  </Typography>
                )}
              </>
            )}
          </MotionBox>

          {/* Subcategory Filter Tabs for Main Categories */}
          {isMainCategory && (
            <Box sx={{ mt: 4 }}>
              <Tabs
                value={selectedSubcategory}
                onChange={handleSubcategoryChange}
                variant="scrollable"
                scrollButtons="auto"
                sx={{
                  '& .MuiTab-root': {
                    textTransform: 'none',
                    fontWeight: 500,
                    minWidth: 'auto',
                    px: 2
                  },
                  '& .Mui-selected': {
                    fontWeight: 600
                  }
                }}
              >
                <Tab label="All" value="all" />
                {category.subcategories.map(sub => (
                  <Tab key={sub.id} label={sub.name} value={String(sub.id)} />
                ))}
              </Tabs>
            </Box>
          )}
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ py: { xs: 4, md: 6 } }}>
        <Grid container spacing={4}>
          {/* Posts Grid */}
          <Grid size={{ xs: 12, lg: 8 }}>
            {postsError && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {postsError}
              </Alert>
            )}
            
            <Grid container spacing={3}>
              {postsLoading ? (
                // Loading skeleton
                [...Array(4)].map((_, index) => (
                  <Grid size={{ xs: 12, sm: 6 }} key={index}>
                    <Box>
                      <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} />
                      <Skeleton variant="text" height={32} sx={{ mt: 2 }} />
                      <Skeleton variant="text" width="80%" />
                      <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                        <Skeleton variant="circular" width={32} height={32} />
                        <Skeleton variant="text" width={100} />
                      </Box>
                    </Box>
                  </Grid>
                ))
              ) : posts.length > 0 ? (
                posts.map((post, index) => (
                  <Grid size={{ xs: 12, sm: 6 }} key={post.id || post.uuid}>
                    <PostCard post={post} animationDelay={index * 0.05} />
                  </Grid>
                ))
              ) : (
                <Grid size={{ xs: 12 }}>
                  <Box sx={{ textAlign: 'center', py: 8 }}>
                    <Typography variant="h6" color="text.secondary">
                      No posts found in this category
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Check back later for new content!
                    </Typography>
                  </Box>
                </Grid>
              )}
            </Grid>

            {/* Pagination */}
            {totalPages > 1 && (
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
              />
            )}
          </Grid>

          {/* Sidebar */}
          <Grid size={{ xs: 12, lg: 4 }}>
            <Sidebar activeCategory={slug} category={category} />
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
