import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Col, Container, Row, Navbar, Form, Alert } from 'react-bootstrap'
import { m } from "framer-motion"

// Components
import Header, { HeaderNav, Menu } from '../../Components/Header/Header'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'
import Buttons from '../../Components/Button/Buttons'
import SideButtons from "../../Components/SideButtons"
import useAuth from '../../api/useAuth'
import { axiosInstance } from '../../api'
import Logo from '../../Components/Logo'

import { fadeIn } from '../../Functions/GlobalAnimations'

const Register = (props) => {
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
            const registerResponse = await axiosInstance.post('/auth/register', {
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
            
            navigate('/dashboard')
        } catch (error) {
            console.error('Registration error:', error)
            let errorMessage = "Registration failed. Please try again."
            
            if (error.response?.data?.detail) {
                if (Array.isArray(error.response.data.detail)) {
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

    return (
        <div style={props.style}>
            <SideButtons />
            
            {/* Header Start */}
            <Header topSpace={{ desktop: true }} type="reverse-scroll">
                <HeaderNav bg="white" theme="light" expand="lg" className="py-[0px] lg:px-[15px] md:px-0">
                    <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                        <Logo className="flex items-center" />
                    </Col>
                    <div className="col-auto hidden order-last md:block">
                        <Navbar.Toggle className="md:ml-[10px] sm:ml-0">
                            <span className="navbar-toggler-line"></span>
                            <span className="navbar-toggler-line"></span>
                            <span className="navbar-toggler-line"></span>
                            <span className="navbar-toggler-line"></span>
                        </Navbar.Toggle>
                    </div>
                    <Navbar.Collapse className="col-auto p-0 justify-end">
                        <Menu />
                    </Navbar.Collapse>
                </HeaderNav>
            </Header>
            {/* Header End */}

            {/* Page Title Section Start */}
            <section className="bg-darkgray py-[25px]">
                <Container>
                    <Row className="items-center justify-center">
                        <Col xl={8} lg={6}>
                            <h1 className="font-serif text-white font-medium mb-0 md:text-center text-lg">Create Account</h1>
                        </Col>
                        <Col xl={4} lg={6} className="breadcrumb justify-end text-xs font-serif md:mt-[10px] mb-0 md:justify-center">
                            <ul className="xs-text-center">
                                <li><Link aria-label="breadcrumb" to="/" className="hover:text-white">Home</Link></li>
                                <li>Register</li>
                            </ul>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Page Title Section End */}

            {/* Register Form Section Start */}
            <section className="py-[160px] lg:py-[120px] md:py-[95px] sm:py-[80px] xs:py-[50px]">
                <Container>
                    <Row className="justify-center">
                        <Col lg={6} md={8} sm={10}>
                            <m.div 
                                className="bg-white shadow-[0_0_30px_rgba(0,0,0,0.1)] rounded-[6px] p-[50px] lg:p-[35px] md:p-[30px] sm:p-[25px]"
                                {...fadeIn}
                            >
                                <div className="text-center mb-[40px]">
                                    <h3 className="font-serif text-darkgray font-medium mb-[15px]">Join CraftyXhub!</h3>
                                    <p className="text-lg mb-0">Create your account to start exploring</p>
                                </div>

                                {error && (
                                    <Alert variant="danger" className="mb-[25px] text-sm">
                                        <i className="feather-alert-circle mr-[8px]"></i>
                                        {error}
                                    </Alert>
                                )}

                                <Form onSubmit={handleSubmit}>
                                    <Row>
                                        <Col xs={12} className="mb-[25px]">
                                            <label className="text-md font-medium text-darkgray mb-[15px] block">
                                                Full Name *
                                            </label>
                                            <input
                                                className="py-[15px] px-[20px] w-full border-[1px] border-solid border-[#dfdfdf] text-md rounded-[4px] focus:border-darkgray focus:outline-none"
                                                type="text"
                                                name="full_name"
                                                placeholder="Enter your full name"
                                                value={formData.full_name}
                                                onChange={handleInputChange}
                                                required
                                            />
                                        </Col>
                                        <Col xs={12} className="mb-[25px]">
                                            <label className="text-md font-medium text-darkgray mb-[15px] block">
                                                Username *
                                            </label>
                                            <input
                                                className="py-[15px] px-[20px] w-full border-[1px] border-solid border-[#dfdfdf] text-md rounded-[4px] focus:border-darkgray focus:outline-none"
                                                type="text"
                                                name="username"
                                                placeholder="Choose a username"
                                                value={formData.username}
                                                onChange={handleInputChange}
                                                required
                                            />
                                        </Col>
                                        <Col xs={12} className="mb-[25px]">
                                            <label className="text-md font-medium text-darkgray mb-[15px] block">
                                                Email Address *
                                            </label>
                                            <input
                                                className="py-[15px] px-[20px] w-full border-[1px] border-solid border-[#dfdfdf] text-md rounded-[4px] focus:border-darkgray focus:outline-none"
                                                type="email"
                                                name="email"
                                                placeholder="Enter your email"
                                                value={formData.email}
                                                onChange={handleInputChange}
                                                required
                                            />
                                        </Col>
                                        <Col xs={12} className="mb-[25px]">
                                            <label className="text-md font-medium text-darkgray mb-[15px] block">
                                                Password *
                                            </label>
                                            <div className="relative">
                                                <input
                                                    className="py-[15px] px-[20px] pr-[50px] w-full border-[1px] border-solid border-[#dfdfdf] text-md rounded-[4px] focus:border-darkgray focus:outline-none"
                                                    type={showPassword ? "text" : "password"}
                                                    name="password"
                                                    placeholder="Create a password"
                                                    value={formData.password}
                                                    onChange={handleInputChange}
                                                    required
                                                />
                                                <button
                                                    type="button"
                                                    className="absolute right-[15px] top-1/2 transform -translate-y-1/2 text-[#666] hover:text-darkgray"
                                                    onClick={() => setShowPassword(!showPassword)}
                                                >
                                                    <i className={showPassword ? "feather-eye-off" : "feather-eye"}></i>
                                                </button>
                                            </div>
                                            <p className="text-xs text-[#666] mt-[8px]">Password must be at least 6 characters long</p>
                                        </Col>
                                        <Col xs={12} className="mb-[25px]">
                                            <label className="text-md font-medium text-darkgray mb-[15px] block">
                                                Confirm Password *
                                            </label>
                                            <div className="relative">
                                                <input
                                                    className="py-[15px] px-[20px] pr-[50px] w-full border-[1px] border-solid border-[#dfdfdf] text-md rounded-[4px] focus:border-darkgray focus:outline-none"
                                                    type={showConfirmPassword ? "text" : "password"}
                                                    name="confirmPassword"
                                                    placeholder="Confirm your password"
                                                    value={formData.confirmPassword}
                                                    onChange={handleInputChange}
                                                    required
                                                />
                                                <button
                                                    type="button"
                                                    className="absolute right-[15px] top-1/2 transform -translate-y-1/2 text-[#666] hover:text-darkgray"
                                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                                >
                                                    <i className={showConfirmPassword ? "feather-eye-off" : "feather-eye"}></i>
                                                </button>
                                            </div>
                                        </Col>
                                        <Col xs={12} className="mb-[25px]">
                                            <label className="flex items-start cursor-pointer">
                                                <input type="checkbox" className="mr-[8px] mt-[2px]" required />
                                                <span className="text-sm">
                                                    I agree to the {" "}
                                                    <Link to="/privacy" className="hover:text-darkgray underline decoration-[1px] underline-offset-[4px]">
                                                        Terms of Service
                                                    </Link>
                                                    {" "} and {" "}
                                                    <Link to="/privacy" className="hover:text-darkgray underline decoration-[1px] underline-offset-[4px]">
                                                        Privacy Policy
                                                    </Link>
                                                </span>
                                            </label>
                                        </Col>
                                        <Col xs={12} className="mb-[25px]">
                                            <Buttons
                                                type="submit"
                                                className={`btn-fill btn-fancy font-medium tracking-[1px] rounded-[4px] uppercase w-full ${loading ? 'opacity-75 cursor-not-allowed' : ''}`}
                                                themeColor="#232323"
                                                color="#fff"
                                                size="lg"
                                                title={loading ? "Creating Account..." : "Create Account"}
                                                disabled={loading}
                                            />
                                        </Col>
                                        <Col xs={12} className="text-center">
                                            <p className="text-md mb-0">
                                                Already have an account? {" "}
                                                <Link 
                                                    to="/auth/login" 
                                                    className="font-medium hover:text-darkgray underline decoration-[1px] underline-offset-[4px]"
                                                >
                                                    Sign In
                                                </Link>
                                            </p>
                                        </Col>
                                    </Row>
                                </Form>
                            </m.div>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Register Form Section End */}

            {/* Footer Start */}
            <FooterStyle05 theme="dark" className="text-[#828282] bg-darkgray" />
            {/* Footer End */}
        </div>
    )
}

export default Register 