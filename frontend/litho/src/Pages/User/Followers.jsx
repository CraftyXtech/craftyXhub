import React, { useState, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'

// Libraries
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { m } from "framer-motion"

// Components
import { Header, HeaderNav, Menu, SearchBar } from '../../Components/Header/Header'
import Logo from '../../Components/Logo'
import UserProfileDropdown from '../../Components/Header/UserProfileDropdown'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'

import FollowButton from '../../Components/User/FollowButton'
import Buttons from '../../Components/Button/Buttons'

// API & Auth
import { useUserFollowers, useUserProfile } from '../../api/useUser'
import useAuth from '../../api/useAuth'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

const UserCard = ({ user, onFollowChange }) => {
    return (
        <m.div 
            className="user-card bg-white rounded-lg p-6 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-300"
            {...fadeIn}
        >
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 rounded-full overflow-hidden bg-lightgray flex-shrink-0">
                        {user.profile_picture ? (
                            <img 
                                src={user.profile_picture} 
                                alt={user.full_name}
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center text-gray-400">
                                <i className="icon-user text-2xl"></i>
                            </div>
                        )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                        <Link 
                            to={`/user/${user.username}`}
                            className="block font-semibold text-darkgray hover:text-black transition-colors duration-200 truncate"
                        >
                            {user.full_name}
                        </Link>
                        <p className="text-sm text-gray-600 truncate">@{user.username}</p>
                        {user.bio && (
                            <p className="text-sm text-gray-700 mt-1 line-clamp-2">{user.bio}</p>
                        )}
                        
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            {user.follower_count !== undefined && (
                                <span>
                                    <i className="icon-people mr-1"></i>
                                    {user.follower_count} followers
                                </span>
                            )}
                            {user.post_count !== undefined && (
                                <span>
                                    <i className="fas fa-file-alt mr-1"></i>
                                    {user.post_count} posts
                                </span>
                            )}
                        </div>
                    </div>
                </div>
                
                <div className="flex-shrink-0 ml-4">
                    <FollowButton 
                        userUuid={user.uuid}
                        size="sm"
                        onFollowChange={onFollowChange}
                    />
                </div>
            </div>
        </m.div>
    )
}

const Followers = (props) => {
    const { username } = useParams()
    const navigate = useNavigate()
    const [page, setPage] = useState(1)
    const { isAuthenticated } = useAuth()

    const { user: profileUser, loading: profileLoading, error: profileError } = useUserProfile(username)
    
    const { 
        followers, 
        loading: followersLoading, 
        error: followersError, 
        hasMore 
    } = useUserFollowers(profileUser?.uuid, page, 20)

    const handleFollowChange = useCallback((userUuid, isNowFollowing) => {
        console.log(`User ${userUuid} is now ${isNowFollowing ? 'followed' : 'unfollowed'}`)
    }, [])

    const loadMore = () => {
        if (hasMore && !followersLoading) {
            setPage(prev => prev + 1)
        }
    }

    if (profileLoading) {
        return (
            <div style={props.style}>
                <Header topSpace={{ md: true }} type="reverse-scroll">
                    <HeaderNav fluid="fluid" theme="light" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" menuPosition="left">
                        <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                            <Logo className="flex items-center" variant="black" asNavbarBrand={false} />
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
                    </HeaderNav>
                </Header>

                <section className="py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                    <Container>
                        <Row className="justify-center">
                            <Col lg={8}>
                                <div className="text-center">
                                    <div className="inline-block">
                                        <i className="fas fa-spinner fa-spin text-4xl text-gray-400"></i>
                                        <p className="mt-4 text-gray-600">Loading user profile...</p>
                                    </div>
                                </div>
                            </Col>
                        </Row>
                    </Container>
                </section>

                <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
    
            </div>
        )
    }

    if (profileError || !profileUser) {
        return (
            <div style={props.style}>
                <Header topSpace={{ md: true }} type="reverse-scroll">
                    <HeaderNav fluid="fluid" theme="light" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" menuPosition="left">
                        <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                            <Logo className="flex items-center" variant="black" asNavbarBrand={false} />
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
                    </HeaderNav>
                </Header>

                <section className="py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                    <Container>
                        <Row className="justify-center">
                            <Col lg={8}>
                                <div className="text-center">
                                    <i className="icon-user text-6xl text-gray-300 mb-4"></i>
                                    <h2 className="text-darkgray font-medium mb-4">User Not Found</h2>
                                    <p className="text-gray-600 mb-6">The user you're looking for doesn't exist or has been removed.</p>
                                    <Buttons
                                        onClick={() => navigate('/')}
                                        className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none"
                                        color="#0038e3"
                                        size="md"
                                        themeColor="#0038e3"
                                        title="Go Home"
                                    />
                                </div>
                            </Col>
                        </Row>
                    </Container>
                </section>

                <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
    
            </div>
        )
    }

    return (
        <div style={props.style}>
            <Header topSpace={{ md: true }} type="reverse-scroll">
                <HeaderNav fluid="fluid" theme="light" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" menuPosition="left">
                    <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                        <Link aria-label="header logo" className="flex items-center" to="/">
                            <img className="default-logo" width="111" height="36" loading="lazy" src='/assets/img/litho-logo-regular-dark.png' data-rjs='/assets/img/litho-logo-regular-dark@2x.png' alt='logo' />
                            <img className="alt-logo" width="111" height="36" loading="lazy" src='/assets/img/litho-logo-regular-dark.png' data-rjs='/assets/img/litho-logo-regular-dark@2x.png' alt='logo' />
                            <img className="mobile-logo" width="111" height="36" loading="lazy" src='/assets/img/litho-logo-regular-dark.png' data-rjs='/assets/img/litho-logo-regular-dark@2x.png' alt='logo' />
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
                        <UserProfileDropdown className="ms-4" />
                    </Navbar.Collapse>
                </HeaderNav>
            </Header>

            <section className="py-[50px] sm:py-[60px] md:py-[75px] lg:py-[90px] xl:py-[130px]">
                <Container className="px-4 sm:px-6">
                    <Row className="justify-center">
                        <Col lg={10} xl={9}>
                            {/* Page Header */}
                            <div className="text-center mb-12 sm:mb-16">
                                <div className="mb-4 sm:mb-6">
                                    <div className="w-16 sm:w-20 lg:w-24 h-16 sm:h-20 lg:h-24 rounded-full overflow-hidden bg-lightgray mx-auto mb-3 sm:mb-4">
                                        {profileUser.profile_picture ? (
                                            <img 
                                                src={profileUser.profile_picture} 
                                                alt={profileUser.full_name}
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-gray-400">
                                                <i className="icon-user text-xl sm:text-2xl lg:text-3xl"></i>
                                            </div>
                                        )}
                                    </div>
                                    <h1 className="text-darkgray font-medium mb-2 text-lg sm:text-xl lg:text-2xl">{profileUser.full_name}'s Followers</h1>
                                    <p className="text-gray-600 text-sm sm:text-base">
                                        People who follow @{profileUser.username}
                                    </p>
                                </div>
                                
                                <div className="flex flex-col xs:flex-row justify-center gap-4 xs:gap-6 text-xs sm:text-sm text-gray-600">
                                    <Link 
                                        to={`/user/${profileUser.username}`}
                                        className="hover:text-black transition-colors duration-200 flex items-center justify-center"
                                    >
                                        <i className="icon-user mr-1 sm:mr-2"></i>
                                        Profile
                                    </Link>
                                    <span className="text-black font-medium flex items-center justify-center">
                                        <i className="icon-people mr-1 sm:mr-2"></i>
                                        Followers ({followers.length})
                                    </span>
                                    <Link 
                                        to={`/user/${profileUser.username}/following`}
                                        className="hover:text-black transition-colors duration-200 flex items-center justify-center"
                                    >
                                        <i className="icon-user-following mr-1 sm:mr-2"></i>
                                        Following
                                    </Link>
                                </div>
                            </div>

                            {/* Followers List */}
                            {followersError ? (
                                <div className="text-center py-12">
                                    <i className="fas fa-exclamation-triangle text-4xl text-gray-300 mb-4"></i>
                                    <h3 className="text-darkgray font-medium mb-2">Error Loading Followers</h3>
                                    <p className="text-gray-600">{followersError}</p>
                                </div>
                            ) : followers.length === 0 && !followersLoading ? (
                                <div className="text-center py-12">
                                    <i className="icon-people text-6xl text-gray-300 mb-4"></i>
                                    <h3 className="text-darkgray font-medium mb-2">No Followers Yet</h3>
                                    <p className="text-gray-600">
                                        {profileUser.full_name} doesn't have any followers yet.
                                    </p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {followers.map((follower) => (
                                        <UserCard 
                                            key={follower.uuid} 
                                            user={follower} 
                                            onFollowChange={handleFollowChange}
                                        />
                                    ))}
                                    
                                    {hasMore && (
                                        <div className="text-center pt-8">
                                            <Buttons
                                                onClick={loadMore}
                                                disabled={followersLoading}
                                                className="btn-outline btn-fancy font-medium font-serif uppercase rounded-none"
                                                color="#0038e3"
                                                size="md"
                                                title={followersLoading ? "Loading..." : "Load More"}
                                                icon={followersLoading ? "fas fa-spinner fa-spin" : "fas fa-chevron-down"}
                                                iconPosition="after"
                                            />
                                        </div>
                                    )}
                                    
                                    {followersLoading && page === 1 && (
                                        <div className="text-center py-8">
                                            <i className="fas fa-spinner fa-spin text-2xl text-gray-400"></i>
                                            <p className="mt-2 text-gray-600">Loading followers...</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </Col>
                    </Row>
                </Container>
            </section>

            <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />

        </div>
    )
}

export default Followers