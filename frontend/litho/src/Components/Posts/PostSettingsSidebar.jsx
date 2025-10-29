import React, { useState, useRef } from 'react'
import PropTypes from 'prop-types'
import { m, AnimatePresence } from 'framer-motion'

const PostSettingsSidebar = ({
    isOpen,
    onClose,
    featuredImage,
    featuredImagePreview,
    onImageChange,
    onImageRemove,
    excerpt,
    autoExcerpt,
    useAutoExcerpt,
    onExcerptModeChange,
    onExcerptChange,
    categories,
    categoryId,
    onCategoryChange,
    tags,
    selectedTags,
    onTagToggle,
    metaTitle,
    metaDescription,
    readingTime,
    onMetaChange,
    categoriesLoading,
    tagsLoading
}) => {
    const [seoExpanded, setSeoExpanded] = useState(false)
    const fileInputRef = useRef(null)

    const handleImageSelect = (event) => {
        const file = event.target.files[0]
        if (file) {
            onImageChange(file)
        }
    }

    return (
        <>
            {/* Overlay */}
            <AnimatePresence>
                {isOpen && (
                    <m.div
                        className="settings-sidebar-overlay fixed inset-0 bg-black bg-opacity-50 z-40"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                    />
                )}
            </AnimatePresence>

            {/* Sidebar */}
            <AnimatePresence>
                {isOpen && (
                    <m.div
                        className="settings-sidebar fixed top-0 right-0 w-full sm:w-96 h-full bg-white shadow-2xl z-50 overflow-y-auto"
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                    >
                        {/* Header */}
                        <div className="sidebar-header sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between z-10">
                            <h3 className="text-lg font-semibold text-darkgray">Post Settings</h3>
                            <button
                                onClick={onClose}
                                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                            >
                                <i className="feather-x text-xl text-gray-600"></i>
                            </button>
                        </div>

                        {/* Content */}
                        <div className="sidebar-content px-6 py-6 space-y-8">
                            {/* Featured Image Section */}
                            <div className="setting-section">
                                <h4 className="text-sm font-semibold text-darkgray mb-3 flex items-center gap-2">
                                    <i className="feather-image"></i>
                                    Featured Image
                                </h4>
                                
                                {featuredImagePreview ? (
                                    <div className="relative group">
                                        <img
                                            src={featuredImagePreview}
                                            alt="Featured preview"
                                            className="w-full h-48 object-cover rounded-lg"
                                        />
                                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all rounded-lg flex items-center justify-center">
                                            <button
                                                type="button"
                                                onClick={onImageRemove}
                                                className="opacity-0 group-hover:opacity-100 px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-all"
                                            >
                                                Remove
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <button
                                        type="button"
                                        onClick={() => fileInputRef.current?.click()}
                                        className="w-full border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-fastblue transition-colors"
                                    >
                                        <i className="feather-upload text-3xl text-gray-400 mb-2"></i>
                                        <p className="text-sm text-gray-600">Click to upload</p>
                                        <p className="text-xs text-gray-400 mt-1">Max 10MB</p>
                                    </button>
                                )}
                                
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    onChange={handleImageSelect}
                                    className="hidden"
                                />
                            </div>

                            {/* Excerpt Section */}
                            <div className="setting-section">
                                <h4 className="text-sm font-semibold text-darkgray mb-3 flex items-center gap-2">
                                    <i className="feather-file-text"></i>
                                    Excerpt
                                </h4>
                                
                                {/* Excerpt Mode Toggle */}
                                <div className="flex gap-2 mb-3">
                                    <button
                                        type="button"
                                        onClick={() => onExcerptModeChange(true)}
                                        className={`flex-1 px-3 py-2 text-sm rounded-md transition-all ${
                                            useAutoExcerpt
                                                ? 'bg-fastblue text-white'
                                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                        }`}
                                    >
                                        Auto
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => onExcerptModeChange(false)}
                                        className={`flex-1 px-3 py-2 text-sm rounded-md transition-all ${
                                            !useAutoExcerpt
                                                ? 'bg-fastblue text-white'
                                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                        }`}
                                    >
                                        Manual
                                    </button>
                                </div>

                                {useAutoExcerpt ? (
                                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-gray-700">
                                        <p className="text-xs text-gray-500 mb-2">Auto-generated:</p>
                                        <p>{autoExcerpt || 'Start writing to generate excerpt...'}</p>
                                    </div>
                                ) : (
                                    <textarea
                                        value={excerpt}
                                        onChange={(e) => onExcerptChange(e.target.value)}
                                        placeholder="Write a brief description..."
                                        rows={4}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:border-fastblue focus:outline-none resize-none"
                                        maxLength={500}
                                    />
                                )}
                            </div>

                            {/* Category Section */}
                            <div className="setting-section">
                                <h4 className="text-sm font-semibold text-darkgray mb-3 flex items-center gap-2">
                                    <i className="feather-folder"></i>
                                    Category
                                </h4>
                                
                                <select
                                    value={categoryId || ''}
                                    onChange={(e) => onCategoryChange(e.target.value)}
                                    disabled={categoriesLoading}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:border-fastblue focus:outline-none"
                                >
                                    <option value="">No category</option>
                                    {categories.map((category) => (
                                        <option key={category.id} value={category.id}>
                                            {category.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Tags Section */}
                            <div className="setting-section">
                                <h4 className="text-sm font-semibold text-darkgray mb-3 flex items-center gap-2">
                                    <i className="feather-tag"></i>
                                    Tags
                                </h4>
                                
                                {tagsLoading ? (
                                    <p className="text-sm text-gray-500">Loading tags...</p>
                                ) : tags.length > 0 ? (
                                    <div className="flex flex-wrap gap-2">
                                        {tags.map(tag => (
                                            <button
                                                key={tag.id}
                                                type="button"
                                                onClick={() => onTagToggle(tag.id)}
                                                className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                                                    selectedTags.includes(tag.id)
                                                        ? 'bg-fastblue text-white'
                                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                                }`}
                                            >
                                                {tag.name}
                                            </button>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-sm text-gray-500">No tags available</p>
                                )}
                            </div>

                            {/* SEO Settings Section */}
                            <div className="setting-section">
                                <button
                                    type="button"
                                    onClick={() => setSeoExpanded(!seoExpanded)}
                                    className="w-full flex items-center justify-between text-sm font-semibold text-darkgray mb-3 hover:text-fastblue transition-colors"
                                >
                                    <span className="flex items-center gap-2">
                                        <i className="feather-search"></i>
                                        SEO Settings
                                    </span>
                                    <i className={`feather-chevron-${seoExpanded ? 'up' : 'down'}`}></i>
                                </button>

                                <AnimatePresence>
                                    {seoExpanded && (
                                        <m.div
                                            initial={{ height: 0, opacity: 0 }}
                                            animate={{ height: 'auto', opacity: 1 }}
                                            exit={{ height: 0, opacity: 0 }}
                                            transition={{ duration: 0.2 }}
                                            className="space-y-4 overflow-hidden"
                                        >
                                            {/* Meta Title */}
                                            <div>
                                                <label className="block text-xs font-medium text-gray-700 mb-2">
                                                    Meta Title
                                                </label>
                                                <input
                                                    type="text"
                                                    value={metaTitle}
                                                    onChange={(e) => onMetaChange({ metaTitle: e.target.value })}
                                                    placeholder="SEO title..."
                                                    maxLength={200}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:border-fastblue focus:outline-none"
                                                />
                                            </div>

                                            {/* Reading Time */}
                                            <div>
                                                <label className="block text-xs font-medium text-gray-700 mb-2">
                                                    Reading Time (auto: {readingTime} min)
                                                </label>
                                                <input
                                                    type="number"
                                                    value={readingTime}
                                                    onChange={(e) => onMetaChange({ readingTime: e.target.value })}
                                                    placeholder="e.g., 5"
                                                    min="1"
                                                    max="120"
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:border-fastblue focus:outline-none"
                                                />
                                            </div>

                                            {/* Meta Description */}
                                            <div>
                                                <label className="block text-xs font-medium text-gray-700 mb-2">
                                                    Meta Description
                                                </label>
                                                <textarea
                                                    value={metaDescription}
                                                    onChange={(e) => onMetaChange({ metaDescription: e.target.value })}
                                                    placeholder="Brief description for search engines..."
                                                    rows={3}
                                                    maxLength={300}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:border-fastblue focus:outline-none resize-none"
                                                />
                                            </div>
                                        </m.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </div>

                        {/* Footer with shortcuts hint */}
                        <div className="sidebar-footer border-t border-gray-200 px-6 py-4 bg-gray-50">
                            <div className="text-xs text-gray-500 space-y-1">
                                <p className="font-medium text-gray-600 mb-2">Keyboard Shortcuts</p>
                                <p><kbd className="px-2 py-1 bg-white border border-gray-300 rounded text-xs">Cmd</kbd> + <kbd className="px-2 py-1 bg-white border border-gray-300 rounded text-xs">,</kbd> Open Settings</p>
                                <p><kbd className="px-2 py-1 bg-white border border-gray-300 rounded text-xs">Esc</kbd> Close Settings</p>
                                <p className="text-gray-400 mt-2">✨ Auto-saves every 30 seconds</p>
                            </div>
                        </div>
                    </m.div>
                )}
            </AnimatePresence>
        </>
    )
}

PostSettingsSidebar.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    featuredImage: PropTypes.object,
    featuredImagePreview: PropTypes.string,
    onImageChange: PropTypes.func.isRequired,
    onImageRemove: PropTypes.func.isRequired,
    excerpt: PropTypes.string,
    autoExcerpt: PropTypes.string,
    useAutoExcerpt: PropTypes.bool,
    onExcerptModeChange: PropTypes.func.isRequired,
    onExcerptChange: PropTypes.func.isRequired,
    categories: PropTypes.array,
    categoryId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    onCategoryChange: PropTypes.func.isRequired,
    tags: PropTypes.array,
    selectedTags: PropTypes.array,
    onTagToggle: PropTypes.func.isRequired,
    metaTitle: PropTypes.string,
    metaDescription: PropTypes.string,
    readingTime: PropTypes.number,
    onMetaChange: PropTypes.func.isRequired,
    categoriesLoading: PropTypes.bool,
    tagsLoading: PropTypes.bool
}

export default PostSettingsSidebar
