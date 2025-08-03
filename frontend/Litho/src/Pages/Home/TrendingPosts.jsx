import React, { memo } from 'react'
import PropTypes from "prop-types"
import { Col, Container, Row } from 'react-bootstrap'
import { m } from "framer-motion"
import BlogClassic from '../../Components/Blogs/BlogClassic'
import { useTrendingPosts } from '../../api/usePosts'
import { fadeIn } from '../../Functions/GlobalAnimations'
import "../../Assets/scss/components/_trending-posts.scss"

const TrendingPosts = (props) => {
  const { 
    className, 
    grid = "grid grid-4col xl-grid-4col lg-grid-3col md-grid-2col sm-grid-2col xs-grid-1col gutter-extra-large",
    limit = 8,
    showTitle = true,
    title = "Trending Articles",
    subtitle = "Discover what's popular right now",
    ...restProps 
  } = props;
  const { posts: trendingPosts, loading, error } = useTrendingPosts({ limit });
  const style = {
    "--gradient-color": typeof(props.themeColor) === "object" 
      ? `linear-gradient(45deg, ${props.themeColor[0]}, ${props.themeColor[1]})` 
      : props.themeColor,
    "--brand-color": props.brandColor,
  }

  if (loading) {
    return (
      <section 
        className={`trending-posts-section py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]${className ? ` ${className}` : ''}`}
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
            <p className="mt-2 text-gray-600">Loading trending articles...</p>
          </div>
        </Container>
      </section>
    );
  }

  if (error) {
    return (
      <section 
        className={`trending-posts-section py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]${className ? ` ${className}` : ''}`}
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
            <p>Unable to load trending articles. Please try again later.</p>
          </div>
        </Container>
      </section>
    );
  }

  if (!trendingPosts || trendingPosts.length === 0) {
    return (
      <section 
        className={`trending-posts-section py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]${className ? ` ${className}` : ''}`}
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
            <i className="feather-trending-up text-4xl text-spanishgray mb-4"></i>
            <p className="text-spanishgray">No trending articles at the moment.</p>
          </div>
        </Container>
      </section>
    );
  }

  return (
    <m.section 
      className={`trending-posts-section py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]${className ? ` ${className}` : ''}`}
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
                <i className="feather-trending-up text-fastblue mr-3"></i>
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
            data={trendingPosts} 
            link="/posts/" 
            pagination={false} 
            grid={grid}
            animation={fadeIn}
            className="trending-posts-grid"
          />
        </m.div>
      </Container>
    </m.section>
  )
}

TrendingPosts.defaultProps = {
  className: "",
  showTitle: true,
  title: "Trending Articles",
  subtitle: "Discover what's popular right now",
  limit: 8,
  grid: "grid grid-4col xl-grid-4col lg-grid-3col md-grid-2col sm-grid-2col xs-grid-1col gutter-extra-large"
}

TrendingPosts.propTypes = {
  className: PropTypes.string,
  themeColor: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
  brandColor: PropTypes.string,
  showTitle: PropTypes.bool,
  title: PropTypes.string,
  subtitle: PropTypes.string,
  limit: PropTypes.number,
  grid: PropTypes.string,
}

export default memo(TrendingPosts)