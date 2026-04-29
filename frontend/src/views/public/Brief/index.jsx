import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Divider,
  Grid,
  InputAdornment,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { IconArrowRight, IconBolt, IconMail, IconSparkles } from '@tabler/icons-react';

import { subscribeToNewsletter } from '@/api/services/newsletterService';
import { getImageUrl, getRecentPosts } from '@/api/services/postService';
import { getApiErrorMessage } from '@/utils/apiError';

const briefTopics = ['AI shifts', 'Crypto flows', 'Market moves', 'Geotech risk'];

export default function Brief() {
  const [email, setEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const [recentPosts, setRecentPosts] = useState([]);
  const [loadingPosts, setLoadingPosts] = useState(true);

  useEffect(() => {
    const loadRecentCoverage = async () => {
      try {
        setLoadingPosts(true);
        const response = await getRecentPosts({ limit: 4 });
        setRecentPosts(response?.posts || []);
      } catch (err) {
        console.error('Failed to load recent brief coverage:', err);
        setRecentPosts([]);
      } finally {
        setLoadingPosts(false);
      }
    };

    loadRecentCoverage();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setError('Enter your email to get the Daily Brief.');
      return;
    }

    try {
      setSubmitting(true);
      setError('');
      await subscribeToNewsletter({ email: trimmedEmail, source: 'daily_brief_page' });
      setSubmitted(true);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not subscribe right now. Please try again.'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box sx={{ bgcolor: '#F6F7FB', py: { xs: 4, md: 6 } }}>
      <Container maxWidth="lg">
        <Grid container spacing={3}>
          <Grid item xs={12} md={7}>
            <Card
              elevation={0}
              sx={{
                height: '100%',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                bgcolor: '#10131A',
                color: 'white',
              }}
            >
              <CardContent sx={{ p: { xs: 3, md: 4 } }}>
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                  <IconSparkles size={18} />
                  <Typography variant="overline" sx={{ color: 'rgba(255,255,255,0.7)', letterSpacing: 1.2 }}>
                    Daily Brief
                  </Typography>
                </Stack>

                <Typography variant="h3" sx={{ fontWeight: 800, lineHeight: 1.1, maxWidth: 560 }}>
                  The daily read on business, AI, crypto, markets, and the world events shaping technology.
                </Typography>

                <Typography variant="body1" sx={{ mt: 2.5, color: 'rgba(255,255,255,0.76)', maxWidth: 560 }}>
                  We keep the signal tight: what moved, why it matters, and where the second-order effects are likely to show up next.
                </Typography>

                <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 3 }}>
                  {briefTopics.map((topic) => (
                    <Chip
                      key={topic}
                      label={topic}
                      icon={<IconBolt size={14} />}
                      sx={{
                        bgcolor: 'rgba(255,255,255,0.08)',
                        color: 'white',
                        borderRadius: 1.5,
                      }}
                    />
                  ))}
                </Stack>

                {!submitted ? (
                  <Box component="form" onSubmit={handleSubmit} sx={{ mt: 4 }}>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
                      <TextField
                        fullWidth
                        type="email"
                        placeholder="Enter your email"
                        value={email}
                        disabled={submitting}
                        onChange={(event) => setEmail(event.target.value)}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <IconMail size={18} color="rgba(0,0,0,0.45)" />
                            </InputAdornment>
                          ),
                        }}
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            bgcolor: 'white',
                            borderRadius: 1.5,
                          },
                        }}
                      />
                      <Button
                        type="submit"
                        variant="contained"
                        disabled={submitting}
                        sx={{
                          minWidth: 180,
                          borderRadius: 1.5,
                          bgcolor: '#D62839',
                          '&:hover': { bgcolor: '#BC2231' },
                        }}
                      >
                        {submitting ? 'Subscribing...' : 'Get the Brief'}
                      </Button>
                    </Stack>
                    {error && (
                      <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError('')}>
                        {error}
                      </Alert>
                    )}
                    <Typography variant="caption" sx={{ mt: 1.5, display: 'block', color: 'rgba(255,255,255,0.62)' }}>
                      Expect a sharp, readable update rather than a dump of headlines.
                    </Typography>
                  </Box>
                ) : (
                  <Alert severity="success" sx={{ mt: 4 }}>
                    You are in. The next Daily Brief will head to your inbox.
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={5}>
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, height: '100%' }}>
              <CardContent sx={{ p: { xs: 3, md: 4 } }}>
                <Typography variant="h6" fontWeight={800}>
                  What shows up in the brief
                </Typography>
                <Divider sx={{ my: 2.5 }} />
                <Stack spacing={2.5}>
                  <Box>
                    <Typography variant="subtitle2" fontWeight={700}>
                      Fast market context
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      The most important market and crypto moves, with enough context to see what changed and why.
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" fontWeight={700}>
                      AI and product shifts
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      Model launches, infra moves, and platform decisions that change how teams build and compete.
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" fontWeight={700}>
                      Geotech and systems risk
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      World events filtered through cyber, supply chains, chips, satellites, infrastructure, and capital.
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ mt: { xs: 4, md: 6 } }}>
          <Stack
            direction={{ xs: 'column', md: 'row' }}
            spacing={1}
            justifyContent="space-between"
            alignItems={{ xs: 'flex-start', md: 'center' }}
            sx={{ mb: 2.5 }}
          >
            <Box>
              <Typography variant="h5" fontWeight={800}>
                Recent Coverage
              </Typography>
              <Typography variant="body2" color="text.secondary">
                A sample of the reporting the Daily Brief pulls from.
              </Typography>
            </Box>
          </Stack>

          <Grid container spacing={2}>
            {loadingPosts ? (
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                  <CircularProgress />
                </Box>
              </Grid>
            ) : recentPosts.length === 0 ? (
              <Grid item xs={12}>
                <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                  <CardContent>
                    <Typography color="text.secondary">
                      Publish a few stories and they will start showing up here automatically.
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ) : (
              recentPosts.map((post) => (
                <Grid item xs={12} sm={6} md={3} key={post.uuid}>
                  <Card
                    component={RouterLink}
                    to={`/post/${post.slug}`}
                    elevation={0}
                    sx={{
                      height: '100%',
                      textDecoration: 'none',
                      color: 'inherit',
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 2,
                      overflow: 'hidden',
                    }}
                  >
                    {post.featured_image ? (
                      <Box
                        component="img"
                        src={getImageUrl(post.featured_image)}
                        alt={post.title}
                        sx={{ width: '100%', aspectRatio: '16 / 10', objectFit: 'cover' }}
                      />
                    ) : (
                      <Box sx={{ aspectRatio: '16 / 10', bgcolor: 'grey.200' }} />
                    )}
                    <CardContent>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        {post.category?.name || 'Coverage'}
                      </Typography>
                      <Typography variant="subtitle1" fontWeight={700} sx={{ mt: 0.75, mb: 1 }}>
                        {post.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {post.excerpt || 'Read the full story.'}
                      </Typography>
                      <Stack direction="row" spacing={0.5} alignItems="center" sx={{ color: 'primary.main' }}>
                        <Typography variant="body2" fontWeight={700}>
                          Read story
                        </Typography>
                        <IconArrowRight size={15} />
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              ))
            )}
          </Grid>
        </Box>
      </Container>
    </Box>
  );
}
