import React from "react";
import {Link} from "react-router-dom";

const Logo = () => {
  return (
    <Link to={`/`} className="logo-link">
      <div className="logo-text">
        <span className="brand-name">CraftyXhub</span>
      </div>
    </Link>
  );
};

export default Logo;
