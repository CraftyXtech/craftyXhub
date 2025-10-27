import React from 'react'

// Libraries
import { Col, Container, Row } from 'react-bootstrap'
import { Parallax } from "react-scroll-parallax";

// Components
import BlogClassic from '../../Components/Blogs/BlogClassic'

// API
import { usePosts } from '../../api';

const BlogListingPage = () => {
  const { posts, loading, error } = usePosts({ published: true })
  
  return (
    <>
      {/* Parallax Section Start */}
      <div className="py-[80px] h-auto overflow-hidden md:relative md:py-[40px]">
        <Parallax className="lg-no-parallax bg-cover absolute -top-[100px] landscape:md:top-[-20px] left-0 w-full h-[100vh]" translateY={[-40, 40]} style={{ backgroundImage: `url(https://via.placeholder.com/1920x1080)` }}></Parallax>
        <Container className="h-full relative">
          <Row className="justify-center h-[300px] sm:h-[250px]">
            <Col xl={6} lg={6} md={8} className="text-center flex justify-center flex-col font-serif">
              <h1 className="text-gradient bg-gradient-to-r from-[#556fff] via-[#e05fc4] to-[#ff798e] mb-[15px] inline-block text-xmd leading-[20px]">Blog</h1>
              <h2 className="text-darkgray font-medium -tracking-[1px] mb-0">Attractive articles updated daily</h2>
            </Col>
          </Row>
        </Container>
      </div>
      {/* Parallax Section End */}

      {/* Section Start */}
      <section className="overflow-hidden relative px-[11%] xl:px-[2%] pb-[130px] lg:px-0 lg:pb-[90px] md:pb-[75px] sm:pb-[50px]">
        <Container fluid className="xs:px-0">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
              <p className="mt-4 text-gray-600 text-lg">Loading articles...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12 text-red-600">
              <p className="text-lg">Error loading articles. Please try again later.</p>
            </div>
          ) : (
            <BlogClassic link="/posts/" data={posts} pagination={true} grid="grid grid-5col xl-grid-4col lg-grid-3col md-grid-2col sm-grid-2col xs-grid-1col gutter-double-extra-large" />
          )}
        </Container>
      </section>
      {/* Section End */}
    </>
  )
}

export default BlogListingPage 