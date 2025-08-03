import React, { useState, memo } from 'react'

// Libraries
import { Link } from "react-router-dom";
import { Col, Container, Navbar, Row } from "react-bootstrap";
import { m } from "framer-motion";

// Components
import Header, { HeaderCart, HeaderLanguage, HeaderNav, Menu, SearchBar } from "../../Components/Header/Header";
import FooterStyle05 from '../../Components/Footers/FooterStyle05';
import SideButtons from "../../Components/SideButtons";
import BlogClassic from '../../Components/Blogs/BlogClassic';

// API & Auth
import { useUserBookmarks } from '../../api/usePosts';
import useAuth from '../../api/useAuth';

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations';

// CSS
import "../../Assets/scss/pages/_bookmarks.scss";

const BookmarksPage = (props) => {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;
  
  const { isAuthenticated, user } = useAuth();
  const { 
    bookmarks, 
    loading, 
    error, 
    refetch 
  } = useUserBookmarks({ 
    skip: (currentPage - 1) * itemsPerPage, 
    limit: itemsPerPage 
  });

  

  // Redirect if not authenticated
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
        <SideButtons />
        
        {/* Authentication Required Section */}
        <section className="py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px] bg-lightgray">
          <Container>
            <Row className="justify-center">
              <Col lg={6} className="text-center">
                <m.div {...fadeIn}>
                  <i className="feather-lock text-6xl text-spanishgray mb-6"></i>
                  <h2 className="heading-4 font-serif font-semibold text-darkgray mb-4">
                    Authentication Required
                  </h2>
                  <p className="text-spanishgray mb-8">
                    Please log in to view your bookmarked articles.
                  </p>
                  <Link 
                    to="/auth/login" 
                    className="btn btn-fancy btn-medium rounded-[4px] font-medium font-serif uppercase bg-fastblue text-white"
                  >
                    Login to Continue
                  </Link>
                </m.div>
              </Col>
            </Row>
          </Container>
        </section>
        
        {/* Footer Start */}
        <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
        {/* Footer End */}
      </div>
    );
  }

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
      <SideButtons />
      
      {/* Page Title Section Start */}
      <section className="bg-darkgray py-[25px] page-title-small">
        <Container>
          <Row className="items-center justify-center">
            <Col xl={8} lg={6}>
              <h1 className="font-serif text-lg text-white font-medium mb-0 md:text-center">
                <i className="feather-bookmark mr-3"></i>
                My Bookmarks
              </h1>
              {!loading && !error && bookmarks && (
                <p className="text-mediumgray text-sm mt-2 md:text-center">
                  {bookmarks.length} bookmarked article{bookmarks.length !== 1 ? 's' : ''}
                </p>
              )}
            </Col>
            <Col xl={4} lg={6} className="breadcrumb justify-end text-sm font-serif mb-0 md:mt-[10px] md:justify-center">
              <ul className="xs:text-center">
                <li><Link aria-label="homepage" to="/" className="hover:text-white">Home</Link></li>
                <li><Link aria-label="profile" to="/profile" className="hover:text-white">Profile</Link></li>
                <li>Bookmarks</li>
              </ul>
            </Col>
          </Row>
        </Container>
      </section>
      {/* Page Title Section End */}

      {/* User Info Section Start */}
      <section className="py-[50px] bg-lightgray border-b border-mediumgray">
        <Container>
          <Row className="items-center">
            <Col md={6}>
              <div className="flex items-center">
                <div className="w-16 h-16 bg-fastblue rounded-full flex items-center justify-center mr-4">
                  <i className="feather-user text-white text-xl"></i>
                </div>
                <div>
                  <h4 className="font-serif text-darkgray mb-1">{user?.full_name || user?.username}</h4>
                  <p className="text-spanishgray text-sm mb-0">@{user?.username}</p>
                </div>
              </div>
            </Col>
            <Col md={6} className="text-md-end mt-4 mt-md-0">
              <Link 
                to="/profile" 
                className="btn btn-outline-primary btn-small rounded-[4px] font-medium font-serif uppercase mr-3"
              >
                View Profile
              </Link>
              <button 
                onClick={refetch}
                disabled={loading}
                className="btn btn-outline-secondary btn-small rounded-[4px] font-medium font-serif uppercase"
              >
                <i className="feather-refresh-cw mr-2"></i>
                Refresh
              </button>
            </Col>
          </Row>
        </Container>
      </section>
      {/* User Info Section End */}

      {/* Bookmarks Section Start */}
      <section className="px-[11%] xl:px-[2%] xs:px-0 bg-white py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
        <Container fluid>
          <Row>
            <Col xs={12} className="xs:px-0">
              {loading ? (
                <m.div className="text-center py-16" {...fadeIn}>
                  <div className="spinner-border text-fastblue" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                  <p className="mt-4 text-spanishgray">Loading your bookmarks...</p>
                </m.div>
              ) : error ? (
                <m.div className="text-center py-16" {...fadeIn}>
                  <i className="feather-alert-circle text-6xl text-red-500 mb-4"></i>
                  <h3 className="text-darkgray mb-4">Error Loading Bookmarks</h3>
                  <p className="text-spanishgray mb-6">{error}</p>
                  <button 
                    onClick={refetch}
                    className="btn btn-fancy btn-medium rounded-[4px] font-medium font-serif uppercase bg-fastblue text-white"
                  >
                    Try Again
                  </button>
                </m.div>
              ) : !bookmarks || bookmarks.length === 0 ? (
                <m.div className="text-center py-16" {...fadeIn}>
                  <i className="feather-bookmark text-6xl text-spanishgray mb-6"></i>
                  <h3 className="text-darkgray mb-4">No Bookmarks Yet</h3>
                  <p className="text-spanishgray mb-8">
                    Start bookmarking articles to see them here. Browse our latest posts to find something interesting!
                  </p>
                  <Link 
                    to="/" 
                    className="btn btn-fancy btn-medium rounded-[4px] font-medium font-serif uppercase bg-fastblue text-white"
                  >
                    Explore Articles
                  </Link>
                </m.div>
              ) : (
                <m.div {...fadeIn}>
                  <BlogClassic 
                    filter={false} 
                    pagination={true} 
                    grid="grid grid-3col xl-grid-3col lg-grid-2col md-grid-2col sm-grid-1col xs-grid-1col gutter-extra-large" 
                    data={bookmarks} 
                    link="/posts/"
                    showBookmarkButton={true}
                    className="bookmarks-grid"
                  />
                </m.div>
              )}
            </Col>
          </Row>
        </Container>
      </section>
      {/* Bookmarks Section End */}

      {/* Footer Start */}
      <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
      {/* Footer End */}
    </div>
  )
}

export default memo(BookmarksPage)