import React, { useEffect, useState } from 'react'

// Libraries
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { Link, useParams } from 'react-router-dom'

// Components
import AuthorBox from "../../../Components/Blogs/HelperComponents/AuthorBox"
import CommentBox from "../../../Components/Blogs/HelperComponents/CommentBox"
import { Header, HeaderNav, Menu } from "../../../Components/Header/Header"
import BlogClassic from "../../../Components/Blogs/BlogClassic";
import SocialIcons from "../../../Components/SocialIcon/SocialIcons"
import FooterStyle05 from "../../../Components/Footers/FooterStyle05"
import ContentRenderer from '../../../Components/Blogs/ContentRenderer'
import Logo from '../../../Components/Logo/Logo'

import Sidebar from '../../../Components/Blogs/HelperComponents/Sidebar';

// API Hooks
import { usePost, useRelatedPosts, getImageUrl, togglePostLike } from '../../../api'

// Utils
import { formatDate } from '../../../utils/dateUtils'

// New Components  
import BookmarkButton from '../../../Components/Blogs/BookmarkButton'
import ReportModal from '../../../Components/Blogs/ReportModal'

// Auth
import useAuth from '../../../api/useAuth'

// Data (for fallback only)
import { blogData } from '../../../Components/Blogs/BlogData'
import { fadeIn } from '../../../Functions/GlobalAnimations'

const SocialIconsData = [
  {
    color: "#3b5998",
    link: process.env.REACT_APP_FACEBOOK_URL,
    icon: "fab fa-facebook-f"
  },
  {
    color: "#ea4c89",
    link: process.env.REACT_APP_DRIBBBLE_URL,
    icon: "fab fa-dribbble"
  },
  {
    color: "#00aced",
    link: process.env.REACT_APP_TWITTER_URL,
    icon: "fab fa-twitter"
  },
  {
    color: "#fe1f49",
    link: process.env.REACT_APP_INSTAGRAM_URL,
    icon: "fab fa-instagram"
  },
  {
    color: "#0077b5",
    link: process.env.REACT_APP_LINKEDIN_URL,
    icon: "fab fa-linkedin-in"
  }
].filter(item => item.link)

