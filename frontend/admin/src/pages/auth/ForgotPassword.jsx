import React from "react";
import { useNavigate } from "react-router-dom";
import Head from "@/layout/head/Head";
import AuthFooter from "./AuthFooter";
import Logo from "@/layout/logo/Logo";
import { Block, BlockContent, BlockDes, BlockHead, BlockTitle, Button, PreviewCard } from "@/components/Component";
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";


const ForgotPassword = () => {
  const navigate = useNavigate();
  const onFormSubmit = () => {
    navigate('/auth-success');
  };
  const {  handleSubmit } = useForm();
  return (
    <>
      <Head title="Forgot-Password" />
        <Block className="nk-block-middle nk-auth-body  wide-xs">
          <div className="brand-logo pb-4 text-center">
            <Logo />
          </div>
          <PreviewCard className="card-bordered" bodyClass="card-inner-lg">
            <BlockHead>
              <BlockContent>
                <BlockTitle tag="h5">Reset password</BlockTitle>
                <BlockDes>
                  <p>If you forgot your password, well, then we’ll email you instructions to reset your password.</p>
                </BlockDes>
              </BlockContent>
            </BlockHead>
            <form onSubmit={handleSubmit(onFormSubmit)}>
              <div className="form-group">
                <div className="form-label-group">
                  <label className="form-label" htmlFor="default-01">
                    Email
                  </label>
                </div>
                <input
                  type="text"
                  className="form-control form-control-lg"
                  id="default-01"
                  placeholder="Enter your email address"
                />
              </div>
              <div className="form-group">
                <Button color="primary" size="lg" className="btn-block" >
                  Send Reset Link
                </Button>
              </div>
            </form>
            <div className="form-note-s2 text-center pt-4">
              <Link to={`/auth-login`}>
                <strong>Return to login</strong>
              </Link>
            </div>
          </PreviewCard>
        </Block>
        <AuthFooter />
    </>
  );
};
export default ForgotPassword;
