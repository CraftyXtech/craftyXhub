import React, { useEffect, useState } from 'react'

// Libraries
import { Col, Container, Row } from 'react-bootstrap'
import { useParams } from 'react-router-dom';
import { Parallax } from "react-scroll-parallax";

// Components
import BlogMetro from '../../Components/Blogs/BlogMetro'
import { Link } from 'react-router-dom'

// API
import { usePostsByCategory, useCategoryBySlug, useCategories } from '../../api'

const CategoryPage = (props) => {
    const { categorySlug } = useParams();
    
    // Get category details directly by slug from API
    const { category: categoryData, loading: categoryLoading, error: categoryError } = useCategoryBySlug(categorySlug);
    
    // Get posts for this category
    const { posts, loading: postsLoading, error: postsError } = usePostsByCategory(categoryData?.id, { published: true });
    
    // Get all categories for related categories sidebar
    const { categories: allCategories } = useCategories();
    
    // Combined loading and error states
    const loading = categoryLoading || postsLoading;
    const error = categoryError || postsError;
    
    // Filter related categories (exclude current one)
    const relatedCategories = allCategories?.filter(cat => cat.id !== categoryData?.id)?.slice(0, 5) || [];

    return (
        <div style={props.style}>
            {/* Parallax Section Start */}
            <div className="py-[80px] h-auto overflow-hidden md:relative md:py-[40px]">
                <Parallax className="lg-no-parallax bg-cover absolute -top-[100px] landscape:md:top-[-20px] left-0 w-full h-[100vh]" translateY={[-40, 40]} style={{ backgroundImage: `url(https://via.placeholder.com/1920x1080)` }}></Parallax>
                <Container className="h-full relative">
                    <Row className="justify-center h-[300px] sm:h-[250px]">
                        <Col xl={6} lg={6} md={8} className="text-center flex justify-center flex-col font-serif">
                            {categoryLoading ? (
                                <div className="animate-pulse">
                                    <div className="h-8 bg-gray-300 rounded mb-4"></div>
                                    <div className="h-6 bg-gray-200 rounded"></div>
                                </div>
                            ) : categoryError ? (
                                <div>
                                    <h1 className="text-gradient bg-gradient-to-r from-[#556fff] via-[#e05fc4] to-[#ff798e] mb-[15px] inline-block text-xmd leading-[20px]">Category Not Found</h1>
                                    <h2 className="text-darkgray font-medium -tracking-[1px] mb-0">The requested category could not be found</h2>
                                </div>
                            ) : categoryData ? (
                                <div>
                                    <h1 className="text-gradient bg-gradient-to-r from-[#556fff] via-[#e05fc4] to-[#ff798e] mb-[15px] inline-block text-xmd leading-[20px]">
                                        {categoryData.name}
                                    </h1>
                                    <h2 className="text-darkgray font-medium -tracking-[1px] mb-0">
                                        {categoryData.description || `Discover the latest articles in ${categoryData.name}`}
                                    </h2>
                                    {posts && posts.length > 0 && (
                                        <p className="text-sm text-gray-500 mt-2">
                                            {posts.length} article{posts.length !== 1 ? 's' : ''} found
                                        </p>
                                    )}
                                </div>
                            ) : (
                                <div>
                                    <h1 className="text-gradient bg-gradient-to-r from-[#556fff] via-[#e05fc4] to-[#ff798e] mb-[15px] inline-block text-xmd leading-[20px]">{categorySlug}</h1>
                                    <h2 className="text-darkgray font-medium -tracking-[1px] mb-0">Loading category information...</h2>
                                </div>
                            )}
                        </Col>
                    </Row>
                </Container>
            </div>
            {/* Parallax Section End */}

            {/* Breadcrumb Section */}
            {categoryData && (
                <section className="bg-white py-4 border-b border-gray-200">
                    <Container fluid>
                        <Row>
                            <Col>
                                <nav className="flex px-[11%] xl:px-[2%] md:px-[15px]" aria-label="Breadcrumb">
                                    <ol className="inline-flex items-center space-x-1 md:space-x-3">
                                        <li className="inline-flex items-center">
                                            <Link to="/" className="inline-flex items-center text-sm font-medium text-gray-700 hover:text-blue-600">
                                                <i className="feather-home mr-2"></i>
                                                Home
                                            </Link>
                                        </li>
                                        <li>
                                            <div className="flex items-center">
                                                <i className="feather-chevron-right text-gray-400 mx-2"></i>
                                                <Link to="/blog" className="ml-1 text-sm font-medium text-gray-700 hover:text-blue-600">
                                                    Blog
                                                </Link>
                                            </div>
                                        </li>
                                        <li aria-current="page">
                                            <div className="flex items-center">
                                                <i className="feather-chevron-right text-gray-400 mx-2"></i>
                                                <span className="ml-1 text-sm font-medium text-gray-500">
                                                    {categoryData.name}
                                                </span>
                                            </div>
                                        </li>
                                    </ol>
                                </nav>
                            </Col>
                        </Row>
                    </Container>
                </section>
            )}

            {/* Section Start */}
            <section className="overflow-hidden relative px-[11%] pb-[130px] bg-lightgray xl:px-[2%] lg:pb-[90px] md:px-0 md:pb-[75px] sm:pb-[50px]">
                <Container fluid>
                    <Row>
                        <Col lg={8}>
                            {loading ? (
                                <div className="text-center py-12">
                                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
                                    <p className="mt-4 text-gray-600 text-lg">Loading {categoryData?.name || categorySlug} articles...</p>
                                </div>
                            ) : categoryError ? (
                                <div className="text-center py-12 text-red-600">
                                    <h3 className="text-xl mb-4">Category Not Found</h3>
                                    <p className="text-lg">The category "{categorySlug}" does not exist.</p>
                                    <p className="text-sm text-gray-500 mt-2">Please check the URL or browse our available categories.</p>
                                </div>
                            ) : postsError ? (
                                <div className="text-center py-12 text-red-600">
                                    <p className="text-lg">Error loading articles. Please try again later.</p>
                                    <p className="text-sm text-gray-500 mt-2">{postsError}</p>
                                </div>
                            ) : posts && posts.length > 0 ? (
                                <BlogMetro 
                                    overlay="#374162" 
                                    grid="grid grid-3col xl-grid-3col lg-grid-2col md-grid-2col sm-grid-2col xs-grid-1col gutter-large" 
                                    data={posts} 
                                    link="/posts/" 
                                    pagination={true} 
                                    className="blog-metro"
                                />
                            ) : categoryData ? (
                                <div className="text-center py-12">
                                    <img src="/assets/img/no-data-bro.svg" className="w-[500px] mx-auto opacity-70" alt="no-data" width="" height="" />
                                    <h3 className="text-xl text-gray-600 mt-4">No articles found in {categoryData.name}</h3>
                                    <p className="text-gray-500">Be the first to publish content in this category!</p>
                                    {categoryData.description && (
                                        <p className="text-sm text-gray-400 mt-2 italic">"{categoryData.description}"</p>
                                    )}
                                </div>
                            ) : (
                                <div className="text-center py-12">
                                    <h3 className="text-xl text-gray-600 mt-4">Category information unavailable</h3>
                                    <p className="text-gray-500">Please try refreshing the page.</p>
                                </div>
                            )}
                        </Col>
                        
                        {/* Sidebar - Related Categories */}
                        <Col lg={4} className="md:mt-[50px]">
                            <div className="bg-white p-6 rounded-lg shadow-sm sticky top-20">
                                <h3 className="text-lg font-semibold text-darkgray mb-4 border-b border-gray-200 pb-2">
                                    Related Categories
                                </h3>
                                {relatedCategories.length > 0 ? (
                                    <ul className="space-y-3">
                                        {relatedCategories.map((cat) => (
                                            <li key={cat.id}>
                                                <Link 
                                                    to={`/category/${cat.slug}`}
                                                    className="flex items-center justify-between p-3 rounded-md hover:bg-gray-50 transition-colors group"
                                                >
                                                    <div>
                                                        <span className="text-darkgray group-hover:text-blue-600 font-medium">
                                                            {cat.name}
                                                        </span>
                                                        {cat.description && (
                                                            <p className="text-xs text-gray-500 mt-1">
                                                                {cat.description.length > 50 
                                                                    ? `${cat.description.substring(0, 50)}...` 
                                                                    : cat.description
                                                                }
                                                            </p>
                                                        )}
                                                    </div>
                                                    <i className="feather-arrow-right text-gray-400 group-hover:text-blue-600"></i>
                                                </Link>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p className="text-gray-500 text-sm">No related categories available</p>
                                )}
                                
                                {/* Category Stats */}
                                {categoryData && (
                                    <div className="mt-6 pt-4 border-t border-gray-200">
                                        <h4 className="text-md font-semibold text-darkgray mb-3">Category Info</h4>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-gray-600">Total Articles:</span>
                                                <span className="font-medium">{posts?.length || 0}</span>
                                            </div>
                                            {categoryData.created_at && (
                                                <div className="flex justify-between">
                                                    <span className="text-gray-600">Created:</span>
                                                    <span className="font-medium">
                                                        {new Date(categoryData.created_at).toLocaleDateString()}
                                                    </span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Section Start */}
        </div>
    )
}

export default CategoryPage
