import React, { useState, useCallback } from 'react'
import { useNavigate, Link } from 'react-router-dom'

// Libraries
import { Col, Container, Navbar, Row } from 'react-bootstrap'
import { m } from "framer-motion"

// Components
import { Header, HeaderCart, HeaderLanguage, HeaderNav, Menu, SearchBar } from '../../Components/Header/Header'
import Logo from '../../Components/Logo'
import UserProfileDropdown from '../../Components/Header/UserProfileDropdown'
import FooterStyle05 from '../../Components/Footers/FooterStyle05'

import MediaUploader from '../../Components/Media/MediaUploader'
import MediaGallery from '../../Components/Media/MediaGallery'
import Buttons from '../../Components/Button/Buttons'

// API & Auth
import { useMediaManagement } from '../../api/useMedia'
import useAuth from '../../api/useAuth'
import { formatFileSize } from '../../api/mediaService'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

const MediaLibrary = (props) => {
    const [showUploader, setShowUploader] = useState(false)
    const [viewMode, setViewMode] = useState('grid') // 'grid' or 'list'
    const [sortBy, setSortBy] = useState('newest') // 'newest', 'oldest', 'name', 'size'
    const [filterType, setFilterType] = useState('all') // 'all', 'images', 'videos', 'documents'
    const [gridSize, setGridSize] = useState(4)
    
    const navigate = useNavigate()
    const { isAuthenticated, user } = useAuth()
    
    const {
        media,
        selectedMedia,
        loading,
        uploading,
        uploadProgress,
        error,
        upload,
        deleteSelected,
        refetch,
        selectMedia,
        selectAll,
        clearSelection
    } = useMediaManagement()

    const handleUploadSuccess = useCallback((uploadedFiles) => {
        setShowUploader(false)
    }, [])

    const handleUploadError = useCallback((errors) => {
        console.error('Upload errors:', errors)
    }, [])

    const filteredAndSortedMedia = React.useMemo(() => {
        let filtered = media

        if (filterType !== 'all') {
            filtered = media.filter(item => {
                switch (filterType) {
                    case 'images':
                        return item.mime_type.startsWith('image/')
                    case 'videos':
                        return item.mime_type.startsWith('video/')
                    case 'documents':
                        return item.mime_type.includes('pdf') || item.mime_type.includes('document')
                    default:
                        return true
                }
            })
        }

        const sorted = [...filtered].sort((a, b) => {
            switch (sortBy) {
                case 'oldest':
                    return new Date(a.created_at) - new Date(b.created_at)
                case 'name':
                    return a.file_name.localeCompare(b.file_name)
                case 'size':
                    return b.file_size - a.file_size
                case 'newest':
                default:
                    return new Date(b.created_at) - new Date(a.created_at)
            }
        })

        return sorted
    }, [media, filterType, sortBy])

    // Calculate stats
    const stats = React.useMemo(() => {
        const totalSize = media.reduce((sum, item) => sum + item.file_size, 0)
        const imageCount = media.filter(item => item.mime_type.startsWith('image/')).length
        const videoCount = media.filter(item => item.mime_type.startsWith('video/')).length
        const documentCount = media.filter(item => !item.mime_type.startsWith('image/') && !item.mime_type.startsWith('video/')).length
        
        return {
            total: media.length,
            totalSize,
            images: imageCount,
            videos: videoCount,
            documents: documentCount
        }
    }, [media])

    // Handle bulk delete
    const handleBulkDelete = useCallback(async () => {
        if (selectedMedia.length === 0) return
        
        const confirmed = window.confirm(
            `Are you sure you want to delete ${selectedMedia.length} selected files? This action cannot be undone.`
        )
        
        if (confirmed) {
            await deleteSelected()
        }
    }, [selectedMedia, deleteSelected])

    if (!isAuthenticated) {
        return (
            <div style={props.style}>
                <Header topSpace={{ md: true }} type="reverse-scroll">
                    <HeaderNav fluid="fluid" theme="light" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" menuPosition="left">
                        <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                            <Logo className="flex items-center" asNavbarBrand={false} />
                        </Col>
                        <div className="col-auto hidden order-last md:block">
                            <Navbar.Toggle className="md:ml-[10px] sm:ml-0">
                                <span className="navbar-toggler-line"></span>
                                <span className="navbar-toggler-line"></span>
                                <span className="navbar-toggler-line"></span>
                                <span className="navbar-toggler-line"></span>
                            </Navbar.Toggle>
                        </div>
                        <Navbar.Collapse className="col-auto px-0 justify-end">
                            <Menu {...props} />
                        </Navbar.Collapse>
                    </HeaderNav>
                </Header>

                <section className="py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                    <Container>
                        <Row className="justify-center">
                            <Col lg={8}>
                                <div className="text-center">
                                    <i className="fas fa-lock text-6xl text-gray-300 mb-4"></i>
                                    <h2 className="text-darkgray font-medium mb-4">Access Restricted</h2>
                                    <p className="text-gray-600 mb-6">You need to be logged in to access your media library.</p>
                                    <Buttons
                                        onClick={() => navigate('/auth/login')}
                                        className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none"
                                        color="#0038e3"
                                        size="md"
                                        themeColor="#0038e3"
                                        title="Sign In"
                                    />
                                </div>
                            </Col>
                        </Row>
                    </Container>
                </section>

                <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />
    
            </div>
        )
    }

    return (
        <div style={props.style}>
            <Header topSpace={{ md: true }} type="reverse-scroll">
                <HeaderNav fluid="fluid" theme="light" bg="white" menu="light" className="px-[35px] py-[0px] md:px-0" menuPosition="left">
                    <Col className="col-auto col-sm-6 col-lg-2 me-auto ps-lg-0">
                        <Link aria-label="header logo" className="flex items-center" to="/">
                            <img className="default-logo" width="111" height="36" loading="lazy" src='/assets/img/litho-logo-regular-dark.png' data-rjs='/assets/img/litho-logo-regular-dark@2x.png' alt='logo' />
                            <img className="alt-logo" width="111" height="36" loading="lazy" src='/assets/img/litho-logo-regular-dark.png' data-rjs='/assets/img/litho-logo-regular-dark@2x.png' alt='logo' />
                            <img className="mobile-logo" width="111" height="36" loading="lazy" src='/assets/img/litho-logo-regular-dark.png' data-rjs='/assets/img/litho-logo-regular-dark@2x.png' alt='logo' />
                        </Link>
                    </Col>
                    <div className="col-auto hidden order-last md:block">
                        <Navbar.Toggle className="md:ml-[10px] sm:ml-0">
                            <span className="navbar-toggler-line"></span>
                            <span className="navbar-toggler-line"></span>
                            <span className="navbar-toggler-line"></span>
                            <span className="navbar-toggler-line"></span>
                        </Navbar.Toggle>
                    </div>
                    <Navbar.Collapse className="col-auto px-0 justify-end">
                        <Menu {...props} />
                        <UserProfileDropdown className="ms-4" />
                    </Navbar.Collapse>
                </HeaderNav>
            </Header>

            <section className="py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px]">
                <Container>
                    <Row>
                        <Col>
                            {/* Page Header */}
                            <div className="text-center mb-16">
                                <h1 className="text-darkgray font-medium mb-4">Media Library</h1>
                                <p className="text-gray-600 mb-8">
                                    Manage your uploaded files and media assets
                                </p>
                                
                                {/* Stats */}
                                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 max-w-2xl mx-auto mb-6 sm:mb-8 px-4">
                                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                                        <div className="text-lg sm:text-2xl font-bold text-blue-600">{stats.total}</div>
                                        <div className="text-xs sm:text-sm text-gray-600">Total Files</div>
                                    </div>
                                    <div className="text-center p-3 bg-green-50 rounded-lg">
                                        <div className="text-lg sm:text-2xl font-bold text-green-600">{stats.images}</div>
                                        <div className="text-xs sm:text-sm text-gray-600">Images</div>
                                    </div>
                                    <div className="text-center p-3 bg-purple-50 rounded-lg">
                                        <div className="text-lg sm:text-2xl font-bold text-purple-600">{stats.videos}</div>
                                        <div className="text-xs sm:text-sm text-gray-600">Videos</div>
                                    </div>
                                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                                        <div className="text-lg sm:text-2xl font-bold text-orange-600">{formatFileSize(stats.totalSize)}</div>
                                        <div className="text-xs sm:text-sm text-gray-600">Total Size</div>
                                    </div>
                                </div>
                            </div>

                            {/* Toolbar */}
                            <div className="flex flex-col lg:flex-row items-center justify-between mb-6 lg:mb-8 p-3 sm:p-4 bg-gray-50 rounded-lg gap-4 lg:gap-0">
                                <div className="flex justify-center lg:justify-start xxs:flex-col xxs:items-center w-full lg:w-auto">
                                    {/* Upload Button */}
                                    <Buttons
                                        onClick={() => setShowUploader(!showUploader)}
                                        className="btn-fill btn-fancy font-medium font-serif uppercase rounded-none mb-[15px] xxs:mx-0"
                                        color="#0038e3"
                                        size="sm"
                                        themeColor="#0038e3"
                                        title={showUploader ? "Hide Uploader" : "Upload Files"}
                                        icon={showUploader ? "fas fa-times" : "fas fa-cloud-upload-alt"}
                                        iconPosition="before"
                                    />
                                    
                                    {/* Bulk Actions */}
                                    {selectedMedia.length > 0 && (
                                        <>
                                            <span className="text-xs sm:text-sm text-gray-600 mr-3 mb-[15px] xxs:mx-0">
                                                {selectedMedia.length} selected
                                            </span>
                                            <Buttons
                                                onClick={handleBulkDelete}
                                                className="btn-outline btn-fancy font-medium font-serif uppercase rounded-none mb-[15px]"
                                                color="#ef4444"
                                                size="sm"
                                                title="Delete Selected"
                                                icon="fas fa-trash"
                                                iconPosition="before"
                                            />
                                        </>
                                    )}
                                </div>
                                
                                <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3 sm:gap-4 w-full lg:w-auto">
                                    {/* Filter */}
                                    <select
                                        value={filterType}
                                        onChange={(e) => setFilterType(e.target.value)}
                                        className="px-3 py-2 border border-gray-300 rounded text-xs sm:text-sm w-full sm:w-auto"
                                    >
                                        <option value="all">All Files</option>
                                        <option value="images">Images</option>
                                        <option value="videos">Videos</option>
                                        <option value="documents">Documents</option>
                                    </select>
                                    
                                    {/* Sort */}
                                    <select
                                        value={sortBy}
                                        onChange={(e) => setSortBy(e.target.value)}
                                        className="px-3 py-2 border border-gray-300 rounded text-xs sm:text-sm w-full sm:w-auto"
                                    >
                                        <option value="newest">Newest First</option>
                                        <option value="oldest">Oldest First</option>
                                        <option value="name">Name A-Z</option>
                                        <option value="size">Size (Largest)</option>
                                    </select>
                                    
                                    {/* Grid Size */}
                                    <div className="flex items-center justify-center gap-2 sm:gap-3">
                                        <span className="text-xs sm:text-sm text-gray-600 hidden sm:inline">View:</span>
                                        <button
                                            onClick={() => setGridSize(3)}
                                            className={`p-2 rounded text-xs sm:text-sm ${gridSize === 3 ? 'text-blue-600 bg-blue-50' : 'text-gray-400 hover:text-gray-600'}`}
                                        >
                                            <i className="fas fa-th-large"></i>
                                        </button>
                                        <button
                                            onClick={() => setGridSize(4)}
                                            className={`p-2 rounded text-xs sm:text-sm ${gridSize === 4 ? 'text-blue-600 bg-blue-50' : 'text-gray-400 hover:text-gray-600'}`}
                                        >
                                            <i className="fas fa-th"></i>
                                        </button>
                                        <button
                                            onClick={() => setGridSize(6)}
                                            className={`p-2 rounded text-xs sm:text-sm ${gridSize === 6 ? 'text-blue-600 bg-blue-50' : 'text-gray-400 hover:text-gray-600'}`}
                                        >
                                            <i className="fas fa-border-all"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Upload Area */}
                            {showUploader && (
                                <m.div 
                                    className="mb-8"
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                >
                                    <MediaUploader
                                        onUploadSuccess={handleUploadSuccess}
                                        onUploadError={handleUploadError}
                                        multiple={true}
                                        maxFileSize={10 * 1024 * 1024} // 10MB
                                    />
                                </m.div>
                            )}

                            {/* Error Display */}
                            {error && (
                                <m.div 
                                    className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                >
                                    <p className="text-red-600">
                                        <i className="fas fa-exclamation-triangle mr-2"></i>
                                        {error}
                                    </p>
                                </m.div>
                            )}

                            {/* Media Gallery */}
                            <MediaGallery
                                media={filteredAndSortedMedia}
                                loading={loading}
                                error={null} // Error is shown separately above
                                onMediaSelect={(selection) => {
                                    // Selection is handled by useMediaManagement
                                }}
                                onMediaUpdate={(updatedMedia) => {
                                    refetch() // Refresh media list
                                }}
                                onMediaDelete={(mediaUuid) => {
                                    refetch() // Refresh media list
                                }}
                                selectable={true}
                                showActions={true}
                                size="medium"
                                columns={gridSize}
                            />
                        </Col>
                    </Row>
                </Container>
            </section>

            <FooterStyle05 theme="dark" className="text-slateblue bg-[#262b35]" />

        </div>
    )
}

export default MediaLibrary