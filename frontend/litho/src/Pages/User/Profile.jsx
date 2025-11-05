import React, { memo } from 'react'

// Libraries
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { m } from "framer-motion"
import { PropTypes } from "prop-types"

// Components
import { Header, HeaderNav, Menu, SearchBar } from '../../Components/Header/Header'
import Logo from '../../Components/Logo'
import UserProfileDropdown from '../../Components/Header/UserProfileDropdown'
import NotificationBell from '../../Components/Header/NotificationBell'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'

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
                            <Logo className="flex items-center" variant="black" />
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
                            <div className="flex items-center gap-2 ms-4">
                                <UserProfileDropdown />
                                <NotificationBell />
                            </div>
                        </Navbar.Collapse>
                    </HeaderNav>
                </Header>
                {/* Header End */}

                {/* Section Start */}
                <section className="pt-[50px] sm:pt-[70px] md:pt-[75px] lg:pt-[90px] xl:pt-[130px]">
                    <Container className="px-4 sm:px-6">
                        <Row className="justify-center">
                            <Col xl={6} lg={7} md={8} className="text-center">
                                <h1 className="font-serif text-darkgray font-semibold text-[24px] sm:text-[30px] md:text-[32px] lg:text-[42px] mb-[20px] sm:mb-[25px]">
                                    Access Required
                                </h1>
                                <p className="w-[95%] sm:w-[85%] lg:w-[90%] md:w-full mx-auto mb-[25px] sm:mb-[35px] text-sm sm:text-base">
                                    Please log in to manage your profile settings.
                                </p>
                                <Buttons 
                                    to="/auth/login" 
                                    className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none"
                                    themeColor="#0038e3"
                                    color="#fff"
                                    size="sm"
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

            
            {/* Header Start */}
            <Header topSpace={{ desktop: true }} type="reverse-scroll">
                <HeaderNav fluid="fluid" theme="light" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" containerClass="sm:px-0">
                    <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                        <Logo className="flex items-center" variant="black" />
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
                        <div className="flex items-center gap-2 ms-4">
                            <UserProfileDropdown />
                            <NotificationBell />
                        </div>
                    </Navbar.Collapse>
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
            <m.section {...fadeIn} className="py-[50px] sm:py-[60px] md:py-[75px] lg:py-[90px] xl:py-[130px]">
                <Container className="px-4 sm:px-6">
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