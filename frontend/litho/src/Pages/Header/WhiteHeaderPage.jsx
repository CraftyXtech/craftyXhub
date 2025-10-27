import React from 'react'

// Libraries
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { Link } from 'react-router-dom'

// Components
import { Header, HeaderCart, HeaderLanguage, HeaderNav, Menu, SearchBar } from "../../Components/Header/Header";
import Logo from '../../Components/Logo';
import FooterStyle05 from '../../Components/Footers/FooterStyle05';
import SideButtons from "../../Components/SideButtons";

const WhiteHeaderPage = (props) => {
  return (
    <>
      {/* Header Start */}
      <Header topSpace={{ desktop: true }} type="reverse-scroll">
        <HeaderNav theme="light" bg="white" menu="light" expand="lg" className="px-[35px] py-[0px] lg:px-[15px] md:px-0" containerClass="sm:px-0">
          <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
            <Logo className="flex items-center" />
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
            <SearchBar className="pr-0 xs:pl-[15px]" />
            <HeaderLanguage className="xs:pl-[15px]" />
            <HeaderCart className="xs:pl-[15px]" style={{ "--base-color": "#0038e3" }} />
          </Col>
        </HeaderNav>
      </Header>
      {/* Header End */}
      <SideButtons />

      {/* Section start */}
      <section className="overflow-visible cover-background" style={{ backgroundImage: `url("https://via.placeholder.com/1920x1080")` }}>
        <Container>
          <Row className="full-screen md:h-[650px] sm:h-[550px] xs:h-[450px]">
            <Col md={5} sm={7} className="flex flex-col py-32">
              <h1 className="font-serif leading-[120px] font-semibold tracking-[-10px] mb-0 mt-auto text-darkgray text-[11rem] md:leading-[90px] md:text-[9rem] sm:leading-[70px] sm:-tracking-[5px] xs:leading-[70px]">
                Brian <br></br>
                <span className="text-border text-[130px] text-border-width-2px fill-transparent inline-block tracking-[-6px] lg:text-[110px] md:text-[90px] md:leading-[85px] sm:text-[65px] sm:leading-[50px] sm:-tracking-[.5px]">miller</span>
              </h1>
              <div className="flex font-serif items-center font-medium text-xmd text-darkgray mt-auto">
                <span className="flex-shrink-0 h-[2px] w-[20px] bg-darkgray item-center mr-[15px]"></span>
                <div className="grow tracking-[-.5px]">Award winner freelancer</div>
              </div>
            </Col>
          </Row>
        </Container>
      </section>
      {/* Section End */}

      {/* Blog Section Start */}
      <section className="pt-[160px] lg:pt-[120px] md:pt-[95px] sm:pt-[80px] xs:pt-[50px]">
        <Container>
          <Row className="justify-center text-center">
            <Col lg={6} className="mb-[95px] md:mb-[75px]">
              <span className="text-md font-serif font-medium uppercase inline-block text-gradient bg-gradient-to-r from-[#556fff] via-[#e05fc4] to-[#ff798e] mb-[15px]">Welcome to</span>
              <h5 className="text-darkgray font-semibold font-serif -tracking-[1px] mb-0">CraftyX Hub Blog Platform</h5>
            </Col>
          </Row>
        </Container>
      </section>
      {/* Blog Section End */}
      {/* footer Start*/}
      <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
      {/* footer End */}
    </>
  )
}

export default WhiteHeaderPage
