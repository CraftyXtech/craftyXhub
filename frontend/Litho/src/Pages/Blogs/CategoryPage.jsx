import React, { useEffect, useState } from 'react'

// Libraries
import { Col, Container, Row } from 'react-bootstrap'
import { useParams } from 'react-router-dom';
import { Parallax } from "react-scroll-parallax";

// Components
import BlogClassic from '../../Components/Blogs/BlogClassic'

// Data
import { blogData } from '../../Components/Blogs/BlogData'

const CategoryPage = (props) => {
    const { category } = useParams();
    const [data, setData] = useState(null)

    useEffect(() => {
        const filteredData = blogData.filter((item) => item.category.toString().split(" ").join("").toLowerCase().includes(category))
        setData(filteredData)
    }, [category])

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
                            {
                                data ? (
                                    data.length > 0 ? (
                                        <BlogClassic link="/blog/post/" data={data} pagination={true} grid="grid grid-4col xl-grid-4col lg-grid-3col md-grid-2col sm-grid-2col xs-grid-1col gutter-extra-large" filter={false} />
                                    ) : (
                                        <div className="text-center">
                                            <img src="/assets/img/no-data-bro.svg" className="w-[500px] mx-auto opacity-70" alt="no-data" width="" height="" />
                                        </div>
                                    )
                                ) : (
                                    <BlogClassic link="/blog/post/" pagination={true} grid="grid grid-4col xl-grid-4col lg-grid-3col md-grid-2col sm-grid-2col xs-grid-1col gutter-extra-large" filter={false} />
                                )
                            }
                        </Col>
                    </Row>
                </Container>
            </section>
            {/* Section Start */}
        </div>
    )
}

export default CategoryPage
