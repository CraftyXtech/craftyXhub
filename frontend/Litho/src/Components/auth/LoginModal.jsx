import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Modal, Form, Alert } from 'react-bootstrap'
import { m } from "framer-motion"
import Buttons from '../Button/Buttons'
import useAuth from '../../api/useAuth'
import { axiosInstance } from '../../api/axios'
import { fadeIn } from '../../Functions/GlobalAnimations'

const LoginModal = ({ show, onHide, onSwitchToRegister, onSwitchToPasswordReset }) => {
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    })
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    
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

        try {
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
            setFormData({ email: '', password: '' })
            setError('')
        } catch (error) {
            console.error('Login error:', error)
            let errorMessage = "Login failed. Please check your credentials."
            
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
        setFormData({ email: '', password: '' })
        setError('')
        setShowPassword(false)
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
                    Welcome Back!
                </Modal.Title>
            </Modal.Header>
            <Modal.Body className="px-4 pb-4">
                <m.div {...fadeIn}>
                    <div className="text-center mb-[30px]">
                        <p className="text-lg mb-0 text-[#666]">Sign in to your CraftyXhub account</p>
                    </div>

                    {error && (
                        <Alert variant="danger" className="mb-[20px] text-sm">
                            <i className="feather-alert-circle mr-[8px]"></i>
                            {error}
                        </Alert>
                    )}

                    <Form onSubmit={handleSubmit}>
                        <div className="mb-[20px]">
                            <label className="text-sm font-medium text-darkgray mb-[10px] block">
                                Email Address *
                            </label>
                            <input
                                className="py-[12px] px-[15px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-darkgray focus:outline-none"
                                type="email"
                                name="email"
                                placeholder="Enter your email"
                                value={formData.email}
                                onChange={handleInputChange}
                                required
                            />
                        </div>
                        <div className="mb-[20px]">
                            <label className="text-sm font-medium text-darkgray mb-[10px] block">
                                Password *
                            </label>
                            <div className="relative">
                                <input
                                    className="py-[12px] px-[15px] pr-[45px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-darkgray focus:outline-none"
                                    type={showPassword ? "text" : "password"}
                                    name="password"
                                    placeholder="Enter your password"
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    required
                                />
                                <button
                                    type="button"
                                    className="absolute right-[12px] top-1/2 transform -translate-y-1/2 text-[#666] hover:text-darkgray"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                    <i className={showPassword ? "feather-eye-off" : "feather-eye"}></i>
                                </button>
                            </div>
                        </div>
                        <div className="mb-[20px]">
                            <div className="flex justify-between items-center">
                                <label className="flex items-center cursor-pointer">
                                    <input type="checkbox" className="mr-[8px]" />
                                    <span className="text-sm">Remember me</span>
                                </label>
                                <button
                                    type="button"
                                    onClick={onSwitchToPasswordReset}
                                    className="text-sm hover:text-darkgray bg-transparent border-0 p-0 underline decoration-[1px] underline-offset-[4px]"
                                >
                                    Change Password
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
                                title={loading ? "Signing In..." : "Sign In"}
                                disabled={loading}
                            />
                        </div>
                        <div className="text-center">
                            <p className="text-sm mb-0">
                                Don't have an account? {" "}
                                <button
                                    type="button"
                                    onClick={onSwitchToRegister}
                                    className="font-medium hover:text-darkgray underline decoration-[1px] underline-offset-[4px] bg-transparent border-0 p-0"
                                >
                                    Create Account
                                </button>
                            </p>
                        </div>
                    </Form>
                </m.div>
            </Modal.Body>
        </Modal>
    )
}

export default LoginModal 