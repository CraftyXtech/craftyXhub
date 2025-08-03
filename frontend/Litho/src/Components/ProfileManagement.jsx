import React, { useState } from 'react';
import { useProfile } from '../api';
import { createProfile, updateProfile, deleteProfile } from '../api/postsService';
import Buttons from './Button/Buttons';
import { Input, TextArea } from './Form/Form';

const ProfileManagement = ({ userUuid }) => {
    const [formData, setFormData] = useState({
        bio: '',
        location: '',
        website: '',
        twitter_handle: '',
        github_handle: '',
        linkedin_handle: '',
        birth_date: '',
        avatar: null
    });

    // State for operations
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    
    // Get profile data
    const { profile, loading: profileLoading, error: profileError, refetch } = useProfile(userUuid);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleFileChange = (e) => {
        setFormData(prev => ({
            ...prev,
            avatar: e.target.files[0]
        }));
    };

    const handleCreateProfile = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            setError(null);
            await createProfile(formData);
            setSuccess(true);
            // Refresh the profile data after creation
            refetch();
        } catch (error) {
            console.error('Failed to create profile:', error);
            setError(error.message || 'Failed to create profile');
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            setError(null);
            await updateProfile(userUuid, formData);
            setSuccess(true);
            // Refresh the profile data after update
            refetch();
        } catch (error) {
            console.error('Failed to update profile:', error);
            setError(error.message || 'Failed to update profile');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteProfile = async () => {
        if (window.confirm('Are you sure you want to delete your profile? This action cannot be undone.')) {
            try {
                setLoading(true);
                setError(null);
                await deleteProfile(userUuid);
                setSuccess(true);
                // Refresh the profile data after deletion
                refetch();
            } catch (error) {
                console.error('Failed to delete profile:', error);
                setError(error.message || 'Failed to delete profile');
            } finally {
                setLoading(false);
            }
        }
    };

    // Populate form with existing profile data
    React.useEffect(() => {
        if (profile) {
            setFormData({
                bio: profile.bio || '',
                location: profile.location || '',
                website: profile.website || '',
                twitter_handle: profile.twitter_handle || '',
                github_handle: profile.github_handle || '',
                linkedin_handle: profile.linkedin_handle || '',
                birth_date: profile.birth_date || '',
                avatar: null
            });
        }
    }, [profile]);

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
    
    if (profileError) return (
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

    return (
        <div className="section-padding">
            <div className="container">
                <div className="row">
                    <div className="col-lg-8 mx-auto">
                        <div className="section-title text-center mb-5">
                            <h2>Profile Management</h2>
                        </div>
                        
                        {/* Display current profile */}
                        {profile && (
                            <div className="current-profile mb-5">
                                <div className="card">
                                    <div className="card-body">
                                        <h3 className="card-title mb-4">Current Profile</h3>
                                        <div className="row">
                                            <div className="col-md-3 text-center">
                                                {profile.avatar_url && (
                                                    <img 
                                                        src={profile.avatar_url} 
                                                        alt="Profile avatar" 
                                                        className="img-fluid rounded-circle mb-3"
                                                        style={{ width: '100px', height: '100px', objectFit: 'cover' }}
                                                    />
                                                )}
                                            </div>
                                            <div className="col-md-9">
                                                <p><strong>Bio:</strong> {profile.bio || 'Not set'}</p>
                                                <p><strong>Location:</strong> {profile.location || 'Not set'}</p>
                                                <p><strong>Website:</strong> {profile.website || 'Not set'}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Profile Form */}
                        <div className="card">
                            <div className="card-body">
                                <form onSubmit={profile ? handleUpdateProfile : handleCreateProfile}>
                                    <div className="row">
                                        <div className="col-12 mb-4">
                                            <TextArea
                                                name="bio"
                                                label="Bio"
                                                className="form-control"
                                                placeholder="Tell us about yourself..."
                                                value={formData.bio}
                                                onChange={handleInputChange}
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
                                                value={formData.location}
                                                onChange={handleInputChange}
                                            />
                                        </div>

                                        <div className="col-md-6 mb-4">
                                            <Input
                                                type="url"
                                                name="website"
                                                label="Website"
                                                className="form-control"
                                                placeholder="https://yourwebsite.com"
                                                value={formData.website}
                                                onChange={handleInputChange}
                                            />
                                        </div>

                                        <div className="col-md-4 mb-4">
                                            <Input
                                                type="text"
                                                name="twitter_handle"
                                                label="Twitter Handle"
                                                className="form-control"
                                                placeholder="@username"
                                                value={formData.twitter_handle}
                                                onChange={handleInputChange}
                                            />
                                        </div>

                                        <div className="col-md-4 mb-4">
                                            <Input
                                                type="text"
                                                name="github_handle"
                                                label="GitHub Handle"
                                                className="form-control"
                                                placeholder="username"
                                                value={formData.github_handle}
                                                onChange={handleInputChange}
                                            />
                                        </div>

                                        <div className="col-md-4 mb-4">
                                            <Input
                                                type="text"
                                                name="linkedin_handle"
                                                label="LinkedIn Handle"
                                                className="form-control"
                                                placeholder="username"
                                                value={formData.linkedin_handle}
                                                onChange={handleInputChange}
                                            />
                                        </div>

                                        <div className="col-md-6 mb-4">
                                            <Input
                                                type="date"
                                                name="birth_date"
                                                label="Birth Date"
                                                className="form-control"
                                                value={formData.birth_date}
                                                onChange={handleInputChange}
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
                                            disabled={loading}
                                            title={profile ? 'Update Profile' : 'Create Profile'}
                                            size="md"
                                            themeColor="#007bff"
                                            className="btn-fill me-3"
                                        />
                                    </div>
                                </form>

                                {/* Delete Profile Button */}
                                {profile && (
                                    <div className="text-center mt-4">
                                        <Buttons 
                                            onClick={handleDeleteProfile}
                                            disabled={loading}
                                            title="Delete Profile"
                                            size="md"
                                            themeColor="#dc3545"
                                            className="btn-fill"
                                        />
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Status Messages */}
                        <div className="mt-4">
                            {success && (
                                <div className="alert alert-success text-center">
                                    Profile operation completed successfully!
                                </div>
                            )}
                            
                            {error && (
                                <div className="alert alert-danger text-center">
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