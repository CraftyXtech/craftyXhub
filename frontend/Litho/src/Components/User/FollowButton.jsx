import React, { useState, useEffect, memo } from 'react'
import PropTypes from 'prop-types'

// Libraries
import { m } from "framer-motion"

// Components
import Buttons from '../Button/Buttons'

// API & Auth
import { useFollowUser, useIsFollowing } from '../../api/useUser'
import useAuth from '../../api/useAuth'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

const FollowButton = ({ 
    userUuid, 
    className, 
    size = "md",
    variant = "outline",
    onFollowChange,
    showFollowingCount = false,
    disabled = false,
    ...props 
}) => {
    const [isHovered, setIsHovered] = useState(false)
    const { isAuthenticated, user } = useAuth()
    const { follow, unfollow, loading: followLoading } = useFollowUser()
    const { isFollowing, loading: checkLoading, refetch } = useIsFollowing(userUuid)

    // Don't show follow button for own profile
    const isOwnProfile = user?.uuid === userUuid

    const handleFollow = async () => {
        if (!isAuthenticated) {
            // Could trigger a login modal here
            alert('Please log in to follow users')
            return
        }

        const success = isFollowing ? await unfollow(userUuid) : await follow(userUuid)
        
        if (success) {
            refetch() // Refresh following status
            onFollowChange?.(userUuid, !isFollowing)
        }
    }

    const getButtonText = () => {
        if (followLoading) return 'Loading...'
        
        if (isFollowing) {
            return isHovered ? 'Unfollow' : 'Following'
        }
        
        return 'Follow'
    }

    const getButtonIcon = () => {
        if (followLoading) return 'fas fa-spinner fa-spin'
        
        if (isFollowing) {
            return isHovered ? 'icon-user-unfollow' : 'icon-user-following'
        }
        
        return 'icon-user-follow'
    }

    const getButtonStyle = () => {
        if (isFollowing) {
            return isHovered ? 'btn-fill btn-fancy border-red text-red hover:bg-red hover:text-white' 
                             : 'btn-fill btn-fancy border-green text-green'
        }
        
        return variant === 'outline' ? 'btn-outline btn-fancy border-black text-black hover:bg-black hover:text-white'
                                     : 'btn-fill btn-fancy bg-black text-white hover:bg-darkgray'
    }

    if (isOwnProfile || checkLoading) {
        return null
    }

    return (
        <m.div 
            className={`follow-button-wrapper ${className || ''}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            {...fadeIn}
            {...props}
        >
            <Buttons
                onClick={handleFollow}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                disabled={disabled || followLoading || checkLoading}
                className={`follow-button ${getButtonStyle()} transition-all duration-300 ease-in-out`}
                size={size}
                title={getButtonText()}
                icon={getButtonIcon()}
                iconPosition="before"
                ariaLabel={isFollowing ? `Unfollow user` : `Follow user`}
            />
        </m.div>
    )
}

FollowButton.propTypes = {
    userUuid: PropTypes.string.isRequired,
    className: PropTypes.string,
    size: PropTypes.oneOf(['xs', 'sm', 'md', 'lg', 'xl']),
    variant: PropTypes.oneOf(['outline', 'filled']),
    onFollowChange: PropTypes.func,
    showFollowingCount: PropTypes.bool,
    disabled: PropTypes.bool
}

export default memo(FollowButton)