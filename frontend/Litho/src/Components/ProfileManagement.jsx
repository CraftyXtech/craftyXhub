import React, { useState } from 'react';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import { useProfile } from '../api';
import { createProfile, updateProfile, deleteProfile } from '../api/postsService';
import Buttons from './Button/Buttons';
import { Input, TextArea } from './Form/Form';

// Validation schema for profile form
const ProfileSchema = Yup.object().shape({
    bio: Yup.string().max(500, 'Bio must be less than 500 characters'),
    location: Yup.string().max(100, 'Location must be less than 100 characters'),
    website: Yup.string().url('Invalid URL format'),
    twitter_handle: Yup.string().max(50, 'Twitter handle must be less than 50 characters'),
    github_handle: Yup.string().max(50, 'GitHub handle must be less than 50 characters'),
    linkedin_handle: Yup.string().max(50, 'LinkedIn handle must be less than 50 characters'),
    birth_date: Yup.date().nullable()
});

const ProfileManagement = ({ userUuid }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const [avatarFile, setAvatarFile] = useState(null);
    const [showForm, setShowForm] = useState(false);
    
    const { profile, loading: profileLoading, error: profileError, refetch } = useProfile(userUuid);

    const handleFileChange = (e) => {
        setAvatarFile(e.target.files[0]);
    };

    const handleSubmit = async (values, actions) => {
        try {
            setLoading(true);
            setError(null);
            actions.setSubmitting(true);

            const formData = {
                ...values,
                avatar: avatarFile
            };

            if (profile) {
                await updateProfile(userUuid, formData);
            } else {
                await createProfile(formData);
            }
            
            setSuccess(true);
            refetch();
            setAvatarFile(null);
            setShowForm(false);
        } catch (error) {
            console.error('Failed to save profile:', error);
            setError(error.message || 'Failed to save profile');
        } finally {
            setLoading(false);
            actions.setSubmitting(false);
        }
    };

    const handleDeleteProfile = async () => {
        if (window.confirm('Are you sure you want to delete your profile? This action cannot be undone.')) {
            try {
                setLoading(true);
                setError(null);
                await deleteProfile(userUuid);
                setSuccess(true);
                refetch();
                setShowForm(true);
            } catch (error) {
                console.error('Failed to delete profile:', error);
                setError(error.message || 'Failed to delete profile');
            } finally {
                setLoading(false);
            }
        }
    };

    // Get initial values for the form
    const getInitialValues = () => ({
        bio: profile?.bio || '',
        location: profile?.location || '',
        website: profile?.website || '',
        twitter_handle: profile?.twitter_handle || '',
        github_handle: profile?.github_handle || '',
        linkedin_handle: profile?.linkedin_handle || '',
        birth_date: profile?.birth_date || ''
    });

    if (profileLoading) return (
        <div className="section-padding">
            <div className="container">
                <div className="row">
                    <div className="col-lg-8 mx-auto text-center">
                        <div className="loading-spinner">Loading profile...</div>
                    </div>
                </div>
            </div>
        </div>
    );
    
    // Only show error for non-404 errors (404 means no profile exists yet, which is normal)
    if (profileError && profileError !== 'Profile not found') return (
        <div className="section-padding">
            <div className="container">
                <div className="row">
                    <div className="col-lg-8 mx-auto text-center">
                        <div className="alert alert-danger">Error loading profile: {profileError}</div>
                    </div>
                </div>
            </div>
        </div>
    );

    // Auto-show form for new users who don't have a profile yet
    const shouldShowForm = showForm || (!profile && !profileError);

    return (
        <div className="section-padding">
            <div className="container">
                <div className="row">
                    <div className="col-lg-8 mx-auto">
                        <div className="section-title text-center mb-5">
                            <h2>Profile Management</h2>
                        </div>
                        
                        {/* Profile Overview - Show when profile exists and form is not visible */}
                        {profile && !shouldShowForm && (
                            <div className="profile-overview">
                                <div className="card shadow-sm">
                                    <div className="card-body p-5">
                                        <div className="d-flex justify-content-between align-items-start mb-4">
                                            <h3 className="card-title mb-0">Your Profile</h3>
                                            <div>
                                                <Buttons 
                                                    onClick={() => setShowForm(true)}
                                                    title="Edit Profile"
                                                    size="sm"
                                                    themeColor="#232323"
                                                    className="btn-fill me-2"
                                                    icon="feather-edit-2"
                                                    iconPosition="before"
                                                />
                                                <Buttons 
                                                    onClick={handleDeleteProfile}
                                                    disabled={loading}
                                                    title="Delete"
                                                    size="sm"
                                                    themeColor="#dc3545"
                                                    className="btn-fill"
                                                    icon="feather-trash-2"
                                                    iconPosition="before"
                                                />
                                            </div>
                                        </div>
                                        
                                        <div className="row">
                                            <div className="col-md-3 text-center mb-4">
                                                {profile.avatar_url ? (
                                                    <img 
                                                        src={profile.avatar_url} 
                                                        alt="Profile avatar" 
                                                        className="img-fluid rounded-circle shadow-sm"
                                                        style={{ width: '120px', height: '120px', objectFit: 'cover' }}
                                                    />
                                                ) : (
                                                    <div 
                                                        className="bg-light rounded-circle d-flex align-items-center justify-content-center shadow-sm"
                                                        style={{ width: '120px', height: '120px', margin: '0 auto' }}
                                                    >
                                                        <i className="feather-user text-muted" style={{ fontSize: '40px' }}></i>
                                                    </div>
                                                )}
                                            </div>
                                            <div className="col-md-9">
                                                <div className="row">
                                                    <div className="col-md-6 mb-3">
                                                        <h6 className="text-muted mb-1">Bio</h6>
                                                        <p className="mb-0">{profile.bio || 'Not provided'}</p>
                                                    </div>
                                                    <div className="col-md-6 mb-3">
                                                        <h6 className="text-muted mb-1">Location</h6>
                                                        <p className="mb-0">{profile.location || 'Not provided'}</p>
                                                    </div>
                                                    <div className="col-md-6 mb-3">
                                                        <h6 className="text-muted mb-1">Website</h6>
                                                        <p className="mb-0">
                                                            {profile.website ? (
                                                                <a href={profile.website} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
                                                                    {profile.website}
                                                                </a>
                                                            ) : 'Not provided'}
                                                        </p>
                                                    </div>
                                                    <div className="col-md-6 mb-3">
                                                        <h6 className="text-muted mb-1">Social Links</h6>
                                                        <div className="d-flex gap-2">
                                                            {profile.twitter_handle && (
                                                                <a href={`https://twitter.com/${profile.twitter_handle.replace('@', '')}`} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
                                                                    <i className="fab fa-twitter text-primary"></i>
                                                                </a>
                                                            )}
                                                            {profile.github_handle && (
                                                                <a href={`https://github.com/${profile.github_handle}`} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
                                                                    <i className="fab fa-github text-dark"></i>
                                                                </a>
                                                            )}
                                                            {profile.linkedin_handle && (
                                                                <a href={`https://linkedin.com/in/${profile.linkedin_handle}`} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
                                                                    <i className="fab fa-linkedin text-primary"></i>
                                                                </a>
                                                            )}
                                                            {!profile.twitter_handle && !profile.github_handle && !profile.linkedin_handle && (
                                                                <span className="text-muted">None added</span>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* No Profile State - Show when no profile exists and form is not visible */}
                        {!profile && !shouldShowForm && (
                            <div className="no-profile-state">
                                <div className="card shadow-sm">
                                    <div className="card-body text-center p-5">
                                        <div className="mb-4">
                                            <i className="feather-user-plus text-muted" style={{ fontSize: '60px' }}></i>
                                        </div>
                                        <h3 className="mb-3">Complete Your Profile</h3>
                                        <p className="text-muted mb-4">
                                            Add your personal information to get started with CraftyXhub!<br/>
                                            Let others know more about you and connect with the community.
                                        </p>
                                        <Buttons 
                                            onClick={() => setShowForm(true)}
                                            title="Create Profile"
                                            size="md"
                                            themeColor="#232323"
                                            className="btn-fill"
                                            icon="feather-plus-circle"
                                            iconPosition="before"
                                        />
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Profile Form - Show when editing/creating */}
                        {shouldShowForm && (
                            <div className="profile-form">
                                <div className="card shadow-sm">
                                    <div className="card-body p-5">
                                        <div className="d-flex justify-content-between align-items-center mb-4">
                                            <div>
                                                <h3 className="card-title mb-1">{profile ? 'Update Profile' : 'Create Your Profile'}</h3>
                                                {!profile && (
                                                    <p className="text-muted mb-0">Complete your profile to get started with CraftyXhub!</p>
                                                )}
                                            </div>
                                            {profile && (
                                                <Buttons 
                                                    onClick={() => setShowForm(false)}
                                                    title="Cancel"
                                                    size="sm"
                                                    themeColor="#6c757d"
                                                    className="btn-fill"
                                                    icon="feather-x"
                                                    iconPosition="before"
                                                />
                                            )}
                                        </div>
                                        
                                        <Formik
                                            enableReinitialize={true}
                                            initialValues={getInitialValues()}
                                            validationSchema={ProfileSchema}
                                            onSubmit={handleSubmit}
                                        >
                                            {({ isSubmitting }) => (
                                                <Form>
                                                    <div className="row">
                                                        <div className="col-12 mb-4">
                                                            <TextArea
                                                                name="bio"
                                                                label="Bio"
                                                                className="form-control"
                                                                placeholder="Tell us about yourself..."
                                                                rows="4"
                                                            />
                                                        </div>

                                                        <div className="col-md-6 mb-4">
                                                            <Input
                                                                type="text"
                                                                name="location"
                                                                label="Location"
                                                                className="form-control"
                                                                placeholder="City, Country"
                                                            />
                                                        </div>

                                                        <div className="col-md-6 mb-4">
                                                            <Input
                                                                type="url"
                                                                name="website"
                                                                label="Website"
                                                                className="form-control"
                                                                placeholder="https://yourwebsite.com"
                                                            />
                                                        </div>

                                                        <div className="col-md-4 mb-4">
                                                            <Input
                                                                type="text"
                                                                name="twitter_handle"
                                                                label="Twitter Handle"
                                                                className="form-control"
                                                                placeholder="@username"
                                                            />
                                                        </div>

                                                        <div className="col-md-4 mb-4">
                                                            <Input
                                                                type="text"
                                                                name="github_handle"
                                                                label="GitHub Handle"
                                                                className="form-control"
                                                                placeholder="username"
                                                            />
                                                        </div>

                                                        <div className="col-md-4 mb-4">
                                                            <Input
                                                                type="text"
                                                                name="linkedin_handle"
                                                                label="LinkedIn Handle"
                                                                className="form-control"
                                                                placeholder="username"
                                                            />
                                                        </div>

                                                        <div className="col-md-6 mb-4">
                                                            <Input
                                                                type="date"
                                                                name="birth_date"
                                                                label="Birth Date"
                                                                className="form-control"
                                                            />
                                                        </div>

                                                        <div className="col-md-6 mb-4">
                                                            <label className="form-label">Avatar</label>
                                                            <input
                                                                type="file"
                                                                accept="image/*"
                                                                onChange={handleFileChange}
                                                                className="form-control"
                                                            />
                                                        </div>
                                                    </div>

                                                    <div className="text-center">
                                                        <Buttons 
                                                            type="submit" 
                                                            disabled={loading || isSubmitting}
                                                            title={loading || isSubmitting ? 'Saving...' : (profile ? 'Update Profile' : 'Create Profile')}
                                                            size="md"
                                                            themeColor="#232323"
                                                            className="btn-fill"
                                                            icon={loading || isSubmitting ? "feather-loader" : "feather-save"}
                                                            iconPosition="before"
                                                        />
                                                    </div>
                                                </Form>
                                            )}
                                        </Formik>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Status Messages */}
                        <div className="mt-4">
                            {success && (
                                <div className="alert alert-success text-center">
                                    <i className="feather-check-circle me-2"></i>
                                    Profile operation completed successfully!
                                </div>
                            )}
                            
                            {error && (
                                <div className="alert alert-danger text-center">
                                    <i className="feather-alert-circle me-2"></i>
                                    Error: {error}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfileManagement; 