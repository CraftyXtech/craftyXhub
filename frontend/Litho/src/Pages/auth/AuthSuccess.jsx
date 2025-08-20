import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Col, Container, Row, Navbar, Alert } from 'react-bootstrap'
import { m } from "framer-motion"
import Header, { HeaderNav, Menu } from '../../Components/Header/Header'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'
import SideButtons from "../../Components/SideButtons"
import Logo from '../../Components/Logo'
import useAuth from '../../api/useAuth'
import { axiosInstance } from '../../api'

// Animations
import { fadeIn } from '../../Functions/GlobalAnimations'

const AuthSuccess = (props) => {
    const [searchParams] = useSearchParams()
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const navigate = useNavigate()
    const { login } = useAuth()

    useEffect(() => {
        const handleOAuthCallback = async () => {
            try {
                const accessToken = searchParams.get('access_token')
                const tokenType = searchParams.get('token_type')
                const expiresIn = searchParams.get('expires_in')

                if (!accessToken) {
                    setError('No access token received from OAuth provider')
                    setLoading(false)
                    return
                }

                // Get user data with the token
                const userResponse = await axiosInstance.get('/auth/me', {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                })

                // Set auth state
                login(accessToken, userResponse.data)

                // Redirect to dashboard after a brief delay
                setTimeout(() => {
                    navigate('/dashboard')
                }, 2000)

            } catch (error) {
                console.error('OAuth callback error:', error)
                setError('Failed to complete authentication. Please try again.')
                setLoading(false)
            }
        }

        handleOAuthCallback()
    }, [searchParams, login, navigate])

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
                            <h1 className="font-serif text-white font-medium mb-0 md:text-center text-lg">Authentication</h1>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Page Title Section End */}

            {/* Success Section Start */}
            <section className="py-[160px] lg:py-[120px] md:py-[95px] sm:py-[80px] xs:py-[50px]">
                <Container>
                    <Row className="justify-center">
                        <Col lg={6} md={8} sm={10}>
                            <m.div 
                                className="bg-white shadow-[0_0_30px_rgba(0,0,0,0.1)] rounded-[6px] p-[50px] lg:p-[35px] md:p-[30px] sm:p-[25px] text-center"
                                {...fadeIn}
                            >
                                {loading && !error && (
                                    <>
                                        <div className="mb-[30px]">
                                            <i className="feather-check-circle text-[60px] text-green-500 mb-[20px] block"></i>
                                            <h3 className="font-serif text-darkgray font-medium mb-[15px]">Authentication Successful!</h3>
                                            <p className="text-lg mb-0 text-[#666]">You have been successfully signed in. Redirecting to your dashboard...</p>
                                        </div>
                                        <div className="flex justify-center">
                                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-darkgray"></div>
                                        </div>
                                    </>
                                )}

                                {error && (
                                    <>
                                        <div className="mb-[30px]">
                                            <i className="feather-x-circle text-[60px] text-red-500 mb-[20px] block"></i>
                                            <h3 className="font-serif text-darkgray font-medium mb-[15px]">Authentication Failed</h3>
                                            <Alert variant="danger" className="mb-[25px] text-sm">
                                                <i className="feather-alert-circle mr-[8px]"></i>
                                                {error}
                                            </Alert>
                                        </div>
                                        <div className="flex gap-[15px] justify-center">
                                            <button
                                                onClick={() => navigate('/auth/login')}
                                                className="btn bg-darkgray text-white px-[20px] py-[10px] rounded-[4px] hover:bg-gray-700 transition-colors duration-300"
                                            >
                                                Try Again
                                            </button>
                                            <button
                                                onClick={() => navigate('/')}
                                                className="btn border border-darkgray text-darkgray px-[20px] py-[10px] rounded-[4px] hover:bg-darkgray hover:text-white transition-colors duration-300"
                                            >
                                                Go Home
                                            </button>
                                        </div>
                                    </>
                                )}
                            </m.div>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Success Section End */}

            {/* Footer Start */}
            <FooterStyle05 theme="dark" className="text-[#828282] bg-darkgray" />
            {/* Footer End */}
        </div>
    )
}

export default AuthSuccess
