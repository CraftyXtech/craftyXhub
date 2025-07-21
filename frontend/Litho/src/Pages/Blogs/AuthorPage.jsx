import React, { useEffect, useState } from "react";

// Libraries
import { Col, Container, Row } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { Parallax } from "react-scroll-parallax";

// Components
import BlogClassic from "../../Components/Blogs/BlogClassic";

// API
import { usePostsByAuthor, useProfile } from "../../api";

const AuthorPage = (props) => {
  const { author } = useParams(); // This could be author's UUID or ID
  
  // Get author profile (use UUID for profile)
  const { profile: authorDetails, loading: profileLoading } = useProfile(author);
  
  // For posts by author, we need the integer ID, not UUID
  // If author param is UUID, we'll need to get the ID from the profile
  // For now, let's assume the URL param is the integer ID
  const authorId = parseInt(author) || null;
  const { posts, loading: postsLoading, error } = usePostsByAuthor(authorId, { published: true });

  return (
    <div style={props.style}>
      {/* Parallax Section Start */}
      <div className="h-[450px] portrait:h-[450px] landscape:md:h-[320px] relative overflow-hidden sm:h-[300px] xxs:h-[300px] xs:portrait:h-[330px]">
        <Parallax className="bg-cover cover-background absolute -top-[100px] landscape:md:top-[-20px] left-0 w-full h-[100vh]" translateY={[-40, 40]} style={{ backgroundImage: `url(/assets/img/webp/portfolio-bg2.webp)` }} ></Parallax>
        <Container className="h-full relative">
          <Row className="justify-center h-full">
            <Col xl={6} lg={6} md={8} className="text-center flex justify-center flex-col font-serif" >
              {profileLoading ? (
                <div className="animate-pulse">
                  <div className="h-8 bg-gray-300 rounded mb-4"></div>
                  <div className="h-6 bg-gray-300 rounded"></div>
                </div>
              ) : (
                <>
                  <h1 className="text-gradient bg-gradient-to-r from-[#556fff] via-[#e05fc4] to-[#ff798e] mb-[15px] inline-block text-xmd">
                    {authorDetails?.full_name || authorDetails?.first_name || 'Author'}
                  </h1>
                  <h2 className="text-darkgray font-medium -tracking-[1px] mb-0">
                    {authorDetails?.bio || 'Every new print and color of the season'}
                  </h2>
                </>
              )}
            </Col>
          </Row>
        </Container>
      </div>
      {/* Parallax Section End */}

      {/* Section Start */}
      <section className="pt-0 relative px-[11%] overflow-hidden bg-lightgray xl:px-[2%] lg:py-[90px] md:pb-[75px] sm:pb-[50px] xs:px-0 xs:pt-[15px]">
        <Container fluid>
          <Row>
            <Col>
              {postsLoading ? (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
                  <p className="mt-4 text-gray-600 text-lg">Loading author's articles...</p>
                </div>
              ) : error ? (
                <div className="text-center py-12 text-red-600">
                  <p className="text-lg">Error loading articles. Please try again later.</p>
                </div>
              ) : posts && posts.length > 0 ? (
                <BlogClassic
                  link="/blog/post/"
                  data={posts}
                  pagination={true}
                  grid="grid grid-4col xl-grid-4col lg-grid-3col md-grid-2col sm-grid-2col xs-grid-1col gutter-extra-large"
                  filter={false}
                />
              ) : (
                <div className="text-center py-12">
                  <img
                    src="/assets/img/no-data-bro.svg"
                    className="w-[500px] mx-auto opacity-70"
                    alt="no-data"
                    width=""
                    height=""
                  />
                  <h3 className="text-xl text-gray-600 mt-4">No articles found by this author</h3>
                  <p className="text-gray-500">Check back later for new content!</p>
                </div>
              )}
            </Col>
          </Row>
        </Container>
      </section>
      {/* Section Start */}
    </div>
  );
};

export default AuthorPage;
