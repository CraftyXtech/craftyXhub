import React, { useState, useEffect, memo } from 'react'

// Libraries
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Col, Container, Navbar, Row, Tab, Nav } from "react-bootstrap";

// Components
import BlogClassic from '../../Components/Blogs/BlogClassic';
import Header, { HeaderCart, HeaderLanguage, HeaderNav, Menu, SearchBar, } from "../../Components/Header/Header";
import FooterStyle05 from '../../Components/Footers/FooterStyle05';
import SideButtons from "../../Components/SideButtons";

// API
import { useSearch } from '../../api/usePosts';

// Animation
import { m } from "framer-motion";
import { fadeIn } from '../../Functions/GlobalAnimations';

const SearchResultPage = (props) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('posts');
  
  const searchQuery = location.state?.search?.search || location.search.split('q=')[1] || '';
  const { searchResults, loading, error, search } = useSearch();

  // Perform search when component mounts or query changes
  useEffect(() => {
    if (searchQuery) {
      search(searchQuery);
    }
  }, [searchQuery, search]);

  const handleTabSelect = (key) => {
    setActiveTab(key);
  };

  const SearchResultsContent = memo(() => {
    if (loading) {
      return (
        <div className="text-center py-16">
          <div className="spinner-border text-fastblue" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-4 text-spanishgray">Searching...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="text-center py-16">
          <i className="feather-alert-circle text-6xl text-red-500 mb-4"></i>
          <h3 className="text-darkgray mb-4">Search Error</h3>
          <p className="text-spanishgray">{error}</p>
        </div>
      );
    }

    const { posts, users, categories } = searchResults;
    const totalResults = posts.length + users.length + categories.length;

    if (totalResults === 0 && searchQuery) {
      return (
        <div className="text-center py-16">
          <i className="feather-search text-6xl text-spanishgray mb-4"></i>
          <h3 className="text-darkgray mb-4">No Results Found</h3>
          <p className="text-spanishgray">Try different keywords or check your spelling.</p>
        </div>
      );
    }

    return (
      <m.div {...fadeIn}>
        <Tab.Container activeKey={activeTab} onSelect={handleTabSelect}>
          <Nav variant="tabs" className="mb-8 border-b border-mediumgray">
            <Nav.Item>
              <Nav.Link eventKey="posts" className="px-6 py-3 font-serif">
                Posts ({posts.length})
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="users" className="px-6 py-3 font-serif">
                Authors ({users.length})
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="categories" className="px-6 py-3 font-serif">
                Categories ({categories.length})
              </Nav.Link>
            </Nav.Item>
          </Nav>
          
          <Tab.Content>
            <Tab.Pane eventKey="posts">
              {posts.length > 0 ? (
                <BlogClassic 
                  filter={false} 
                  pagination={true} 
                  grid="grid grid-3col xl-grid-3col lg-grid-2col md-grid-2col sm-grid-1col xs-grid-1col gutter-extra-large" 
                  data={posts} 
                  link="/posts/" 
                />
              ) : (
                <p className="text-center text-spanishgray py-8">No posts found.</p>
              )}
            </Tab.Pane>
            
            <Tab.Pane eventKey="users">
              {users.length > 0 ? (
                <Row className="justify-center">
                  {users.map((user, index) => (
                    <Col key={user.uuid || index} lg={4} md={6} className="mb-8">
                      <m.div 
                        className="text-center bg-white p-8 rounded-lg shadow-sm"
                        {...fadeIn}
                        transition={{ delay: index * 0.1 }}
                      >
                        <div className="w-20 h-20 bg-lightgray rounded-full mx-auto mb-4 flex items-center justify-center">
                          <i className="feather-user text-2xl text-spanishgray"></i>
                        </div>
                        <h5 className="font-serif text-darkgray mb-2">{user.full_name || user.username}</h5>
                        <p className="text-spanishgray text-sm mb-4">@{user.username}</p>
                        <Link 
                          to={`/author/${user.uuid}`}
                          className="btn btn-sm btn-outline-primary"
                        >
                          View Profile
                        </Link>
                      </m.div>
                    </Col>
                  ))}
                </Row>
              ) : (
                <p className="text-center text-spanishgray py-8">No authors found.</p>
              )}
            </Tab.Pane>
            
            <Tab.Pane eventKey="categories">
              {categories.length > 0 ? (
                <Row className="justify-center">
                  {categories.map((category, index) => (
                    <Col key={category.uuid || index} lg={4} md={6} className="mb-6">
                      <m.div 
                        className="bg-white p-6 rounded-lg shadow-sm border border-lightgray"
                        {...fadeIn}
                        transition={{ delay: index * 0.1 }}
                      >
                        <h5 className="font-serif text-darkgray mb-3">{category.name}</h5>
                        {category.description && (
                          <p className="text-spanishgray text-sm mb-4">{category.description}</p>
                        )}
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-spanishgray">
                            {category.post_count || 0} posts
                          </span>
                          <Link 
                            to={`/category/${category.slug}`}
                            className="text-fastblue hover:text-blue-600 text-sm font-medium"
                          >
                            Browse Category →
                          </Link>
                        </div>
                      </m.div>
                    </Col>
                  ))}
                </Row>
              ) : (
                <p className="text-center text-spanishgray py-8">No categories found.</p>
              )}
            </Tab.Pane>
          </Tab.Content>
        </Tab.Container>
      </m.div>
    );
  });

  return (
    <div style={props.style}>
      {/* Header Start */}
      <Header topSpace={{ desktop: true }} type="reverse-scroll">
        <HeaderNav fluid="fluid" theme="ligt" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" containerClass="sm:px-0">
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
                Search results for "{searchQuery}"
              </h1>
              {!loading && !error && (
                <p className="text-mediumgray text-sm mt-2 md:text-center">
                  Found {(searchResults.posts?.length || 0) + (searchResults.users?.length || 0) + (searchResults.categories?.length || 0)} results
                </p>
              )}
            </Col>
            <Col xl={4} lg={6} className="breadcrumb justify-end text-sm font-serif mb-0 md:mt-[10px] md:justify-center">
              <ul className="xs:text-center">
                <li><Link aria-label="homepage" to="/" className="hover:text-white">Home</Link></li>
                <li><Link aria-label="pages" to="#" className="hover:text-white">Search</Link></li>
                <li>Results</li>
              </ul>
            </Col>
          </Row>
        </Container>
      </section>
      {/* Page Title Section End */}

      {/* Search Results Section Start */}
      <section className="px-[11%] xl:px-[2%] xs:px-0 bg-lightgray py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
        <Container fluid>
          <Row>
            <Col xs={12} className="xs:px-0">
              <SearchResultsContent />
            </Col>
          </Row>
        </Container>
      </section>
      {/* Search Results Section End */}

      {/* Footer Start */}
      <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
      {/* Footer End */}
    </div>
  )
}

export default SearchResultPage