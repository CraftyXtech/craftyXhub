import React, { useState, useRef, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Dropdown } from 'react-bootstrap'
import PropTypes from 'prop-types'
import useAuth from '../../api/useAuth'


const UserProfileDropdown = ({ 
  className = "", 
  iconColor = "#232323",
  dropdownPosition = "end"
}) => {
  const [showDropdown, setShowDropdown] = useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const dropdownRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/')
    setShowDropdown(false)
  }

  const toggleDropdown = () => {
    setShowDropdown(!showDropdown)
  }

  const handleItemClick = () => {
    setShowDropdown(false)
  }

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!user?.full_name) return 'U'
    const names = user.full_name.split(' ')
    return names.length > 1 
      ? `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase()
      : names[0][0].toUpperCase()
  }

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        onClick={toggleDropdown}
        className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
        aria-label="User profile menu"
        aria-expanded={showDropdown}
      >
        <div 
          className="w-8 h-8 rounded-full bg-fastblue text-white flex items-center justify-center text-sm font-semibold"
          style={{ backgroundColor: iconColor }}
        >
          {getUserInitials()}
        </div>
        
        <span className="hidden md:block text-sm font-medium text-darkgray max-w-[120px] truncate">
          {user?.username || 'User'}
        </span>
        
        <i className={`fas fa-chevron-down text-xs text-gray-500 transition-transform duration-200 ${
          showDropdown ? 'rotate-180' : ''
        }`}></i>
      </button>

      {showDropdown && (
        <div className={`absolute top-full mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50 ${
          dropdownPosition === 'end' ? 'right-0' : 'left-0'
        }`}>
          <div className="px-4 py-3 border-b border-gray-100">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-fastblue text-white flex items-center justify-center font-semibold">
                {getUserInitials()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-darkgray truncate">
                  {user?.full_name || 'User Name'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  @{user?.username || 'username'}
                </p>
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <div className="py-1">
            <Link
              to="/dashboard"
              onClick={handleItemClick}
              className="flex items-center px-4 py-2 text-sm text-darkgray hover:bg-gray-50 transition-colors"
            >
              <i className="feather-home w-4 mr-3 text-gray-400"></i>
              Dashboard
            </Link>

            <Link
              to="/profile"
              onClick={handleItemClick}
              className="flex items-center px-4 py-2 text-sm text-darkgray hover:bg-gray-50 transition-colors"
            >
              <i className="fas fa-user w-4 mr-3 text-gray-400"></i>
              My Profile
            </Link>

            <Link
              to="/user/posts"
              onClick={handleItemClick}
              className="flex items-center px-4 py-2 text-sm text-darkgray hover:bg-gray-50 transition-colors"
            >
              <i className="fas fa-edit w-4 mr-3 text-gray-400"></i>
              My Posts
            </Link>

            <Link
              to="/user/bookmarks"
              onClick={handleItemClick}
              className="flex items-center px-4 py-2 text-sm text-darkgray hover:bg-gray-50 transition-colors"
            >
              <i className="fas fa-bookmark w-4 mr-3 text-gray-400"></i>
              Reading List
            </Link>



            <Link
              to="/user/media-library"
              onClick={handleItemClick}
              className="flex items-center px-4 py-2 text-sm text-darkgray hover:bg-gray-50 transition-colors"
            >
              <i className="fas fa-images w-4 mr-3 text-gray-400"></i>
              Media Library
            </Link>

            <div className="border-t border-gray-100 my-1"></div>

            <button
              onClick={handleLogout}
              className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <i className="fas fa-sign-out-alt w-4 mr-3"></i>
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

UserProfileDropdown.propTypes = {
  className: PropTypes.string,
  iconColor: PropTypes.string,
  dropdownPosition: PropTypes.oneOf(['start', 'end'])
}

export default UserProfileDropdown