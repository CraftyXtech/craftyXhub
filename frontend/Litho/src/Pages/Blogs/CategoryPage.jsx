import React, { useEffect, useState } from 'react'

// Libraries
import { Col, Container, Row } from 'react-bootstrap'
import { useParams } from 'react-router-dom';
import { Parallax } from "react-scroll-parallax";

// Components
import BlogClassic from '../../Components/Blogs/BlogClassic'

// API
import { usePostsByCategory, useCategories } from '../../api'

const CategoryPage = (props) => {
    const { category } = useParams();
    const { categories } = useCategories();
    
    // Find the category ID based on the category slug/name
    const categoryData = categories?.find(cat => 
        cat.name?.toLowerCase().replace(/\s+/g, '').includes(category?.toLowerCase()) ||
        cat.slug?.toLowerCase() === category?.toLowerCase()
    );
    
    const { posts, loading, error } = usePostsByCategory(categoryData?.id, { published: true });

    return (
        <div style={props.style}>
            {/* Parallax Section Start */}
            <div className="py-[80px] h-auto overflow-hidden md:relative md:py-[40px]">
                <Parallax className="lg-no-parallax bg-cover absolute -top-[100px] landscape:md:top-[-20px] left-0 w-full h-[100vh]" translateY={[-40, 40]} style={{ backgroundImage: `url(https://via.placeholder.com/1920x1080)` }}></Parallax>
                <Container className="h-full relative">
                    <Row className="justify-center h-[300px] sm:h-[250px]">
                        <Col xl={6} lg={6} md={8} className="text-center flex justify-center flex-col font-serif">
                            <h1 className="text-gradient bg-gradient-to-r from-[#556fff] via-[#e05fc4] to-[#ff798e] mb-[15px] inline-block text-xmd leading-[20px]">{category}</h1>
                            <h2 className="text-darkgray font-medium -tracking-[1px] mb-0">Every new print and color of the season</h2>
                        </Col>
                    </Row>
                </Container>
            </div>
            {/* Parallax Section End */}

            {/* Section Start */}
            <section className="overflow-hidden relative px-[11%] pb-[130px] bg-lightgray xl:px-[2%] lg:pb-[90px] md:px-0 md:pb-[75px] sm:pb-[50px]">
                <Container fluid>
                    <Row>
                        <Col>
                            {loading ? (
                                <div className="text-center py-12">
                                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
                                    <p className="mt-4 text-gray-600 text-lg">Loading {category} articles...</p>
                                </div>
                            ) : error ? (
                                <div className="text-center py-12 text-red-600">
                                    <p className="text-lg">Error loading articles. Please try again later.</p>
                                </div>
                            ) : posts && posts.length > 0 ? (
                                <BlogClassic link="/posts/" data={posts} pagination={true} grid="grid grid-4col xl-grid-4col lg-grid-3col md-grid-2col sm-grid-2col xs-grid-1col gutter-extra-large" filter={false} />
                            ) : (
                                <div className="text-center py-12">
                                    <img src="/assets/img/no-data-bro.svg" className="w-[500px] mx-auto opacity-70" alt="no-data" width="" height="" />
                                    <h3 className="text-xl text-gray-600 mt-4">No articles found in this category</h3>
                                    <p className="text-gray-500">Check back later for new content!</p>
                                </div>
                            )}
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Section Start */}
        </div>
    )
}

export default CategoryPage
