import React, { useState, useCallback, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

// Libraries
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { m } from "framer-motion"

// Components
import { Header, HeaderNav, Menu, SearchBar } from '../../Components/Header/Header'
import Logo from '../../Components/Logo'
import UserProfileDropdown from '../../Components/Header/UserProfileDropdown'
import EditorOnlyPostForm from '../../Components/Posts/EditorOnlyPostForm'
import Buttons from '../../Components/Button/Buttons'

// API & Hooks
import { useCreatePost, useSaveAsDraft, usePost, useUpdatePost } from '../../api/usePosts'
import useAuth from '../../api/useAuth'

// Utilities
import { fadeIn } from '../../Functions/GlobalAnimations'

const CreatePost = (props) => {
    const [submitSuccess, setSubmitSuccess] = useState(false)
    const [submitError, setSubmitError] = useState('')
    const [canEdit, setCanEdit] = useState(false)
    
    const { uuid } = useParams()
    const navigate = useNavigate()
    const { isAuthenticated, user } = useAuth()
    
    // Determine if we're in edit mode
    const isEditMode = !!uuid
    
    // API hooks
    const { createPost, loading: createLoading, error: createError } = useCreatePost()
    const { saveAsDraft, loading: saveLoading, error: draftError } = useSaveAsDraft()
    const { post, loading: postLoading, error: postError } = usePost(uuid)
    const { updatePost, loading: updateLoading, error: updateError } = useUpdatePost()

    // Check if user owns this post (for edit mode)
    useEffect(() => {
        if (isEditMode && post && user) {
            setCanEdit(post.author?.uuid === user.uuid || user.is_admin)
        }
    }, [isEditMode, post, user])

    const handleSubmit = useCallback(async (postData) => {
        try {
            setSubmitError('')
            setSubmitSuccess(false)
            
            if (isEditMode) {
                await updatePost(post.uuid, postData)
                setSubmitSuccess(true)
                setTimeout(() => {
                    navigate(`/posts/${post.slug}`)
                }, 2000)
            } else {
                await createPost(postData)
                setSubmitSuccess(true)
                setTimeout(() => {
                    navigate(`/user/posts`)
                }, 2000)
            }
            
        } catch (error) {
            console.error('Error saving post:', error)
            setSubmitError(error.message || `Failed to ${isEditMode ? 'update' : 'create'} post. Please try again.`)
        }
    }, [isEditMode, createPost, updatePost, post?.uuid, post?.slug, navigate])

    const handleSaveDraft = useCallback(async (postData) => {
        try {
            setSubmitError('')
            
            if (isEditMode) {
                const draftData = { ...postData, is_published: false }
                await updatePost(post.uuid, draftData)
                alert('Post converted to draft successfully!')
                navigate('/user/posts')
            } else {
                await saveAsDraft(postData)
                alert('Post saved as draft successfully!')
                navigate('/user/posts')
            }
            
        } catch (error) {
            console.error('Error saving draft:', error)
            setSubmitError(error.message || 'Failed to save draft. Please try again.')
        }
    }, [isEditMode, saveAsDraft, updatePost, post?.uuid, navigate])

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
                            <UserProfileDropdown className="ms-4" />
                        </Navbar.Collapse>
                    </HeaderNav>
                </Header>
                {/* Header End */}
    
                {/* Auth Required Section */}
                <section className="pt-[50px] sm:pt-[70px] md:pt-[75px] lg:pt-[90px] xl:pt-[130px]">
                    <Container className="px-4 sm:px-6">
                        <Row className="justify-center">
                            <Col xl={6} lg={7} md={8} className="text-center">
                                <h1 className="font-serif text-darkgray font-semibold text-[24px] sm:text-[30px] md:text-[32px] lg:text-[42px] mb-[20px] sm:mb-[25px]">
                                    Authentication Required
                                </h1>
                                <p className="w-[95%] sm:w-[85%] lg:w-[90%] md:w-full mx-auto mb-[25px] sm:mb-[35px] text-sm sm:text-base">
                                    Please log in to {isEditMode ? 'edit' : 'create and publish'} posts on our platform.
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
            </div>
        )
    }

    // Show loading state while fetching post (edit mode only)
    if (isEditMode && postLoading) {
        return (
            <div style={props.style}>
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
    
                <section className="pt-[50px] sm:pt-[70px] md:pt-[75px] lg:pt-[90px] xl:pt-[130px]">
                    <Container className="px-4 sm:px-6">
                        <Row className="justify-center">
                            <Col xl={6} lg={7} md={8} className="text-center">
                                <div className="spinner-border text-fastblue mb-4" role="status">
                                    <span className="visually-hidden">Loading...</span>
                                </div>
                                <p className="text-darkgray">Loading post...</p>
                            </Col>
                        </Row>
                    </Container>
                </section>
            </div>
        )
    }

    // Show error if post not found or error loading (edit mode only)
    if (isEditMode && (postError || !post)) {
        return (
            <div style={props.style}>
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
    
                <section className="pt-[50px] sm:pt-[70px] md:pt-[75px] lg:pt-[90px] xl:pt-[130px]">
                    <Container className="px-4 sm:px-6">
                        <Row className="justify-center">
                            <Col xl={6} lg={7} md={8} className="text-center">
                                <h1 className="font-serif text-darkgray font-semibold text-[24px] sm:text-[30px] md:text-[32px] lg:text-[42px] mb-[20px] sm:mb-[25px]">
                                    Post Not Found
                                </h1>
                                <p className="w-[95%] sm:w-[85%] lg:w-[90%] md:w-full mx-auto mb-[25px] sm:mb-[35px] text-sm sm:text-base">
                                    The post you're trying to edit could not be found or you don't have permission to edit it.
                                </p>
                                <div className="flex gap-3 justify-center">
                                    <Buttons 
                                        to="/user/posts" 
                                        className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none"
                                        themeColor="#0038e3"
                                        color="#fff"
                                        size="sm"
                                        title="My Posts"
                                    />
                                    <Buttons 
                                        to="/" 
                                        className="btn-transparent-dark-gray btn-fancy font-medium font-serif uppercase rounded-none"
                                        themeColor="transparent"
                                        color="#232323"
                                        size="sm"
                                        title="Go Home"
                                    />
                                </div>
                            </Col>
                        </Row>
                    </Container>
                </section>
            </div>
        )
    }

    // Show permission error if user can't edit (edit mode only)
    if (isEditMode && !canEdit) {
        return (
            <div style={props.style}>
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
    
                <section className="pt-[50px] sm:pt-[70px] md:pt-[75px] lg:pt-[90px] xl:pt-[130px]">
                    <Container className="px-4 sm:px-6">
                        <Row className="justify-center">
                            <Col xl={6} lg={7} md={8} className="text-center">
                                <h1 className="font-serif text-darkgray font-semibold text-[24px] sm:text-[30px] md:text-[32px] lg:text-[42px] mb-[20px] sm:mb-[25px]">
                                    Permission Denied
                                </h1>
                                <p className="w-[95%] sm:w-[85%] lg:w-[90%] md:w-full mx-auto mb-[25px] sm:mb-[35px] text-sm sm:text-base">
                                    You don't have permission to edit this post. Only the author can edit their posts.
                                </p>
                                <div className="flex gap-3 justify-center">
                                    <Buttons 
                                        to={`/posts/${post.slug}`}
                                        className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none"
                                        themeColor="#0038e3"
                                        color="#fff"
                                        size="sm"
                                        title="View Post"
                                    />
                                    <Buttons 
                                        to="/" 
                                        className="btn-transparent-dark-gray btn-fancy font-medium font-serif uppercase rounded-none"
                                        themeColor="transparent"
                                        color="#232323"
                                        size="sm"
                                        title="Go Home"
                                    />
                                </div>
                            </Col>
                        </Row>
                    </Container>
                </section>
            </div>
        )
    }

    // Prepare initial values for the form (edit mode only)
    const initialValues = isEditMode ? {
        title: post.title || '',
        content: post.content || '',
        content_blocks: post.content_blocks || null,
        excerpt: post.excerpt || '',
        category_id: post.category?.id || '',
        tag_ids: post.tags?.map(tag => tag.id) || [],
        meta_title: post.meta_title || '',
        meta_description: post.meta_description || '',
        reading_time: post.reading_time || null,
        slug: post.slug || '',
        featured_image: post.featured_image || null
    } : {}

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

            {/* Full-Screen Editor-Only Post Form */}
            <EditorOnlyPostForm
                initialValues={initialValues}
                onSubmit={handleSubmit}
                onSaveDraft={handleSaveDraft}
                loading={isEditMode ? updateLoading : (createLoading || saveLoading)}
                isEditMode={isEditMode}
            />
        </div>
    )
}

export default CreatePost