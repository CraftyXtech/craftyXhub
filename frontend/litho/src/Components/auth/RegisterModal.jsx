import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Modal, Form, Alert } from 'react-bootstrap'
import { m } from "framer-motion"
import Buttons from '../Button/Buttons'
import useAuth from '../../api/useAuth'
import { axiosInstance } from '../../api/axios'
import { fadeIn } from '../../Functions/GlobalAnimations'
const RegisterModal = ({ show, onHide, onSwitchToLogin }) => {
    const [formData, setFormData] = useState({
        full_name: '',
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    })
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    const [showConfirmPassword, setShowConfirmPassword] = useState(false)
    
    const { login } = useAuth()
    const navigate = useNavigate()

    const handleInputChange = (e) => {
        const { name, value } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: value
        }))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        // Validate username format
        const usernamePattern = /^[a-zA-Z0-9_-]+$/;
        if (!usernamePattern.test(formData.username)) {
            setError('Username can only contain letters, numbers, underscores (_), and hyphens (-). No spaces or special characters allowed.')
            setLoading(false)
            return
        }

        // Validate username length
        if (formData.username.length < 3) {
            setError('Username must be at least 3 characters long')
            setLoading(false)
            return
        }

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match')
            setLoading(false)
            return
        }

        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters long')
            setLoading(false)
            return
        }

        try {
            await axiosInstance.post('/auth/register', {
                full_name: formData.full_name,
                username: formData.username,
                email: formData.email,
                password: formData.password,
                confirm_password: formData.confirmPassword,
                role: 'user'
            })

            const loginResponse = await axiosInstance.post('/auth/login', {
                email: formData.email,
                password: formData.password
            })

            const token = loginResponse.data.access_token

            const userResponse = await axiosInstance.get('/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            login(token, userResponse.data)
            onHide()
            setFormData({
                full_name: '',
                username: '',
                email: '',
                password: '',
                confirmPassword: ''
            })
            setError('')
            
            // Redirect to user dashboard
            navigate('/dashboard')
        } catch (error) {
            console.error('Registration error:', error)
            let errorMessage = "Registration failed. Please try again."
            
            if (error.response?.data?.detail) {
                if (Array.isArray(error.response.data.detail)) {
                    // Handle validation errors from FastAPI
                    const errors = error.response.data.detail.map(err => {
                        const msg = err.msg || err.message || 'Validation error';
                        const field = err.loc ? err.loc[err.loc.length - 1] : '';
                        
                        // Make username pattern errors user-friendly
                        if (msg.includes("String should match pattern") && field === 'username') {
                            return 'Username can only contain letters, numbers, underscores (_), and hyphens (-). No spaces or special characters allowed.';
                        }
                        
                        // Make other validation errors friendly
                        if (msg.includes('value is not a valid email')) {
                            return 'Please enter a valid email address.';
                        }
                        
                        if (msg.includes('ensure this value has at least')) {
                            return `${field} is too short. ${msg}`;
                        }
                        
                        if (msg.includes('field required')) {
                            return `${field} is required.`;
                        }
                        
                        return msg;
                    });
                    errorMessage = errors.join(' ');
                } else if (typeof error.response.data.detail === 'string') {
                    errorMessage = error.response.data.detail;
                    
                    // Check if it's a common error and make it friendly
                    if (errorMessage.includes('already registered') || errorMessage.includes('already exists')) {
                        if (errorMessage.toLowerCase().includes('email')) {
                            errorMessage = 'This email is already registered. Please login or use a different email.';
                        } else if (errorMessage.toLowerCase().includes('username')) {
                            errorMessage = 'This username is already taken. Please choose a different one.';
                        }
                    }
                }
            } else if (error.response?.data?.message) {
                errorMessage = error.response.data.message
            } else if (error.message) {
                errorMessage = error.message
            }
            
            setError(errorMessage)
        } finally {
            setLoading(false)
        }
    }

    const handleClose = () => {
        setFormData({
            full_name: '',
            username: '',
            email: '',
            password: '',
            confirmPassword: ''
        })
        setError('')
        setShowPassword(false)
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
                    Join CraftyXhub!
                </Modal.Title>
            </Modal.Header>
            <Modal.Body className="px-4 pb-4 max-h-[70vh] overflow-y-auto">
                <m.div {...fadeIn}>
                    <div className="text-center mb-[25px]">
                        <p className="text-lg mb-0 text-[#666]">Create your account to start exploring</p>
                    </div>

                    {error && (
                        <Alert variant="danger" className="mb-[20px] text-sm">
                            <i className="feather-alert-circle mr-[8px]"></i>
                            {error}
                        </Alert>
                    )}

                    <Form onSubmit={handleSubmit}>
                        <div className="mb-[15px]">
                            <label className="text-sm font-medium text-darkgray mb-[8px] block">
                                Full Name *
                            </label>
                            <input
                                className="py-[10px] px-[12px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-darkgray focus:outline-none"
                                type="text"
                                name="full_name"
                                placeholder="Enter your full name"
                                value={formData.full_name}
                                onChange={handleInputChange}
                                required
                            />
                        </div>
                        <div className="mb-[15px]">
                            <label className="text-sm font-medium text-darkgray mb-[8px] block">
                                Username *
                            </label>
                            <input
                                className="py-[10px] px-[12px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-darkgray focus:outline-none"
                                type="text"
                                name="username"
                                placeholder="e.g. john_doe or john-doe123"
                                value={formData.username}
                                onChange={handleInputChange}
                                pattern="[a-zA-Z0-9_-]+"
                                title="Only letters, numbers, underscores, and hyphens allowed"
                                required
                            />
                            <small className="text-xs text-gray-500 mt-1 block">
                                Only letters, numbers, underscores (_), and hyphens (-) allowed. No spaces.
                            </small>
                        </div>
                        <div className="mb-[15px]">
                            <label className="text-sm font-medium text-darkgray mb-[8px] block">
                                Email Address *
                            </label>
                            <input
                                className="py-[10px] px-[12px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-darkgray focus:outline-none"
                                type="email"
                                name="email"
                                placeholder="Enter your email"
                                value={formData.email}
                                onChange={handleInputChange}
                                required
                            />
                        </div>
                        <div className="mb-[15px]">
                            <label className="text-sm font-medium text-darkgray mb-[8px] block">
                                Password *
                            </label>
                            <div className="relative">
                                <input
                                    className="py-[10px] px-[12px] pr-[40px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-darkgray focus:outline-none"
                                    type={showPassword ? "text" : "password"}
                                    name="password"
                                    placeholder="Create a password"
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    required
                                />
                                <button
                                    type="button"
                                    className="absolute right-[10px] top-1/2 transform -translate-y-1/2 text-[#666] hover:text-darkgray"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                    <i className={showPassword ? "feather-eye-off" : "feather-eye"}></i>
                                </button>
                            </div>
                            <p className="text-xs text-[#666] mt-[5px]">At least 6 characters</p>
                        </div>
                        <div className="mb-[15px]">
                            <label className="text-sm font-medium text-darkgray mb-[8px] block">
                                Confirm Password *
                            </label>
                            <div className="relative">
                                <input
                                    className="py-[10px] px-[12px] pr-[40px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-darkgray focus:outline-none"
                                    type={showConfirmPassword ? "text" : "password"}
                                    name="confirmPassword"
                                    placeholder="Confirm your password"
                                    value={formData.confirmPassword}
                                    onChange={handleInputChange}
                                    required
                                />
                                <button
                                    type="button"
                                    className="absolute right-[10px] top-1/2 transform -translate-y-1/2 text-[#666] hover:text-darkgray"
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                >
                                    <i className={showConfirmPassword ? "feather-eye-off" : "feather-eye"}></i>
                                </button>
                            </div>
                        </div>
                        <div className="mb-[20px]">
                            <label className="flex items-start cursor-pointer">
                                <input type="checkbox" className="mr-[8px] mt-[2px]" required />
                                <span className="text-xs">
                                    I agree to the {" "}
                                    <Link 
                                        to="/privacy" 
                                        className="hover:text-darkgray underline decoration-[1px] underline-offset-[4px]"
                                        onClick={handleClose}
                                    >
                                        Terms of Service
                                    </Link>
                                    {" "} and {" "}
                                    <Link 
                                        to="/privacy" 
                                        className="hover:text-darkgray underline decoration-[1px] underline-offset-[4px]"
                                        onClick={handleClose}
                                    >
                                        Privacy Policy
                                    </Link>
                                </span>
                            </label>
                        </div>
                        <div className="mb-[15px]">
                            <Buttons
                                type="submit"
                                className={`btn-fill btn-fancy font-medium tracking-[1px] rounded-[4px] uppercase w-full ${loading ? 'opacity-75 cursor-not-allowed' : ''}`}
                                themeColor="#232323"
                                color="#fff"
                                size="md"
                                title={loading ? "Creating Account..." : "Create Account"}
                                disabled={loading}
                            />
                        </div>
                        <div className="text-center">
                            <p className="text-sm mb-0">
                                Already have an account? {" "}
                                <button
                                    type="button"
                                    onClick={onSwitchToLogin}
                                    className="font-medium hover:text-darkgray underline decoration-[1px] underline-offset-[4px] bg-transparent border-0 p-0"
                                >
                                    Sign In
                                </button>
                            </p>
                        </div>
                    </Form>
                </m.div>
            </Modal.Body>
        </Modal>
    )
}

export default RegisterModal 