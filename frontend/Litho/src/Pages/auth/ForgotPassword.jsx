import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Col, Container, Row, Navbar, Form, Alert } from 'react-bootstrap'
import { m } from "framer-motion"

// Components
import Header, { HeaderNav, Menu } from '../../Components/Header/Header'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'
import Buttons from '../../Components/Button/Buttons'
import SideButtons from "../../Components/SideButtons"

// API - Using barrel export
import { axiosInstance } from '../../api'

// Data
import HeaderData from '../../Components/Header/HeaderData'

// Animations
import { fadeIn } from '../../Functions/GlobalAnimations'

const ForgotPassword = (props) => {
    const [email, setEmail] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        setSuccess(false)

        try {
            await axiosInstance.post('/auth/forgot-password', {
                email: email
            })

            setSuccess(true)
        } catch (error) {
            console.error('Forgot password error:', error)
            const errorMessage = error.response?.data?.detail || 
                              error.response?.data?.message || 
                              error.message || 
                              "Failed to send reset email. Please try again."
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
                            <h1 className="font-serif text-white font-medium mb-0 md:text-center text-lg">Reset Password</h1>
                        </Col>
                        <Col xl={4} lg={6} className="breadcrumb justify-end text-xs font-serif md:mt-[10px] mb-0 md:justify-center">
                            <ul className="xs-text-center">
                                <li><Link aria-label="breadcrumb" to="/" className="hover:text-white">Home</Link></li>
                                <li>Reset Password</li>
                            </ul>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Page Title Section End */}

            {/* Forgot Password Form Section Start */}
            <section className="py-[160px] lg:py-[120px] md:py-[95px] sm:py-[80px] xs:py-[50px]">
                <Container>
                    <Row className="justify-center">
                        <Col lg={5} md={7} sm={9}>
                            <m.div 
                                className="bg-white shadow-[0_0_30px_rgba(0,0,0,0.1)] rounded-[6px] p-[50px] lg:p-[35px] md:p-[30px] sm:p-[25px]"
                                {...fadeIn}
                            >
                                <div className="text-center mb-[40px]">
                                    <div className="mb-[25px]">
                                        <i className="feather-lock text-[50px] text-darkgray"></i>
                                    </div>
                                    <h3 className="font-serif text-darkgray font-medium mb-[15px]">Forgot Password?</h3>
                                    <p className="text-lg mb-0">
                                        {success 
                                            ? "We've sent you a password reset link!"
                                            : "Enter your email and we'll send you a reset link"
                                        }
                                    </p>
                                </div>

                                {error && (
                                    <Alert variant="danger" className="mb-[25px] text-sm">
                                        <i className="feather-alert-circle mr-[8px]"></i>
                                        {error}
                                    </Alert>
                                )}

                                {success ? (
                                    <div className="text-center">
                                        <Alert variant="success" className="mb-[25px] text-sm">
                                            <i className="feather-check-circle mr-[8px]"></i>
                                            Password reset link has been sent to your email address. Please check your inbox and follow the instructions.
                                        </Alert>
                                        <div className="space-y-4">
                                            <p className="text-sm text-[#666]">
                                                Didn't receive the email? Check your spam folder or try again.
                                            </p>
                                            <Buttons
                                                onClick={() => {
                                                    setSuccess(false)
                                                    setEmail('')
                                                }}
                                                className="btn-transparent btn-fancy font-medium tracking-[1px] rounded-[4px] uppercase"
                                                themeColor="#232323"
                                                color="#232323"
                                                size="md"
                                                title="Send Another Email"
                                            />
                                        </div>
                                    </div>
                                ) : (
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
                                                    placeholder="Enter your email address"
                                                    value={email}
                                                    onChange={(e) => setEmail(e.target.value)}
                                                    required
                                                />
                                            </Col>
                                            <Col xs={12} className="mb-[25px]">
                                                <Buttons
                                                    type="submit"
                                                    className={`btn-fill btn-fancy font-medium tracking-[1px] rounded-[4px] uppercase w-full ${loading ? 'opacity-75 cursor-not-allowed' : ''}`}
                                                    themeColor="#232323"
                                                    color="#fff"
                                                    size="lg"
                                                    title={loading ? "Sending..." : "Send Reset Link"}
                                                    disabled={loading}
                                                />
                                            </Col>
                                        </Row>
                                    </Form>
                                )}

                                <div className="text-center mt-[30px] pt-[25px] border-t border-[#dfdfdf]">
                                    <p className="text-md mb-0">
                                        Remember your password? {" "}
                                        <Link 
                                            to="/auth/login" 
                                            className="font-medium hover:text-darkgray underline decoration-[1px] underline-offset-[4px]"
                                        >
                                            Back to Login
                                        </Link>
                                    </p>
                                </div>
                            </m.div>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Forgot Password Form Section End */}

            {/* Footer Start */}
            <FooterStyle05 theme="dark" className="text-[#828282] bg-darkgray" />
            {/* Footer End */}
        </div>
    )
}

export default ForgotPassword 