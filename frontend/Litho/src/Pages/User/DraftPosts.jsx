import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

// Libraries
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { m } from "framer-motion"

// Components
import { Header, HeaderCart, HeaderLanguage, HeaderNav, Menu, SearchBar } from '../../Components/Header/Header'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'
import SideButtons from "../../Components/SideButtons"
import DraftPostCard from '../../Components/Posts/DraftPostCard'
import Buttons from '../../Components/Button/Buttons'

// API & Auth
import { useUserDraftPosts } from '../../api/usePosts'
import useAuth from '../../api/useAuth'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

const DraftPosts = (props) => {
    const [selectedDrafts, setSelectedDrafts] = useState([])
    const [showBulkActions, setShowBulkActions] = useState(false)
    
    const navigate = useNavigate()
    const { isAuthenticated, user } = useAuth()
    const { drafts, loading, error, refetch } = useUserDraftPosts()

    const handleDraftDelete = useCallback((draftId) => {
        refetch()
        
        setSelectedDrafts(prev => prev.filter(id => id !== draftId))
    }, [refetch])

    const handleDraftPublish = useCallback((draftId, publishedPost) => {
        refetch()
        
        setSelectedDrafts(prev => prev.filter(id => id !== draftId))
        
        alert(`Draft published successfully! You can view it at /posts/${publishedPost.post.slug}`)
    }, [refetch])

    const handleSelectDraft = useCallback((draftId) => {
        setSelectedDrafts(prev => {
            if (prev.includes(draftId)) {
                return prev.filter(id => id !== draftId)
            } else {
                return [...prev, draftId]
            }
        })
    }, [])

    const handleSelectAll = useCallback(() => {
        if (selectedDrafts.length === drafts.length) {
            setSelectedDrafts([])
        } else {
            setSelectedDrafts(drafts.map(draft => draft.uuid))
        }
    }, [selectedDrafts.length, drafts])

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
                <SideButtons />
                
                {/* Auth Required Section */}
                <section className="bg-lightgray py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                    <Container>
                        <Row className="justify-center">
                            <Col lg={8} md={10} className="text-center">
                                <m.div {...fadeIn}>
                                    <i className="feather-lock text-6xl text-spanishgray mb-6"></i>
                                    <h2 className="font-serif text-darkgray mb-6">Authentication Required</h2>
                                    <p className="text-spanishgray mb-8 text-lg">
                                        Please log in to view and manage your draft posts.
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
                                My Draft Posts
                            </h1>
                        </Col>
                        <Col xl={4} lg={6} className="breadcrumb justify-end text-sm font-serif mb-0 md:mt-[10px] md:justify-center">
                            <ul className="xs:text-center">
                                <li><Link aria-label="homepage" to="/" className="hover:text-white">Home</Link></li>
                                <li><Link aria-label="user dashboard" to="/user" className="hover:text-white">Dashboard</Link></li>
                                <li>Drafts</li>
                            </ul>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Page Title Section End */}

            {/* Draft Posts Section Start */}
            <section className="bg-lightgray py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                <Container>
                    <Row>
                        <Col xs={12}>
                            {/* User Info & Actions */}
                            <m.div 
                                className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8"
                                {...fadeIn}
                            >
                                <div className="mb-4 sm:mb-0">
                                    <h2 className="font-serif text-darkgray text-2xl font-medium mb-2">
                                        Welcome back, {user?.full_name || user?.username}
                                    </h2>
                                    <p className="text-spanishgray">
                                        Manage your draft posts and publish them when ready.
                                    </p>
                                </div>
                                <Link to="/posts/create">
                                    <Buttons
                                        ariaLabel="create new post"
                                        className="font-medium font-serif uppercase text-sm"
                                        themeColor={["#0038e3", "#ff7a56"]}
                                        size="md"
                                        color="#fff"
                                        title="Create New Post"
                                    />
                                </Link>
                            </m.div>

                            {/* Loading State */}
                            {loading && (
                                <m.div className="text-center py-16" {...fadeIn}>
                                    <div className="spinner-border text-fastblue" role="status">
                                        <span className="visually-hidden">Loading...</span>
                                    </div>
                                    <p className="mt-4 text-spanishgray">Loading your drafts...</p>
                                </m.div>
                            )}

                            {/* Error State */}
                            {error && (
                                <m.div 
                                    className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg mb-8"
                                    {...fadeIn}
                                >
                                    <div className="flex items-center">
                                        <i className="feather-alert-circle text-xl mr-3"></i>
                                        <div>
                                            <h4 className="font-medium mb-1">Error Loading Drafts</h4>
                                            <p className="text-sm mb-0">{error}</p>
                                        </div>
                                    </div>
                                </m.div>
                            )}

                            {/* No Drafts State */}
                            {!loading && !error && drafts.length === 0 && (
                                <m.div className="text-center py-16" {...fadeIn}>
                                    <i className="feather-edit text-6xl text-spanishgray mb-6"></i>
                                    <h3 className="font-serif text-darkgray mb-4">No Draft Posts</h3>
                                    <p className="text-spanishgray mb-8 text-lg">
                                        You haven't created any draft posts yet. Start writing your first post!
                                    </p>
                                    <Link to="/posts/create">
                                        <Buttons
                                            ariaLabel="create first post"
                                            className="font-medium font-serif uppercase text-sm"
                                            themeColor={["#0038e3", "#ff7a56"]}
                                            size="lg"
                                            color="#fff"
                                            title="Create Your First Post"
                                        />
                                    </Link>
                                </m.div>
                            )}

                            {/* Drafts Grid */}
                            {!loading && !error && drafts.length > 0 && (
                                <m.div {...fadeIn}>
                                    {/* Bulk Actions */}
                                    {selectedDrafts.length > 0 && (
                                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                                            <div className="flex items-center justify-between">
                                                <span className="text-sm text-blue-800">
                                                    {selectedDrafts.length} draft{selectedDrafts.length > 1 ? 's' : ''} selected
                                                </span>
                                                <div className="flex space-x-3">
                                                    <button className="text-sm text-blue-600 hover:text-blue-800">
                                                        Bulk Publish
                                                    </button>
                                                    <button className="text-sm text-red-600 hover:text-red-800">
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
                                                <i className={`feather-${selectedDrafts.length === drafts.length ? 'check-' : ''}square mr-2`}></i>
                                                {selectedDrafts.length === drafts.length ? 'Deselect All' : 'Select All'}
                                            </button>
                                        </div>
                                        <p className="text-sm text-spanishgray">
                                            {drafts.length} draft{drafts.length > 1 ? 's' : ''} found
                                        </p>
                                    </div>

                                    {/* Drafts Grid */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        {drafts.map((draft, index) => (
                                            <DraftPostCard
                                                key={draft.uuid}
                                                post={draft}
                                                onDelete={handleDraftDelete}
                                                onPublish={handleDraftPublish}
                                                transition={{ delay: index * 0.1 }}
                                            />
                                        ))}
                                    </div>
                                </m.div>
                            )}
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Draft Posts Section End */}

            {/* Footer Start */}
            <FooterStyle05 theme="dark" className="bg-[#262b35] text-slateblue" />
            {/* Footer End */}
        </div>
    )
}

export default DraftPosts