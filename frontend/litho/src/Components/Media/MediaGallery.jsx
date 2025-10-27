import React, { useState, useCallback, memo } from 'react'
import PropTypes from 'prop-types'

// Libraries
import { m } from "framer-motion"

// Components
import Buttons from '../Button/Buttons'

// API
import { 
    getImageUrl, 
    formatFileSize, 
    isImageFile, 
    isVideoFile, 
    getFileIcon 
} from '../../api/mediaService'
import { useUpdateMedia, useDeleteMedia } from '../../api/useMedia'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

const MediaCard = ({ 
    media, 
    isSelected, 
    onSelect, 
    onEdit, 
    onDelete, 
    onClick,
    selectable = true,
    showActions = true,
    size = 'medium'
}) => {
    const [isEditing, setIsEditing] = useState(false)
    const [description, setDescription] = useState(media.description || '')
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
    
    const { update, loading: updateLoading } = useUpdateMedia()
    const { deleteFile, loading: deleteLoading } = useDeleteMedia()

    const sizeClasses = {
        small: 'w-24 h-24',
        medium: 'w-32 h-32',
        large: 'w-48 h-48'
    }

    const handleEdit = useCallback(async () => {
        if (isEditing) {
            // Save changes
            const result = await update(media.uuid, description)
            if (result && onEdit) {
                onEdit(result)
            }
            setIsEditing(false)
        } else {
            setIsEditing(true)
        }
    }, [isEditing, description, media.uuid, update, onEdit])

    const handleDelete = useCallback(async () => {
        const success = await deleteFile(media.uuid)
        if (success && onDelete) {
            onDelete(media.uuid)
        }
        setShowDeleteConfirm(false)
    }, [media.uuid, deleteFile, onDelete])

    const handleCardClick = useCallback(() => {
        if (onClick) {
            onClick(media)
        }
    }, [media, onClick])

    return (
        <m.div 
            className={`media-card bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-md ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
            {...fadeIn}
            onClick={handleCardClick}
        >
            {/* Selection Checkbox */}
            {selectable && (
                <div className="absolute top-2 left-2 z-10">
                    <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => {
                            e.stopPropagation()
                            onSelect?.(media.uuid)
                        }}
                        className="w-4 h-4 text-blue-600 bg-white border-gray-300 rounded focus:ring-blue-500"
                    />
                </div>
            )}

            {/* Media Preview */}
            <div className={`relative ${sizeClasses[size]} bg-gray-100 flex items-center justify-center overflow-hidden`}>
                {isImageFile(media.mime_type) ? (
                    <img 
                        src={getImageUrl(media.file_path)} 
                        alt={media.file_name}
                        className="w-full h-full object-cover"
                        loading="lazy"
                    />
                ) : isVideoFile(media.mime_type) ? (
                    <>
                        <video 
                            src={getImageUrl(media.file_path)}
                            className="w-full h-full object-cover"
                            muted
                        />
                        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30">
                            <i className="fas fa-play-circle text-white text-2xl"></i>
                        </div>
                    </>
                ) : (
                    <div className="text-center">
                        <i className={`${getFileIcon(media.mime_type)} text-3xl text-gray-400 mb-2`}></i>
                        <p className="text-xs text-gray-500 px-2 truncate">{media.file_name}</p>
                    </div>
                )}
                
                {/* File Type Badge */}
                <div className="absolute top-2 right-2 bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded">
                    {media.file_name.split('.').pop()?.toUpperCase()}
                </div>
            </div>

            {/* Media Info */}
            <div className="p-3">
                {/* File Name */}
                <h4 className="text-sm font-medium text-gray-700 truncate mb-1">
                    {media.file_name}
                </h4>
                
                {/* Description */}
                {isEditing ? (
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        className="w-full text-xs text-gray-600 border border-gray-300 rounded px-2 py-1 resize-none"
                        rows={2}
                        placeholder="Add description..."
                        disabled={updateLoading}
                    />
                ) : (
                    <p className="text-xs text-gray-600 mb-2 line-clamp-2">
                        {media.description || 'No description'}
                    </p>
                )}
                
                {/* File Details */}
                <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                    <span>{formatFileSize(media.file_size)}</span>
                    <span>{media.mime_type}</span>
                </div>

                {/* Actions */}
                {showActions && (
                    <div className="flex items-center justify-between">
                        <div className="flex space-x-1">
                            {/* Edit Button */}
                            <button
                                onClick={(e) => {
                                    e.stopPropagation()
                                    handleEdit()
                                }}
                                disabled={updateLoading || deleteLoading}
                                className="p-1 text-gray-400 hover:text-blue-500 transition-colors duration-200"
                                title={isEditing ? "Save" : "Edit"}
                            >
                                <i className={`fas ${isEditing ? 'fa-save' : 'fa-edit'} text-xs`}></i>
                            </button>
                            
                            {/* Copy URL Button */}
                            <button
                                onClick={(e) => {
                                    e.stopPropagation()
                                    navigator.clipboard.writeText(getImageUrl(media.file_path))
                                }}
                                className="p-1 text-gray-400 hover:text-green-500 transition-colors duration-200"
                                title="Copy URL"
                            >
                                <i className="fas fa-copy text-xs"></i>
                            </button>
                            
                            {/* Delete Button */}
                            <button
                                onClick={(e) => {
                                    e.stopPropagation()
                                    setShowDeleteConfirm(true)
                                }}
                                disabled={updateLoading || deleteLoading}
                                className="p-1 text-gray-400 hover:text-red-500 transition-colors duration-200"
                                title="Delete"
                            >
                                <i className="fas fa-trash text-xs"></i>
                            </button>
                        </div>
                        
                        {/* Loading Indicator */}
                        {(updateLoading || deleteLoading) && (
                            <i className="fas fa-spinner fa-spin text-xs text-gray-400"></i>
                        )}
                    </div>
                )}
            </div>

            {/* Delete Confirmation Modal */}
            {showDeleteConfirm && (
                <div 
                    className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                    onClick={(e) => {
                        e.stopPropagation()
                        setShowDeleteConfirm(false)
                    }}
                >
                    <div 
                        className="bg-white rounded-lg p-6 max-w-sm mx-4"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Delete Media</h3>
                        <p className="text-sm text-gray-600 mb-6">
                            Are you sure you want to delete "{media.file_name}"? This action cannot be undone.
                        </p>
                        <div className="flex space-x-3">
                            <Buttons
                                onClick={handleDelete}
                                disabled={deleteLoading}
                                className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none"
                                color="#ef4444"
                                size="sm"
                                themeColor="#ef4444"
                                title={deleteLoading ? "Deleting..." : "Delete"}
                                icon={deleteLoading ? "fas fa-spinner fa-spin" : "fas fa-trash"}
                                iconPosition="before"
                            />
                            <Buttons
                                onClick={() => setShowDeleteConfirm(false)}
                                className="btn-outline btn-fancy font-medium font-serif uppercase rounded-none"
                                color="#6b7280"
                                size="sm"
                                title="Cancel"
                            />
                        </div>
                    </div>
                </div>
            )}
        </m.div>
    )
}

const MediaGallery = ({ 
    media = [], 
    loading = false,
    error = null,
    onMediaSelect,
    onMediaUpdate,
    onMediaDelete,
    onLoadMore,
    hasMore = false,
    selectable = true,
    showActions = true,
    size = 'medium',
    columns = 4,
    className,
    ...props 
}) => {
    const [selectedMedia, setSelectedMedia] = useState([])

    const handleSelect = useCallback((mediaUuid) => {
        const newSelection = selectedMedia.includes(mediaUuid)
            ? selectedMedia.filter(id => id !== mediaUuid)
            : [...selectedMedia, mediaUuid]
        
        setSelectedMedia(newSelection)
        onMediaSelect?.(newSelection)
    }, [selectedMedia, onMediaSelect])

    const handleSelectAll = useCallback(() => {
        const allUuids = media.map(item => item.uuid)
        setSelectedMedia(allUuids)
        onMediaSelect?.(allUuids)
    }, [media, onMediaSelect])

    const handleClearSelection = useCallback(() => {
        setSelectedMedia([])
        onMediaSelect?.([])
    }, [onMediaSelect])

    const gridCols = {
        1: 'grid-cols-1',
        2: 'grid-cols-2',
        3: 'grid-cols-3',
        4: 'grid-cols-4 md:grid-cols-3 sm:grid-cols-2',
        5: 'grid-cols-5 lg:grid-cols-4 md:grid-cols-3 sm:grid-cols-2',
        6: 'grid-cols-6 lg:grid-cols-4 md:grid-cols-3 sm:grid-cols-2'
    }

    if (loading && media.length === 0) {
        return (
            <div className="text-center py-12">
                <i className="fas fa-spinner fa-spin text-4xl text-gray-400 mb-4"></i>
                <p className="text-gray-600">Loading media...</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <i className="fas fa-exclamation-triangle text-4xl text-gray-300 mb-4"></i>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Media</h3>
                <p className="text-gray-600">{error}</p>
            </div>
        )
    }

    if (media.length === 0) {
        return (
            <div className="text-center py-12">
                <i className="fas fa-images text-6xl text-gray-300 mb-4"></i>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Media Files</h3>
                <p className="text-gray-600">Upload some files to get started.</p>
            </div>
        )
    }

    return (
        <div className={`media-gallery ${className || ''}`} {...props}>
            {/* Gallery Header */}
            {selectable && media.length > 0 && (
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-4">
                        <p className="text-sm text-gray-600">
                            {selectedMedia.length} of {media.length} selected
                        </p>
                        {selectedMedia.length > 0 && (
                            <button
                                onClick={handleClearSelection}
                                className="text-sm text-blue-600 hover:text-blue-800"
                            >
                                Clear selection
                            </button>
                        )}
                    </div>
                    
                    <button
                        onClick={selectedMedia.length === media.length ? handleClearSelection : handleSelectAll}
                        className="text-sm text-blue-600 hover:text-blue-800"
                    >
                        {selectedMedia.length === media.length ? 'Deselect all' : 'Select all'}
                    </button>
                </div>
            )}

            {/* Media Grid */}
            <div className={`grid ${gridCols[columns]} gap-4`}>
                {media.map((item) => (
                    <MediaCard
                        key={item.uuid}
                        media={item}
                        isSelected={selectedMedia.includes(item.uuid)}
                        onSelect={handleSelect}
                        onEdit={onMediaUpdate}
                        onDelete={onMediaDelete}
                        selectable={selectable}
                        showActions={showActions}
                        size={size}
                    />
                ))}
            </div>

            {/* Load More */}
            {hasMore && (
                <div className="text-center mt-8">
                    <Buttons
                        onClick={onLoadMore}
                        disabled={loading}
                        className="btn-outline btn-fancy font-medium font-serif uppercase rounded-none"
                        color="#0038e3"
                        size="md"
                        title={loading ? "Loading..." : "Load More"}
                        icon={loading ? "fas fa-spinner fa-spin" : "fas fa-chevron-down"}
                        iconPosition="after"
                    />
                </div>
            )}

            {/* Loading More Indicator */}
            {loading && media.length > 0 && (
                <div className="text-center mt-4">
                    <i className="fas fa-spinner fa-spin text-xl text-gray-400"></i>
                    <p className="text-sm text-gray-600 mt-2">Loading more media...</p>
                </div>
            )}
        </div>
    )
}

MediaGallery.propTypes = {
    media: PropTypes.array,
    loading: PropTypes.bool,
    error: PropTypes.string,
    onMediaSelect: PropTypes.func,
    onMediaUpdate: PropTypes.func,
    onMediaDelete: PropTypes.func,
    onLoadMore: PropTypes.func,
    hasMore: PropTypes.bool,
    selectable: PropTypes.bool,
    showActions: PropTypes.bool,
    size: PropTypes.oneOf(['small', 'medium', 'large']),
    columns: PropTypes.oneOf([1, 2, 3, 4, 5, 6]),
    className: PropTypes.string
}

export default memo(MediaGallery)