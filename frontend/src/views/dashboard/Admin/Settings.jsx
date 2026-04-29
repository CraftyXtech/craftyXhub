import { useEffect, useMemo, useState } from 'react';
import { Controller, useFieldArray, useForm } from 'react-hook-form';

import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CircularProgress from '@mui/material/CircularProgress';
import Divider from '@mui/material/Divider';
import FormControlLabel from '@mui/material/FormControlLabel';
import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import MenuItem from '@mui/material/MenuItem';
import Stack from '@mui/material/Stack';
import Switch from '@mui/material/Switch';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

import {
  IconDeviceFloppy,
  IconEye,
  IconPlus,
  IconTrash,
} from '@tabler/icons-react';

import {
  getAdminSettings,
  updateAdminSettings,
} from '@/api/services/settingsService';
import { getApiErrorMessage } from '@/utils/apiError';

const DEFAULT_VALUES = {
  site_name: 'CraftyXHub',
  site_description: '',
  contact_email: '',
  posts_per_page: 10,
  allow_comments: true,
  allow_registration: true,
  require_email_verification: true,
  identity_label: 'MARKET WATCH',
  breaking_label: 'BREAKING',
  daily_brief_label: 'DAILY BRIEF',
  daily_brief_url: '/brief',
  ad_slot: {
    enabled: true,
    mode: 'placeholder',
    label: 'ADVERTISEMENT',
    image_url: '',
    target_url: '',
    background_color: '#F4F6F8',
  },
  social_links: [
    { platform: 'x', label: 'X', url: '' },
    { platform: 'facebook', label: 'Facebook', url: '' },
    { platform: 'instagram', label: 'Instagram', url: '' },
    { platform: 'linkedin', label: 'LinkedIn', url: '' },
  ],
  market_watchlist: [
    { symbol: 'IXIC', label: 'NASDAQ', enabled: true },
    { symbol: 'GSPC', label: 'S&P 500', enabled: true },
    { symbol: 'BTC/USD', label: 'BTC', enabled: true },
    { symbol: 'ETH/USD', label: 'ETH', enabled: true },
    { symbol: 'EUR/USD', label: 'EUR/USD', enabled: true },
    { symbol: 'GBP/USD', label: 'GBP/USD', enabled: true },
  ],
  spotlight_items: [
    {
      label: 'AI PULSE',
      target_url: '/category/ai',
      icon: 'sparkles',
      theme: 'emerald',
      enabled: true,
      start_at: '',
      end_at: '',
      priority: 100,
      is_default: true,
    },
  ],
};

const toDateTimeLocal = (value) => {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const offsetMs = date.getTimezoneOffset() * 60 * 1000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
};

const fromDateTimeLocalToUtcIso = (value) => {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString();
};

const normalizeSettingsForForm = (settings) => ({
  ...DEFAULT_VALUES,
  ...settings,
  ad_slot: {
    ...DEFAULT_VALUES.ad_slot,
    ...(settings?.ad_slot || {}),
  },
  social_links: settings?.social_links?.length ? settings.social_links : DEFAULT_VALUES.social_links,
  market_watchlist: settings?.market_watchlist?.length
    ? settings.market_watchlist
    : DEFAULT_VALUES.market_watchlist,
  spotlight_items: (settings?.spotlight_items?.length ? settings.spotlight_items : DEFAULT_VALUES.spotlight_items).map((item) => ({
    ...item,
    start_at: toDateTimeLocal(item.start_at),
    end_at: toDateTimeLocal(item.end_at),
  })),
});

