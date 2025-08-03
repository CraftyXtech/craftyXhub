import React, { memo } from 'react'

// Libraries
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { m } from "framer-motion"
import { PropTypes } from "prop-types"

// Components
import { Header, HeaderCart, HeaderLanguage, HeaderNav, Menu, SearchBar } from '../../Components/Header/Header'
import Logo from '../../Components/Logo'
import UserProfileDropdown from '../../Components/Header/UserProfileDropdown'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'
import SideButtons from "../../Components/SideButtons"
import Counter from '../../Components/Counters/Counter'
import Buttons from '../../Components/Button/Buttons'
import BlogClassic from '../../Components/Blogs/BlogClassic'

// API & Auth
import { usePosts, useUserDraftPosts, useUserBookmarks } from '../../api/usePosts'
import { useMediaManagement } from '../../api/useMedia'
import useAuth from '../../api/useAuth'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

// CSS
import "../../Assets/scss/pages/_dashboard.scss"

const Dashboard = (props) => {
    const { isAuthenticated, user } = useAuth()
    
    // API hooks for dashboard data
    const { posts: userPosts } = usePosts({ author_id: user?.id })
    const { drafts } = useUserDraftPosts()
    const { bookmarks } = useUserBookmarks()
    const { media } = useMediaManagement()

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
                            <HeaderLanguage className="xs:pl-[15px]" />
                            <HeaderCart className="xs:pl-[15px]" style={{ "--base-color": "#0038e3" }} />
                        </Col>
                    </HeaderNav>
                </Header>
                {/* Header End */}

                {/* Section Start */}
                <section className="pt-[130px] lg:pt-[90px] md:pt-[75px] sm:pt-[50px]">
                    <Container>
                        <Row className="justify-center">
                            <Col xl={6} lg={7} md={8} className="text-center">
                                <h1 className="font-serif text-darkgray font-semibold text-[42px] lg:text-[32px] md:text-[30px] mb-[25px]">
                                    Access Required
                                </h1>
                                <p className="w-[85%] mx-auto mb-[35px] lg:w-[90%] md:w-full">
                                    Please log in to access your dashboard and manage your content.
                                </p>
                                <Buttons 
                                    to="/auth/login" 
                                    className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none"
                                    themeColor="#0038e3"
                                    color="#fff"
                                    title="Login to Dashboard"
                                />
                            </Col>
                        </Row>
                    </Container>
                </section>
                {/* Section End */}

                {/* Footer Start */}
                <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
                {/* Footer End */}
            </div>
        )
    }

    // Prepare stats data for Counter component - Enhanced with social stats
    const statsData = [
        {
            number: { text: userPosts?.length || 0, class: "text-darkgray font-serif font-semibold text-[40px] tracking-[-1px]" },
            title: "Published Posts",
            content: "Total posts published",
            icon: "feather-edit",
            link: "/user/posts"
        },
        {
            number: { text: drafts?.length || 0, class: "text-darkgray font-serif font-semibold text-[40px] tracking-[-1px]" },
            title: "Draft Posts", 
            content: "Posts in draft",
            icon: "feather-file-text",
            link: "/user/posts?tab=drafts"
        },
        {
            number: { text: 0, class: "text-darkgray font-serif font-semibold text-[40px] tracking-[-1px]" },
            title: "Followers",
            content: "People following you",
            icon: "feather-users",
            link: "#followers-modal"
        },
        {
            number: { text: 0, class: "text-darkgray font-serif font-semibold text-[40px] tracking-[-1px]" },
            title: "Following", 
            content: "People you follow",
            icon: "feather-user-plus",
            link: "#following-modal"
        },
        {
            number: { text: bookmarks?.length || 0, class: "text-darkgray font-serif font-semibold text-[40px] tracking-[-1px]" },
            title: "Bookmarks",
            content: "Saved articles",
            icon: "feather-bookmark", 
            link: "/user/bookmarks"
        },
        {
            number: { text: media?.length || 0, class: "text-darkgray font-serif font-semibold text-[40px] tracking-[-1px]" },
            title: "Media Library",
            content: "Uploaded files",
            icon: "feather-image",
            link: "/user/media-library"
        }
    ]

    // Recent posts data for BlogClassic component
    const recentPosts = userPosts?.slice(0, 3) || []

    return (
        <div style={props.style}>
            <SideButtons />
            
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

            {/* Page Title Start */}
            <section className="bg-lightgray py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                <Container>
                    <Row className="items-center justify-center">
                        <Col xl={8} lg={6}>
                            <h1 className="font-serif text-darkgray font-semibold text-[42px] lg:text-[32px] md:text-[30px] mb-[15px]">
                                Welcome back, {user?.full_name || user?.username}!
                            </h1>
                            <p className="mb-0 text-lg">
                                Manage your content, track your progress, and engage with your audience.
                            </p>
                        </Col>
                        <Col xl={4} lg={6} className="breadcrumb justify-end text-right mt-[10px] lg:mt-[20px] xs:mt-0">
                            <ul className="xs-text-center">
                                <li><Link aria-label="breadcrumb" to="/">Home</Link></li>
                                <li>Dashboard</li>
                            </ul>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Page Title End */}

            {/* Dashboard Stats Section Start */}
            <m.section {...fadeIn} className="py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                <Container>
                    <Row className="justify-center">
                        <Col lg={6} className="text-center mb-[6%]">
                            <h2 className="font-serif text-darkgray font-semibold text-[42px] lg:text-[32px] md:text-[30px] mb-[20px]">
                                Your Statistics
                            </h2>
                            <p className="w-[85%] mx-auto lg:w-[90%] md:w-full">
                                Overview of your content and engagement metrics
                            </p>
                        </Col>
                    </Row>
                    <Row>
                        <Counter
                            theme="counter-style-01"
                            grid="row-cols-1 row-cols-md-2 row-cols-lg-4"
                            className="text-center counter-style-01"
                            data={statsData}
                            animation={fadeIn}
                            animationDelay={0.2}
                        />
                    </Row>
                </Container>
            </m.section>
            {/* Dashboard Stats Section End */}

            {/* Quick Actions Section Start */}
            <section className="bg-lightgray py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                <Container>
                    <Row className="justify-center">
                        <Col lg={6} className="text-center mb-[6%]">
                            <h2 className="font-serif text-darkgray font-semibold text-[42px] lg:text-[32px] md:text-[30px] mb-[20px]">
                                Quick Actions
                            </h2>
                            <p className="w-[85%] mx-auto lg:w-[90%] md:w-full">
                                Shortcuts to your most used features
                            </p>
                        </Col>
                    </Row>
                    <Row className="justify-center">
                        <Col lg={3} md={4} sm={6} className="mb-[30px]">
                            <Buttons
                                to="/posts/create"
                                className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none w-full h-[60px] flex items-center justify-center"
                                themeColor="#0038e3"
                                size="sm"
                                color="#fff"
                                title="Create New Post"
                                icon="fas fa-plus mr-2"
                            />
                        </Col>
                        <Col lg={3} md={4} sm={6} className="mb-[30px]">
                            <Buttons
                                to="/user/posts"
                                className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none w-full h-[60px] flex items-center justify-center"
                                themeColor="#ff7a56"
                                size="sm"
                                color="#fff"
                                title="Manage Posts"
                                icon="fas fa-edit mr-2"
                            />
                        </Col>
                        <Col lg={3} md={4} sm={6} className="mb-[30px]">
                            <Buttons
                                to="/user/media-library"
                                className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none w-full h-[60px] flex items-center justify-center"
                                themeColor="#28a745"
                                size="sm"
                                color="#fff"
                                title="Media Library"
                                icon="fas fa-images mr-2"
                            />
                        </Col>
                        <Col lg={3} md={4} sm={6} className="mb-[30px]">
                            <Buttons
                                to="/user/bookmarks"
                                className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none w-full h-[60px] flex items-center justify-center"
                                themeColor="#6c757d"
                                size="sm"
                                color="#fff"
                                title="Bookmarks"
                                icon="fas fa-bookmark mr-2"
                            />
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Quick Actions Section End */}

            {/* Recent Posts Section Start */}
            {userPosts && userPosts.length > 0 && (
                <m.section {...fadeIn} className="py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                    <Container>
                        <Row className="justify-center">
                            <Col lg={6} className="text-center mb-[6%]">
                                <h2 className="font-serif text-darkgray font-semibold text-[42px] lg:text-[32px] md:text-[30px] mb-[20px]">
                                    Your Recent Posts
                                </h2>
                                <p className="w-[85%] mx-auto lg:w-[90%] md:w-full">
                                    Latest posts you've published
                                </p>
                            </Col>
                        </Row>
                        <Row>
                            <Col>
                                <BlogClassic
                                    filter={false}
                                    data={recentPosts}
                                    animation={fadeIn}
                                    animationDelay={0.2}
                                    pagination={false}
                                    grid="grid grid-4col xl-grid-4col lg-grid-3col md-grid-2col sm-grid-2col xs-grid-1col gutter-extra-large"
                                />
                                <div className="text-center mt-[50px]">
                                    <Buttons
                                        to="/user/posts"
                                        className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none"
                                        themeColor="#0038e3"
                                        color="#fff"
                                        title="View All Posts"
                                    />
                                </div>
                            </Col>
                        </Row>
                    </Container>
                </m.section>
            )}
            {/* Recent Posts Section End */}

            {/* Footer Start */}
            <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
            {/* Footer End */}
        </div>
    )
}

Dashboard.defaultProps = {
    className: "",
}

Dashboard.propTypes = {
    className: PropTypes.string,
}

export default memo(Dashboard)