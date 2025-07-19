import React, { useState, useEffect } from "react";
import { NavLink } from "react-router-dom";
import { Icon, UserAvatar } from "@/components/Component";
import { findUpper } from "@/utils/Utils";
import {  DropdownItem, UncontrolledDropdown, DropdownMenu, DropdownToggle } from "reactstrap";
import { useAuth } from "@/api/AuthProvider";

const UserProfileAside = ({updateSm,sm}) => {
  const { auth, isAuthenticated } = useAuth();
  const [profileName, setProfileName] = useState("");
  const [profileEmail, setProfileEmail] = useState("");
  
  useEffect(() => {
    sm ? document.body.classList.add("toggle-shown") : document.body.classList.remove("toggle-shown");
  }, [sm]);

  useEffect(() => {
    if (isAuthenticated && auth?.user) {
      setProfileName(auth.user.full_name || "User");
      setProfileEmail(auth.user.email || "");
    } else {
      setProfileName("Guest User");
      setProfileEmail("Not signed in");
    }
  }, [isAuthenticated, auth]);
  
  return (
    <div className="card-inner-group">
    <div className="card-inner">
        <div className="user-card">
        <UserAvatar text={findUpper(profileName)} theme="primary" />
        <div className="user-info">
            <span className="lead-text">{profileName}</span>
            <span className="sub-text">{profileEmail}</span>
        </div>
        <div className="user-action">
            <UncontrolledDropdown >
            <DropdownToggle tag="a" className="btn btn-icon btn-trigger me-n2">
                <Icon name="more-v"></Icon>
            </DropdownToggle>
            <DropdownMenu end>
                <ul className="link-list-opt no-bdr">
                <li>
                    <DropdownItem
                    tag="a"
                    href="#dropdownitem"
                    onClick={(ev) => {
                        ev.preventDefault();
                    }}
                    >
                    <Icon name="camera-fill"></Icon>
                    <span>Change Photo</span>
                    </DropdownItem>
                </li>
                <li>
                    <DropdownItem
                    tag="a"
                    href="#dropdownitem"
                    onClick={(ev) => {
                        ev.preventDefault();
                    }}
                    >
                    <Icon name="edit-fill"></Icon>
                    <span>Update Profile</span>
                    </DropdownItem>
                </li>
                </ul>
            </DropdownMenu>
            </UncontrolledDropdown>
        </div>
        </div>
    </div>
    <div className="card-inner">
        <div className="user-account-info py-0">
        <h6 className="overline-title-alt">Account Status</h6>
        <div className="user-balance">
            {isAuthenticated ? (
              <>
                <span className="text-success">Active</span>
                {auth?.user?.is_verified && (
                  <small className="text-info"> • Verified</small>
                )}
              </>
            ) : (
              <span className="text-warning">Not Signed In</span>
            )}
        </div>
        <div className="user-balance-sub">
            Member since{" "}
            <span>
            {auth?.user?.created_at ? 
              new Date(auth.user.created_at).toLocaleDateString() : 
              "N/A"
            }
            </span>
        </div>
        </div>
    </div>
    <div className="card-inner p-0">
        <ul className="link-list-menu">
        <li onClick={() => updateSm(false)}>
            <NavLink
            to={`/user-profile-regular`}
            >
            <Icon name="user-fill-c"></Icon>
            <span>Personal Information</span>
            </NavLink>
        </li>
        <li onClick={() => updateSm(false)}>
            <NavLink
            to={`/user-profile-notification`}
            >
            <Icon name="bell-fill"></Icon>
            <span>Notification</span>
            </NavLink>
        </li>
        <li onClick={() => updateSm(false)}>
            <NavLink
            to={`/user-profile-activity`}
            >
            <Icon name="activity-round-fill"></Icon>
            <span>Account Activity</span>
            </NavLink>
        </li>
        <li onClick={() => updateSm(false)}>
            <NavLink
            to={`/user-profile-setting`}
            >
            <Icon name="lock-alt-fill"></Icon>
            <span>Security Setting</span>
            </NavLink>
        </li>
        </ul>
    </div>
    </div>
  );
};

export default UserProfileAside;
