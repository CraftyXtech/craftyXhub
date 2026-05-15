import { useEffect, useState } from 'react';
import { Link as RouterLink, useNavigate, useSearchParams } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Grid,
  InputAdornment,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { IconArrowRight, IconSearch } from '@tabler/icons-react';

import { getImageUrl } from '@/api/services/postService';
import { searchPosts } from '@/api/services/searchService';
import { getApiErrorMessage } from '@/utils/apiError';
import { Helmet } from 'react-helmet-async';

export default function Search() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';

  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  useEffect(() => {
    const trimmedQuery = initialQuery.trim();
    if (!trimmedQuery) {
      setResults([]);
      setTotal(0);
      setLoading(false);
      return;
    }

    const runSearch = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await searchPosts(trimmedQuery, { limit: 24 });
        setResults(response?.posts || []);
        setTotal(response?.total || response?.posts?.length || 0);
      } catch (err) {
        setError(getApiErrorMessage(err, 'Search failed'));
      } finally {
        setLoading(false);
      }
    };

    runSearch();
  }, [initialQuery]);

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmedQuery = query.trim();
    if (!trimmedQuery) return;
    navigate(`/search?q=${encodeURIComponent(trimmedQuery)}`);
  };

  return (
    <Box sx={{ bgcolor: '#F8F9FC', py: { xs: 4, md: 5 } }}>
      <Helmet>
        <title>Search | CraftyXHub</title>
        <meta name="description" content="Search for articles, topics, and companies on CraftyXHub." />
      </Helmet>
      <Container maxWidth="lg">
        <Stack spacing={3}>
          <Box>
            <Typography variant="h4" fontWeight={800}>
              Search Coverage
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
              Look across published reporting, market explainers, AI stories, and tech-driven world news.
            </Typography>
          </Box>

          <Box component="form" onSubmit={handleSubmit}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
              <TextField
                fullWidth
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search stories, topics, or companies"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <IconSearch size={18} />
                    </InputAdornment>
                  ),
                }}
              />
              <Button type="submit" variant="contained" sx={{ minWidth: 160 }}>
                Search
              </Button>
            </Stack>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          {initialQuery.trim() && !loading && (
            <Typography variant="body2" color="text.secondary">
              {total} result{total === 1 ? '' : 's'} for "{initialQuery}"
            </Typography>
          )}

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : !initialQuery.trim() ? (
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <CardContent>
                <Typography color="text.secondary">
                  Start with a topic, company, keyword, or technology and we will pull matching published stories.
                </Typography>
              </CardContent>
            </Card>
          ) : results.length === 0 ? (
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <CardContent>
                <Typography color="text.secondary">
                  No published stories matched that search yet. Try a broader keyword or publish more coverage around the topic.
                </Typography>
              </CardContent>
            </Card>
          ) : (
            <Grid container spacing={2}>
              {results.map((post) => (
                <Grid item xs={12} md={6} key={post.uuid}>
                  <Card
                    component={RouterLink}
                    to={`/post/${post.slug}`}
                    elevation={0}
                    sx={{
                      display: 'flex',
                      gap: 2,
                      p: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 2,
                      textDecoration: 'none',
                      color: 'inherit',
                      height: '100%',
                    }}
                  >
                    <Box
                      sx={{
                        width: 160,
                        minWidth: 160,
                        display: { xs: 'none', sm: 'block' },
                        borderRadius: 1.5,
                        overflow: 'hidden',
                        bgcolor: 'grey.200',
                        aspectRatio: '16 / 11',
                      }}
                    >
                      {post.featured_image && (
                        <Box
                          component="img"
                          src={getImageUrl(post.featured_image)}
                          alt={post.title}
                          sx={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        />
                      )}
                    </Box>
                    <Box sx={{ minWidth: 0 }}>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        {post.category?.name || 'Coverage'}
                      </Typography>
                      <Typography variant="h6" fontWeight={800} sx={{ mt: 0.75, mb: 1 }}>
                        {post.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {post.excerpt || 'Read the full story.'}
                      </Typography>
                      <Stack direction="row" spacing={0.5} alignItems="center" sx={{ color: 'primary.main' }}>
                        <Typography variant="body2" fontWeight={700}>
                          Open story
                        </Typography>
                        <IconArrowRight size={15} />
                      </Stack>
                    </Box>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Stack>
      </Container>
    </Box>
  );
}
