import React, { useState } from 'react'
import { Modal, Form, Alert } from 'react-bootstrap'
import { m } from "framer-motion"
import Buttons from '../Button/Buttons'
import useAuth from '../../api/useAuth'
import { axiosPrivate } from '../../api/axios'
import { fadeIn } from '../../Functions/GlobalAnimations'

const PasswordResetModal = ({ show, onHide, onSwitchToLogin }) => {
    const [formData, setFormData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmNewPassword: ''
    })
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const [showCurrentPassword, setShowCurrentPassword] = useState(false)
    const [showNewPassword, setShowNewPassword] = useState(false)
    const [showConfirmPassword, setShowConfirmPassword] = useState(false)
    
    const { updateUser } = useAuth()

    const handleInputChange = (e) => {
        const { name, value } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: value
        }))
        // Clear errors when user starts typing
        if (error) setError('')
        if (success) setSuccess('')
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        setSuccess('')

        // Validation
        if (formData.newPassword !== formData.confirmNewPassword) {
            setError('New passwords do not match')
            setLoading(false)
            return
        }

        if (formData.newPassword.length < 6) {
            setError('New password must be at least 6 characters long')
            setLoading(false)
            return
        }

        if (formData.newPassword === formData.currentPassword) {
            setError('New password must be different from current password')
            setLoading(false)
            return
        }

        try {
            await axiosPrivate.put('/auth/reset-password', {
                current_password: formData.currentPassword,
                new_password: formData.newPassword,
                confirm_new_password: formData.confirmNewPassword
            })

            setSuccess('Password updated successfully! You can now use your new password.')
            setFormData({
                currentPassword: '',
                newPassword: '',
                confirmNewPassword: ''
            })

            // Auto-close modal after 2 seconds on success
            setTimeout(() => {
                handleClose()
            }, 2000)
            
        } catch (error) {
            console.error('Password reset error:', error)
            const errorMessage = error.response?.data?.detail || 
                              error.response?.data?.message || 
                              error.message || 
                              "Failed to update password. Please try again."
            setError(errorMessage)
        } finally {
            setLoading(false)
        }
    }

    const handleClose = () => {
        setFormData({
            currentPassword: '',
            newPassword: '',
            confirmNewPassword: ''
        })
        setError('')
        setSuccess('')
        setShowCurrentPassword(false)
        setShowNewPassword(false)
        setShowConfirmPassword(false)
        onHide()
    }

    return (
        <Modal 
            show={show} 
            onHide={handleClose}
            centered
            size="md"
            className="custom-modal"
        >
            <Modal.Header closeButton className="border-0 pb-0">
                <Modal.Title className="font-serif text-darkgray font-medium">
                    Change Password
                </Modal.Title>
            </Modal.Header>
            <Modal.Body className="px-4 pb-4">
                <m.div {...fadeIn}>
                    <div className="text-center mb-[25px]">
                        <p className="text-lg mb-0 text-[#666]">Update your account password</p>
                    </div>

                    {error && (
                        <Alert variant="danger" className="mb-[20px] text-sm">
                            <i className="feather-alert-circle mr-[8px]"></i>
                            {error}
                        </Alert>
                    )}

                    {success && (
                        <Alert variant="success" className="mb-[20px] text-sm">
                            <i className="feather-check-circle mr-[8px]"></i>
                            {success}
                        </Alert>
                    )}

                    <Form onSubmit={handleSubmit}>
                        <div className="mb-[20px]">
                            <label className="text-sm font-medium text-darkgray mb-[10px] block">
                                Current Password *
                            </label>
                            <div className="relative">
                                <input
                                    className="py-[12px] px-[15px] pr-[45px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-darkgray focus:outline-none"
                                    type={showCurrentPassword ? "text" : "password"}
                                    name="currentPassword"
                                    placeholder="Enter your current password"
                                    value={formData.currentPassword}
                                    onChange={handleInputChange}
                                    required
                                />
                                <button
                                    type="button"
                                    className="absolute right-[12px] top-1/2 transform -translate-y-1/2 text-[#666] hover:text-darkgray"
                                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                                >
                                    <i className={showCurrentPassword ? "feather-eye-off" : "feather-eye"}></i>
                                </button>
                            </div>
                        </div>

                        <div className="mb-[20px]">
                            <label className="text-sm font-medium text-darkgray mb-[10px] block">
                                New Password *
                            </label>
                            <div className="relative">
                                <input
                                    className="py-[12px] px-[15px] pr-[45px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-darkgray focus:outline-none"
                                    type={showNewPassword ? "text" : "password"}
                                    name="newPassword"
                                    placeholder="Enter your new password"
                                    value={formData.newPassword}
                                    onChange={handleInputChange}
                                    required
                                />
                                <button
                                    type="button"
                                    className="absolute right-[12px] top-1/2 transform -translate-y-1/2 text-[#666] hover:text-darkgray"
                                    onClick={() => setShowNewPassword(!showNewPassword)}
                                >
                                    <i className={showNewPassword ? "feather-eye-off" : "feather-eye"}></i>
                                </button>
                            </div>
                            <p className="text-xs text-[#666] mt-[5px]">At least 6 characters</p>
                        </div>

                        <div className="mb-[20px]">
                            <label className="text-sm font-medium text-darkgray mb-[10px] block">
                                Confirm New Password *
                            </label>
                            <div className="relative">
                                <input
                                    className="py-[12px] px-[15px] pr-[45px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-darkgray focus:outline-none"
                                    type={showConfirmPassword ? "text" : "password"}
                                    name="confirmNewPassword"
                                    placeholder="Confirm your new password"
                                    value={formData.confirmNewPassword}
                                    onChange={handleInputChange}
                                    required
                                />
                                <button
                                    type="button"
                                    className="absolute right-[12px] top-1/2 transform -translate-y-1/2 text-[#666] hover:text-darkgray"
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                >
                                    <i className={showConfirmPassword ? "feather-eye-off" : "feather-eye"}></i>
                                </button>
                            </div>
                        </div>

                        <div className="mb-[20px]">
                            <Buttons
                                type="submit"
                                className={`btn-fill btn-fancy font-medium tracking-[1px] rounded-[4px] uppercase w-full ${loading ? 'opacity-75 cursor-not-allowed' : ''}`}
                                themeColor="#232323"
                                color="#fff"
                                size="md"
                                title={loading ? "Updating Password..." : "Update Password"}
                                disabled={loading || success}
                            />
                        </div>

                        {onSwitchToLogin && (
                            <div className="text-center">
                                <p className="text-sm mb-0">
                                    Want to go back? {" "}
                                    <button
                                        type="button"
                                        onClick={onSwitchToLogin}
                                        className="font-medium hover:text-darkgray underline decoration-[1px] underline-offset-[4px] bg-transparent border-0 p-0"
                                    >
                                        Back to Login
                                    </button>
                                </p>
                            </div>
                        )}
                    </Form>
                </m.div>
            </Modal.Body>
        </Modal>
    )
}

export default PasswordResetModal