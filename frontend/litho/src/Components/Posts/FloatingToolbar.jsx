import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'
import AutoSaveIndicator from './AutoSaveIndicator'
import Buttons from '../Button/Buttons'

const FloatingToolbar = ({
    onBack,
    onSaveDraft,
    onPublish,
    saveStatus,
    lastSaved,
    isSaving,
    isPublishing,
    onOpenSettings,
    readingTime,
    wordCount,
    showBackButton = false
}) => {
    return (
        <div className="floating-toolbar sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
            <div className="max-w-[1400px] mx-auto px-6 py-3">
                <div className="flex items-center justify-between">
                    {/* Left Section */}
                    <div className="flex items-center gap-4">
                        {/* Auto-save indicator */}
                        <div className="hidden md:block">
                            <AutoSaveIndicator 
                                status={saveStatus} 
                                lastSaved={lastSaved}
                            />
                        </div>
                    </div>

                    {/* Center Section - Stats */}
                    <div className="hidden lg:flex items-center gap-4 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                            <i className="feather-file-text text-base"></i>
                            {wordCount} words
                        </span>
                        <span className="flex items-center gap-1">
                            <i className="feather-clock text-base"></i>
                            {readingTime} min read
                        </span>
                    </div>

                    {/* Right Section - Actions */}
                    <div className="flex items-center gap-2">
                        {/* Publish Button - Small & Simple */}
                        <button
                            type="button"
                            onClick={onPublish}
                            disabled={isSaving || isPublishing}
                            className="px-3 py-1.5 text-sm font-medium text-white bg-fastblue border border-fastblue rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            {isPublishing ? 'Publishing...' : 'Publish'}
                        </button>

                        {/* Settings Button */}
                        <button
                            type="button"
                            onClick={onOpenSettings}
                            className="p-2 text-gray-600 hover:text-fastblue hover:bg-gray-100 rounded-md transition-all"
                            title="Post Settings"
                        >
                            <i className="feather-settings text-lg"></i>
                        </button>
                    </div>
                </div>

                {/* Mobile stats and auto-save indicator */}
                <div className="md:hidden mt-2 flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center gap-3">
                        <span>{wordCount} words</span>
                        <span>{readingTime} min</span>
                    </div>
                    <AutoSaveIndicator 
                        status={saveStatus} 
                        lastSaved={lastSaved}
                    />
                </div>
            </div>
        </div>
    )
}

FloatingToolbar.propTypes = {
    onBack: PropTypes.func,
    onSaveDraft: PropTypes.func, // Not required anymore - auto-save handles it
    onPublish: PropTypes.func.isRequired,
    saveStatus: PropTypes.oneOf(['idle', 'saving', 'saved', 'error']).isRequired,
    lastSaved: PropTypes.number,
    isSaving: PropTypes.bool,
    isPublishing: PropTypes.bool,
    onOpenSettings: PropTypes.func.isRequired,
    readingTime: PropTypes.number,
    wordCount: PropTypes.number,
    showBackButton: PropTypes.bool
}

export default FloatingToolbar
