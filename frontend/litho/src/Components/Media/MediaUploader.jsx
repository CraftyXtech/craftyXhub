import React, { useState, useCallback, useRef, memo } from 'react'
import PropTypes from 'prop-types'

// Libraries
import { m } from "framer-motion"

// Components
import Buttons from '../Button/Buttons'

// API
import { useUploadMedia } from '../../api/useMedia'
import { validateFile, formatFileSize } from '../../api/mediaService'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

const MediaUploader = ({ 
    onUploadSuccess, 
    onUploadError,
    multiple = true,
    acceptedTypes = 'image/*,video/*,.pdf',
    maxFileSize = 10 * 1024 * 1024, // 10MB
    className,
    disabled = false,
    showPreview = true,
    ...props 
}) => {
    const [dragActive, setDragActive] = useState(false)
    const [selectedFiles, setSelectedFiles] = useState([])
    const [previews, setPreviews] = useState([])
    const fileInputRef = useRef(null)
    
    const { upload, uploadMultiple, uploading, uploadProgress, error, setError } = useUploadMedia()

    // Handle drag events
    const handleDrag = useCallback((e) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true)
        } else if (e.type === "dragleave") {
            setDragActive(false)
        }
    }, [])

    // Handle drop
    const handleDrop = useCallback((e) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)
        
        if (disabled) return

        const files = Array.from(e.dataTransfer.files)
        handleFiles(files)
    }, [disabled])

    // Handle file input change
    const handleFileInput = useCallback((e) => {
        const files = Array.from(e.target.files)
        handleFiles(files)
    }, [])

    // Process selected files
    const handleFiles = useCallback((files) => {
        if (files.length === 0) return

        // Limit to single file if multiple is false
        const filesToProcess = multiple ? files : [files[0]]
        
        // Validate files
        const validFiles = []
        const errors = []

        filesToProcess.forEach(file => {
            const validation = validateFile(file, maxFileSize)
            if (validation.isValid) {
                validFiles.push(file)
            } else {
                errors.push(`${file.name}: ${validation.errors.join(', ')}`)
            }
        })

        if (errors.length > 0) {
            setError(errors.join('; '))
            if (onUploadError) {
                onUploadError(errors)
            }
            return
        }

        setSelectedFiles(validFiles)
        
        // Generate previews for images
        if (showPreview) {
            generatePreviews(validFiles)
        }

        setError(null)
    }, [multiple, maxFileSize, showPreview, setError, onUploadError])

    // Generate file previews
    const generatePreviews = useCallback((files) => {
        const previewPromises = files.map(file => {
            return new Promise((resolve) => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader()
                    reader.onload = (e) => resolve({
                        file,
                        url: e.target.result,
                        type: 'image'
                    })
                    reader.readAsDataURL(file)
                } else {
                    resolve({
                        file,
                        url: null,
                        type: 'file'
                    })
                }
            })
        })

        Promise.all(previewPromises).then(setPreviews)
    }, [])

    // Upload files
    const handleUpload = useCallback(async (descriptions = []) => {
        if (selectedFiles.length === 0) return

        try {
            let results
            if (selectedFiles.length === 1) {
                const result = await upload(selectedFiles[0], descriptions[0])
                results = result ? [{ success: true, data: result }] : [{ success: false }]
            } else {
                results = await uploadMultiple(selectedFiles, descriptions)
            }

            const successful = results.filter(r => r.success)
            const failed = results.filter(r => !r.success)

            if (successful.length > 0 && onUploadSuccess) {
                onUploadSuccess(successful.map(r => r.data))
            }

            if (failed.length > 0 && onUploadError) {
                onUploadError(failed.map(r => r.error))
            }

            // Clear files after successful upload
            if (successful.length === results.length) {
                clearFiles()
            }

        } catch (err) {
            if (onUploadError) {
                onUploadError([err.message])
            }
        }
    }, [selectedFiles, upload, uploadMultiple, onUploadSuccess, onUploadError])

    // Clear selected files
    const clearFiles = useCallback(() => {
        setSelectedFiles([])
        setPreviews([])
        if (fileInputRef.current) {
            fileInputRef.current.value = ''
        }
    }, [])

    // Remove specific file
    const removeFile = useCallback((index) => {
        setSelectedFiles(prev => prev.filter((_, i) => i !== index))
        setPreviews(prev => prev.filter((_, i) => i !== index))
    }, [])

    const dropZoneClass = `
        media-uploader 
        border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ease-in-out
        ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:bg-gray-50'}
        ${className || ''}
    `

    return (
        <m.div 
            className={`media-uploader-container ${props.containerClassName || ''}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            {...fadeIn}
        >
            {/* Drop Zone */}
            <div
                className={dropZoneClass}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => !disabled && fileInputRef.current?.click()}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    multiple={multiple}
                    accept={acceptedTypes}
                    onChange={handleFileInput}
                    className="hidden"
                    disabled={disabled}
                />
                
                <div className="media-uploader-content">
                    <i className={`${dragActive ? 'fas fa-cloud-upload-alt text-blue-500' : 'fas fa-cloud-upload-alt text-gray-400'} text-4xl mb-4`}></i>
                    
                    <h3 className="text-lg font-medium text-gray-700 mb-2">
                        {dragActive ? 'Drop files here' : 'Upload Media'}
                    </h3>
                    
                    <p className="text-sm text-gray-500 mb-4">
                        {multiple ? 'Drag & drop files here, or click to select' : 'Drag & drop a file here, or click to select'}
                    </p>
                    
                    <div className="text-xs text-gray-400">
                        <p>Max file size: {formatFileSize(maxFileSize)}</p>
                        <p>Supported formats: Images, Videos, PDF</p>
                    </div>
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <m.div 
                    className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                >
                    <p className="text-sm text-red-600">
                        <i className="fas fa-exclamation-triangle mr-2"></i>
                        {error}
                    </p>
                </m.div>
            )}

            {/* File Previews */}
            {selectedFiles.length > 0 && (
                <m.div 
                    className="mt-6"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <h4 className="text-md font-medium text-gray-700 mb-4">
                        Selected Files ({selectedFiles.length})
                    </h4>
                    
                    <div className="space-y-3">
                        {previews.map((preview, index) => (
                            <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                                {/* Preview */}
                                <div className="flex-shrink-0 w-16 h-16 bg-gray-200 rounded-lg overflow-hidden">
                                    {preview.type === 'image' ? (
                                        <img 
                                            src={preview.url} 
                                            alt={preview.file.name}
                                            className="w-full h-full object-cover"
                                        />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                                            <i className={`fas fa-file text-xl`}></i>
                                        </div>
                                    )}
                                </div>
                                
                                {/* File Info */}
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-gray-700 truncate">
                                        {preview.file.name}
                                    </p>
                                    <p className="text-xs text-gray-500">
                                        {formatFileSize(preview.file.size)} • {preview.file.type}
                                    </p>
                                </div>
                                
                                {/* Remove Button */}
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        removeFile(index)
                                    }}
                                    className="flex-shrink-0 text-gray-400 hover:text-red-500 transition-colors duration-200"
                                    disabled={uploading}
                                >
                                    <i className="fas fa-times"></i>
                                </button>
                            </div>
                        ))}
                    </div>
                    
                    {/* Upload Progress */}
                    {uploading && (
                        <div className="mt-4">
                            <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                                <span>Uploading...</span>
                                <span>{uploadProgress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${uploadProgress}%` }}
                                ></div>
                            </div>
                        </div>
                    )}
                    
                    {/* Action Buttons */}
                    <div className="flex space-x-3 mt-4">
                        <Buttons
                            onClick={handleUpload}
                            disabled={uploading || disabled}
                            className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none"
                            color="#0038e3"
                            size="sm"
                            themeColor="#0038e3"
                            title={uploading ? "Uploading..." : "Upload Files"}
                            icon={uploading ? "fas fa-spinner fa-spin" : "fas fa-upload"}
                            iconPosition="before"
                        />
                        
                        <Buttons
                            onClick={clearFiles}
                            disabled={uploading}
                            className="btn-outline btn-fancy font-medium font-serif uppercase rounded-none"
                            color="#6b7280"
                            size="sm"
                            title="Clear"
                            icon="fas fa-times"
                            iconPosition="before"
                        />
                    </div>
                </m.div>
            )}
        </m.div>
    )
}

MediaUploader.propTypes = {
    onUploadSuccess: PropTypes.func,
    onUploadError: PropTypes.func,
    multiple: PropTypes.bool,
    acceptedTypes: PropTypes.string,
    maxFileSize: PropTypes.number,
    className: PropTypes.string,
    containerClassName: PropTypes.string,
    disabled: PropTypes.bool,
    showPreview: PropTypes.bool
}

export default memo(MediaUploader)