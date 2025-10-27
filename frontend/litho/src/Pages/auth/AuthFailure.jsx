import React from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { Col, Container, Row, Navbar, Alert } from 'react-bootstrap'
import { m } from "framer-motion"
import Header, { HeaderNav, Menu } from '../../Components/Header/Header'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'
import Buttons from '../../Components/Button/Buttons'
import SideButtons from "../../Components/SideButtons"
import Logo from '../../Components/Logo'

// Animations
import { fadeIn } from '../../Functions/GlobalAnimations'

const AuthFailure = (props) => {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    
    const error = searchParams.get('error') || 'Authentication failed'

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
                            <h1 className="font-serif text-white font-medium mb-0 md:text-center text-lg">Authentication Failed</h1>
                        </Col>
                        <Col xl={4} lg={6} className="breadcrumb justify-end text-xs font-serif md:mt-[10px] mb-0 md:justify-center">
                            <ul className="xs-text-center">
                                <li><Link aria-label="breadcrumb" to="/" className="hover:text-white">Home</Link></li>
                                <li>Auth Error</li>
                            </ul>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Page Title Section End */}

            {/* Error Section Start */}
            <section className="py-[160px] lg:py-[120px] md:py-[95px] sm:py-[80px] xs:py-[50px]">
                <Container>
                    <Row className="justify-center">
                        <Col lg={6} md={8} sm={10}>
                            <m.div 
                                className="bg-white shadow-[0_0_30px_rgba(0,0,0,0.1)] rounded-[6px] p-[50px] lg:p-[35px] md:p-[30px] sm:p-[25px] text-center"
                                {...fadeIn}
                            >
                                <div className="mb-[40px]">
                                    <i className="feather-x-circle text-[80px] text-red-500 mb-[25px] block"></i>
                                    <h3 className="font-serif text-darkgray font-medium mb-[15px]">Authentication Failed</h3>
                                    <p className="text-lg mb-[20px] text-[#666]">
                                        We couldn't complete your sign-in request
                                    </p>
                                </div>

                                <Alert variant="danger" className="mb-[30px] text-sm text-left">
                                    <i className="feather-alert-circle mr-[8px]"></i>
                                    <strong>Error:</strong> {error}
                                </Alert>

                                <div className="mb-[30px] text-left">
                                    <p className="text-sm text-[#666] mb-[15px]">
                                        <strong>Common causes:</strong>
                                    </p>
                                    <ul className="text-sm text-[#666] space-y-[8px] list-disc list-inside">
                                        <li>Email permission denied during OAuth flow</li>
                                        <li>Account access restricted by provider</li>
                                        <li>Network connection issues</li>
                                        <li>Browser blocking third-party cookies</li>
                                    </ul>
                                </div>

                                <div className="flex gap-[15px] justify-center flex-wrap">
                                    <Buttons
                                        onClick={() => navigate('/auth/login')}
                                        className="btn-fill btn-fancy font-medium tracking-[1px] rounded-[4px] uppercase"
                                        themeColor="#232323"
                                        color="#fff"
                                        size="md"
                                        title="Try Again"
                                    />
                                    <Buttons
                                        onClick={() => navigate('/')}
                                        className="btn-outline btn-fancy font-medium tracking-[1px] rounded-[4px] uppercase"
                                        themeColor="#232323"
                                        color="#232323"
                                        size="md"
                                        title="Go Home"
                                    />
                                </div>

                                <div className="mt-[30px] pt-[20px] border-t border-[#e5e5e5]">
                                    <p className="text-sm text-[#666] mb-[10px]">
                                        Still having trouble?
                                    </p>
                                    <Link 
                                        to="/auth/register" 
                                        className="text-sm font-medium hover:text-darkgray underline decoration-[1px] underline-offset-[4px]"
                                    >
                                        Create a new account with email
                                    </Link>
                                </div>
                            </m.div>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Error Section End */}

            {/* Footer Start */}
            <FooterStyle05 theme="dark" className="text-[#828282] bg-darkgray" />
            {/* Footer End */}
        </div>
    )
}

export default AuthFailure