const PostDetails = (props) => {
  const [data, setData] = useState(null)
  const [showReportModal, setShowReportModal] = useState(false)
  const [isBookmarked, setIsBookmarked] = useState(false)
  const [likeCount, setLikeCount] = useState(0)
  const [isLiked, setIsLiked] = useState(false)
  const [likingPost, setLikingPost] = useState(false)

  const { isAuthenticated, user } = useAuth()

  // Canonical param: UUID
  const { uuid } = useParams();
  
  // Fetch post by UUID
  const { post, loading, error } = usePost(uuid);
  
  // Fetch related posts by UUID directly to avoid intermediate undefined
  const { relatedPosts, loading: relatedLoading, error: relatedError } = useRelatedPosts(uuid, { limit: 3 });

  useEffect(() => {
    if (post) {
      setData([post]);
      
      setLikeCount(post.liked_by?.length || 0);
      
      if (isAuthenticated && user && post.liked_by) {
        const userLiked = post.liked_by.some(likedUser => likedUser.uuid === user.uuid || likedUser.id === user.id);
        setIsLiked(userLiked);
      }
      
      if (isAuthenticated && post.bookmarked_by) {
        setIsBookmarked(post.bookmarked_by.length > 0);
      }
    } else if (!loading && !post) {
      let getData;
      // Legacy fallback removed: this page expects a server UUID in URL.
      setData(getData);
    }
  }, [post, loading, isAuthenticated, user]);

  // Scroll to comment if hash is present in URL (e.g., #comment-123)
  useEffect(() => {
    if (window.location.hash && data && !loading) {
      const hash = window.location.hash.substring(1); // Remove the #
      const timer = setTimeout(() => {
        const element = document.getElementById(hash);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
          element.classList.add('highlight-comment');
          // Remove highlight after 3 seconds
          setTimeout(() => {
            element.classList.remove('highlight-comment');
          }, 3000);
        }
      }, 800); // Wait longer for Litho's animations
      
      return () => clearTimeout(timer);
    }
  }, [window.location.hash, data, loading]);

  const handleLike = async () => {
    if (!isAuthenticated) {
      return;
    }

    if (likingPost) return;

    setLikingPost(true);
    try {
      const result = await togglePostLike(data[0].uuid);
      setIsLiked(result);
      setLikeCount(prev => result ? prev + 1 : prev - 1);
    } catch (error) {
      console.error('Error toggling like:', error);
    } finally {
      setLikingPost(false);
    }
  };

  if (loading) {
    return (
      <div style={props.style}>
        <Header topSpace={{ desktop: true }} type="reverse-scroll" className="border-b border-b-[#0000001a]">
          <HeaderNav theme="white" menu="light" expand="lg" fluid="sm" containerClass="sm:px-0" className="py-[0px] md:pr-[15px] md:pl-0 md:py-[20px]">
            <Col className="col-auto col-lg-2 me-auto ps-lg-0">
              <Logo variant="black" />
            </Col>
            <Navbar.Toggle className="order-last md:ml-[8px]">
              <span className="navbar-toggler-line"></span>
              <span className="navbar-toggler-line"></span>
              <span className="navbar-toggler-line"></span>
              <span className="navbar-toggler-line"></span>
            </Navbar.Toggle>
            <Navbar.Collapse className="col-auto justify-center">
              <Menu {...props} />
            </Navbar.Collapse>
            <Col className="col-auto col-lg-2 text-end pe-0 md:mr-[10px] xs:hidden">
              <SocialIcons theme="social-icon-style-01 block text-end" iconColor="dark" size="xs" data={SocialIconsData.slice(0, 3)} />
            </Col>
          </HeaderNav>
        </Header>
        
        <div className="flex justify-center items-center min-h-[400px]">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mb-4"></div>
            <p className="text-gray-600 text-lg">Loading post...</p>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error && !data) {
    return (
      <div style={props.style}>
        <Header topSpace={{ desktop: true }} type="reverse-scroll" className="border-b border-b-[#0000001a]">
          <HeaderNav theme="white" menu="light" expand="lg" fluid="sm" containerClass="sm:px-0" className="py-[0px] md:pr-[15px] md:pl-0 md:py-[20px]">
            <Col className="col-auto col-lg-2 me-auto ps-lg-0">
              <Logo variant="black" />
            </Col>
            <Navbar.Toggle className="order-last md:ml-[8px]">
              <span className="navbar-toggler-line"></span>
              <span className="navbar-toggler-line"></span>
              <span className="navbar-toggler-line"></span>
              <span className="navbar-toggler-line"></span>
            </Navbar.Toggle>
            <Navbar.Collapse className="col-auto justify-center">
              <Menu {...props} />
            </Navbar.Collapse>
            <Col className="col-auto col-lg-2 text-end pe-0 md:mr-[10px] xs:hidden">
              <SocialIcons theme="social-icon-style-01 block text-end" iconColor="dark" size="xs" data={SocialIconsData.slice(0, 3)} />
            </Col>
          </HeaderNav>
        </Header>
        
        <div className="flex justify-center items-center min-h-[400px]">
          <div className="text-center">
            <h2 className="text-2xl font-serif font-medium text-darkgray mb-4">Post Not Found</h2>
            <p className="text-medium mb-6">The post you are looking for does not exist or has been removed.</p>
            <Link 
              to="/" 
              className="inline-block bg-fastblue text-white px-6 py-3 rounded hover:bg-opacity-90 transition-all"
            >
              Back to Homepage
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={props.style}>
      {/* Header Start */}
      <Header topSpace={{ desktop: true }} type="reverse-scroll" className="border-b border-b-[#0000001a]">
        <HeaderNav theme="white" menu="light" expand="lg" fluid="sm" containerClass="sm:px-0" className="py-[0px] md:pr-[15px] md:pl-0 md:py-[20px]">
          <Col className="col-auto col-lg-2 me-auto ps-lg-0">
            <Logo variant="black" />
          </Col>
          <Navbar.Toggle className="order-last md:ml-[8px]">
            <span className="navbar-toggler-line"></span>
            <span className="navbar-toggler-line"></span>
            <span className="navbar-toggler-line"></span>
            <span className="navbar-toggler-line"></span>
          </Navbar.Toggle>
          <Navbar.Collapse className="col-auto justify-center">
            <Menu {...props} />
          </Navbar.Collapse>
          <Col className="col-auto col-lg-2 text-end pe-0 md:mr-[10px] xs:hidden">
            <SocialIcons theme="social-icon-style-01 block text-end" iconColor="dark" size="xs" data={SocialIconsData.slice(0, 3)} />
          </Col>
        </HeaderNav>
      </Header>
      {/* Header End */}
      
      {data && data.length > 0 && data[0] ? (
        <>
          <section className="py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
            <Container>
              <Row className="justify-center">
                <Col lg={8} className="right-sidebar md:mb-[60px] sm:mb-[40px]">
                  <Row>
                    <Col className="blog-details-text last:mb-0 mb-24">
                      <ul className="flex mb-8 xs:block">
                        {/* Published Date */}
                        {(data[0]?.published_at || data[0]?.date) && (
                          <li className="inline-block align-middle mr-[25px]">
                            <i className="feather-calendar text-fastblue mr-[10px]"></i>
                            <span>{data[0]?.published_at ? formatDate(data[0].published_at) : data[0]?.date}</span>
                          </li>
                        )}
                        
                        {/* Reading Time */}
                        {data[0]?.reading_time && (
                          <li className="inline-block align-middle mr-[25px]">
                            <i className="feather-clock text-fastblue mr-[10px]"></i>
                            <span>{data[0].reading_time} min read</span>
                          </li>
                        )}
                        
                        {/* Category */}
                        <li className="inline-block align-middle mr-[25px]">
                          <i className="feather-folder text-fastblue mr-[10px]"></i>
                          {data[0]?.category ? (
                            // API data - category is an object
                            <Link 
                              aria-label="category link" 
                              to={`/blogs/category/${data[0].category.slug || data[0].category.name?.toLowerCase().replace(/\s+/g, '-')}`}
                            >
                              {data[0].category.name}
                            </Link>
                          ) : data[0]?.category && Array.isArray(data[0].category) ? (
                            // Static data - category is an array
                            data[0].category.map((item, i) => {
                              return (
                                <Link 
                                  aria-label="category link" 
                                  key={i} 
                                  to={`/blogs/category/${item.toString().split(" ").join("").toLowerCase()}`}
                                >
                                  {i === data[0].category.length - 1 ? item : `${item}, `}
                                </Link>
                              )
                            })
                          ) : (
                            <span>Uncategorized</span>
                          )}
                        </li>
                        
                        {/* Author */}
                        <li className="inline-block align-middle">
                          <i className="feather-user text-fastblue mr-[10px]"></i>
                          By {data[0]?.author ? (
                            // API data - author is an object
                            <Link to={`/blogs/author/${data[0].author.uuid || data[0].author.username}`}>
                              {data[0].author.full_name || data[0].author.username}
                            </Link>
                          ) : (
                            <span>Unknown Author</span>
                          )}
                        </li>
                      </ul>
                      <h5 className="font-serif font-medium text-darkgray mb-[4.5rem]">{data[0]?.title || 'Untitled Post'}</h5>
                      
                      {/* Featured Image */}
                      {(data[0]?.featured_image || data[0]?.img) && (
                        <img 
                          width="" 
                          height="" 
                          src={getImageUrl(data[0].featured_image, "posts") || data[0].img} 
                          alt={data[0]?.title || "Post image"} 
                          className="w-full rounded-[6px] mb-[4.5rem]"
                        />
                      )}
                      
                      {/* Excerpt */}
                      {data[0]?.excerpt && (
                        <p className="mb-[25px] text-lg font-medium text-gray-700 italic">{data[0].excerpt}</p>
                      )}
                      
                      {/* Content */}
                      <ContentRenderer 
                        content={data[0]?.content} 
                        contentBlocks={data[0]?.content_blocks?.blocks || data[0]?.content_blocks} 
                      />
                    </Col>
                    <Col xs={12} className="flex items-center justify-between mb-[35px] sm:block">
                      {/* Tags */}
                      {((data[0]?.tags && data[0].tags.length > 0) || (Array.isArray(data[0]?.tags) && data[0].tags.length > 0)) && (
                          <div className="tag-cloud sm:flex sm:justify-center sm:mb-[10px] sm:flex-wrap gap-y-5">
                          {(data[0]?.tags || []).map((item, i) => {
                            // Handle both API format (object with name/slug) and static format (string)
                            const tagName = typeof item === 'object' ? item.name : item;
                            const tagSlug = typeof item === 'object' ? item.slug : item.toLowerCase().replace(/\s+/g, '-');
                            
                                return (
                              <Link 
                                aria-label={`Tag: ${tagName}`} 
                                key={i} 
                                to={`/blogs/tag/${tagSlug}`}
                                className="mr-2"
                              >
                                {tagName}
                              </Link>
                            )
                          })}
                          </div>
                      )}
                      
                      {/* Likes, Bookmark, and Report Actions */}
                      <div className="text-center md:text-end px-0 flex justify-end sm:justify-center items-center gap-3">
                        {/* Likes */}
                        <button
                          onClick={handleLike}
                          disabled={!isAuthenticated || likingPost}
                          aria-label="like post"
                          className={`uppercase text-darkgray text-xs w-auto font-medium inline-block border border-mediumgray rounded pt-[5px] pb-[6px] px-[18px] leading-[20px] transition-default hover:shadow-[0_0_10px_rgba(23,23,23,0.10)] ${
                            isLiked ? 'bg-red-50 border-red-300' : ''
                          } ${!isAuthenticated ? 'opacity-50 cursor-not-allowed' : 'hover:text-black cursor-pointer'}`}
                        >
                          <i className={`${isLiked ? 'fas' : 'far'} fa-heart mr-2 text-[#fa5c47]`}></i>
                          <span>{likeCount} {likeCount === 1 ? 'Like' : 'Likes'}</span>
                        </button>
                        
                        {/* Bookmark Button */}
                        {data[0]?.uuid && (
                          <BookmarkButton 
                            postUuid={data[0].uuid}
                            isBookmarked={isBookmarked}
                            onBookmarkChange={setIsBookmarked}
                            size="md"
                            variant="outline"
                            themeColor={["#0038e3", "#ff7a56"]}
                          />
                        )}
                        
                        {/* Report Button */}
                        {data[0]?.uuid && (
                          <button
                            onClick={() => setShowReportModal(true)}
                            className="flex items-center justify-center w-10 h-10 border border-mediumgray rounded-full text-spanishgray hover:text-red-500 hover:border-red-500 transition-all duration-300"
                            aria-label="Report post"
                            title="Report this post"
                          >
                            <i className="feather-flag text-sm"></i>
                          </button>
                        )}
                      </div>
                    </Col>
                    <Col>
                      <AuthorBox 
                        authorData={data[0]?.author} 
                        className="mb-[45px]" 
                      />
                    </Col>
                    <SocialIcons animation={fadeIn} theme="social-icon-style-09 m-auto" className="justify-center" size="md" iconColor="dark" data={SocialIconsData} />
                  </Row>
                </Col>

                <Sidebar data={data[0]} />
              </Row>
            </Container>
          </section>
          {/* Section Start */}
          <section className="bg-lightgray py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px] overflow-hidden">
            <Container>
              <Row className="justify-center">
                <Col lg={5} md={6} className="text-center mb-20">
                  <span className="font-serif font-medium uppercase inline-block">You may also like</span>
                  <h5 className="font-serif font-medium text-darkgray -tracking-[1px]">Related Posts</h5>
                </Col>
              </Row>
              {relatedLoading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                  <p className="mt-2 text-gray-600">Loading related posts...</p>
                </div>
              ) : relatedError ? (
                <div className="text-center py-8 text-red-600">
                  <p>Unable to load related posts. Please try again later.</p>
                </div>
              ) : relatedPosts && relatedPosts.length > 0 ? (
                <BlogClassic filter={false} pagination={false} grid="grid grid-3col xl-grid-3col lg-grid-3col md-grid-2col sm-grid-2col xs-grid-1col gutter-extra-large" data={relatedPosts} link="/posts/" />
              ) : (
                <div className="text-center py-8 text-gray-600">
                  <p>No related posts available at the moment.</p>
                </div>
              )}
            </Container>
          </section>
          {/* Section End */}

          <CommentBox postUuid={post?.uuid || uuid} postData={data[0]} />

          {/* Section Start */}
          <FooterStyle05 theme="dark" className="bg-[#262b35] text-slateblue" />
          {/* Section End */}

          {/* Report Modal */}
          {data[0]?.uuid && (
            <ReportModal 
              show={showReportModal}
              onHide={() => setShowReportModal(false)}
              postUuid={data[0].uuid}
              postTitle={data[0].title}
              onReportSuccess={() => {
                console.log('Post reported successfully');
                // Could show a toast notification here
              }}
            />
          )}
        </>
      ) : undefined}
    </div>
  )
}

export default PostDetails