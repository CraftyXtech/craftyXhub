import React, { useState, useEffect } from 'react'

// Libraries
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { Link } from 'react-router-dom';
import { Keyboard, Autoplay } from "swiper/modules";
import { Swiper, SwiperSlide } from 'swiper/react'
import { m } from "framer-motion";

// Components
import Header, { HeaderNav, Menu, SearchBar, Topbar } from '../../Components/Header/Header'
import Logo from '../../Components/Logo'
import SocialIcons from '../../Components/SocialIcon/SocialIcons'
import BlogClassic from '../../Components/Blogs/BlogClassic';
import BlogMetro from '../../Components/Blogs/BlogMetro';

import Instagram from '../../Components/Instagram/Instagram';
import FooterStyle05 from '../../Components/Footers/FooterStyle05'

import Buttons from '../../Components/Button/Buttons'
import LoginModal from '../../Components/auth/LoginModal'
import RegisterModal from '../../Components/auth/RegisterModal'
import PasswordResetModal from '../../Components/auth/PasswordResetModal'
import { fadeIn } from '../../Functions/GlobalAnimations';

import useAuth from '../../api/useAuth';
import { usePosts, usePopularPosts } from '../../api';


const SocialIconsData = [
  {
    color: "#fff",
    link: "https://www.facebook.com/",
    icon: "fab fa-facebook-f text-white",
  },
  {
    color: "#fff",
    link: "https://dribbble.com/",
    icon: "fab fa-dribbble"
  },
  {
    color: "#fff",
    link: "https://twitter.com/",
    icon: "fab fa-twitter text-white",
  },
  {
    color: "#fff",
    link: "https://www.instagram.com/",
    icon: "fab fa-instagram"
  }
]



