import React from 'react'

// Libraries
import { Col, Navbar } from 'react-bootstrap'
import { Link, Outlet } from 'react-router-dom'

// Components
import Header, { HeaderNav, Menu, SearchBar } from '../Components/Header/Header'
import Logo from '../Components/Logo/Logo'
import FooterStyle05 from '../Components/Footers/FooterStyle05'

const ModalPopupPage = (props) => {
    return (
        <div>
            {/* Header Start */}
            <Header topSpace={{ desktop: true }} type="reverse-scroll">
                <HeaderNav fluid="fluid" theme="light" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" containerClass="sm:px-0">
                    <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                        <Logo variant="default" />
                    </Col>
                    <div className="col-auto hidden order-last md:block">
                        <Navbar.Toggle className="md:ml-[10px] sm:ml-0">
                            <span className="navbar-toggler-line"></span>
                            <span className="navbar-toggler-line"></span>
                            <span className="navbar-toggler-line"></span>
                            <span className="navbar-toggler-line"></span>
                        </Navbar.Toggle>
                    </div>
                    <Navbar.Collapse className="col-auto pe-0 justify-end">
                        <Menu {...props} />
                    </Navbar.Collapse>
                    <Col className="col-auto text-right pe-0 !pl-[15px]">
                        <SearchBar className="xs:pl-[15px] pr-0" />
                    </Col>
                </HeaderNav>
            </Header>
            {/* Header End */}
            <Outlet />
            <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
        </div>
    )
}

export default ModalPopupPage