const sanitizeSettingsPayload = (data) => ({
  ...data,
  posts_per_page: Number(data.posts_per_page) || 10,
  social_links: (data.social_links || []).map((item) => ({
    platform: item.platform?.trim() || 'x',
    label: item.label?.trim() || item.platform?.trim() || 'Link',
    url: item.url?.trim() || '',
  })),
  market_watchlist: (data.market_watchlist || [])
    .filter((item) => item.symbol?.trim() && item.label?.trim())
    .map((item) => ({
      symbol: item.symbol.trim(),
      label: item.label.trim(),
      enabled: Boolean(item.enabled),
    })),
  spotlight_items: (data.spotlight_items || [])
    .filter((item) => item.label?.trim() && item.target_url?.trim())
    .map((item, index) => ({
      label: item.label.trim(),
      target_url: item.target_url.trim(),
      icon: item.icon?.trim() || null,
      theme: item.theme?.trim() || 'emerald',
      enabled: Boolean(item.enabled),
      start_at: fromDateTimeLocalToUtcIso(item.start_at),
      end_at: fromDateTimeLocalToUtcIso(item.end_at),
      priority: Number(item.priority) || 0,
      is_default: Boolean(item.is_default) && !(index > 0 && data.spotlight_items.some((entry, i) => i < index && entry.is_default)),
    })),
});

const resolvePreviewSpotlight = (spotlightItems = []) => {
  const now = new Date();
  const enabledItems = spotlightItems.filter((item) => item.enabled && item.label && item.target_url);
  const activeItems = enabledItems
    .filter((item) => {
      const starts = item.start_at ? new Date(item.start_at) <= now : true;
      const ends = item.end_at ? new Date(item.end_at) >= now : true;
      return starts && ends;
    })
    .sort((a, b) => Number(b.priority || 0) - Number(a.priority || 0));

  if (activeItems.length > 0) return activeItems[0];

  const defaultItems = enabledItems
    .filter((item) => item.is_default)
    .sort((a, b) => Number(b.priority || 0) - Number(a.priority || 0));

  return defaultItems[0] || enabledItems[0] || null;
};

const sectionCardSx = {
  border: '1px solid',
  borderColor: 'divider',
  borderRadius: 2,
  height: '100%',
};

const fieldRowSx = {
  p: 2,
  border: '1px solid',
  borderColor: 'divider',
  borderRadius: 2,
};

