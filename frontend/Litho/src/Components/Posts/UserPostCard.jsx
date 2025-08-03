import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'

// Libraries
import { Link } from 'react-router-dom'
import { m } from "framer-motion"

// Components
import Buttons from '../Button/Buttons'

// API
import { useDeletePost, usePublishDraft } from '../../api/usePosts'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

// Utils
import { getImageUrl } from '../../api/postsService'

const UserPostCard = ({ post, onDelete, onPublish, className, ...props }) => {
    // Determine if this is a draft or published post
    const isDraft = !post.is_published
    const [isDeleting, setIsDeleting] = useState(false)
    const [isPublishing, setIsPublishing] = useState(false)
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

    const { deletePost } = useDeletePost()
    const { publishDraft } = usePublishDraft()

    // Format date
    const formatDate = (dateString) => {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    // Handle delete
    const handleDelete = async () => {
        if (!showDeleteConfirm) {
            setShowDeleteConfirm(true)
            return
        }

        try {
            setIsDeleting(true)
            await deletePost(post.uuid)
            onDelete && onDelete(post.uuid)
        } catch (error) {
            console.error('Error deleting draft:', error)
            alert('Failed to delete draft. Please try again.')
        } finally {
            setIsDeleting(false)
            setShowDeleteConfirm(false)
        }
    }

    // Handle publish
    const handlePublish = async () => {
        try {
            setIsPublishing(true)
            const result = await publishDraft(post.uuid)
            onPublish && onPublish(post.uuid, result)
        } catch (error) {
            console.error('Error publishing draft:', error)
            alert('Failed to publish draft. Please try again.')
        } finally {
            setIsPublishing(false)
        }
    }

    // Cancel delete confirmation
    const cancelDelete = () => {
        setShowDeleteConfirm(false)
    }

    const featuredImageUrl = post.featured_image 
        ? getImageUrl(post.featured_image, 'posts')
        : null

    return (
        <m.div 
            className={`draft-post-card bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-300${className ? ` ${className}` : ''}`}
            {...fadeIn}
            {...props}
        >
            {/* Featured Image */}
            {featuredImageUrl && (
                <div className="relative h-48 bg-gray-100">
                    <img
                        src={featuredImageUrl}
                        alt={post.title || 'Draft post'}
                        className="w-full h-full object-cover"
                        loading="lazy"
                    />
                    <div className="absolute top-3 left-3">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            isDraft 
                                ? 'bg-yellow-100 text-yellow-800' 
                                : 'bg-green-100 text-green-800'
                        }`}>
                            {isDraft ? 'Draft' : 'Published'}
                        </span>
                    </div>
                </div>
            )}

            <div className="p-6">
                {/* Status Badge for non-image posts */}
                {!featuredImageUrl && (
                    <div className="mb-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            isDraft 
                                ? 'bg-yellow-100 text-yellow-800' 
                                : 'bg-green-100 text-green-800'
                        }`}>
                            {isDraft ? 'Draft' : 'Published'}
                        </span>
                    </div>
                )}

                {/* Title */}
                <h3 className="text-xl font-serif font-medium text-darkgray mb-3 line-clamp-2">
                    {post.title || (isDraft ? 'Untitled Draft' : 'Untitled Post')}
                </h3>

                {/* Excerpt */}
                {post.excerpt && (
                    <p className="text-spanishgray text-sm mb-4 line-clamp-3">
                        {post.excerpt}
                    </p>
                )}

                {/* Content Preview (if no excerpt) */}
                {!post.excerpt && post.content && (
                    <p className="text-spanishgray text-sm mb-4 line-clamp-3">
                        {post.content.replace(/<[^>]*>/g, '').substring(0, 150)}...
                    </p>
                )}

                {/* Metadata */}
                <div className="flex items-center justify-between text-xs text-spanishgray mb-6">
                    <div className="flex items-center space-x-4">
                        <span className="flex items-center">
                            <i className="feather-clock mr-1"></i>
                            {formatDate(post.updated_at)}
                        </span>
                        {post.reading_time && (
                            <span className="flex items-center">
                                <i className="feather-book-open mr-1"></i>
                                {post.reading_time} min read
                            </span>
                        )}
                    </div>
                    {post.category && (
                        <span className="text-fastblue">
                            {post.category.name}
                        </span>
                    )}
                </div>

                {/* Delete Confirmation */}
                {showDeleteConfirm && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                        <div className="flex items-center mb-3">
                            <i className="feather-alert-triangle text-red-500 mr-2"></i>
                            <h4 className="text-sm font-medium text-red-800">
                                Delete {isDraft ? 'Draft' : 'Post'}?
                            </h4>
                        </div>
                        <p className="text-sm text-red-700 mb-4">
                            This action cannot be undone. The {isDraft ? 'draft' : 'post'} will be permanently deleted.
                        </p>
                        <div className="flex space-x-3">
                            <button
                                onClick={handleDelete}
                                disabled={isDeleting}
                                className="px-3 py-1.5 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 transition-colors disabled:opacity-50"
                            >
                                {isDeleting ? 'Deleting...' : 'Delete'}
                            </button>
                            <button
                                onClick={cancelDelete}
                                className="px-3 py-1.5 bg-gray-200 text-gray-800 text-sm rounded-md hover:bg-gray-300 transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}

                {/* Action Buttons */}
                {!showDeleteConfirm && (
                    <div className="flex flex-col sm:flex-row gap-3">
                        {/* Edit Button */}
                        <Link
                            to={`/posts/edit/${post.uuid}`}
                            className="flex-1"
                        >
                            <Buttons
                                ariaLabel="edit post"
                                className="font-medium font-serif uppercase text-xs w-full"
                                themeColor={["#6c757d", "#495057"]}
                                size="sm"
                                color="#fff"
                                title={`Edit ${isDraft ? 'Draft' : 'Post'}`}
                            />
                        </Link>

                        {/* Publish Button - Only show for drafts */}
                        {isDraft && onPublish && (
                            <Buttons
                                ariaLabel="publish draft"
                                className={`font-medium font-serif uppercase text-xs flex-1 ${isPublishing ? 'loading' : ''}`}
                                themeColor={["#28a745", "#20c997"]}
                                size="sm"
                                color="#fff"
                                title={isPublishing ? "Publishing..." : "Publish"}
                                onClick={handlePublish}
                                disabled={isPublishing}
                            />
                        )}

                        {/* View Button - Only show for published posts */}
                        {!isDraft && (
                            <Link
                                to={`/posts/${post.slug}`}
                                className="flex-1"
                            >
                                <Buttons
                                    ariaLabel="view post"
                                    className="font-medium font-serif uppercase text-xs w-full"
                                    themeColor={["#0038e3", "#ff7a56"]}
                                    size="sm"
                                    color="#fff"
                                    title="View Post"
                                />
                            </Link>
                        )}

                        {/* Delete Button */}
                        <button
                            onClick={handleDelete}
                            className="px-4 py-2 text-xs font-medium text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors flex items-center justify-center"
                            title={`Delete ${isDraft ? 'Draft' : 'Post'}`}
                        >
                            <i className="feather-trash-2 text-sm"></i>
                        </button>
                    </div>
                )}
            </div>
        </m.div>
    )
}

UserPostCard.defaultProps = {
    className: ""
}

UserPostCard.propTypes = {
    post: PropTypes.shape({
        uuid: PropTypes.string.isRequired,
        title: PropTypes.string,
        content: PropTypes.string,
        excerpt: PropTypes.string,
        featured_image: PropTypes.string,
        updated_at: PropTypes.string.isRequired,
        reading_time: PropTypes.number,
        category: PropTypes.shape({
            name: PropTypes.string
        })
    }).isRequired,
    onDelete: PropTypes.func,
    onPublish: PropTypes.func,
    className: PropTypes.string
}

export default memo(UserPostCard)