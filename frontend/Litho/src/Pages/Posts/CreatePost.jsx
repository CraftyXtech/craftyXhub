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
import PostForm from '../../Components/Posts/PostForm'
import { useCreatePost, useSaveAsDraft } from '../../api/usePosts'
import useAuth from '../../api/useAuth'
import { fadeIn } from '../../Functions/GlobalAnimations'

const CreatePost = (props) => {
    const [submitSuccess, setSubmitSuccess] = useState(false)
    const [submitError, setSubmitError] = useState('')
    
    const navigate = useNavigate()
    const { isAuthenticated } = useAuth()
    const { createPost, loading: createLoading, error: createError } = useCreatePost()
    const { saveAsDraft, loading: draftLoading, error: draftError } = useSaveAsDraft()

    const handleSubmit = useCallback(async (postData) => {
        try {
            setSubmitError('')
            setSubmitSuccess(false)
            
            const result = await createPost(postData)
            
            setSubmitSuccess(true)
            
            setTimeout(() => {
                navigate(`/posts/${result.post.uuid}`)
            }, 2000)
            
        } catch (error) {
            console.error('Error creating post:', error)
            setSubmitError(error.message || 'Failed to create post. Please try again.')
        }
    }, [createPost, navigate])

    const handleSaveDraft = useCallback(async (postData) => {
        try {
            setSubmitError('')
            
            const result = await saveAsDraft(postData)
            
            alert('Post saved as draft successfully!')
            navigate('/user/drafts')
            
        } catch (error) {
            console.error('Error saving draft:', error)
            setSubmitError(error.message || 'Failed to save draft. Please try again.')
        }
    }, [saveAsDraft, navigate])

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
                                        Please log in to create and publish posts on our platform.
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
                                Create New Post
                            </h1>
                        </Col>
                        <Col xl={4} lg={6} className="breadcrumb justify-end text-sm font-serif mb-0 md:mt-[10px] md:justify-center">
                            <ul className="xs:text-center">
                                <li><Link aria-label="homepage" to="/" className="hover:text-white">Home</Link></li>
                                <li><Link aria-label="posts" to="/posts" className="hover:text-white">Posts</Link></li>
                                <li>Create</li>
                            </ul>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Page Title Section End */}

            {/* Create Post Section Start */}
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
                                            <h4 className="font-medium mb-1">Post Created Successfully!</h4>
                                            <p className="text-sm mb-0">Redirecting to your new post...</p>
                                        </div>
                                    </div>
                                </m.div>
                            )}

                            {/* Error Message */}
                            {(submitError || createError || draftError) && (
                                <m.div 
                                    className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg mb-8"
                                    {...fadeIn}
                                >
                                    <div className="flex items-center">
                                        <i className="feather-alert-circle text-xl mr-3"></i>
                                        <div>
                                            <h4 className="font-medium mb-1">Error</h4>
                                            <p className="text-sm mb-0">{submitError || createError || draftError}</p>
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
                                    <h2 className="font-serif text-darkgray text-2xl font-medium mb-4">Create Your Post</h2>
                                    <p className="text-spanishgray">
                                        Share your thoughts, insights, and stories with our community. 
                                        Fill out the form below to create your new post.
                                    </p>
                                </div>

                                <PostForm
                                    onSubmit={handleSubmit}
                                    onSaveDraft={handleSaveDraft}
                                    loading={createLoading}
                                    submitButtonText="Publish Post"
                                    draftButtonText="Save as Draft"
                                    showAdvancedFields={true}
                                />
                            </m.div>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Create Post Section End */}

            {/* Footer Start */}
            <FooterStyle05 theme="dark" className="bg-[#262b35] text-slateblue" />
            {/* Footer End */}
        </div>
    )
}

export default CreatePost