export default function Settings() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const {
    control,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm({
    defaultValues: DEFAULT_VALUES,
  });

  const socialLinksArray = useFieldArray({ control, name: 'social_links' });
  const marketWatchlistArray = useFieldArray({ control, name: 'market_watchlist' });
  const spotlightItemsArray = useFieldArray({ control, name: 'spotlight_items' });

  const watchedValues = watch();

  const previewSpotlight = useMemo(
    () => resolvePreviewSpotlight(watchedValues.spotlight_items || []),
    [watchedValues.spotlight_items],
  );

  const previewMarkets = useMemo(
    () => (watchedValues.market_watchlist || []).filter((item) => item.enabled && item.label).slice(0, 6),
    [watchedValues.market_watchlist],
  );

  useEffect(() => {
    const loadSettings = async () => {
      try {
        setLoading(true);
        const settings = await getAdminSettings();
        reset(normalizeSettingsForForm(settings));
      } catch (err) {
        setError(getApiErrorMessage(err, 'Failed to load settings'));
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, [reset]);

  const onSubmit = async (data) => {
    try {
      setSaving(true);
      setError('');
      setSuccess(false);
      const payload = sanitizeSettingsPayload(data);
      if (payload.spotlight_items.length === 0) {
        payload.spotlight_items = [];
      }
      const savedSettings = await updateAdminSettings(payload);
      reset(normalizeSettingsForForm(savedSettings));
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to save settings'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Stack
        direction={{ xs: 'column', md: 'row' }}
        spacing={2}
        justifyContent="space-between"
        alignItems={{ xs: 'flex-start', md: 'center' }}
        sx={{ mb: 3 }}
      >
        <Box>
          <Typography variant="h5" fontWeight={700}>
            Editorial Header Settings
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Control the masthead copy, Daily Brief CTA, market strip, spotlight rotation, and core site defaults.
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<IconDeviceFloppy size={18} />}
          onClick={handleSubmit(onSubmit)}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully.
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, lg: 8 }}>
            <Stack spacing={3}>
              <Card elevation={0} sx={sectionCardSx}>
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
                    Site Basics
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <Controller
                        name="site_name"
                        control={control}
                        rules={{ required: 'Site name is required' }}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Site Name"
                            fullWidth
                            error={Boolean(errors.site_name)}
                            helperText={errors.site_name?.message}
                          />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <Controller
                        name="contact_email"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="Contact Email" type="email" fullWidth />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 12 }}>
                      <Controller
                        name="site_description"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Site Description"
                            multiline
                            rows={3}
                            fullWidth
                          />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 4 }}>
                      <Controller
                        name="posts_per_page"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Posts Per Page"
                            type="number"
                            fullWidth
                            InputProps={{ inputProps: { min: 1, max: 50 } }}
                          />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 8 }}>
                      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
                        <Controller
                          name="allow_comments"
                          control={control}
                          render={({ field }) => (
                            <FormControlLabel
                              control={<Switch checked={field.value} onChange={(_, checked) => field.onChange(checked)} />}
                              label="Allow comments"
                            />
                          )}
                        />
                        <Controller
                          name="allow_registration"
                          control={control}
                          render={({ field }) => (
                            <FormControlLabel
                              control={<Switch checked={field.value} onChange={(_, checked) => field.onChange(checked)} />}
                              label="Allow registration"
                            />
                          )}
                        />
                        <Controller
                          name="require_email_verification"
                          control={control}
                          render={({ field }) => (
                            <FormControlLabel
                              control={<Switch checked={field.value} onChange={(_, checked) => field.onChange(checked)} />}
                              label="Require email verification"
                            />
                          )}
                        />
                      </Stack>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>

              <Card elevation={0} sx={sectionCardSx}>
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
                    Masthead Copy
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <Controller
                        name="identity_label"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="Identity Label" fullWidth helperText="Example: MARKET WATCH" />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <Controller
                        name="breaking_label"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="Breaking Label" fullWidth helperText="Example: BREAKING" />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <Controller
                        name="daily_brief_label"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="Daily Brief Button Label" fullWidth />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <Controller
                        name="daily_brief_url"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="Daily Brief URL" fullWidth />
                        )}
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>

              <Card elevation={0} sx={sectionCardSx}>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={700}>
                        Social Links
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        These links feed the top utility bar.
                      </Typography>
                    </Box>
                    <Button
                      startIcon={<IconPlus size={16} />}
                      onClick={() => socialLinksArray.append({ platform: '', label: '', url: '' })}
                    >
                      Add Link
                    </Button>
                  </Stack>
                  <Stack spacing={1.5}>
                    {socialLinksArray.fields.map((field, index) => (
                      <Stack key={field.id} direction={{ xs: 'column', md: 'row' }} spacing={1.5} sx={fieldRowSx}>
                        <Controller
                          name={`social_links.${index}.platform`}
                          control={control}
                          render={({ field: itemField }) => (
                            <TextField {...itemField} label="Platform" fullWidth />
                          )}
                        />
                        <Controller
                          name={`social_links.${index}.label`}
                          control={control}
                          render={({ field: itemField }) => (
                            <TextField {...itemField} label="Label" fullWidth />
                          )}
                        />
                        <Controller
                          name={`social_links.${index}.url`}
                          control={control}
                          render={({ field: itemField }) => (
                            <TextField {...itemField} label="URL" fullWidth />
                          )}
                        />
                        <IconButton
                          color="error"
                          onClick={() => socialLinksArray.remove(index)}
                          aria-label="Remove social link"
                        >
                          <IconTrash size={18} />
                        </IconButton>
                      </Stack>
                    ))}
                  </Stack>
                </CardContent>
              </Card>

              <Card elevation={0} sx={sectionCardSx}>
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
                    Advertisement Slot
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12 }}>
                      <Controller
                        name="ad_slot.enabled"
                        control={control}
                        render={({ field }) => (
                          <FormControlLabel
                            control={<Switch checked={field.value} onChange={(_, checked) => field.onChange(checked)} />}
                            label="Show advertisement band"
                          />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 4 }}>
                      <Controller
                        name="ad_slot.mode"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="Mode" select fullWidth>
                            <MenuItem value="placeholder">Placeholder</MenuItem>
                            <MenuItem value="image">Image Banner</MenuItem>
                          </TextField>
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 4 }}>
                      <Controller
                        name="ad_slot.label"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="Placeholder Label" fullWidth />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 4 }}>
                      <Controller
                        name="ad_slot.background_color"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="Background Color" fullWidth />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <Controller
                        name="ad_slot.image_url"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="Image URL" fullWidth />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <Controller
                        name="ad_slot.target_url"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="Target URL" fullWidth />
                        )}
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>

              <Card elevation={0} sx={sectionCardSx}>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={700}>
                        Market Watchlist
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Powered by Twelve Data when `TWELVEDATA_API_KEY` is configured.
                      </Typography>
                    </Box>
                    <Button
                      startIcon={<IconPlus size={16} />}
                      onClick={() => marketWatchlistArray.append({ symbol: '', label: '', enabled: true })}
                    >
                      Add Instrument
                    </Button>
                  </Stack>
                  <Stack spacing={1.5}>
                    {marketWatchlistArray.fields.map((field, index) => (
                      <Stack key={field.id} direction={{ xs: 'column', md: 'row' }} spacing={1.5} sx={fieldRowSx}>
                        <Controller
                          name={`market_watchlist.${index}.symbol`}
                          control={control}
                          render={({ field: itemField }) => (
                            <TextField {...itemField} label="Symbol" fullWidth helperText="Examples: BTC/USD, IXIC" />
                          )}
                        />
                        <Controller
                          name={`market_watchlist.${index}.label`}
                          control={control}
                          render={({ field: itemField }) => (
                            <TextField {...itemField} label="Label" fullWidth />
                          )}
                        />
                        <Controller
                          name={`market_watchlist.${index}.enabled`}
                          control={control}
                          render={({ field: itemField }) => (
                            <FormControlLabel
                              control={<Switch checked={itemField.value} onChange={(_, checked) => itemField.onChange(checked)} />}
                              label="Enabled"
                            />
                          )}
                        />
                        <IconButton
                          color="error"
                          onClick={() => marketWatchlistArray.remove(index)}
                          aria-label="Remove market item"
                        >
                          <IconTrash size={18} />
                        </IconButton>
                      </Stack>
                    ))}
                  </Stack>
                </CardContent>
              </Card>

              <Card elevation={0} sx={sectionCardSx}>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={700}>
                        Spotlight CTA
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Configure the right-side masthead CTA for AI Pulse, Crypto Watch, Geotech, events, or anything time-sensitive.
                      </Typography>
                    </Box>
                    <Button
                      startIcon={<IconPlus size={16} />}
                      onClick={() => spotlightItemsArray.append({
                        label: '',
                        target_url: '',
                        icon: '',
                        theme: 'emerald',
                        enabled: true,
                        start_at: '',
                        end_at: '',
                        priority: 0,
                        is_default: false,
                      })}
                    >
                      Add Spotlight
                    </Button>
                  </Stack>
                  <Stack spacing={1.5}>
                    {spotlightItemsArray.fields.map((field, index) => (
                      <Box key={field.id} sx={fieldRowSx}>
                        <Grid container spacing={2}>
                          <Grid size={{ xs: 12, md: 4 }}>
                            <Controller
                              name={`spotlight_items.${index}.label`}
                              control={control}
                              render={({ field: itemField }) => (
                                <TextField {...itemField} label="Label" fullWidth />
                              )}
                            />
                          </Grid>
                          <Grid size={{ xs: 12, md: 4 }}>
                            <Controller
                              name={`spotlight_items.${index}.target_url`}
                              control={control}
                              render={({ field: itemField }) => (
                                <TextField {...itemField} label="Target URL" fullWidth />
                              )}
                            />
                          </Grid>
                          <Grid size={{ xs: 12, md: 2 }}>
                            <Controller
                              name={`spotlight_items.${index}.icon`}
                              control={control}
                              render={({ field: itemField }) => (
                                <TextField {...itemField} label="Icon" fullWidth />
                              )}
                            />
                          </Grid>
                          <Grid size={{ xs: 12, md: 2 }}>
                            <Controller
                              name={`spotlight_items.${index}.theme`}
                              control={control}
                              render={({ field: itemField }) => (
                                <TextField {...itemField} label="Theme" fullWidth />
                              )}
                            />
                          </Grid>
                          <Grid size={{ xs: 12, md: 3 }}>
                            <Controller
                              name={`spotlight_items.${index}.start_at`}
                              control={control}
                              render={({ field: itemField }) => (
                                <TextField
                                  {...itemField}
                                  label="Starts At"
                                  type="datetime-local"
                                  fullWidth
                                  helperText="Your local time. Saved to the backend in UTC automatically."
                                  InputLabelProps={{ shrink: true }}
                                />
                              )}
                            />
                          </Grid>
                          <Grid size={{ xs: 12, md: 3 }}>
                            <Controller
                              name={`spotlight_items.${index}.end_at`}
                              control={control}
                              render={({ field: itemField }) => (
                                <TextField
                                  {...itemField}
                                  label="Ends At"
                                  type="datetime-local"
                                  fullWidth
                                  helperText="Your local time. Saved to the backend in UTC automatically."
                                  InputLabelProps={{ shrink: true }}
                                />
                              )}
                            />
                          </Grid>
                          <Grid size={{ xs: 12, md: 2 }}>
                            <Controller
                              name={`spotlight_items.${index}.priority`}
                              control={control}
                              render={({ field: itemField }) => (
                                <TextField {...itemField} label="Priority" type="number" fullWidth />
                              )}
                            />
                          </Grid>
                          <Grid size={{ xs: 12, md: 2 }}>
                            <Controller
                              name={`spotlight_items.${index}.enabled`}
                              control={control}
                              render={({ field: itemField }) => (
                                <FormControlLabel
                                  control={<Switch checked={itemField.value} onChange={(_, checked) => itemField.onChange(checked)} />}
                                  label="Enabled"
                                />
                              )}
                            />
                          </Grid>
                          <Grid size={{ xs: 12, md: 2 }}>
                            <Controller
                              name={`spotlight_items.${index}.is_default`}
                              control={control}
                              render={({ field: itemField }) => (
                                <FormControlLabel
                                  control={<Switch checked={itemField.value} onChange={(_, checked) => itemField.onChange(checked)} />}
                                  label="Default"
                                />
                              )}
                            />
                          </Grid>
                          <Grid size={{ xs: 12 }}>
                            <Stack direction="row" justifyContent="space-between" alignItems="center">
                              <Typography variant="caption" color="text.secondary">
                                Higher priority wins when multiple active items overlap.
                              </Typography>
                              <IconButton
                                color="error"
                                onClick={() => spotlightItemsArray.remove(index)}
                                aria-label="Remove spotlight"
                              >
                                <IconTrash size={18} />
                              </IconButton>
                            </Stack>
                          </Grid>
                        </Grid>
                      </Box>
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </Stack>
          </Grid>

          <Grid size={{ xs: 12, lg: 4 }}>
            <Stack spacing={3}>
              <Card elevation={0} sx={sectionCardSx}>
                <CardContent>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                    <IconEye size={18} />
                    <Typography variant="subtitle1" fontWeight={700}>
                      Header Preview
                    </Typography>
                  </Stack>

                  <Box sx={{ bgcolor: '#17181C', borderRadius: 2, overflow: 'hidden' }}>
                    <Stack
                      direction="row"
                      justifyContent="space-between"
                      alignItems="center"
                      sx={{ px: 2, py: 1.25, color: 'white', gap: 1 }}
                    >
                      <Stack direction="row" spacing={1} alignItems="center" sx={{ minWidth: 0 }}>
                        <Box
                          sx={{
                            px: 1.25,
                            py: 0.5,
                            borderRadius: 1,
                            bgcolor: '#D62839',
                            color: 'white',
                            fontSize: 12,
                            fontWeight: 700,
                            letterSpacing: 0.6,
                          }}
                        >
                          {watchedValues.identity_label || 'MARKET WATCH'}
                        </Box>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.72)' }}>
                          {new Date().toLocaleDateString('en-US', {
                            weekday: 'long',
                            month: 'long',
                            day: 'numeric',
                            year: 'numeric',
                          })}
                        </Typography>
                      </Stack>
                    </Stack>

                    <Box sx={{ bgcolor: '#D62839', px: 2, py: 1 }}>
                      <Stack direction="row" spacing={1.5} alignItems="center">
                        <Box
                          sx={{
                            px: 1.25,
                            py: 0.5,
                            borderRadius: 1,
                            bgcolor: '#352B7A',
                            color: 'white',
                            fontSize: 12,
                            fontWeight: 700,
                            letterSpacing: 0.8,
                          }}
                        >
                          {watchedValues.breaking_label || 'BREAKING'}
                        </Box>
                        <Typography variant="caption" sx={{ color: 'white' }}>
                          Breaking headlines will scroll here from admin-picked posts.
                        </Typography>
                      </Stack>
                    </Box>

                    <Box
                      sx={{
                        px: 2,
                        py: 2.5,
                        bgcolor: watchedValues.ad_slot?.background_color || '#F4F6F8',
                        color: '#55606F',
                        textAlign: 'center',
                        borderTop: '1px dashed rgba(23,24,28,0.12)',
                        borderBottom: '1px dashed rgba(23,24,28,0.12)',
                      }}
                    >
                      <Typography variant="caption" sx={{ letterSpacing: 1.2 }}>
                        {watchedValues.ad_slot?.label || 'ADVERTISEMENT'}
                      </Typography>
                    </Box>

                    <Stack
                      direction={{ xs: 'column', sm: 'row' }}
                      justifyContent="space-between"
                      alignItems="center"
                      sx={{ px: 2, py: 2.5, bgcolor: 'white', gap: 1.5 }}
                    >
                      <Button variant="contained" color="error" size="small">
                        {watchedValues.daily_brief_label || 'DAILY BRIEF'}
                      </Button>
                      <Typography variant="h6" fontWeight={800} color="primary.main">
                        {watchedValues.site_name || 'CraftyXHub'}
                      </Typography>
                      <Button variant="contained" color="success" size="small">
                        {previewSpotlight?.label || 'AI PULSE'}
                      </Button>
                    </Stack>

                    <Box sx={{ bgcolor: '#2C2A74', px: 2, py: 1.25 }}>
                      <Typography variant="caption" sx={{ color: 'white', fontWeight: 700 }}>
                        NEWS   BUSINESS   AI   CRYPTO   MARKETS   GEOTECH
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>

              <Card elevation={0} sx={sectionCardSx}>
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
                    Resolved Spotlight
                  </Typography>
                  <Stack spacing={1.25}>
                    <Typography variant="body2" color="text.secondary">
                      The CTA that would render publicly right now.
                    </Typography>
                    <Divider />
                    <Typography variant="body2">
                      <strong>Label:</strong> {previewSpotlight?.label || 'None configured'}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Target:</strong> {previewSpotlight?.target_url || '-'}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Theme:</strong> {previewSpotlight?.theme || '-'}
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>

              <Card elevation={0} sx={sectionCardSx}>
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
                    Market Strip Preview
                  </Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {previewMarkets.length > 0 ? previewMarkets.map((item) => (
                      <Box
                        key={`${item.symbol}-${item.label}`}
                        sx={{
                          px: 1.25,
                          py: 0.75,
                          borderRadius: 1.5,
                          bgcolor: 'success.lighter',
                          color: 'success.dark',
                          fontSize: 12,
                          fontWeight: 700,
                        }}
                      >
                        {item.label}
                      </Box>
                    )) : (
                      <Typography variant="body2" color="text.secondary">
                        No enabled instruments.
                      </Typography>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            </Stack>
          </Grid>
        </Grid>
      </form>
    </Box>
  );
}
