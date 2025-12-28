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
import Avatar from '@mui/material/Avatar';
import Alert from '@mui/material/Alert';
import Divider from '@mui/material/Divider';
import CircularProgress from '@mui/material/CircularProgress';

// Icons
import {
  IconUser,
  IconDeviceFloppy,
  IconPhoto,
  IconX
} from '@tabler/icons-react';

// API
import { useAuth } from '@/api/AuthProvider';
import { getProfile, updateProfile } from '@/api/services/profileService';

/**
 * Profile Settings Page
 */
export default function Profile() {
  const { user, updateUser } = useAuth();
  
  // State
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState(null);

  // Form
  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      full_name: '',
      username: '',
      email: '',
      bio: '',
      website: '',
      twitter: '',
      linkedin: ''
    }
  });

  // Load profile
  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        const profile = await getProfile();
        reset({
          full_name: profile.full_name || '',
          username: profile.username || '',
          email: profile.email || '',
          bio: profile.bio || '',
          website: profile.website || '',
          twitter: profile.twitter || '',
          linkedin: profile.linkedin || ''
        });
        if (profile.avatar) {
          setAvatarPreview(profile.avatar);
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
        // Use auth user data as fallback
        if (user) {
          reset({
            full_name: user.full_name || '',
            username: user.username || '',
            email: user.email || '',
            bio: user.bio || '',
            website: '',
            twitter: '',
            linkedin: ''
          });
          if (user.avatar) {
            setAvatarPreview(user.avatar);
          }
        }
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, [reset, user]);

  // Handle avatar change
  const handleAvatarChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setAvatarFile(file);
      setAvatarPreview(URL.createObjectURL(file));
    }
  };

  const handleAvatarRemove = () => {
    setAvatarFile(null);
    setAvatarPreview(null);
  };

  // Submit
  const onSubmit = async (data) => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(false);

      const formData = new FormData();
      Object.entries(data).forEach(([key, value]) => {
        if (value) formData.append(key, value);
      });
      
      if (avatarFile) {
        formData.append('avatar', avatarFile);
      }

      const updatedProfile = await updateProfile(formData);
      
      // Update auth context
      if (updateUser) {
        updateUser(updatedProfile);
      }
      
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to update profile:', err);
      setError(err.response?.data?.detail || 'Failed to update profile');
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
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" fontWeight={600}>
          Profile Settings
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Manage your personal information
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Profile updated successfully!
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <Grid container spacing={3}>
          {/* Avatar Section */}
          <Grid item xs={12} md={4}>
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <Box sx={{ position: 'relative', display: 'inline-block' }}>
                  <Avatar
                    src={avatarPreview}
                    sx={{ width: 120, height: 120, mx: 'auto', mb: 2, fontSize: 48 }}
                  >
                    {user?.full_name?.[0] || user?.username?.[0] || <IconUser size={48} />}
                  </Avatar>
                  {avatarPreview && (
                    <Button
                      size="small"
                      onClick={handleAvatarRemove}
                      sx={{
                        position: 'absolute',
                        top: 0,
                        right: -10,
                        minWidth: 'auto',
                        p: 0.5,
                        bgcolor: 'background.paper',
                        boxShadow: 1
                      }}
                    >
                      <IconX size={16} />
                    </Button>
                  )}
                </Box>
                
                <Typography variant="h6" gutterBottom>
                  {user?.full_name || user?.username}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {user?.email}
                </Typography>
                
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<IconPhoto size={18} />}
                  size="small"
                >
                  Change Photo
                  <input type="file" hidden accept="image/*" onChange={handleAvatarChange} />
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Form Section */}
          <Grid item xs={12} md={8}>
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 3 }}>
                  Personal Information
                </Typography>

                <Stack spacing={3}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Controller
                        name="full_name"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="Full Name" fullWidth />
                        )}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Controller
                        name="username"
                        control={control}
                        rules={{ required: 'Username is required' }}
                        render={({ field }) => (
                          <TextField 
                            {...field} 
                            label="Username" 
                            fullWidth 
                            error={Boolean(errors.username)}
                            helperText={errors.username?.message}
                          />
                        )}
                      />
                    </Grid>
                  </Grid>

                  <Controller
                    name="email"
                    control={control}
                    render={({ field }) => (
                      <TextField {...field} label="Email" type="email" fullWidth disabled />
                    )}
                  />

                  <Controller
                    name="bio"
                    control={control}
                    render={({ field }) => (
                      <TextField {...field} label="Bio" multiline rows={3} fullWidth />
                    )}
                  />
                </Stack>

                <Divider sx={{ my: 3 }} />

                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 3 }}>
                  Social Links
                </Typography>

                <Stack spacing={2}>
                  <Controller
                    name="website"
                    control={control}
                    render={({ field }) => (
                      <TextField {...field} label="Website" fullWidth placeholder="https://" />
                    )}
                  />
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Controller
                        name="twitter"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="Twitter" fullWidth placeholder="@username" />
                        )}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Controller
                        name="linkedin"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} label="LinkedIn" fullWidth placeholder="linkedin.com/in/..." />
                        )}
                      />
                    </Grid>
                  </Grid>
                </Stack>

                <Box sx={{ mt: 4 }}>
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<IconDeviceFloppy size={18} />}
                    disabled={saving}
                  >
                    {saving ? 'Saving...' : 'Save Changes'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </form>
    </Box>
  );
}