const MagazinePage = (props) => {
  const swiperRef = React.useRef(null)
  const [showLoginModal, setShowLoginModal] = useState(false)
  const [showRegisterModal, setShowRegisterModal] = useState(false)
  const [showPasswordResetModal, setShowPasswordResetModal] = useState(false)
  
  const { isAuthenticated, user, logout } = useAuth()
  
  // API hooks
  const { posts: allPosts, loading: postsLoading, error: postsError } = usePosts({ published: true })
  const { posts: popularPosts, loading: popularLoading, error: popularError } = usePopularPosts({ limit: 6 })
  
  // Explicit hero slides from public assets
  const heroSlides = [
    {
      image: `${process.env.PUBLIC_URL}/assets/img/hero/hero.jpg`,
      label: 'Featured',
      title: 'Featured Articles',
      to: '/featured-articles',
    },
    {
      image: `${process.env.PUBLIC_URL}/assets/img/hero/hero2.jpg`,
      label: 'Trending',
      title: 'Trending Articles',
      to: '/trending-articles',
    },
  ]

  // Prepare data for components
  const recentPosts = allPosts?.slice(0, 2) || []
  const latestPosts = allPosts?.slice(0, 10) || []

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

          {/* Auth Buttons – Right (responsive) */}
          <Col className="col-auto col-lg-2 text-end pe-0">
            {!isAuthenticated ? (
              <div className="flex items-center justify-end space-x-1 sm:space-x-2">
                <Buttons
                  onClick={() => setShowLoginModal(true)}
                  className="btn-transparent btn-fancy font-medium text-xs px-2 py-1 sm:px-3 sm:py-2 rounded-[3px] tracking-[0.5px]"
                  themeColor="#232323"
                  color="#232323"
                  title="Login"
                />
                <Buttons
                  onClick={() => setShowRegisterModal(true)}
                  className="btn-fill btn-fancy font-medium text-xs px-2 py-1 sm:px-3 sm:py-2 rounded-[3px] tracking-[0.5px]"
                  themeColor="#232323"
                  color="#fff"
                  title="Sign Up"
                />
              </div>
            ) : (
              <div className="flex items-center justify-end space-x-1 sm:space-x-2">
                <span className="text-xs sm:text-sm text-darkgray hidden sm:inline">
                  Welcome, {user?.full_name || user?.username}!
                </span>
                <Buttons
                  onClick={logout}
                  className="btn-transparent btn-fancy font-medium text-xs px-2 py-1 sm:px-3 sm:py-2 rounded-[3px] tracking-[0.5px]"
                  themeColor="#232323"
                  color="#232323"
                  title="Logout"
                />
              </div>
            )}
          </Col>

          {/* Mobile Navigation – handled by Bootstrap collapse; duplicate block removed */}

          {/* Auth Buttons – Mobile block removed to avoid duplication */}
        </HeaderNav>
      </Header>
      {/* Header End */}

      {/* Section Start */}
      <section className="bg-[#f8f4f0] overflow-hidden py-[100px] lg:py-[60px] md:py-[60px] sm:py-[50px] px-[90px] lg:px-[40px] xs:px-0">
        <Container fluid>
          <Row>
            <Col xl={6} className="lg:mb-[10px] py-[10px] px-[10px] font-serif xs:px-[15px] p-[10px] lg:px-[25px] sm:px-[15px]">
              <Swiper
                ref={swiperRef}
                className="white-move swiper-pagination-light h-full relative lg:h-[500px] xs:h-[300px]"
                modules={[Keyboard, Autoplay]}
                keyboard={{ enabled: true, onlyInViewport: true }}
                autoplay={{ delay: 4000, disableOnInteraction: false, pauseOnMouseEnter: true }}
                loop={true}
              >
                {heroSlides.map((s, i) => (
                  <SwiperSlide
                    key={i}
                    className="overflow-hidden cover-background relative"
                    style={{ backgroundImage: `url(${s.image})` }}
                  >
                    <div className="flex items-center bg-[#000000b3] absolute left-0 bottom-0 w-full py-[55px] xl:py-[20px] lg:py-[55px] md:py-[40px] xs:py-[30px] px-[60px] xl:px-[50px] xs:pl-[30px] xs:pr-[50px] xs:flex-col xs:items-start">
                      <Link aria-label="link for" to={s.to} className="uppercase ps-0 pr-8 mr-8 border-r border-[#ffffff33] text-[#c89965] tracking-[2px] text-md font-medium tracking-2px font-serif md:border-0 md:mb-[10px] hover:text-white xs:mb-[5px]">{s.label}</Link>
                      <h2 className="heading-6 m-0">
                        <Link aria-label="link for" to={s.to} className="text-white font-light">{s.title}</Link>
                      </h2>
                    </div>
                  </SwiperSlide>
                ))}
                <div className="h-[140px] absolute w-full bottom-0 md:h-[110px] xs:h-[115px]">
                  <div onClick={() => swiperRef.current.swiper.slideNext()} className="bg-black text-white absolute border-0 top-0 right-0 z-[1] h-1/2 text-[20px] w-[50px] flex justify-center text-center items-center">
                    <i className="feather-arrow-right"></i>
                  </div>
                  <div onClick={() => swiperRef.current.swiper.slidePrev()} className="bg-black text-white absolute bottom-0 border-0 right-0 text-[20px] w-[50px] flex h-1/2 text-center justify-center items-center z-[1]">
                    <i className="feather-arrow-left"></i>
                  </div>
                </div>
              </Swiper>
            </Col>
            <Col xl={6} className="lg:px-[15px] sm:px-[5px] xs:px-0">
              {postsLoading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                  <p className="mt-2 text-gray-600">Loading latest articles...</p>
                </div>
              ) : postsError ? (
                <div className="text-center py-8 text-red-600">
                  <p>Error loading articles. Please try again later.</p>
                </div>
              ) : (
                <BlogMetro overlay="#374162" grid="grid grid-2col xl-grid-2col lg-grid-2col md-grid-2col sm-grid-2col xs-grid-1col gutter-large" data={recentPosts.slice(0,2)} link="/posts/" pagination={false} animation={fadeIn} animationDelay={0.1} className="blog-clean px-[6%] xl:px-[3%] lg:px-[15px]" />
              )}
            </Col>
          </Row>
        </Container>
      </section>
      {/* Section End */}





      {/* Section Start */}
      <section className="py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px] bg-white px-[75px] xl:px-[30px] lg:px-[15px] sm:px-0">
        <Container>
          <Row className="justify-center">
            <Col lg={6} className="text-center mb-10 sm:mb-6">
              <h2 className="heading-5 font-serif font-semibold text-darkgray mb-[5px]">Latest article</h2>
              <p className="mb-[25px]">Explore our blog for insightful articles</p>
            </Col>
          </Row>
        </Container>
        <Container fluid>
          {postsLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
              <p className="mt-2 text-gray-600">Loading latest articles...</p>
            </div>
          ) : postsError ? (
            <div className="text-center py-8 text-red-600">
              <p>Error loading articles. Please try again later.</p>
            </div>
          ) : (
            <BlogClassic filter={false} data={latestPosts} link="/posts/" pagination={false} grid="grid grid-4col xl-grid-4col lg-grid-3col md-grid-2col sm-grid-2col xs-grid-1col gutter-extra-large" />
          )}
        </Container>
      </section>
      {/* Section End */}

      {/* Popular Posts Section Start */}
      <section className="py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px] px-[75px] xl:px-[30px] lg:px-[15px] sm:px-0">
        <Container>
          <Row className="justify-center">
            <Col lg={6} className="text-center mb-10 sm:mb-6">
              <h2 className="heading-5 font-serif font-semibold text-darkgray mb-[5px]">Popular Articles</h2>
              <p className="mb-[25px]">Most liked and viewed articles from our community</p>
            </Col>
          </Row>
        </Container>
        <Container fluid>
          {popularLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
              <p className="mt-2 text-gray-600">Loading popular articles...</p>
            </div>
          ) : popularError ? (
            <div className="text-center py-8 text-red-600">
              <p>Error loading popular articles. Please try again later.</p>
            </div>
          ) : (
            <BlogClassic filter={false} data={popularPosts} link="/posts/" pagination={false} grid="grid grid-3col xl-grid-3col lg-grid-2col md-grid-2col sm-grid-1col xs-grid-1col gutter-extra-large" />
          )}
        </Container>
      </section>
      {/* Popular Posts Section End */}

      {/* Section Start */}
      <m.section className="py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]" {...fadeIn}>
        <Container>
          <Instagram carousel={true}
            carouselOption={{
              loop: true,
              slidesPerView: 2,
              spaceBetween: 15,
              autoplay: { "delay": 3500, "disableOnInteraction": false },
              keyboard: { "enabled": true, "onlyInViewport": true },
              breakpoints: { 1200: { slidesPerView: 6 }, 992: { slidesPerView: 3 }, 768: { slidesPerView: 3 } }
            }}
            total_posts={8} title="#instagram decor" grid="" />
        </Container>
      </m.section>
      {/* Section End */}

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

export default MagazinePage