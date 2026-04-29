import { useEffect, useMemo, useRef, useState } from 'react';

import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CircularProgress from '@mui/material/CircularProgress';
import FormControlLabel from '@mui/material/FormControlLabel';
import MenuItem from '@mui/material/MenuItem';
import Stack from '@mui/material/Stack';
import Switch from '@mui/material/Switch';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

import {
  IconDeviceFloppy,
  IconExternalLink,
  IconPhotoUp,
  IconTrash,
} from '@tabler/icons-react';

import { uploadMedia, validateFile } from '@/api/services/mediaService';
import { getAdminSettings, updateAdminSettings } from '@/api/services/settingsService';
import { getImageUrl } from '@/api/utils/imageUrl';
import { getApiErrorMessage } from '@/utils/apiError';

const DEFAULT_AD_SLOT = {
  enabled: true,
  mode: 'placeholder',
  label: 'ADVERTISEMENT',
  image_url: '',
  target_url: '',
  background_color: '#F4F6F8',
};

const normalizeAdSlot = (adSlot) => ({
  ...DEFAULT_AD_SLOT,
  ...(adSlot || {}),
});

export default function AdBanners() {
  const fileInputRef = useRef(null);
  const [settings, setSettings] = useState(null);
  const [adSlot, setAdSlot] = useState(DEFAULT_AD_SLOT);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const previewImageUrl = useMemo(() => getImageUrl(adSlot.image_url), [adSlot.image_url]);

  useEffect(() => {
    const loadSettings = async () => {
      try {
        setLoading(true);
        setError('');
        const data = await getAdminSettings();
        setSettings(data);
        setAdSlot(normalizeAdSlot(data.ad_slot));
      } catch (err) {
        setError(getApiErrorMessage(err, 'Failed to load advertisement settings'));
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, []);

  const updateField = (field, value) => {
    setAdSlot((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const saveAdSlot = async (nextAdSlot = adSlot, message = 'Advertisement banner saved.') => {
    if (!settings) return;

    try {
      setSaving(true);
      setError('');
      setSuccess('');
      const payload = {
        ...settings,
        ad_slot: normalizeAdSlot(nextAdSlot),
      };
      const savedSettings = await updateAdminSettings(payload);
      setSettings(savedSettings);
      setAdSlot(normalizeAdSlot(savedSettings.ad_slot));
      setSuccess(message);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to save advertisement banner'));
    } finally {
      setSaving(false);
    }
  };

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const validation = validateFile(file, 5 * 1024 * 1024);
    if (!file.type.startsWith('image/') || !validation.isValid) {
      setError(validation.errors[0] || 'Please upload an image file under 5 MB.');
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    try {
      setUploading(true);
      setError('');
      setSuccess('');
      const media = await uploadMedia(file, 'Advertisement banner');
      const nextAdSlot = normalizeAdSlot({
        ...adSlot,
        enabled: true,
        mode: 'image',
        image_url: media.file_path,
      });
      setAdSlot(nextAdSlot);
      await saveAdSlot(nextAdSlot, 'Banner uploaded and published.');
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to upload banner'));
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleRemoveImage = () => {
    const nextAdSlot = normalizeAdSlot({
      ...adSlot,
      mode: 'placeholder',
      image_url: '',
    });
    setAdSlot(nextAdSlot);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'grid', placeItems: 'center', minHeight: 360 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Stack
        direction={{ xs: 'column', md: 'row' }}
        justifyContent="space-between"
        alignItems={{ xs: 'flex-start', md: 'center' }}
        sx={{ mb: 3, gap: 2 }}
      >
        <Box>
          <Typography variant="h5" fontWeight={700}>
            Ad Banners
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Upload and publish the top advertisement band shown on the public site.
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button
            component="label"
            variant="outlined"
            startIcon={<IconPhotoUp size={18} />}
            disabled={uploading || saving}
          >
            {uploading ? 'Uploading...' : 'Upload Banner'}
            <input
              ref={fileInputRef}
              type="file"
              hidden
              accept="image/*"
              onChange={handleUpload}
            />
          </Button>
          <Button
            variant="contained"
            startIcon={<IconDeviceFloppy size={18} />}
            disabled={saving || uploading}
            onClick={() => saveAdSlot()}
          >
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </Stack>
      </Stack>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      <Stack direction={{ xs: 'column', lg: 'row' }} spacing={3} alignItems="stretch">
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', flex: 1 }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
              Banner Settings
            </Typography>

            <Stack spacing={2.5}>
              <FormControlLabel
                control={
                  <Switch
                    checked={Boolean(adSlot.enabled)}
                    onChange={(_, checked) => updateField('enabled', checked)}
                  />
                }
                label="Show advertisement band"
              />

              <TextField
                label="Mode"
                select
                value={adSlot.mode}
                onChange={(event) => updateField('mode', event.target.value)}
                fullWidth
              >
                <MenuItem value="placeholder">Placeholder</MenuItem>
                <MenuItem value="image">Image Banner</MenuItem>
              </TextField>

              <TextField
                label="Label"
                value={adSlot.label}
                onChange={(event) => updateField('label', event.target.value)}
                fullWidth
              />

              <TextField
                label="Click Target URL"
                value={adSlot.target_url}
                onChange={(event) => updateField('target_url', event.target.value)}
                placeholder="https://advertiser.example"
                fullWidth
              />

              <TextField
                label="Background Color"
                value={adSlot.background_color}
                onChange={(event) => updateField('background_color', event.target.value)}
                fullWidth
              />

              <TextField
                label="Image Path or URL"
                value={adSlot.image_url}
                onChange={(event) => updateField('image_url', event.target.value)}
                helperText="Uploading a banner fills this automatically. External image URLs also work."
                fullWidth
              />

              {adSlot.image_url && (
                <Button
                  color="error"
                  variant="outlined"
                  startIcon={<IconTrash size={18} />}
                  onClick={handleRemoveImage}
                  sx={{ alignSelf: 'flex-start' }}
                >
                  Remove Image
                </Button>
              )}
            </Stack>
          </CardContent>
        </Card>

        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', flex: 1 }}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="subtitle1" fontWeight={700}>
                Public Preview
              </Typography>
              {adSlot.target_url && (
                <Button
                  component="a"
                  href={adSlot.target_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  size="small"
                  endIcon={<IconExternalLink size={16} />}
                >
                  Target
                </Button>
              )}
            </Stack>

            <Box
              sx={{
                bgcolor: adSlot.background_color || '#F4F6F8',
                p: { xs: 2, md: 3 },
              }}
            >
              {adSlot.enabled ? (
                adSlot.mode === 'image' && adSlot.image_url ? (
                  <Box
                    component="img"
                    src={previewImageUrl}
                    alt={adSlot.label || 'Advertisement'}
                    sx={{
                      width: '100%',
                      maxHeight: 180,
                      objectFit: 'cover',
                      display: 'block',
                      borderRadius: 1,
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  />
                ) : (
                  <Box
                    sx={{
                      minHeight: 132,
                      display: 'grid',
                      placeItems: 'center',
                      borderTop: '1px dashed rgba(23,24,28,0.18)',
                      borderBottom: '1px dashed rgba(23,24,28,0.18)',
                      color: '#8A95A5',
                      fontSize: 13,
                      letterSpacing: 1.2,
                      textTransform: 'uppercase',
                    }}
                  >
                    {adSlot.label || 'Advertisement'}
                  </Box>
                )
              ) : (
                <Box
                  sx={{
                    minHeight: 132,
                    display: 'grid',
                    placeItems: 'center',
                    color: 'text.secondary',
                    border: '1px dashed',
                    borderColor: 'divider',
                    borderRadius: 1,
                  }}
                >
                  Advertisement band hidden
                </Box>
              )}
            </Box>
          </CardContent>
        </Card>
      </Stack>
    </Box>
  );
}
