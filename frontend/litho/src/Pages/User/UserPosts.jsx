import React, { useState, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

// Libraries
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { m } from "framer-motion"

// Components
import { Header, HeaderNav, Menu, SearchBar } from '../../Components/Header/Header'
import Logo from '../../Components/Logo'
import UserProfileDropdown from '../../Components/Header/UserProfileDropdown'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'

import BlogWidget from '../../Components/Blogs/BlogWidget'
import Buttons from '../../Components/Button/Buttons'

// API & Auth
import { useUserDraftPosts, usePosts } from '../../api/usePosts'
import useAuth from '../../api/useAuth'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

const UserPosts = (props) => {
    const [selectedPosts, setSelectedPosts] = useState([])
    const [showBulkActions, setShowBulkActions] = useState(false)
    const [activeTab, setActiveTab] = useState('all') // 'all' or 'drafts'
    
    const navigate = useNavigate()
    const { isAuthenticated, user } = useAuth()
    
    // Fetch both drafts and all posts 
    const { drafts, loading: draftsLoading, error: draftsError, refetch: refetchDrafts } = useUserDraftPosts()
    const { posts: allPosts, loading: postsLoading, error: postsError, refetch: refetchPosts } = usePosts(
        user?.id ? { 
            author_id: user.id,
            published: true 
        } : { skip: true } 
    )
    
    // Determine which data to show based on active tab
    const currentPosts = activeTab === 'drafts' ? drafts : allPosts
    const loading = activeTab === 'drafts' ? draftsLoading : postsLoading
    const error = activeTab === 'drafts' ? draftsError : postsError
    const isDraftMode = activeTab === 'drafts'

    const handlePostDelete = useCallback((postId) => {
        refetchDrafts()
        refetchPosts()
        
        setSelectedPosts(prev => prev.filter(id => id !== postId))
        
        console.log('Post deleted successfully:', postId)
    }, [refetchDrafts, refetchPosts])

    const handleDraftPublish = useCallback((draftId, publishedPost) => {
        refetchDrafts()
        refetchPosts()
        
        setSelectedPosts(prev => prev.filter(id => id !== draftId))
        
        if (publishedPost?.post?.slug) {
            alert(`Draft published successfully! You can view it at /posts/${publishedPost.post.slug}`)
        } else {
            alert('Draft published successfully!')
        }
        
        console.log('Draft published successfully:', draftId, publishedPost)
    }, [refetchDrafts, refetchPosts])

    const handleSelectPost = useCallback((postId) => {
        setSelectedPosts(prev => {
            if (prev.includes(postId)) {
                return prev.filter(id => id !== postId)
            } else {
                return [...prev, postId]
            }
        })
    }, [])

    const handleSelectAll = useCallback(() => {
        if (selectedPosts.length === currentPosts.length) {
            setSelectedPosts([])
        } else {
            setSelectedPosts(currentPosts.map(post => post.uuid))
        }
    }, [selectedPosts.length, currentPosts])

    const handleTabChange = useCallback((tab) => {
        setActiveTab(tab)
        setSelectedPosts([]) 
    }, [])

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
                        </Navbar.Collapse>
                        <Col className="col-auto text-right pe-0">
                            <SearchBar className="xs:pl-[15px] pr-0" />
                        </Col>
                    </HeaderNav>
                </Header>
                {/* Header End */}

                
                {/* Auth Required Section */}
                <section className="bg-lightgray py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                    <Container>
                        <Row className="justify-center">
                            <Col lg={8} md={10} className="text-center">
                                <m.div {...fadeIn}>
                                    <i className="feather-lock text-6xl text-spanishgray mb-6"></i>
                                    <h2 className="font-serif text-darkgray mb-6">Authentication Required</h2>
                                    <p className="text-spanishgray mb-8 text-lg">
                                        Please log in to view and manage your posts.
                                    </p>
                                    <Link 
                                        to="/" 
                                        className="btn btn-large btn-dark-gray btn-box-shadow font-medium font-serif uppercase inline-block"
                                    >
                                        Go to Homepage
                                    </Link>
                                </m.div>
                            </Col>
                        </Row>
                    </Container>
                </section>

                {/* Footer Start */}
                <FooterStyle05 theme="dark" className="bg-[#262b35] text-slateblue" />
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
                                My Posts
                            </h1>
                        </Col>
                        <Col xl={4} lg={6} className="breadcrumb justify-end text-sm font-serif mb-0 md:mt-[10px] md:justify-center">
                            <ul className="xs:text-center">
                                <li><Link aria-label="homepage" to="/" className="hover:text-white">Home</Link></li>
                                <li><Link aria-label="user dashboard" to="/dashboard" className="hover:text-white">Dashboard</Link></li>
                                <li>Posts</li>
                            </ul>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Page Title Section End */}

            {/* Posts Section Start */}
            <section className="bg-lightgray py-[50px] sm:py-[60px] md:py-[75px] lg:py-[90px] xl:py-[130px]">
                <Container className="px-4 sm:px-6">
                    <Row>
                        <Col xs={12}>
                            {/* Create Post Action */}
                            <m.div 
                                className="flex justify-center md:justify-end mb-8"
                                {...fadeIn}
                            >
                                <Buttons
                                    to="/posts/create"
                                    ariaLabel="create new post"
                                    className="font-medium font-serif uppercase text-sm btn-fill"
                                    themeColor="#232323"
                                    size="sm"
                                    color="#fff"
                                    title="Create New Post"
                                />
                            </m.div>

                            {/* Tab Navigation */}
                            <m.div className="mb-8" {...fadeIn}>
                                <div className="flex flex-wrap border-b border-[#dfdfdf] overflow-x-auto">
                                    <button
                                        onClick={() => handleTabChange('all')}
                                        className={`px-4 sm:px-6 py-3 font-medium text-xs sm:text-sm border-b-2 transition-colors whitespace-nowrap ${
                                            activeTab === 'all' 
                                                ? 'border-fastblue text-fastblue' 
                                                : 'border-transparent text-spanishgray hover:text-darkgray'
                                        }`}
                                    >
                                        All Posts ({allPosts?.length || 0})
                                    </button>
                                    <button
                                        onClick={() => handleTabChange('drafts')}
                                        className={`px-4 sm:px-6 py-3 font-medium text-xs sm:text-sm border-b-2 transition-colors whitespace-nowrap ${
                                            activeTab === 'drafts' 
                                                ? 'border-fastblue text-fastblue' 
                                                : 'border-transparent text-spanishgray hover:text-darkgray'
                                        }`}
                                    >
                                        Drafts ({drafts?.length || 0})
                                    </button>
                                </div>
                            </m.div>

                            {/* Loading State */}
                            {loading && (
                                <m.div className="text-center py-12 sm:py-16" {...fadeIn}>
                                    <div className="spinner-border text-fastblue" role="status">
                                        <span className="visually-hidden">Loading...</span>
                                    </div>
                                    <p className="mt-4 text-spanishgray text-sm sm:text-base">Loading your {activeTab === 'drafts' ? 'drafts' : 'posts'}...</p>
                                </m.div>
                            )}

                            {/* Error State */}
                            {error && (
                                <m.div 
                                    className="bg-red-100 border border-red-400 text-red-700 px-4 sm:px-6 py-4 rounded-lg mb-8"
                                    {...fadeIn}
                                >
                                    <div className="flex flex-col sm:flex-row items-start sm:items-center">
                                        <i className="feather-alert-circle text-xl mr-0 sm:mr-3 mb-2 sm:mb-0"></i>
                                        <div className="text-center sm:text-left">
                                            <h4 className="font-medium mb-1 text-sm sm:text-base">Error Loading {activeTab === 'drafts' ? 'Drafts' : 'Posts'}</h4>
                                            <p className="text-xs sm:text-sm mb-0">{error}</p>
                                        </div>
                                    </div>
                                </m.div>
                            )}

                            {/* No Posts State */}
                            {!loading && !error && currentPosts.length === 0 && (
                                <m.div className="text-center py-12 sm:py-16 px-4" {...fadeIn}>
                                    <i className="feather-edit text-4xl sm:text-6xl text-spanishgray mb-4 sm:mb-6"></i>
                                    <h3 className="font-serif text-darkgray mb-3 sm:mb-4 text-lg sm:text-xl">
                                        No {activeTab === 'drafts' ? 'Draft Posts' : 'Posts'}
                                    </h3>
                                    <p className="text-spanishgray mb-6 sm:mb-8 text-sm sm:text-lg max-w-md mx-auto">
                                        {activeTab === 'drafts' 
                                            ? "You haven't created any draft posts yet. Start writing your first post!"
                                            : "You haven't published any posts yet. Start writing your first post!"
                                        }
                                    </p>
                                    <Buttons
                                        to="/posts/create"
                                        ariaLabel="create first post"
                                        className="font-medium font-serif uppercase text-sm btn-fill"
                                        themeColor="#232323"
                                        size="sm"
                                        color="#fff"
                                        title="Create Your First Post"
                                    />
                                </m.div>
                            )}

                            {/* Posts Grid */}
                            {!loading && !error && currentPosts.length > 0 && (
                                <m.div {...fadeIn}>
                                    {/* Bulk Actions */}
                                    {selectedPosts.length > 0 && (
                                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 sm:p-4 mb-6">
                                            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
                                                <span className="text-xs sm:text-sm text-blue-800 text-center sm:text-left">
                                                    {selectedPosts.length} {activeTab === 'drafts' ? 'draft' : 'post'}{selectedPosts.length > 1 ? 's' : ''} selected
                                                </span>
                                                <div className="flex justify-center sm:justify-start gap-4 sm:gap-3 w-full sm:w-auto">
                                                    {activeTab === 'drafts' && (
                                                        <button className="text-xs sm:text-sm text-blue-600 hover:text-blue-800 font-medium">
                                                            Bulk Publish
                                                        </button>
                                                    )}
                                                    <button className="text-xs sm:text-sm text-red-600 hover:text-red-800 font-medium">
                                                        Bulk Delete
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Select All */}
                                    <div className="flex items-center justify-between mb-6">
                                        <div className="flex items-center">
                                            <button
                                                onClick={handleSelectAll}
                                                className="text-sm text-fastblue hover:text-blue-600 flex items-center"
                                            >
                                                <i className={`feather-${selectedPosts.length === currentPosts.length ? 'check-' : ''}square mr-2`}></i>
                                                {selectedPosts.length === currentPosts.length ? 'Deselect All' : 'Select All'}
                                            </button>
                                        </div>
                                        <p className="text-sm text-spanishgray">
                                            {currentPosts.length} {activeTab === 'drafts' ? 'draft' : 'post'}{currentPosts.length > 1 ? 's' : ''} found
                                        </p>
                                    </div>

                                    {/* Posts List */}
                                    <BlogWidget
                                        filter={false}
                                        data={currentPosts}
                                        link="/posts/"
                                        grid="grid grid-1col gutter-large"
                                        pagination={false}
                                        onPublish={isDraftMode ? handleDraftPublish : undefined}
                                        onDelete={handlePostDelete}
                                    />
                                </m.div>
                            )}
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Posts Section End */}

            {/* Footer Start */}
            <FooterStyle05 theme="dark" className="bg-[#262b35] text-slateblue" />
            {/* Footer End */}
        </div>
    )
}

export default UserPosts