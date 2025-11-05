import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
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
import { Spinner, Alert } from "reactstrap";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { axiosPublic } from "@/api/axios";

const Register = () => {
  const [passState, setPassState] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorVal, setError] = useState("");
  const { register, handleSubmit, formState: { errors } } = useForm();
  const navigate = useNavigate();
  
  const handleFormSubmit = async (formData) => {
    setLoading(true);
    setError("");
    
    // Validate username format
    const usernamePattern = /^[a-zA-Z0-9_-]+$/;
    if (!usernamePattern.test(formData.username)) {
      setError('Username can only contain letters, numbers, underscores (_), and hyphens (-). No spaces or special characters allowed.');
      setLoading(false);
      return;
    }
    
    try {
      const response = await axiosPublic.post('auth/register', {
        full_name: formData.name,
        username: formData.username,
        email: formData.email,
        password: formData.password,
        confirm_password: formData.confirm_password,
      });
      
      console.log('Registration successful:', response.data);
      
      // Redirect to registration success page
      navigate('/auth-register-success');
    } catch (error) {
      console.error('Registration error:', error);
      // Prefer backend-provided messages
      let errorMessage = error.response?.data?.message;
      const detail = error.response?.data?.detail;
      
      // FastAPI can return `detail` as a string (HTTPException) or a list (validation errors)
      if (!errorMessage && typeof detail === 'string') {
        errorMessage = detail;
        
        // Make common errors user-friendly
        if (errorMessage.includes('already registered') || errorMessage.includes('already exists')) {
          if (errorMessage.toLowerCase().includes('email')) {
            errorMessage = 'This email is already registered. Please login or use a different email.';
          } else if (errorMessage.toLowerCase().includes('username')) {
            errorMessage = 'This username is already taken. Please choose a different one.';
          }
        }
      }
      
      if (!errorMessage && Array.isArray(detail)) {
        const errors = detail.map(err => {
          const msg = err.msg || err.message || JSON.stringify(err);
          const field = err.loc ? err.loc[err.loc.length - 1] : '';
          
          // Make username pattern errors user-friendly
          if (msg.includes("String should match pattern") && field === 'username') {
            return 'Username can only contain letters, numbers, underscores (_), and hyphens (-). No spaces or special characters allowed.';
          }
          
          // Make other validation errors friendly
          if (msg.includes('value is not a valid email')) {
            return 'Please enter a valid email address.';
          }
          
          if (msg.includes('ensure this value has at least')) {
            return `${field} is too short. ${msg}`;
          }
          
          if (msg.includes('field required')) {
            return `${field} is required.`;
          }
          
          return msg;
        });
        errorMessage = errors.join(' ');
      }
      
      if (!errorMessage) {
        errorMessage = error.message || "Registration failed. Please try again.";
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  return <>
    <Head title="Register" />
      <Block className="nk-block-middle nk-auth-body  wide-xs">
        <div className="brand-logo pb-4 text-center">
          <Logo />
        </div>
        <PreviewCard className="card-bordered" bodyClass="card-inner-lg">
          <BlockHead>
            <BlockContent>
              <BlockTitle tag="h4">Register</BlockTitle>
              <BlockDes>
                <p>Create New CraftyXhub Account</p>
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
          <form className="is-alter" onSubmit={handleSubmit(handleFormSubmit)}>
            <div className="form-group">
              <label className="form-label" htmlFor="name">
                Name
              </label>
              <div className="form-control-wrap">
                <input
                  type="text"
                  id="name"
                  {...register('name', { required: true })}
                  placeholder="Enter your name"
                  className="form-control-lg form-control" />
                {errors.name && <p className="invalid">This field is required</p>}
              </div>
            </div>
            <div className="form-group">
              <div className="form-label-group">
                <label className="form-label" htmlFor="username">
                  Username
                </label>
              </div>
              <div className="form-control-wrap">
                <input
                  type="text"
                  id="username"
                  {...register('username', { 
                    required: true, 
                    minLength: 3,
                    pattern: {
                      value: /^[a-zA-Z0-9_-]+$/,
                      message: "Only letters, numbers, underscores (_), and hyphens (-) allowed"
                    }
                  })}
                  className="form-control-lg form-control"
                  placeholder="e.g. john_doe or john-doe123"
                  title="Only letters, numbers, underscores, and hyphens allowed" />
                {errors.username && (
                  <p className="invalid">
                    {errors.username.type === 'pattern' 
                      ? 'Username can only contain letters, numbers, underscores (_), and hyphens (-). No spaces or special characters.'
                      : 'Username is required (min 3 characters)'}
                  </p>
                )}
                <span className="form-note text-muted">
                  Only letters, numbers, underscores (_), and hyphens (-) allowed. No spaces.
                </span>
              </div>
            </div>
            <div className="form-group">
              <div className="form-label-group">
                <label className="form-label" htmlFor="default-01">
                  Email
                </label>
              </div>
              <div className="form-control-wrap">
                <input
                  type="text"
                  bssize="lg"
                  id="default-01"
                  {...register('email', { required: true })}
                  className="form-control-lg form-control"
                  placeholder="Enter your email address" />
                {errors.email && <p className="invalid">This field is required</p>}
              </div>
            </div>
            <div className="form-group">
              <div className="form-label-group">
                <label className="form-label" htmlFor="password">
                  Password
                </label>
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
                  {...register('password', { required: "This field is required", minLength: { value: 8, message: "Password must be at least 8 characters" } })}
                  placeholder="Enter your password"
                  className={`form-control-lg form-control ${passState ? "is-hidden" : "is-shown"}`} />
                {errors.password && <span className="invalid">{errors.password.message || 'This field is required'}</span>}
              </div>
            </div>
            <div className="form-group">
              <div className="form-label-group">
                <label className="form-label" htmlFor="confirm_password">
                  Confirm Password
                </label>
              </div>
              <div className="form-control-wrap">
                <input
                  type={passState ? "text" : "password"}
                  id="confirm_password"
                  {...register('confirm_password', { required: "This field is required" })}
                  placeholder="Re-enter your password"
                  className={`form-control-lg form-control ${passState ? "is-hidden" : "is-shown"}`} />
                {errors.confirm_password && <span className="invalid">{errors.confirm_password.message}</span>}
              </div>
            </div>
            <div className="form-group">
              <Button type="submit" color="primary" size="lg" className="btn-block">
                {loading ? <Spinner size="sm" color="light" /> : "Register"}
              </Button>
            </div>
          </form>
          <div className="form-note-s2 text-center pt-4">
            {" "}
            Already have an account?{" "}
            <Link to={`/login`}>
              <strong>Sign in instead</strong>
            </Link>
          </div>
          <div className="text-center pt-4 pb-3">
            <h6 className="overline-title overline-title-sap">
              <span>OR</span>
            </h6>
          </div>
          <ul className="nav justify-center gx-8">
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
export default Register;
