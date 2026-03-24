import { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import Grid from '@mui/material/Grid';
import Divider from '@mui/material/Divider';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';

// Icons
import { IconDeviceFloppy } from '@tabler/icons-react';

// API
import { axiosPrivate } from '@/api/axios';

// Mock API for settings
const getSettings = async () => {
  try {
    const response = await axiosPrivate.get('/settings');
    return response.data;
  } catch {
    return {
      site_name: 'CraftyXHub',
      site_description: '',
      contact_email: '',
      posts_per_page: 10,
      allow_comments: true,
      allow_registration: true,
      require_email_verification: true
    };
  }
};

const updateSettings = async (data) => {
  return axiosPrivate.put('/settings', data);
};

/**
 * Site Settings Page (Admin Only)
 */
export default function Settings() {
  // State
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  // Form
  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      site_name: '',
      site_description: '',
      contact_email: '',
      posts_per_page: 10,
      allow_comments: true,
      allow_registration: true,
      require_email_verification: true
    }
  });

  // Load settings
  useEffect(() => {
    const loadSettings = async () => {
      try {
        setLoading(true);
        const settings = await getSettings();
        reset(settings);
      } catch (err) {
        console.error('Failed to load settings:', err);
      } finally {
        setLoading(false);
      }
    };
    loadSettings();
  }, [reset]);

  // Submit
  const onSubmit = async (data) => {
    try {
      setSaving(true);
      setError(null);
      await updateSettings(data);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to save settings:', err);
      setError('Failed to save settings');
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
      {/* Header */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="h5" fontWeight={600}>
          Site Settings
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Configure site-wide settings
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <Grid container spacing={3}>
          {/* General Settings */}
          <Grid item xs={12} md={6}>
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', height: '100%' }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                  General
                </Typography>

                <Stack spacing={2.5}>
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
                        helperText="Brief description for SEO"
                      />
                    )}
                  />

                  <Controller
                    name="contact_email"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Contact Email"
                        type="email"
                        fullWidth
                      />
                    )}
                  />

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
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          {/* Feature Toggles */}
          <Grid item xs={12} md={6}>
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', height: '100%' }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                  Features
                </Typography>

                <Stack spacing={1.5}>
                  <Controller
                    name="allow_comments"
                    control={control}
                    render={({ field }) => (
                      <FormControlLabel
                        control={<Switch {...field} checked={field.value} />}
                        label="Allow comments on posts"
                      />
                    )}
                  />

                  <Controller
                    name="allow_registration"
                    control={control}
                    render={({ field }) => (
                      <FormControlLabel
                        control={<Switch {...field} checked={field.value} />}
                        label="Allow new user registrations"
                      />
                    )}
                  />

                  <Controller
                    name="require_email_verification"
                    control={control}
                    render={({ field }) => (
                      <FormControlLabel
                        control={<Switch {...field} checked={field.value} />}
                        label="Require email verification"
                      />
                    )}
                  />
                </Stack>

                <Divider sx={{ my: 3 }} />

                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Danger Zone
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  These actions are irreversible. Be careful.
                </Typography>
                <Button variant="outlined" color="error" size="small" disabled>
                  Clear All Cache
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Save Button */}
        <Box sx={{ mt: 3 }}>
          <Button
            type="submit"
            variant="contained"
            startIcon={<IconDeviceFloppy size={18} />}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </Box>
      </form>
    </Box>
  );
}
