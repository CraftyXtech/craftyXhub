import React, { useState } from 'react';
import { useProfile, useCreateProfile, useUpdateProfile, useDeleteProfile } from '../api';
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

    // Hooks for different operations
    const { profile, loading: profileLoading, error: profileError, refetch } = useProfile(userUuid);
    const { createProfile, loading: createLoading, error: createError, success: createSuccess } = useCreateProfile();
    const { updateProfile, loading: updateLoading, error: updateError, success: updateSuccess } = useUpdateProfile();
    const { deleteProfile, loading: deleteLoading, error: deleteError, success: deleteSuccess } = useDeleteProfile();

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
            await createProfile(formData);
            // Refresh the profile data after creation
            refetch();
        } catch (error) {
            console.error('Failed to create profile:', error);
        }
    };

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        try {
            await updateProfile(userUuid, formData);
            // Refresh the profile data after update
            refetch();
        } catch (error) {
            console.error('Failed to update profile:', error);
        }
    };

    const handleDeleteProfile = async () => {
        if (window.confirm('Are you sure you want to delete your profile? This action cannot be undone.')) {
            try {
                await deleteProfile(userUuid);
                // You might want to redirect or show a message
                alert('Profile deleted successfully');
            } catch (error) {
                console.error('Failed to delete profile:', error);
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
                                            disabled={createLoading || updateLoading}
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
                                            disabled={deleteLoading}
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
                            {createSuccess && (
                                <div className="alert alert-success text-center">
                                    Profile created successfully!
                                </div>
                            )}
                            {updateSuccess && (
                                <div className="alert alert-success text-center">
                                    Profile updated successfully!
                                </div>
                            )}
                            {deleteSuccess && (
                                <div className="alert alert-success text-center">
                                    Profile deleted successfully!
                                </div>
                            )}
                            
                            {createError && (
                                <div className="alert alert-danger text-center">
                                    Error creating profile: {createError}
                                </div>
                            )}
                            {updateError && (
                                <div className="alert alert-danger text-center">
                                    Error updating profile: {updateError}
                                </div>
                            )}
                            {deleteError && (
                                <div className="alert alert-danger text-center">
                                    Error deleting profile: {deleteError}
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