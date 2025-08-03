import React, { useState } from 'react'
import { Link } from 'react-router-dom'
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
        } catch (error) {
            console.error('Registration error:', error)
            let errorMessage = "Registration failed. Please try again."
            
            if (error.response?.data?.detail) {
                if (Array.isArray(error.response.data.detail)) {
                    // Handle validation errors from FastAPI
                    errorMessage = error.response.data.detail
                        .map(err => err.msg || err.message || 'Validation error')
                        .join(', ')
                } else if (typeof error.response.data.detail === 'string') {
                    errorMessage = error.response.data.detail
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
                                placeholder="Choose a username"
                                value={formData.username}
                                onChange={handleInputChange}
                                required
                            />
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