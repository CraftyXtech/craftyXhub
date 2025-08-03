import React, { memo } from 'react'

// Libraries
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { m } from "framer-motion"
import { PropTypes } from "prop-types"

// Components
import { Header, HeaderCart, HeaderLanguage, HeaderNav, Menu, SearchBar } from '../../Components/Header/Header'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'
import SideButtons from "../../Components/SideButtons"
import ProfileManagement from '../../Components/ProfileManagement'
import Buttons from '../../Components/Button/Buttons'

// API & Auth
import useAuth from '../../api/useAuth'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

const Profile = (props) => {
    const { isAuthenticated, user } = useAuth()

    // Show auth required message for non-authenticated users
    if (!isAuthenticated) {
        return (
            <div style={props.style}>
                {/* Header Start */}
                <Header topSpace={{ desktop: true }} type="reverse-scroll">
                    <HeaderNav fluid="fluid" theme="light" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" containerClass="sm:px-0">
                        <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                            <Link aria-label="header logo" className="flex items-center" to="/">
                                <Navbar.Brand className="inline-block p-0 m-0">
                                    <img className="default-logo" width="111" height="36" loading="lazy" src='/assets/img/webp/logo-fast-blue-black.webp' data-rjs='/assets/img/webp/logo-fast-blue-black@2x.webp' alt='logo' />
                                    <img className="alt-logo" width="111" height="36" loading="lazy" src='/assets/img/webp/logo-fast-blue-black.webp' data-rjs='/assets/img/webp/logo-fast-blue-black@2x.webp' alt='logo' />
                                    <img className="mobile-logo" width="111" height="36" loading="lazy" src='/assets/img/webp/logo-fast-blue-black.webp' data-rjs='/assets/img/webp/logo-fast-blue-black@2x.webp' alt='logo' />
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
                        <Navbar.Collapse className="col-auto px-0 justify-end">
                            <Menu {...props} />
                        </Navbar.Collapse>
                        <Col className="col-auto text-right pe-0">
                            <SearchBar className="xs:pl-[15px] pr-0" />
                            <HeaderLanguage className="xs:pl-[15px]" />
                            <HeaderCart className="xs:pl-[15px]" style={{ "--base-color": "#0038e3" }} />
                        </Col>
                    </HeaderNav>
                </Header>
                {/* Header End */}

                {/* Section Start */}
                <section className="pt-[130px] lg:pt-[90px] md:pt-[75px] sm:pt-[50px]">
                    <Container>
                        <Row className="justify-center">
                            <Col xl={6} lg={7} md={8} className="text-center">
                                <h1 className="font-serif text-darkgray font-semibold text-[42px] lg:text-[32px] md:text-[30px] mb-[25px]">
                                    Access Required
                                </h1>
                                <p className="w-[85%] mx-auto mb-[35px] lg:w-[90%] md:w-full">
                                    Please log in to manage your profile settings.
                                </p>
                                <Buttons 
                                    to="/auth/login" 
                                    className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none"
                                    themeColor="#0038e3"
                                    color="#fff"
                                    title="Login to Continue"
                                />
                            </Col>
                        </Row>
                    </Container>
                </section>
                {/* Section End */}

                {/* Footer Start */}
                <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
                {/* Footer End */}
            </div>
        )
    }

    return (
        <div style={props.style}>
            <SideButtons />
            
            {/* Header Start */}
            <Header topSpace={{ desktop: true }} type="reverse-scroll">
                <HeaderNav fluid="fluid" theme="light" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" containerClass="sm:px-0">
                    <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                        <Link aria-label="header logo" className="flex items-center" to="/">
                            <Navbar.Brand className="inline-block p-0 m-0">
                                <img className="default-logo" width="111" height="36" loading="lazy" src='/assets/img/webp/logo-fast-blue-black.webp' data-rjs='/assets/img/webp/logo-fast-blue-black@2x.webp' alt='logo' />
                                <img className="alt-logo" width="111" height="36" loading="lazy" src='/assets/img/webp/logo-fast-blue-black@2x.webp' alt='logo' />
                                <img className="mobile-logo" width="111" height="36" loading="lazy" src='/assets/img/webp/logo-fast-blue-black@2x.webp' alt='logo' />
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
                    <Navbar.Collapse className="col-auto px-0 justify-end">
                        <Menu {...props} />
                    </Navbar.Collapse>
                    <Col className="col-auto text-right pe-0">
                        <SearchBar className="xs:pl-[15px] pr-0" />
                        <HeaderLanguage className="xs:pl-[15px]" />
                        <HeaderCart className="xs:pl-[15px]" style={{ "--base-color": "#0038e3" }} />
                    </Col>
                </HeaderNav>
            </Header>
            {/* Header End */}

            {/* Page Title Start */}
            <section className="bg-lightgray py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                <Container>
                    <Row className="items-center justify-center">
                        <Col xl={8} lg={6}>
                            <h1 className="font-serif text-darkgray font-semibold text-[42px] lg:text-[32px] md:text-[30px] mb-[15px]">
                                Profile Settings
                            </h1>
                            <p className="mb-0 text-lg">
                                Manage your profile information and preferences.
                            </p>
                        </Col>
                        <Col xl={4} lg={6} className="breadcrumb justify-end text-right mt-[10px] lg:mt-[20px] xs:mt-0">
                            <ul className="xs-text-center">
                                <li><Link aria-label="breadcrumb" to="/">Home</Link></li>
                                <li><Link aria-label="breadcrumb" to="/dashboard">Dashboard</Link></li>
                                <li>Profile</li>
                            </ul>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Page Title End */}

            {/* Profile Management Section Start */}
            <m.section {...fadeIn} className="py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                <Container>
                    <Row className="justify-center">
                        <Col lg={8}>
                            <ProfileManagement userUuid={user?.uuid} />
                        </Col>
                    </Row>
                </Container>
            </m.section>
            {/* Profile Management Section End */}

            {/* Footer Start */}
            <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
            {/* Footer End */}
        </div>
    )
}

Profile.defaultProps = {
    className: "",
}

Profile.propTypes = {
    className: PropTypes.string,
}

export default memo(Profile)