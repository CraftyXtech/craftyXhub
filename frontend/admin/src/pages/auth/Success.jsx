import React from "react";
import Head from "@/layout/head/Head";
import AuthFooter from "./AuthFooter";
import Logo from "@/layout/logo/Logo";
import { Block, BlockContent, BlockDes, BlockHead, BlockTitle } from "@/components/Component";
import { Link } from "react-router-dom";
import {Button} from "@/components/Component";

const Success = () => {
  return (
    <>
      <Head title="Success" />
        <Block className="nk-block-middle nk-auth-body">
          <div className="brand-logo pb-5">
            <Logo />
          </div>
          <BlockHead>
            <BlockContent>
              <BlockTitle tag="h4">Registration Successful!</BlockTitle>
              <BlockDes className="text-success">
                <p>Welcome to CraftyXhub! Your account has been created successfully.</p>
                <p>You can now sign in with your credentials and explore the dashboard.</p>
                <Link to={`/login`}>
                  <Button color="primary" size="lg">
                    Sign In Now
                  </Button>
                </Link>
              </BlockDes>
            </BlockContent>
          </BlockHead>
        </Block>
        <AuthFooter />
    </>
  );
};
export default Success;
