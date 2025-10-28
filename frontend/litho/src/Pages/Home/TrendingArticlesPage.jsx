import React, { useState } from 'react'
import { Container, Row, Col, Navbar } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import Header, { HeaderNav, Menu, SearchBar, Topbar } from '../../Components/Header/Header'
import Logo from '../../Components/Logo'
import SocialIcons from '../../Components/SocialIcon/SocialIcons'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'

import Buttons from '../../Components/Button/Buttons'
import LoginModal from '../../Components/auth/LoginModal'
import RegisterModal from '../../Components/auth/RegisterModal'
import PasswordResetModal from '../../Components/auth/PasswordResetModal'
import TrendingPosts from './TrendingPosts'
import useAuth from '../../api/useAuth'


const SocialIconsData = [
  {
    color: "#fff",
    link: process.env.REACT_APP_FACEBOOK_URL,
    icon: "fab fa-facebook-f text-white",
  },
  {
    color: "#fff",
    link: process.env.REACT_APP_DRIBBBLE_URL,
    icon: "fab fa-dribbble"
  },
  {
    color: "#fff",
    link: process.env.REACT_APP_TWITTER_URL,
    icon: "fab fa-twitter text-white",
  },
  {
    color: "#fff",
    link: process.env.REACT_APP_INSTAGRAM_URL,
    icon: "fab fa-instagram"
  }
].filter(item => item.link)

const TrendingArticlesPage = (props) => {
  const [showLoginModal, setShowLoginModal] = useState(false)
  const [showRegisterModal, setShowRegisterModal] = useState(false)
  const [showPasswordResetModal, setShowPasswordResetModal] = useState(false)
  
  const { isAuthenticated, user, logout } = useAuth()

  const handleSwitchToRegister = () => {
    setShowLoginModal(false)
    setShowRegisterModal(true)
  }

  const handleSwitchToLogin = () => {
    setShowRegisterModal(false)
    setShowPasswordResetModal(false)
    setShowLoginModal(true)
  }

  const handleSwitchToPasswordReset = () => {
    setShowLoginModal(false)
    setShowRegisterModal(false)
    setShowPasswordResetModal(true)
  }

  return (
    <div style={props.style}>
      

      {/* Header Start */}
      <Header className="header-with-topbar" topSpace={{ desktop: true }} type="reverse-scroll">
        <Topbar className="bg-darkgray text-white sm:hidden md:px-[15px]">
          <Container fluid="lg">
            <Row className="items-center justify-center">
              <Col className="col-12 col-md-3 header-social-icon d-none d-md-inline-block border-0">
                <SocialIcons theme="social-icon-style-01" className="justify-start" size="xs" iconColor="light" data={SocialIconsData}
                />
              </Col>
              <Col className="col-12 col-md-6 text-center px-md-0 sm-padding-5px-tb line-height-normal">
                <span className="text-sm font-serif uppercase -tracking-[0.5px] inline-block">
                  Discover, Learn & Stay Inspired
                </span>
              </Col>
              <Col className="col-auto col-md-3 text-right">
                <SearchBar className="!py-[7px] text-white" />
              </Col>
            </Row>
          </Container>
        </Topbar>
        <HeaderNav bg="white" theme="light" expand="lg" containerClass="!px-0" className="py-[0px] md:py-[18px] md:px-[15px] sm:px-0">
          {/* Logo – Left */}
          <Col sm={6} lg={2} className="col-auto me-auto ps-lg-0">
            <Logo variant="black" />
          </Col>

          {/* Toggler */}
          <div className="order-last px-[15px] md:block">
            <Navbar.Toggle className="ml-[10px]">
              <span className="navbar-toggler-line"></span>
              <span className="navbar-toggler-line"></span>
              <span className="navbar-toggler-line"></span>
              <span className="navbar-toggler-line"></span>
            </Navbar.Toggle>
          </div>

          {/* Menu – Center */}
          <Navbar.Collapse className="col-auto col-lg-8 justify-center">
            <Menu {...props} />
          </Navbar.Collapse>

          {/* Auth Buttons – Right (desktop) */}
          <Col className="col-auto col-lg-2 text-end pe-0">
            {!isAuthenticated ? (
              <div className="flex items-center justify-end space-x-3">
                <Buttons
                  onClick={() => setShowLoginModal(true)}
                  className="btn-transparent btn-fancy font-medium tracking-[1px] rounded-[4px]"
                  themeColor="#232323"
                  color="#232323"
                  size="xs"
                  title="Login"
                />
                <Buttons
                  onClick={() => setShowRegisterModal(true)}
                  className="btn-fill btn-fancy font-medium tracking-[1px] rounded-[4px]"
                  themeColor="#232323"
                  color="#fff"
                  size="xs"
                  title="Sign Up"
                />
              </div>
            ) : (
              <div className="flex items-center justify-end space-x-3">
                <span className="text-sm text-darkgray">
                  Welcome, {user?.full_name || user?.username}!
                </span>
                <Buttons
                  onClick={logout}
                  className="btn-transparent btn-fancy font-medium tracking-[1px] rounded-[4px]"
                  themeColor="#232323"
                  color="#232323"
                  size="xs"
                  title="Logout"
                />
              </div>
            )}
          </Col>
        </HeaderNav>
      </Header>
      {/* Header End */}

      {/* Trending Articles Section */}
      <TrendingPosts 
        className="px-[75px] xl:px-[30px] lg:px-[15px] sm:px-0"
        limit={12}
        themeColor={["#0038e3", "#ff7a56"]}
        showTitle={true}
        title="Trending Articles"
        subtitle="Discover what's popular right now"
      />

      {/* Footer Start */}
      <FooterStyle05 className="text-[#828282] bg-darkgray" theme="dark" />

      {/* Auth Modals */}
      <LoginModal 
        show={showLoginModal}
        onHide={() => setShowLoginModal(false)}
        onSwitchToRegister={handleSwitchToRegister}
        onSwitchToPasswordReset={handleSwitchToPasswordReset}
      />
      <RegisterModal 
        show={showRegisterModal}
        onHide={() => setShowRegisterModal(false)}
        onSwitchToLogin={handleSwitchToLogin}
      />
      <PasswordResetModal 
        show={showPasswordResetModal}
        onHide={() => setShowPasswordResetModal(false)}
        onSwitchToLogin={handleSwitchToLogin}
      />
    </div>
  )
}

export default TrendingArticlesPage 