import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Head from "@/layout/head/Head";
import AuthFooter from "./AuthFooter";
import Logo from "@/layout/logo/Logo";
import {
  Block,
  BlockContent,
  BlockDes,
  BlockHead,
  BlockTitle,
  Button,
  Icon,
  PreviewCard,
} from "@/components/Component";
import { Form, Spinner, Alert } from "reactstrap";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import useAuth from "@/api/useAuth";
import { axiosPrivate } from "@/api/axios";

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [passState, setPassState] = useState(false);
  const [errorVal, setError] = useState("");
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const onFormSubmit = async (formData) => {
    setLoading(true);
    setError("");
    
    try {
      // Step 1: Login to get token
      const loginResponse = await axiosPrivate.post('auth/login', {
        email: formData.name,
        password: formData.passcode
      });
      
      console.log('Login response:', loginResponse.data);
      
      // Step 2: Fetch user data using the token
      const token = loginResponse.data.access_token;
      const userResponse = await axiosPrivate.get('auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('User data:', userResponse.data);
      
      // Step 3: Store both token and user data
      login(token, userResponse.data);
      
      // Navigate to the intended destination or dashboard
      const redirectTo = location.state?.from?.pathname || '/';
      navigate(redirectTo, { replace: true });
    } catch (error) {
      console.error('Login error:', error);
      
      // Handle CORS/network errors
      if (error.code === 'ERR_NETWORK' || !error.response) {
        setError("Network error. Please check your connection and try again.");
        return;
      }
      
      // Handle FastAPI validation errors (422) - detail is an array of error objects
      const detail = error.response?.data?.detail;
      let errorMessage = error.response?.data?.message || error.message || "Login failed. Please check your credentials.";
      
      if (detail) {
        if (Array.isArray(detail)) {
          // Pydantic validation errors - format them nicely
          const validationErrors = detail.map(err => {
            const field = Array.isArray(err.loc) ? err.loc.slice(1).join('.') : 'field';
            return `${field}: ${err.msg}`;
          }).join('; ');
          errorMessage = validationErrors || errorMessage;
        } else if (typeof detail === 'string') {
          // Simple string error
          errorMessage = detail;
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const {  register, handleSubmit, formState: { errors } } = useForm();

  return <>
    <Head title="Login" />
      <Block className="nk-block-middle nk-auth-body  wide-xs">
        <div className="brand-logo pb-4 text-center">
          <Logo />
        </div>

        <PreviewCard className="card-bordered" bodyClass="card-inner-lg">
          <BlockHead>
            <BlockContent>
              <BlockTitle tag="h4">Sign-In</BlockTitle>
              <BlockDes>
                <p>Access Dashboard using your email and password.</p>
              </BlockDes>
            </BlockContent>
          </BlockHead>
          {errorVal && (
            <div className="mb-3">
              <Alert color="danger" className="alert-icon">
                <Icon name="alert-circle" /> {errorVal}
              </Alert>
            </div>
          )}
          <Form className="is-alter" onSubmit={handleSubmit(onFormSubmit)}>
            <div className="form-group">
              <div className="form-label-group">
                <label className="form-label" htmlFor="default-01">
                  Email or Username
                </label>
              </div>
              <div className="form-control-wrap">
                <input
                  type="text"
                  id="default-01"
                  {...register('name', { required: "This field is required" })}
                  placeholder="Enter your email address"
                  className="form-control-lg form-control" />
                {errors.name && <span className="invalid">{errors.name.message}</span>}
              </div>
            </div>
            <div className="form-group">
              <div className="form-label-group">
                <label className="form-label" htmlFor="password">
                  Password
                </label>
                <Link className="link link-primary link-sm" to={`/auth-reset`}>
                  Forgot Password?
                </Link>
              </div>
              <div className="form-control-wrap">
                <a
                  href="#password"
                  onClick={(ev) => {
                    ev.preventDefault();
                    setPassState(!passState);
                  }}
                  className={`form-icon lg form-icon-right passcode-switch ${passState ? "is-hidden" : "is-shown"}`}
                >
                  <Icon name="eye" className="passcode-icon icon-show"></Icon>

                  <Icon name="eye-off" className="passcode-icon icon-hide"></Icon>
                </a>
                <input
                  type={passState ? "text" : "password"}
                  id="password"
                {...register('passcode', { required: "This field is required" })}
                  placeholder="Enter your passcode"
                  className={`form-control-lg form-control ${passState ? "is-hidden" : "is-shown"}`} />
                {errors.passcode && <span className="invalid">{errors.passcode.message}</span>}
              </div>
            </div>
            <div className="form-group">
              <Button size="lg" className="btn-block" type="submit" color="primary">
                {loading ? <Spinner size="sm" color="light" /> : "Sign in"}
              </Button>
            </div>
          </Form>
          <div className="form-note-s2 text-center pt-4">
            New on our platform? <Link to={`/auth-register`}>Create an account</Link>
          </div>
          <div className="text-center pt-4 pb-3">
            <h6 className="overline-title overline-title-sap">
              <span>OR</span>
            </h6>
          </div>
          <ul className="nav justify-center gx-4">
            <li className="nav-item">
              <a
                className="nav-link"
                href="#socials"
                onClick={(ev) => {
                  ev.preventDefault();
                }}
              >
                Facebook
              </a>
            </li>
            <li className="nav-item">
              <a
                className="nav-link"
                href="#socials"
                onClick={(ev) => {
                  ev.preventDefault();
                }}
              >
                Google
              </a>
            </li>
          </ul>
        </PreviewCard>
      </Block>
      <AuthFooter />
  </>;
};
export default Login;