import React, { memo } from 'react'
import { Link } from 'react-router-dom'
import { Navbar } from 'react-bootstrap'
import PropTypes from 'prop-types'

/**
 * Reusable Logo Component for CraftyXhub
 * 
 * @param {Object} props - Component props
 * @param {string} props.to - Link destination (default: "/")
 * @param {string} props.variant - Logo variant: "default", "white", "large", "small" (default: "default")
 * @param {string} props.className - Additional CSS classes
 * @param {string} props.ariaLabel - Accessibility label (default: "CraftyXhub logo")
 * @param {boolean} props.asNavbarBrand - Whether to wrap in Navbar.Brand (default: true)
 */
const Logo = ({
  to = "/",
  variant = "default",
  className = "",
  ariaLabel = "CraftyXhub logo",
  asNavbarBrand = true,
  ...props
}) => {
  // Define styles based on variant
  const getLogoStyles = () => {
    const baseStyles = "font-bold tracking-wide transition-colors duration-300"
    
    switch (variant) {
      case "white":
        return `${baseStyles} text-2xl text-white hover:text-gray-200`
      case "black":
        return `${baseStyles} text-3xl text-black hover:text-gray-800`
      case "large":
        return `${baseStyles} text-3xl text-fastblue hover:text-blue-600`
      case "small":
        return `${baseStyles} text-lg text-fastblue hover:text-blue-600`
      case "default":
      default:
        return `${baseStyles} text-2xl text-fastblue hover:text-blue-600`
    }
  }

  const logoElement = (
    <span className={`${getLogoStyles()} ${className}`}>
      CraftyXhub
    </span>
  )

  const linkElement = (
    <Link 
      aria-label={ariaLabel} 
      className="inline-block relative z-10" 
      to={to}
      {...props}
    >
      {logoElement}
    </Link>
  )

  // Wrap in Navbar.Brand if requested (for header usage)
  if (asNavbarBrand) {
    return (
      <Navbar.Brand className="inline-block p-0 m-0 align-middle">
        {linkElement}
      </Navbar.Brand>
    )
  }

  return linkElement
}

Logo.propTypes = {
  to: PropTypes.string,
  variant: PropTypes.oneOf(['default', 'white', 'black', 'large', 'small']),
  className: PropTypes.string,
  ariaLabel: PropTypes.string,
  asNavbarBrand: PropTypes.bool,
}

export default memo(Logo)