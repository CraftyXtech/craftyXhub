import React, { useEffect, useLayoutEffect, Fragment } from "react";
import Icon from "@/components/icon/Icon";
import classNames from "classnames";
import { NavLink, Link, useLocation } from "react-router-dom";
import { slideUp, slideDown, getParents } from "@/utils/Utils";
import { useThemeUpdate } from '@/layout/provider/Theme';

const Menu = ({data}) => {

  const themeUpdate = useThemeUpdate();
  const location = useLocation();

  // Helper function to check if a menu link should be active
  const isLinkActive = (link) => {
    const currentPath = location.pathname;
    
    // Exact match
    if (currentPath === link) return true;
    
    // Special case: /posts-edit/:id should highlight "Create Post" (/posts-create)
    if (link === '/posts-create' && currentPath.startsWith('/posts-edit/')) {
      return true;
    }
    
    return false;
  };

  let currentLink = function(){
      // First, remove all active states
      let allMenuItems = document.querySelectorAll('.nk-menu-item');
      allMenuItems.forEach(item => {
        item.classList.remove('active', 'current-page');
      });
      
      // Find all active links
      let activeLinks = document.querySelectorAll('.nk-menu-link.active');
      activeLinks.forEach(function(item){
          // Add active class to parent menu items and open dropdowns
          let parents = getParents(item, `.nk-menu`, 'nk-menu-item');
          parents.forEach(parentElement => {
              parentElement.classList.add('active', 'current-page');
              let subItem = parentElement.querySelector(`.nk-menu-wrap`);
              if (subItem !== null) {
                subItem.style.display = "block";
              }
          });
          
          // Add active to immediate parent
          if (item.parentElement) {
            item.parentElement.classList.add('active', 'current-page');
          }
      });
  } 
  // dropdown toggle
  let dropdownToggle = function(elm){
      let parent = elm.parentElement;
      let nextelm = elm.nextElementSibling;
      let speed = nextelm.children.length > 5 ? 400 + nextelm.children.length * 10 : 400;
      if(!parent.classList.contains('active')){
          parent.classList.add('active');
          slideDown(nextelm,speed);
      }else{
          parent.classList.remove('active');
          slideUp(nextelm,speed);
      }
  }

  // dropdown close siblings
  let closeSiblings = function(elm){
      let parent = elm.parentElement;
      let siblings = parent.parentElement.children;
      Array.from(siblings).forEach(item => {
      if(item !== parent){
          item.classList.remove('active');
          if(item.classList.contains('has-sub')){
          let subitem = item.querySelectorAll(`.nk-menu-wrap`);
          subitem.forEach(child => {
              child.parentElement.classList.remove('active');
              slideUp(child,400);
          })
          }
      }
      });
  }

  let menuToggle = function(e){
      e.preventDefault();
      let item = e.target.closest(`.nk-menu-toggle`)
      dropdownToggle(item);
      closeSiblings(item);
  }

  let routeChange = function(e){
      let selector = document.querySelectorAll(".nk-menu-link")
      selector.forEach((item, index)=>{
          if(item.classList.contains('active')){
              closeSiblings(item);
              item.parentElement.classList.add("active");
          }else{
              item.parentElement.classList.remove("active");
              currentLink(`.nk-menu-link`);
          }
      })
  }
  
  useLayoutEffect(() =>{
      routeChange();
      themeUpdate.sidebarHide();
  },[location.pathname])

  useEffect(() =>{
      // Apply active states after render
      currentLink();
      // eslint-disable-next-line
  },[location.pathname])


  return (
    <ul className="nk-menu">
      {data.map((item, index) =>
        <Fragment key={index}>
            {item.heading ? (
              <li className="nk-menu-heading">
                <h6 className="overline-title text-primary-alt">{item.heading}</h6>
              </li>
            ) : (
              <li className={classNames({'nk-menu-item': true, 'has-sub' : item.subMenu})}>
                {!item.subMenu ? (
                  <Link 
                    to={item.link} 
                    className={classNames('nk-menu-link', { 'active': isLinkActive(item.link) })} 
                    target={item.newTab && '_blank'}
                  >
                    {item.icon  && <span className="nk-menu-icon">
                      <Icon name={item.icon} />
                    </span>}
                    <span className="nk-menu-text">{item.text}</span>
                    {item.badge && <span className="nk-menu-badge">{item.badge}</span>}
                  </Link>
                  ) : (
                  <>
                    <a href="#" className="nk-menu-link nk-menu-toggle" onClick={menuToggle}>
                      {item.icon  && <span className="nk-menu-icon">
                        <Icon name={item.icon} />
                      </span>}
                      <span className="nk-menu-text">{item.text}</span>
                      {item.badge && <span className="nk-menu-badge">{item.badge}</span>}
                    </a>
                    <div className="nk-menu-wrap">
                      <ul className="nk-menu-sub">
                        {item.subMenu.map((sItem, sIndex) =>
                          <li className={classNames({'nk-menu-item': true, 'has-sub' : sItem.subMenu})} key={sIndex}>
                              {!sItem.subMenu ? (
                                <Link 
                                  to={sItem.link} 
                                  className={classNames('nk-menu-link', { 'active': isLinkActive(sItem.link) })} 
                                  target={sItem.newTab && '_blank'}
                                >
                                  <span className="nk-menu-text">{sItem.text}</span>
                                  {sItem.badge && <span className="nk-menu-badge">{sItem.badge}</span>}
                                </Link>
                                ) : (
                                <>
                                  <a href="#" className="nk-menu-link nk-menu-toggle" onClick={menuToggle}>
                                    <span className="nk-menu-text">{sItem.text}</span>
                                    {sItem.badge && <span className="nk-menu-badge">{sItem.badge}</span>}
                                  </a>
                                  <div className="nk-menu-wrap">
                                    <ul className="nk-menu-sub">
                                      {sItem.subMenu.map((s2Item, s2Index) =>
                                        <li className={classNames({'nk-menu-item': true, 'has-sub' : s2Item.subMenu})} key={s2Index}>
                                            {!s2Item.subMenu ? (
                                              <Link 
                                                to={s2Item.link} 
                                                className={classNames('nk-menu-link', { 'active': isLinkActive(s2Item.link) })} 
                                                target={s2Item.newTab && '_blank'}
                                              >
                                                <span className="nk-menu-text">{s2Item.text}</span>
                                                {s2Item.badge && <span className="nk-menu-badge">{s2Item.badge}</span>}
                                              </Link>
                                              ) : (
                                              <>
                                                <a href="#" className="nk-menu-link nk-menu-toggle" onClick={menuToggle}>
                                                  <span className="nk-menu-text">{s2Item.text}</span>
                                                  {s2Item.badge && <span className="nk-menu-badge">{s2Item.badge}</span>}
                                                </a>
                                                <div className="nk-menu-wrap">
                                                  <ul className="nk-menu-sub">
                                                    {s2Item.subMenu.map((s3Item, s3Index) =>
                                                      <li className="nk-menu-item" key={s3Index}>
                                                          <Link 
                                                            to={s3Item.link} 
                                                            className={classNames('nk-menu-link', { 'active': isLinkActive(s3Item.link) })} 
                                                            target={s3Item.newTab && '_blank'}
                                                          >
                                                            <span className="nk-menu-text">{s3Item.text}</span>
                                                            {s3Item.badge && <span className="nk-menu-badge">{s3Item.badge}</span>}
                                                          </Link>
                                                      </li>
                                                    )}
                                                  </ul>
                                                </div>
                                              </>
                                            )}
                                        </li>
                                      )}
                                    </ul>
                                  </div>
                                </>
                              )}
                          </li>
                        )}
                      </ul>
                    </div>
                  </>
                )}
              </li>
            )}
        </Fragment>
      )}
    </ul>
  );
};

export default Menu;
