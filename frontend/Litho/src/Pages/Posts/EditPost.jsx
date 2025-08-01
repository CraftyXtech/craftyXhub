import React, { useState, useCallback, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { m } from "framer-motion"
import { Header, HeaderCart, HeaderLanguage, HeaderNav, Menu, SearchBar } from '../../Components/Header/Header'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'
import SideButtons from "../../Components/SideButtons"
import PostForm from '../../Components/Posts/PostForm'
import { usePost, useUpdatePost } from '../../api/usePosts'
import useAuth from '../../api/useAuth'
import { fadeIn } from '../../Functions/GlobalAnimations'

const EditPost = (props) => {
    const [submitSuccess, setSubmitSuccess] = useState(false)
    const [submitError, setSubmitError] = useState('')
    
    const { slug } = useParams()
    const navigate = useNavigate()
    const { isAuthenticated, user } = useAuth()
    const { post, loading: postLoading, error: postError } = usePost(slug)
    const { updatePost, loading: updateLoading, error: updateError } = useUpdatePost()

    // Check if user owns this post
    const [canEdit, setCanEdit] = useState(false)

    useEffect(() => {
        if (post && user) {
            setCanEdit(post.author?.uuid === user.uuid || user.is_admin)
        }
    }, [post, user])

    const handleSubmit = useCallback(async (postData) => {
        try {
            setSubmitError('')
            setSubmitSuccess(false)
            
            const result = await updatePost(post.uuid, postData)
            
            setSubmitSuccess(true)
            
            setTimeout(() => {
                navigate(`/posts/${result.post.slug}`)
            }, 2000)
            
        } catch (error) {
            console.error('Error updating post:', error)
            setSubmitError(error.message || 'Failed to update post. Please try again.')
        }
    }, [updatePost, post?.uuid, navigate])

    const handleSaveDraft = useCallback(async (postData) => {
        try {
            setSubmitError('')
            
            const draftData = { ...postData, is_published: false }
            await updatePost(post.uuid, draftData)
            
            alert('Post converted to draft successfully!')
            navigate('/user/drafts')
            
        } catch (error) {
            console.error('Error converting to draft:', error)
            setSubmitError(error.message || 'Failed to convert to draft. Please try again.')
        }
    }, [updatePost, post?.uuid, navigate])

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
                                    <img className="alt-logo" width="111" height="36" loading="lazy" src='/assets/img/webp/logo-fast-blue-black@2x.webp' alt='logo' />
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
                                        Please log in to edit posts.
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

    // Show loading state while fetching post
    if (postLoading) {
        return (
            <div style={props.style}>
                <Header topSpace={{ desktop: true }} type="reverse-scroll">
                    <HeaderNav fluid="fluid" theme="light" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" containerClass="sm:px-0">
                        <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                            <Link aria-label="header logo" className="flex items-center" to="/">
                                <Navbar.Brand className="inline-block p-0 m-0">
                                    <img className="default-logo" width="111" height="36" loading="lazy" src='/assets/img/webp/logo-fast-blue-black.webp' data-rjs='/assets/img/webp/logo-fast-blue-black@2x.webp' alt='logo' />
                                </Navbar.Brand>
                            </Link>
                        </Col>
                        <Navbar.Collapse className="col-auto px-0 justify-end">
                            <Menu {...props} />
                        </Navbar.Collapse>
                    </HeaderNav>
                </Header>
                <SideButtons />
                
                <section className="bg-lightgray py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                    <Container>
                        <Row className="justify-center">
                            <Col lg={8} md={10} className="text-center">
                                <m.div {...fadeIn}>
                                    <div className="spinner-border text-fastblue" role="status">
                                        <span className="visually-hidden">Loading...</span>
                                    </div>
                                    <p className="mt-4 text-spanishgray">Loading post...</p>
                                </m.div>
                            </Col>
                        </Row>
                    </Container>
                </section>

                <FooterStyle05 theme="dark" className="bg-[#262b35] text-slateblue" />
            </div>
        )
    }

    // Show error if post not found or error loading
    if (postError || !post) {
        return (
            <div style={props.style}>
                <Header topSpace={{ desktop: true }} type="reverse-scroll">
                    <HeaderNav fluid="fluid" theme="light" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" containerClass="sm:px-0">
                        <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                            <Link aria-label="header logo" className="flex items-center" to="/">
                                <Navbar.Brand className="inline-block p-0 m-0">
                                    <img className="default-logo" width="111" height="36" loading="lazy" src='/assets/img/webp/logo-fast-blue-black.webp' data-rjs='/assets/img/webp/logo-fast-blue-black@2x.webp' alt='logo' />
                                </Navbar.Brand>
                            </Link>
                        </Col>
                        <Navbar.Collapse className="col-auto px-0 justify-end">
                            <Menu {...props} />
                        </Navbar.Collapse>
                    </HeaderNav>
                </Header>
                <SideButtons />
                
                <section className="bg-lightgray py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                    <Container>
                        <Row className="justify-center">
                            <Col lg={8} md={10} className="text-center">
                                <m.div {...fadeIn}>
                                    <i className="feather-alert-circle text-6xl text-red-500 mb-6"></i>
                                    <h2 className="font-serif text-darkgray mb-6">Post Not Found</h2>
                                    <p className="text-spanishgray mb-8 text-lg">
                                        The post you're trying to edit could not be found or you don't have permission to edit it.
                                    </p>
                                    <Link 
                                        to="/user/drafts" 
                                        className="btn btn-large btn-dark-gray btn-box-shadow font-medium font-serif uppercase inline-block mr-4"
                                    >
                                        My Drafts
                                    </Link>
                                    <Link 
                                        to="/" 
                                        className="btn btn-large btn-transparent-black btn-box-shadow font-medium font-serif uppercase inline-block"
                                    >
                                        Go Home
                                    </Link>
                                </m.div>
                            </Col>
                        </Row>
                    </Container>
                </section>

                <FooterStyle05 theme="dark" className="bg-[#262b35] text-slateblue" />
            </div>
        )
    }

    // Show permission error if user can't edit
    if (!canEdit) {
        return (
            <div style={props.style}>
                <Header topSpace={{ desktop: true }} type="reverse-scroll">
                    <HeaderNav fluid="fluid" theme="light" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" containerClass="sm:px-0">
                        <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                            <Link aria-label="header logo" className="flex items-center" to="/">
                                <Navbar.Brand className="inline-block p-0 m-0">
                                    <img className="default-logo" width="111" height="36" loading="lazy" src='/assets/img/webp/logo-fast-blue-black.webp' data-rjs='/assets/img/webp/logo-fast-blue-black@2x.webp' alt='logo' />
                                </Navbar.Brand>
                            </Link>
                        </Col>
                        <Navbar.Collapse className="col-auto px-0 justify-end">
                            <Menu {...props} />
                        </Navbar.Collapse>
                    </HeaderNav>
                </Header>
                <SideButtons />
                
                <section className="bg-lightgray py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                    <Container>
                        <Row className="justify-center">
                            <Col lg={8} md={10} className="text-center">
                                <m.div {...fadeIn}>
                                    <i className="feather-shield text-6xl text-yellow-500 mb-6"></i>
                                    <h2 className="font-serif text-darkgray mb-6">Permission Denied</h2>
                                    <p className="text-spanishgray mb-8 text-lg">
                                        You don't have permission to edit this post. Only the author can edit their posts.
                                    </p>
                                    <Link 
                                        to={`/posts/${post.slug}`}
                                        className="btn btn-large btn-dark-gray btn-box-shadow font-medium font-serif uppercase inline-block mr-4"
                                    >
                                        View Post
                                    </Link>
                                    <Link 
                                        to="/" 
                                        className="btn btn-large btn-transparent-black btn-box-shadow font-medium font-serif uppercase inline-block"
                                    >
                                        Go Home
                                    </Link>
                                </m.div>
                            </Col>
                        </Row>
                    </Container>
                </section>

                <FooterStyle05 theme="dark" className="bg-[#262b35] text-slateblue" />
            </div>
        )
    }

    // Prepare initial values for the form
    const initialValues = {
        title: post.title || '',
        content: post.content || '',
        excerpt: post.excerpt || '',
        category_id: post.category?.id || '',
        tag_ids: post.tags?.map(tag => tag.id) || [],
        meta_title: post.meta_title || '',
        meta_description: post.meta_description || '',
        reading_time: post.reading_time || '',
        slug: post.slug || '',
        featured_image: post.featured_image || null
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
                                Edit Post
                            </h1>
                        </Col>
                        <Col xl={4} lg={6} className="breadcrumb justify-end text-sm font-serif mb-0 md:mt-[10px] md:justify-center">
                            <ul className="xs:text-center">
                                <li><Link aria-label="homepage" to="/" className="hover:text-white">Home</Link></li>
                                <li><Link aria-label="posts" to="/posts" className="hover:text-white">Posts</Link></li>
                                <li><Link aria-label="view post" to={`/posts/${post.slug}`} className="hover:text-white">View</Link></li>
                                <li>Edit</li>
                            </ul>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Page Title Section End */}

            {/* Edit Post Section Start */}
            <section className="bg-lightgray py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                <Container>
                    <Row className="justify-center">
                        <Col xl={10} lg={12}>
                            {/* Success Message */}
                            {submitSuccess && (
                                <m.div 
                                    className="bg-green-100 border border-green-400 text-green-700 px-6 py-4 rounded-lg mb-8"
                                    {...fadeIn}
                                >
                                    <div className="flex items-center">
                                        <i className="feather-check-circle text-xl mr-3"></i>
                                        <div>
                                            <h4 className="font-medium mb-1">Post Updated Successfully!</h4>
                                            <p className="text-sm mb-0">Redirecting to your updated post...</p>
                                        </div>
                                    </div>
                                </m.div>
                            )}

                            {/* Error Message */}
                            {(submitError || updateError) && (
                                <m.div 
                                    className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg mb-8"
                                    {...fadeIn}
                                >
                                    <div className="flex items-center">
                                        <i className="feather-alert-circle text-xl mr-3"></i>
                                        <div>
                                            <h4 className="font-medium mb-1">Error</h4>
                                            <p className="text-sm mb-0">{submitError || updateError}</p>
                                        </div>
                                    </div>
                                </m.div>
                            )}

                            {/* Post Form */}
                            <m.div 
                                className="bg-white rounded-lg shadow-sm p-8 lg:p-6 md:p-4"
                                {...fadeIn}
                            >
                                <div className="mb-8">
                                    <h2 className="font-serif text-darkgray text-2xl font-medium mb-4">Edit Your Post</h2>
                                    <p className="text-spanishgray">
                                        Update your post content, images, and settings. Changes will be saved when you publish.
                                    </p>
                                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                                        <div className="flex items-center">
                                            <i className="feather-info text-blue-500 mr-2"></i>
                                            <div className="text-sm text-blue-800">
                                                <strong>Current Status:</strong> {post.is_published ? 'Published' : 'Draft'} | 
                                                <strong className="ml-2">Last Updated:</strong> {new Date(post.updated_at).toLocaleDateString()}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <PostForm
                                    initialValues={initialValues}
                                    onSubmit={handleSubmit}
                                    onSaveDraft={post.is_published ? handleSaveDraft : undefined}
                                    loading={updateLoading}
                                    isEdit={true}
                                    submitButtonText={post.is_published ? "Update Post" : "Publish Post"}
                                    draftButtonText="Convert to Draft"
                                    showAdvancedFields={true}
                                />
                            </m.div>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Edit Post Section End */}

            {/* Footer Start */}
            <FooterStyle05 theme="dark" className="bg-[#262b35] text-slateblue" />
            {/* Footer End */}
        </div>
    )
}

export default EditPost