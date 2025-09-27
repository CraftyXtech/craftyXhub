import React from "react";
import Head from "@/layout/head/Head";
import AuthFooter from "./AuthFooter";
import Logo from "@/layout/logo/Logo";
import { Block, BlockContent, BlockDes, BlockHead, BlockTitle, Icon } from "@/components/Component";
import { Link } from "react-router-dom";
import { Button } from "@/components/Component";

const RegisterSuccess = () => {
  return (
    <>
      <Head title="Registration Successful" />
        <Block className="nk-block-middle nk-auth-body">
          <div className="brand-logo pb-5">
            <Logo />
          </div>
          <BlockHead>
            <BlockContent>
              <div className="text-center pb-4">
                <Icon name="check-circle" className="text-success" style={{ fontSize: '4rem' }}></Icon>
              </div>
              <BlockTitle tag="h4" className="text-center">Welcome to CraftyXhub!</BlockTitle>
              <BlockDes className="text-center">
                <p className="text-success mb-3">Your account has been created successfully.</p>
                <p className="text-muted mb-4">
                  You can now sign in with your credentials and start exploring our content management dashboard.
                </p>
                <div className="d-grid gap-2">
                  <Link to="/login">
                    <Button color="primary" size="lg" className="w-100">
                      <Icon name="sign-in" className="me-2"></Icon>
                      Sign In Now
                    </Button>
                  </Link>
                  <Link to="/" className="text-muted">
                    <small>Or go to homepage</small>
                  </Link>
                </div>
              </BlockDes>
            </BlockContent>
          </BlockHead>
        </Block>
        <AuthFooter />
    </>
  );
};

export default RegisterSuccess;