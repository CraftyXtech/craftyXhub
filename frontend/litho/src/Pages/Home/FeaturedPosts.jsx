import React, { memo } from 'react'
import PropTypes from "prop-types"

// Libraries
import { Col, Container, Row } from 'react-bootstrap'
import { m } from "framer-motion"

// Components
import BlogClassic from '../../Components/Blogs/BlogClassic'

// API
import { useFeaturedPosts } from '../../api/usePosts'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

// CSS
import "../../Assets/scss/components/_featured-posts.scss"

const FeaturedPosts = (props) => {
  const { 
    className, 
    grid = "grid grid-3col xl-grid-3col lg-grid-2col md-grid-2col sm-grid-1col xs-grid-1col gutter-extra-large",
    limit = 6,
    showTitle = true,
    title = "Featured Articles",
    subtitle = "Hand-picked content just for you",
    ...restProps 
  } = props;

  const { posts: featuredPosts, loading, error } = useFeaturedPosts({ limit });

  // Dynamic styling with CSS custom properties
  const style = {
    "--gradient-color": typeof(props.themeColor) === "object" 
      ? `linear-gradient(45deg, ${props.themeColor[0]}, ${props.themeColor[1]})` 
      : props.themeColor,
    "--brand-color": props.brandColor,
  }

  if (loading) {
    return (
      <section 
        className={`featured-posts-section py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]${className ? ` ${className}` : ''}`}
        style={style}
        {...restProps}
      >
        <Container>
          {showTitle && (
            <Row className="justify-center">
              <Col lg={6} className="text-center mb-10 sm:mb-6">
                <h2 className="heading-5 font-serif font-semibold text-darkgray mb-[5px]">{title}</h2>
                {subtitle && <p className="mb-[25px]">{subtitle}</p>}
              </Col>
            </Row>
          )}
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <p className="mt-2 text-gray-600">Loading featured articles...</p>
          </div>
        </Container>
      </section>
    );
  }

  if (error) {
    return (
      <section 
        className={`featured-posts-section py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]${className ? ` ${className}` : ''}`}
        style={style}
        {...restProps}
      >
        <Container>
          {showTitle && (
            <Row className="justify-center">
              <Col lg={6} className="text-center mb-10 sm:mb-6">
                <h2 className="heading-5 font-serif font-semibold text-darkgray mb-[5px]">{title}</h2>
                {subtitle && <p className="mb-[25px]">{subtitle}</p>}
              </Col>
            </Row>
          )}
          <div className="text-center py-8 text-red-600">
            <i className="feather-alert-triangle text-4xl mb-4"></i>
            <p>Unable to load featured articles. Please try again later.</p>
          </div>
        </Container>
      </section>
    );
  }

  if (!featuredPosts || featuredPosts.length === 0) {
    return (
      <section 
        className={`featured-posts-section py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]${className ? ` ${className}` : ''}`}
        style={style}
        {...restProps}
      >
        <Container>
          {showTitle && (
            <Row className="justify-center">
              <Col lg={6} className="text-center mb-10 sm:mb-6">
                <h2 className="heading-5 font-serif font-semibold text-darkgray mb-[5px]">{title}</h2>
                {subtitle && <p className="mb-[25px]">{subtitle}</p>}
              </Col>
            </Row>
          )}
          <div className="text-center py-8">
            <i className="feather-star text-4xl text-spanishgray mb-4"></i>
            <p className="text-spanishgray">No featured articles at the moment.</p>
          </div>
        </Container>
      </section>
    );
  }

  return (
    <m.section 
      className={`featured-posts-section py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]${className ? ` ${className}` : ''}`}
      style={style}
      {...fadeIn}
      {...restProps}
    >
      <Container>
        {showTitle && (
          <Row className="justify-center">
            <Col lg={6} className="text-center mb-10 sm:mb-6">
              <m.h2 
                className="heading-5 font-serif font-semibold text-darkgray mb-[5px]"
                {...fadeIn}
                transition={{ delay: 0.1 }}
              >
                <i className="feather-star text-fastblue mr-3"></i>
                {title}
              </m.h2>
              {subtitle && (
                <m.p 
                  className="mb-[25px]"
                  {...fadeIn}
                  transition={{ delay: 0.2 }}
                >
                  {subtitle}
                </m.p>
              )}
            </Col>
          </Row>
        )}
      </Container>
      
      <Container fluid>
        <m.div {...fadeIn} transition={{ delay: 0.3 }}>
          <BlogClassic 
            filter={false} 
            data={featuredPosts} 
            link="/posts/" 
            pagination={false} 
            grid={grid}
            animation={fadeIn}
            className="featured-posts-grid"
          />
        </m.div>
      </Container>
    </m.section>
  )
}

FeaturedPosts.defaultProps = {
  className: "",
  showTitle: true,
  title: "Featured Articles",
  subtitle: "Hand-picked content just for you",
  limit: 6,
  grid: "grid grid-3col xl-grid-3col lg-grid-2col md-grid-2col sm-grid-1col xs-grid-1col gutter-extra-large"
}

FeaturedPosts.propTypes = {
  className: PropTypes.string,
  themeColor: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
  brandColor: PropTypes.string,
  showTitle: PropTypes.bool,
  title: PropTypes.string,
  subtitle: PropTypes.string,
  limit: PropTypes.number,
  grid: PropTypes.string,
}

export default memo(FeaturedPosts)