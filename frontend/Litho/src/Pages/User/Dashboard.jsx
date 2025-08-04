import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

// Libraries
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { m } from "framer-motion"

// Components
import { Header, HeaderCart, HeaderLanguage, HeaderNav, Menu, SearchBar } from '../../Components/Header/Header'
import Logo from '../../Components/Logo'
import UserProfileDropdown from '../../Components/Header/UserProfileDropdown'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'
import BlogWidget from '../../Components/Blogs/BlogWidget'
import BlogClassic from '../../Components/Blogs/BlogClassic'
import Buttons from '../../Components/Button/Buttons'

// API & Auth
import { useRecentPosts, usePopularPosts, usePosts, useUserDraftPosts } from '../../api/usePosts'
import useAuth from '../../api/useAuth'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

const Dashboard = (props) => {
    const [activeSection, setActiveSection] = useState('overview') // 'overview', 'reading-list', 'my-posts'
    const [showDrafts, setShowDrafts] = useState(false) // Toggle between published posts and drafts
    
    const navigate = useNavigate()
    const { isAuthenticated, user } = useAuth()
    
    const { posts: recentlyViewed, loading: recentLoading, error: recentError } = useRecentPosts()
    const { posts: recommended, loading: recLoading, error: recError } = usePopularPosts()
    const { posts: trendingPosts, loading: trendingLoading, error: trendingError } = usePosts({ trending: true, limit: 6 })
    
    const { posts: userPosts, loading: userPostsLoading, error: userPostsError } = usePosts(
        activeSection === 'my-posts' && user?.id ? { 
            author_id: user.id,
            published: true 
        } : { skip: true }
    )
    
    const { drafts: userDrafts, loading: draftsLoading, error: draftsError } = useUserDraftPosts(
        activeSection === 'my-posts' ? {} : { skip: true }
    )

    const handleSectionChange = useCallback((section) => {
        setActiveSection(section)
        setShowDrafts(false)
    }, [])
    
    const handleToggleDrafts = useCallback(() => {
        setShowDrafts(!showDrafts)
    }, [showDrafts])
    
    const handleDraftPublish = useCallback((postId) => {
        console.log('Publishing draft:', postId)
    }, [])
    
    const handlePostDelete = useCallback((postId) => {
        // TODO: Implement delete post functionality  
        console.log('Deleting post:', postId)
    }, [])

    const readingList = []
    const bookmarks = []
    const recentlyViewedPosts = recentlyViewed?.slice(0, 4) || []

    if (!isAuthenticated) {
        navigate('/auth/login')
        return null
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
                        <UserProfileDropdown className="ms-4" />
                    </Navbar.Collapse>
                </HeaderNav>
            </Header>
            {/* Header End */}

            {/* Page Title Section Start */}
            <section className="bg-darkgray py-[25px] page-title-small">
                <Container>
                    <Row className="items-center justify-center">
                        <Col xl={8} lg={6}>
                            <h1 className="font-serif text-lg text-white font-medium mb-0 md:text-center">
                                Dashboard
                            </h1>
                        </Col>
                        <Col xl={4} lg={6} className="breadcrumb justify-end text-sm font-serif mb-0 md:mt-[10px] md:justify-center">
                            <ul className="xs:text-center">
                                <li><Link aria-label="homepage" to="/" className="hover:text-white">Home</Link></li>
                                <li>Dashboard</li>
                            </ul>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Page Title Section End */}

            {/* Dashboard Section Start */}
            <section className="bg-lightgray py-[50px] sm:py-[60px] md:py-[75px] lg:py-[90px] xl:py-[130px]">
                <Container className="px-4 sm:px-6">
                    <Row>
                        <Col xs={12}>
                            {/* Welcome Section */}
                            <m.div 
                                className="text-center mb-10 lg:mb-12"
                                {...fadeIn}
                            >
                                {/* Welcome Message */}
                                <div className="mb-6">
                                    <h2 className="font-serif text-darkgray text-xl sm:text-2xl lg:text-3xl font-medium mb-3">
                                        Welcome back, {user?.full_name || user?.username}
                                    </h2>
                                    <p className="text-spanishgray text-sm sm:text-md lg:text-lg">
                                        Ready to discover something interesting today?
                                    </p>
                                </div>
                                
                                {/* Quick Actions - Centered below welcome message */}
                                <div className="flex justify-center items-center gap-4">
                                    <Buttons
                                        to="/"
                                        ariaLabel="explore posts"
                                        className="font-medium font-serif uppercase border-2 border-[#232323] bg-white text-[#232323] hover:bg-[#232323] hover:text-white transition-all duration-300"
                                        size="xs"
                                        color="#232323"
                                        icon="feather-arrow-right"
                                        iconPosition="after"
                                        title="Explore Posts"
                                    />
                                    <Buttons
                                        to="/posts/create"
                                        ariaLabel="create new post"
                                        className="font-medium font-serif uppercase btn-fill"
                                        themeColor="#232323"
                                        size="xs"
                                        color="#fff"
                                        icon="feather-edit"
                                        iconPosition="after"
                                        title="Write Post"
                                    />
                                </div>
                            </m.div>

                            {/* Navigation Tabs */}
                            <m.div className="mb-8 md:mb-10" {...fadeIn}>
                                <div className="flex flex-wrap border-b border-[#dfdfdf] overflow-x-auto">
                                    {[
                                        { id: 'overview', label: 'Overview', icon: 'feather-home', count: null },
                                        { id: 'reading-list', label: 'Reading List', icon: 'feather-bookmark', count: readingList.length },
                                        { id: 'my-posts', label: 'My Posts', icon: 'feather-edit-3', count: (userPosts?.length || 0) + (userDrafts?.length || 0) }
                                    ].map(tab => (
                                        <button
                                            key={tab.id}
                                            onClick={() => handleSectionChange(tab.id)}
                                            className={`flex items-center px-4 sm:px-6 py-3 sm:py-4 font-medium text-xs sm:text-sm border-b-2 transition-all duration-300 whitespace-nowrap ${
                                                activeSection === tab.id 
                                                    ? 'border-fastblue text-fastblue bg-blue-50' 
                                                    : 'border-transparent text-spanishgray hover:text-darkgray hover:bg-gray-50'
                                            }`}
                                        >
                                            <i className={`${tab.icon} mr-1 sm:mr-2`}></i>
                                            <span className="hidden xs:inline">{tab.label}</span>
                                            <span className="xs:hidden">{tab.label.split(' ')[0]}</span>
                                            {tab.count !== null && <span className="ml-1">({tab.count})</span>}
                                        </button>
                                    ))}
                                </div>
                            </m.div>

                            {/* Content Sections */}
                            {activeSection === 'overview' && (
                                <m.div {...fadeIn}>
                                    {/* Recently Viewed Posts */}
                                    <div className="mb-16">
                                        <div className="flex justify-between items-center mb-8">
                                            <div>
                                                <h3 className="font-serif text-darkgray text-lg sm:text-xl lg:text-2xl font-medium mb-2 flex items-center">
                                                    <i className="feather-clock mr-2 sm:mr-3 text-fastblue text-sm sm:text-base"></i>
                                                    Recently Viewed
                                                </h3>
                                                <p className="text-spanishgray">
                                                    Continue reading where you left off
                                                </p>
                                            </div>
                                            <Link 
                                                to="/reading-history" 
                                                className="text-fastblue hover:text-darkgray transition-colors text-sm font-medium"
                                            >
                                                View All →
                                            </Link>
                                        </div>
                                        
                                        {recentlyViewedPosts.length > 0 ? (
                                            <BlogWidget
                                                filter={false}
                                                data={recentlyViewedPosts}
                                                link="/posts/"
                                                grid="grid grid-1col gutter-large"
                                                pagination={false}
                                                showActions={false}
                                            />
                                        ) : (
                                            <div className="text-center py-12 bg-white rounded-lg shadow-sm">
                                                <div className="text-4xl sm:text-5xl lg:text-6xl mb-3 sm:mb-4 text-spanishgray">
                                                    <i className="feather-book-open"></i>
                                                </div>
                                                <h4 className="font-serif text-darkgray text-base sm:text-lg lg:text-xl mb-2">No reading history yet</h4>
                                                <p className="text-spanishgray mb-6">Start exploring posts to build your reading history</p>
                                                <Buttons
                                                    to="/"
                                                    ariaLabel="explore posts"
                                                    className="font-medium font-serif uppercase btn-fill"
                                                    themeColor="#232323"
                                                    size="xs"
                                                    color="#fff"
                                                    title="Start Reading"
                                                />
                                            </div>
                                        )}
                                    </div>

                                    {/* Recommended for You */}
                                    <div className="mb-16">
                                        <div className="flex justify-between items-center mb-8">
                                            <div>
                                                <h3 className="font-serif text-darkgray text-lg sm:text-xl lg:text-2xl font-medium mb-2 flex items-center">
                                                    <i className="feather-star mr-2 sm:mr-3 text-fastblue text-sm sm:text-base"></i>
                                                    Recommended for You
                                                </h3>
                                                <p className="text-spanishgray">
                                                    Based on your reading preferences
                                                </p>
                                            </div>
                                        </div>
                                        
                                        {!recLoading && recommended?.length > 0 ? (
                                            <BlogClassic 
                                                filter={false} 
                                                data={recommended.slice(0, 6)} 
                                                link="/posts/" 
                                                grid="grid grid-3col xl-grid-3col lg-grid-2col md-grid-2col sm-grid-1col xs-grid-1col gutter-large"
                                                pagination={false}
                                                animation={fadeIn}
                                                animationDelay={0.1}
                                            />
                                        ) : recLoading ? (
                                            <div className="text-center py-8">
                                                <div className="spinner-border text-fastblue" role="status">
                                                    <span className="visually-hidden">Loading...</span>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="text-center py-12 bg-white rounded-lg shadow-sm">
                                                <div className="text-4xl sm:text-5xl lg:text-6xl mb-3 sm:mb-4 text-spanishgray">
                                                    <i className="feather-target"></i>
                                                </div>
                                                <h4 className="font-serif text-darkgray text-base sm:text-lg lg:text-xl mb-2">Building your recommendations</h4>
                                                <p className="text-spanishgray">Read a few posts to get personalized recommendations</p>
                                            </div>
                                        )}
                                    </div>

                                    {/* Trending Now */}
                                    <div>
                                        <div className="flex justify-between items-center mb-8">
                                            <div>
                                                <h3 className="font-serif text-darkgray text-lg sm:text-xl lg:text-2xl font-medium mb-2 flex items-center">
                                                    <i className="feather-trending-up mr-2 sm:mr-3 text-fastblue text-sm sm:text-base"></i>
                                                    Trending Now
                                                </h3>
                                                <p className="text-spanishgray">
                                                    What everyone's talking about
                                                </p>
                                            </div>
                                        </div>
                                        
                                        {!trendingLoading && trendingPosts?.length > 0 ? (
                                            <BlogClassic 
                                                filter={false} 
                                                data={trendingPosts} 
                                                link="/posts/" 
                                                grid="grid grid-3col xl-grid-3col lg-grid-2col md-grid-2col sm-grid-1col xs-grid-1col gutter-large"
                                                pagination={false}
                            animation={fadeIn}
                            animationDelay={0.2}
                        />
                                        ) : trendingLoading ? (
                                            <div className="text-center py-8">
                                                <div className="spinner-border text-fastblue" role="status">
                                                    <span className="visually-hidden">Loading...</span>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="text-center py-12 bg-white rounded-lg shadow-sm">
                                                <div className="text-4xl sm:text-5xl lg:text-6xl mb-3 sm:mb-4 text-spanishgray">
                                                    <i className="feather-bar-chart-2"></i>
                                                </div>
                                                <h4 className="font-serif text-darkgray text-base sm:text-lg lg:text-xl mb-2">No trending posts yet</h4>
                                                <p className="text-spanishgray">Check back later for trending content</p>
                                            </div>
                                        )}
                                    </div>
                                </m.div>
                            )}

                            {activeSection === 'reading-list' && (
                                <m.div {...fadeIn}>
                                    <div className="text-center py-16 bg-white rounded-lg shadow-sm">
                                        <div className="text-4xl sm:text-5xl lg:text-6xl mb-3 sm:mb-4 text-spanishgray">
                                            <i className="feather-bookmark"></i>
                                        </div>
                                        <h3 className="font-serif text-darkgray text-base sm:text-lg lg:text-xl font-medium mb-3">
                                            Your Reading List
                                        </h3>
                                        <p className="text-spanishgray mb-6 max-w-md mx-auto">
                                            Save posts to read later. Start bookmarking content that interests you!
                                        </p>
                            <Buttons
                                            to="/"
                                            ariaLabel="explore posts"
                                            className="font-medium font-serif uppercase btn-fill"
                                            themeColor="#232323"
                                size="xs"
                                color="#fff"
                                            title="Explore Posts"
                                        />
                                    </div>
                                </m.div>
                            )}

                                                        {activeSection === 'my-posts' && (
                                <m.div {...fadeIn}>
                                    <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-8">
                                        <div className="mb-4 lg:mb-0 text-center lg:text-left">
                                            <h3 className="font-serif text-darkgray text-xl lg:text-2xl font-medium mb-2 flex items-center justify-center lg:justify-start">
                                                <i className="feather-edit-3 mr-3 text-fastblue"></i>
                                                {showDrafts ? 'Your Drafts' : 'Your Published Posts'}
                                            </h3>
                                            <p className="text-spanishgray text-sm lg:text-base">
                                                {showDrafts 
                                                    ? 'Work in progress posts that are not yet published'
                                                    : 'Manage and track your published content'
                                                }
                                            </p>
                                        </div>
                                        <div className="flex justify-center lg:justify-start xxs:flex-col xxs:items-center w-full lg:w-auto">
                                            <button
                                                onClick={handleToggleDrafts}
                                                onMouseEnter={(e) => {
                                                    if (!showDrafts) {
                                                        e.target.style.backgroundColor = '#232323';
                                                        e.target.style.color = 'white';
                                                    }
                                                }}
                                                onMouseLeave={(e) => {
                                                    if (!showDrafts) {
                                                        e.target.style.backgroundColor = 'white';
                                                        e.target.style.color = '#232323';
                                                    }
                                                }}
                                                style={{
                                                    backgroundColor: showDrafts ? '#232323' : 'white',
                                                    color: showDrafts ? 'white' : '#232323'
                                                }}
                                                className="font-medium font-serif uppercase text-xs border-2 border-[#232323] transition-all duration-300 px-3 py-2 rounded mr-6 mb-[15px] xxs:mx-0"
                                            >
                                                {showDrafts ? `Published (${userPosts?.length || 0})` : `Drafts (${userDrafts?.length || 0})`}
                                            </button>
                                            <Buttons
                                                to="/posts/create"
                                                ariaLabel="create new post"
                                                className="font-medium font-serif uppercase btn-fill mb-[15px]"
                                                themeColor="#232323"
                                                size="xs"
                                                color="#fff"
                                                title="New Post"
                                            />
                                        </div>
                                    </div>

                                                                        {showDrafts ? (
                                        // Drafts view
                                        draftsLoading ? (
                                            <div className="text-center py-8">
                                                <div className="spinner-border text-fastblue" role="status">
                                                    <span className="visually-hidden">Loading drafts...</span>
                                                </div>
                                            </div>
                                        ) : userDrafts?.length > 0 ? (
                                            <BlogWidget
                                                filter={false}
                                                data={userDrafts}
                                                link="/posts/"
                                                grid="grid grid-1col gutter-large"
                                                pagination={false}
                                                showActions={true}
                                                onPublish={handleDraftPublish}
                                                onDelete={handlePostDelete}
                                            />
                                        ) : (
                                            <div className="text-center py-16 bg-white rounded-lg shadow-sm">
                                                <div className="text-4xl sm:text-5xl lg:text-6xl mb-3 sm:mb-4 text-spanishgray">
                                                    <i className="feather-file-text"></i>
                                                </div>
                                                <h4 className="font-serif text-darkgray text-base sm:text-lg lg:text-xl mb-2">No drafts yet</h4>
                                                <p className="text-spanishgray mb-6">Start writing and save your work as drafts</p>
                            <Buttons
                                                    to="/posts/create"
                                                    ariaLabel="create new post"
                                                    className="font-medium font-serif uppercase btn-fill"
                                                    themeColor="#232323"
                                size="xs"
                                color="#fff"
                                                    title="Create Your First Draft"
                                                />
                                            </div>
                                        )
                                    ) : (
                                        // Published posts view
                                        userPostsLoading ? (
                                            <div className="text-center py-8">
                                                <div className="spinner-border text-fastblue" role="status">
                                                    <span className="visually-hidden">Loading posts...</span>
                                                </div>
                                            </div>
                                        ) : userPosts?.length > 0 ? (
                                            <BlogWidget
                                                filter={false}
                                                data={userPosts}
                                                link="/posts/"
                                                grid="grid grid-1col gutter-large"
                                                pagination={false}
                                                showActions={true}
                                                onDelete={handlePostDelete}
                                            />
                                        ) : (
                                            <div className="text-center py-16 bg-white rounded-lg shadow-sm">
                                                <div className="text-4xl sm:text-5xl lg:text-6xl mb-3 sm:mb-4 text-spanishgray">
                                                    <i className="feather-edit"></i>
                                                </div>
                                                <h4 className="font-serif text-darkgray text-base sm:text-lg lg:text-xl mb-2">No published posts yet</h4>
                                                <p className="text-spanishgray mb-6">Share your thoughts and ideas with the community</p>
                            <Buttons
                                                    to="/posts/create"
                                                    ariaLabel="create new post"
                                                    className="font-medium font-serif uppercase btn-fill"
                                                    themeColor="#232323"
                                size="xs"
                                color="#fff"
                                                    title="Write Your First Post"
                            />
                                            </div>
                                        )
                                    )}
                                </m.div>
                            )}
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Dashboard Section End */}

            {/* Footer */}
            <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
        </div>
    )
}

export default Dashboard