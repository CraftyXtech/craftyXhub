import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Col, Container, Row, Navbar, Form, Alert } from 'react-bootstrap'
import { m } from "framer-motion"
import Header, { HeaderNav, Menu } from '../../Components/Header/Header'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'
import Buttons from '../../Components/Button/Buttons'
import SideButtons from "../../Components/SideButtons"

// API - Using barrel exports
import useAuth from '../../api/useAuth'
import { axiosInstance } from '../../api'

// Data
import HeaderData from '../../Components/Header/HeaderData'

// Animations
import { fadeIn } from '../../Functions/GlobalAnimations'

const Login = (props) => {
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
            // Step 1: Login to get token
            const loginResponse = await axiosInstance.post('/auth/login', {
                email: formData.email,
                password: formData.password
            })

            const token = loginResponse.data.access_token

            // Step 2: Fetch user data using the token
            const userResponse = await axiosInstance.get('/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            // Step 3: Store both token and user data
            login(token, userResponse.data)
            
            // Redirect to home page
            navigate('/')
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

    return (
        <div style={props.style}>
            <SideButtons />
            
            {/* Header Start */}
            <Header topSpace={{ desktop: true }} type="reverse-scroll">
                <HeaderNav bg="white" theme="light" expand="lg" className="py-[0px] lg:px-[15px] md:px-0">
                    <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                        <Link aria-label="header logo" className="flex items-center" to="/">
                            <Navbar.Brand className="inline-block p-0 m-0">
                                <span className="text-2xl font-bold text-darkgray tracking-wide">CraftyXhub</span>
                            </Navbar.Brand>
                        </Link>
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
                        <Menu data={HeaderData} />
                    </Navbar.Collapse>
                </HeaderNav>
            </Header>
            {/* Header End */}

            {/* Page Title Section Start */}
            <section className="bg-darkgray py-[25px]">
                <Container>
                    <Row className="items-center justify-center">
                        <Col xl={8} lg={6}>
                            <h1 className="font-serif text-white font-medium mb-0 md:text-center text-lg">Login to CraftyXhub</h1>
                        </Col>
                        <Col xl={4} lg={6} className="breadcrumb justify-end text-xs font-serif md:mt-[10px] mb-0 md:justify-center">
                            <ul className="xs-text-center">
                                <li><Link aria-label="breadcrumb" to="/" className="hover:text-white">Home</Link></li>
                                <li>Login</li>
                            </ul>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Page Title Section End */}

            {/* Login Form Section Start */}
            <section className="py-[160px] lg:py-[120px] md:py-[95px] sm:py-[80px] xs:py-[50px]">
                <Container>
                    <Row className="justify-center">
                        <Col lg={6} md={8} sm={10}>
                            <m.div 
                                className="bg-white shadow-[0_0_30px_rgba(0,0,0,0.1)] rounded-[6px] p-[50px] lg:p-[35px] md:p-[30px] sm:p-[25px]"
                                {...fadeIn}
                            >
                                <div className="text-center mb-[40px]">
                                    <h3 className="font-serif text-darkgray font-medium mb-[15px]">Welcome Back!</h3>
                                    <p className="text-lg mb-0">Sign in to your CraftyXhub account</p>
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
                                                    placeholder="Enter your password"
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
                                        </Col>
                                        <Col xs={12} className="mb-[25px]">
                                            <div className="flex justify-between items-center">
                                                <label className="flex items-center cursor-pointer">
                                                    <input type="checkbox" className="mr-[8px]" />
                                                    <span className="text-sm">Remember me</span>
                                                </label>
                                                <Link 
                                                    to="/auth/forgot-password" 
                                                    className="text-sm hover:text-darkgray"
                                                >
                                                    Forgot Password?
                                                </Link>
                                            </div>
                                        </Col>
                                        <Col xs={12} className="mb-[25px]">
                                            <Buttons
                                                type="submit"
                                                className={`btn-fill btn-fancy font-medium tracking-[1px] rounded-[4px] uppercase w-full ${loading ? 'opacity-75 cursor-not-allowed' : ''}`}
                                                themeColor="#232323"
                                                color="#fff"
                                                size="lg"
                                                title={loading ? "Signing In..." : "Sign In"}
                                                disabled={loading}
                                            />
                                        </Col>
                                        <Col xs={12} className="text-center">
                                            <p className="text-md mb-0">
                                                Don't have an account? {" "}
                                                <Link 
                                                    to="/auth/register" 
                                                    className="font-medium hover:text-darkgray underline decoration-[1px] underline-offset-[4px]"
                                                >
                                                    Create Account
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
            {/* Login Form Section End */}

            {/* Footer Start */}
            <FooterStyle05 theme="dark" className="text-[#828282] bg-darkgray" />
            {/* Footer End */}
        </div>
    )
}

export default Login 