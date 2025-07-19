import React, { useState, useEffect } from "react";
import UserAvatar from "@/components/user/UserAvatar";
import { DropdownToggle, DropdownMenu, Dropdown } from "reactstrap";
import { Icon } from "@/components/Component";
import { LinkList, LinkItem } from "@/components/links/Links";
import { useTheme, useThemeUpdate } from "@/layout/provider/Theme";
import { useAuth } from "@/api/AuthProvider";
import { userService } from "@/api/userService";

const User = () => {
  const theme = useTheme();
  const themeUpdate = useThemeUpdate();
  const { auth, logout, isAuthenticated } = useAuth();
  const [open, setOpen] = useState(false);
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);

  const toggle = () => setOpen((prevState) => !prevState);

  useEffect(() => {
    const fetchUserData = async () => {
      if (isAuthenticated && auth?.user) {
        try {
          // Try to get fresh user data from API
          const currentUser = await userService.getCurrentUser();
          setUserData(currentUser);
        } catch (error) {
          console.error('Error fetching user data:', error);
          // Fallback to stored user data
          setUserData(auth.user);
        }
      }
      setLoading(false);
    };

    fetchUserData();
  }, [isAuthenticated, auth]);

  const handleLogout = () => {
    logout();
    toggle();
  };

  // Show loading state or fallback if not authenticated
  if (loading) {
    return (
      <div className="user-dropdown">
        <div className="user-toggle">
          <UserAvatar icon="user-alt" className="sm" />
          <div className="user-info d-none d-md-block">
            <div className="user-status">Loading...</div>
            <div className="user-name dropdown-indicator">...</div>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !userData) {
    return (
      <div className="user-dropdown">
        <a href="/login" className="user-toggle">
          <UserAvatar icon="user-alt" className="sm" />
          <div className="user-info d-none d-md-block">
            <div className="user-status">Guest</div>
            <div className="user-name dropdown-indicator">Sign In</div>
          </div>
        </a>
      </div>
    );
  }

  // Generate initials from full name
  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <Dropdown isOpen={open} className="user-dropdown" toggle={toggle}>
      <DropdownToggle
        tag="a"
        href="#toggle"
        className="dropdown-toggle"
        onClick={(ev) => {
          ev.preventDefault();
        }}
      >
        <div className="user-toggle">
          <UserAvatar icon="user-alt" className="sm" />
          <div className="user-info d-none d-md-block">
            <div className="user-status">
              {userData.is_verified ? 'Verified User' : 'User'}
            </div>
            <div className="user-name dropdown-indicator">{userData.full_name}</div>
          </div>
        </div>
      </DropdownToggle>
      <DropdownMenu end className="dropdown-menu-md dropdown-menu-s1">
        <div className="dropdown-inner user-card-wrap bg-lighter d-none d-md-block">
          <div className="user-card sm">
            <div className="user-avatar">
              <span>{getInitials(userData.full_name)}</span>
            </div>
            <div className="user-info">
              <span className="lead-text">{userData.full_name}</span>
              <span className="sub-text">{userData.email}</span>
            </div>
          </div>
        </div>
        <div className="dropdown-inner">
          <LinkList>
            <LinkItem link="/user-profile-regular" icon="user-alt" onClick={toggle}>
              View Profile
            </LinkItem>
            <LinkItem link="/user-profile-setting" icon="setting-alt" onClick={toggle}>
              Account Setting
            </LinkItem>
            <LinkItem link="/user-profile-activity" icon="activity-alt" onClick={toggle}>
              Login Activity
            </LinkItem>
            <li>
              <a className={`dark-switch ${theme.skin === 'dark' ? 'active' : ''}`} href="#" 
              onClick={(ev) => {
                ev.preventDefault();
                themeUpdate.skin(theme.skin === 'dark' ? 'light' : 'dark');
              }}>
                {theme.skin === 'dark' ? 
                  <><em className="icon ni ni-sun"></em><span>Light Mode</span></> 
                  : 
                  <><em className="icon ni ni-moon"></em><span>Dark Mode</span></>
                }
              </a>
            </li>
          </LinkList>
        </div>
        <div className="dropdown-inner">
          <LinkList>
            <a href="#" onClick={handleLogout}>
              <Icon name="signout"></Icon>
              <span>Sign Out</span>
            </a>
          </LinkList>
        </div>
      </DropdownMenu>
    </Dropdown>
  );
};

export default User;
