import React, { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "reactstrap";
import { useForm } from "react-hook-form";
import { Editor } from "@tinymce/tinymce-react";
import Dropzone from 'react-dropzone';
import { useTheme } from '@/layout/provider/Theme';
import Head from "@/layout/head/Head";
import Content from "@/layout/content/Content";
import {
  Block,
  BlockHead,
  BlockTitle,
  BlockBetween,
  BlockHeadContent,
  BlockDes,
  Icon,
  RSelect,
  BackTo,
  Row,
  Col,
  PreviewCard,
} from "@/components/Component";
import { useCreatePost, useUpdatePost, useGetPost, useGetCategories, useGetTags, useCreateCategory, useCreateTag, useImageUrl } from "@/api/postService";
import { toast } from "react-toastify";
import { debounce } from 'lodash';  
import 'tinymce/tinymce';
import 'tinymce/models/dom/model';
import 'tinymce/themes/silver';
import 'tinymce/icons/default';
import 'tinymce/skins/content/default/content';
import useAxiosPrivate from "@/api/useAxiosPrivate";

const PostForm = () => {
  const navigate = useNavigate();
  const { postId } = useParams(); 
  const isEditMode = Boolean(postId);
  const theme = useTheme();
  const editorRef = useRef(null);
  const { register, handleSubmit, setValue, formState: { errors } } = useForm();
  
    
  // Form state
  const [formData, setFormData] = useState({
    title: "",
    slug: "",
    content: "",
    excerpt: "",
    category_id: null,
    tag_ids: [],
    featured_image: "",
    reading_time: null,
    meta_title: "",
    meta_description: "",
  });

  // File upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState("");

  // API hooks
  const { createPost, loading: createLoading } = useCreatePost();
  const { updatePost, loading: updateLoading } = useUpdatePost();
  const { post: editPost, loading: postLoading } = useGetPost(postId);
  const { categories, refetch: refetchCategories } = useGetCategories();
  const { tags, refetch: refetchTags } = useGetTags();
  const { createCategory } = useCreateCategory();
  const { createTag } = useCreateTag();
  const { getImageUrl } = useImageUrl();

  // Separate loading states for autosave vs manual save
  const [autosaveLoading, setAutosaveLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Screen size state for responsive behavior
  const [screenSize, setScreenSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1200,
    isMobile: typeof window !== 'undefined' ? window.innerWidth < 576 : false,
    isTablet: typeof window !== 'undefined' ? window.innerWidth < 768 : false
  });
  
  // Separate axios instance for autosave to avoid interfering with manual save
  const axiosPrivate = useAxiosPrivate();
  
  // Handle window resize for responsive behavior
  useEffect(() => {
    const handleResize = () => {
      setScreenSize({
        width: window.innerWidth,
        isMobile: window.innerWidth < 576,
        isTablet: window.innerWidth < 768
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    }, [createLoading, updateLoading, postLoading]);
  const isLoading = createLoading || updateLoading;

  const debouncedUpdate = useCallback(
    debounce(async (data) => {
      try {
        setAutosaveLoading(true);
        const jsonData = {
          title: data.title,
          slug: data.slug,
          content: data.content,
          excerpt: data.excerpt,
          meta_title: data.meta_title,
          meta_description: data.meta_description,
          reading_time: data.reading_time,
          category_id: data.category_id,
          tag_ids: data.tag_ids
        };
        
        // Use separate axios call for autosave to avoid interfering with manual save
        await axiosPrivate.put(`/posts/${postId}`, jsonData);
        toast.info('Post autosaved');
      } catch (err) {
        toast.error('Autosave failed');
      } finally {
        setAutosaveLoading(false);
      }
    }, 5000),
    [axiosPrivate, postId]
  );

  useEffect(() => {
    if (isEditMode && !isSubmitting) {
      debouncedUpdate(formData);
    }
  }, [formData, isEditMode, debouncedUpdate, isSubmitting]);

  // Initialize form when editing
  useEffect(() => {
    if (isEditMode && editPost) {
      const postData = {
        title: editPost.title || "",
        slug: editPost.slug || "",
        content: editPost.content || "",
        excerpt: editPost.excerpt || "",
        category_id: editPost.category_id || null,
        tag_ids: editPost.tags?.map(tag => tag.id) || [],
        featured_image: editPost.featured_image || "",
        reading_time: editPost.reading_time || null,
        meta_title: editPost.meta_title || "",
        meta_description: editPost.meta_description || "",
      };
      setFormData(postData);
      
      
      if (editPost.featured_image) {
        const imageUrl = getImageUrl(editPost.featured_image, "posts");
        setPreview(imageUrl);
      } else {
        setPreview(""); 
      }
      
      Object.keys(postData).forEach(key => {
        setValue(key, postData[key]);
      });
    }
  }, [editPost, isEditMode, setValue, getImageUrl]);

  
  const generateSlug = (title) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9 -]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  };

  
  const handleTitleChange = (e) => {
    const title = e.target.value;
    setFormData(prev => ({ ...prev, title }));
    
    
    if (!isEditMode || !formData.slug) {
      const slug = generateSlug(title);
      setFormData(prev => ({ ...prev, slug }));
      setValue('slug', slug);
    }
  };

  
  const calculateReadingTime = (content) => {
    if (!content) return null;
    const wordsPerMinute = 200;
    const wordCount = content.replace(/<[^>]*>/g, '').split(/\s+/).length;
    return Math.ceil(wordCount / wordsPerMinute);
  };

  
  const handleContentChange = (content) => {
    setFormData(prev => ({ ...prev, content }));
    setValue('content', content);
    
    
    const readingTime = calculateReadingTime(content);
    setFormData(prev => ({ ...prev, reading_time: readingTime }));
    setValue('reading_time', readingTime);
  };

  
  const handleCreateCategory = async (inputValue) => {
    try {
      const newCategory = await createCategory({
        name: inputValue,
        slug: generateSlug(inputValue),
        description: ""
      });
      refetchCategories();
      toast.success("Category created successfully");
      return { value: newCategory.id, label: newCategory.name };
    } catch (error) {
      toast.error("Failed to create category");
      return null;
    }
  };

  
  const handleCreateTag = async (inputValue) => {
    try {
      const newTag = await createTag({
        name: inputValue,
        slug: generateSlug(inputValue)
      });
      refetchTags();
      toast.success("Tag created successfully");
      return { value: newTag.id, label: newTag.name };
    } catch (error) {
      toast.error("Failed to create tag");
      return null;
    }
  };

  
  const categoryOptions = categories.map(cat => ({
    value: String(cat.id),
    label: cat.name
  }));

  const tagOptions = tags.map(tag => ({
    value: tag.id,
    label: tag.name
  }));

  
  const onSubmit = async (data) => {
    try {
      setIsSubmitting(true);
      
      const content = editorRef.current?.getContent() || formData.content;
      
      const formDataToSend = new FormData();
      
      formDataToSend.append('title', formData.title);
      formDataToSend.append('slug', formData.slug);
      formDataToSend.append('content', content);
      if (formData.excerpt) formDataToSend.append('excerpt', formData.excerpt);
      if (formData.meta_title) formDataToSend.append('meta_title', formData.meta_title);
      if (formData.meta_description) formDataToSend.append('meta_description', formData.meta_description);
      if (formData.reading_time) formDataToSend.append('reading_time', formData.reading_time.toString());
      
      if (formData.category_id) {
        formDataToSend.append('category_id', formData.category_id.toString());
      }
      
      if (formData.tag_ids && formData.tag_ids.length > 0) {
        formDataToSend.append('tag_ids', formData.tag_ids.join(','));
      }
      
      if (selectedFile) {
        formDataToSend.append('featured_image', selectedFile);
      }

      const formDataObj = {};
      formDataToSend.forEach((value, key) => {
        if (key === 'featured_image') {
          formDataObj[key] = value.name ? `File: ${value.name} (${value.size} bytes)` : value;
        } else {
          formDataObj[key] = value;
        }
      });
      
      let result;
      if (isEditMode) {
        result = await updatePost(postId, formDataToSend);
        toast.success("Post updated successfully");
      } else {
        result = await createPost(formDataToSend);
        toast.success("Post created successfully");
      }
      
      navigate('/posts-list');
    } catch (error) {
      if (error.response) {
      }
      toast.error(isEditMode ? "Failed to update post" : "Failed to create post");
    } finally {
      setIsSubmitting(false);
    }
  };

  
  const handleCancel = () => {
    navigate('/posts-list');
  };

  if (isEditMode && postLoading) {
    return (
      <Content>
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '60vh' }}>
          <div className="text-center">
            <div className="spinner-border text-primary mb-3" role="status" style={{ width: '3rem', height: '3rem' }}>
              <span className="visually-hidden">Loading...</span>
            </div>
            <h5 className="text-muted">Loading post data...</h5>
          </div>
        </div>
      </Content>
    );
  }

  const initialContent = isEditMode ? (editPost?.content || "") : "";

  return (
    <>
      <Head title={isEditMode ? "Edit Post" : "Create Post"} />
      <Content>
        {/* Enhanced Header */}
        <BlockHead size="sm" className="nk-block-head-sm">
          <BlockBetween className="flex-column flex-lg-row">
            <BlockHeadContent className="mb-3 mb-lg-0">
              <BlockTitle page className="d-flex align-items-center flex-wrap">
                <Icon name={isEditMode ? "edit-alt" : "plus-circle"} className="me-2 text-primary" />
                <span className="text-break">{isEditMode ? "Edit Post" : "Create New Post"}</span>
              </BlockTitle>
              <BlockDes className="text-soft">
                <p className="mb-0 text-muted">
                  {isEditMode ? "Update your post content and settings" : "Create a new post for your blog"}
                </p>
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              <div className="d-flex flex-column flex-sm-row gap-2 align-items-sm-center">
                {isEditMode && (
                  <div className={`badge badge-pill px-3 py-2 mb-2 mb-sm-0 ${autosaveLoading ? 'badge-warning-soft' : 'badge-success-soft'}`}>
                    <Icon name={autosaveLoading ? "loader" : "save"} className={`me-1 ${autosaveLoading ? 'fa-spin' : ''}`} />
                    <span className="d-none d-sm-inline">{autosaveLoading ? 'Auto-saving...' : 'Auto-saved'}</span>
                    <span className="d-inline d-sm-none">{autosaveLoading ? 'Saving...' : 'Saved'}</span>
                  </div>
                )}
                <BackTo link="/posts-list" icon="arrow-left" className="btn btn-outline-primary w-100 w-sm-auto">
                  <span className="d-none d-sm-inline">Back to Posts</span>
                  <span className="d-inline d-sm-none">Back</span>
                </BackTo>
              </div>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <form onSubmit={handleSubmit(onSubmit)}>
            <Row className="g-4">
              {/* Main Content Column */}
              <Col xxl="8" lg="8" md="12" className="order-2 order-lg-1">
                <div className="gap gy-4">
                  {/* Mobile: Show Quick Actions first on mobile only */}
                  <div className="d-block d-lg-none mb-4">
                    <PreviewCard className="card-bordered shadow-sm">
                      <div className="card-head border-bottom pb-2">
                        <div className="d-flex align-items-center">
                          <div className="icon-circle icon-circle-sm bg-warning-soft me-2">
                            <Icon name="zap" className="text-warning" />
                          </div>
                          <h6 className="card-title mb-0">Quick Actions</h6>
                        </div>
                      </div>
                      <div className="card-body p-3">
                        <div className="d-flex flex-row gap-2 justify-content-center">
                          <Button 
                            onClick={handleCancel} 
                            disabled={isLoading}
                            className="btn btn-dim btn-primary btn-outline-primary px-4 py-2"
                          >
                            <Icon name="arrow-left" className="me-1" />
                            <span className="d-none d-sm-inline">Cancel</span>
                          </Button>
                          <Button 
                            type="submit" 
                            disabled={isLoading}
                            className="btn btn-dim btn-primary px-4 py-2"
                          >
                            {isLoading ? (
                              <>
                                <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                                <span className="visually-hidden">Loading...</span>
                                {isEditMode ? 'Updating...' : 'Creating...'}
                              </>
                            ) : (
                              <>
                                <Icon name={isEditMode ? "check" : "plus"} className="me-1" />
                                {isEditMode ? 'Update Post' : 'Create Post'}
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    </PreviewCard>
                  </div>

                  {/* Post Information Section - Enhanced */}
                  <PreviewCard className="card-bordered shadow-sm mb-4">
                    <div className="card-head border-bottom pb-3">
                      <div className="d-flex align-items-center">
                        <div className="icon-circle icon-circle-sm bg-primary-soft me-2 me-md-3">
                          <Icon name="file-text" className="text-primary" />
                        </div>
                        <div>
                          <h5 className="card-title mb-1 fs-6 fs-md-5">Post Information</h5>
                          <p className="card-text text-muted mb-0 small">Basic information about your post</p>
                        </div>
                      </div>
                    </div>
                    <div className="card-body p-3 p-md-4">
                      <Row className="g-4">
                        <Col lg="8" md="12">
                          <div className="form-group">
                            <label className="form-label fw-medium" htmlFor="post-title">
                              <Icon name="type" className="me-1 text-primary" />
                              Post Title *
                            </label>
                            <div className="form-control-wrap">
                              <input
                                id="post-title"
                                type="text"
                                className={`form-control ${screenSize.isMobile ? '' : 'form-control-lg'} ${errors.title ? 'is-invalid' : ''}`}
                                {...register('title', {
                                  required: "Title is required",
                                  minLength: { value: 3, message: "Title must be at least 3 characters" }
                                })}
                                value={formData.title}
                                onChange={handleTitleChange}
                                placeholder="Enter an engaging post title"
                                style={{ borderRadius: '8px' }}
                              />
                              {errors.title && <div className="invalid-feedback">{errors.title.message}</div>}
                            </div>
                          </div>
                        </Col>
                        <Col lg="4" md="12">
                          <div className="form-group">
                            <label className="form-label fw-medium" htmlFor="post-slug">
                              <Icon name="link" className="me-1 text-primary" />
                              URL Slug *
                            </label>
                            <div className="form-control-wrap">
                              <input
                                id="post-slug"
                                type="text"
                                className={`form-control ${errors.slug ? 'is-invalid' : ''}`}
                                {...register('slug', {
                                  required: "Slug is required",
                                  pattern: {
                                    value: /^[a-z0-9-]+$/,
                                    message: "Slug can only contain lowercase letters, numbers, and hyphens"
                                  }
                                })}
                                value={formData.slug}
                                onChange={(e) => setFormData(prev => ({ ...prev, slug: e.target.value }))}
                                placeholder="post-url-slug"
                                style={{ borderRadius: '8px' }}
                              />
                              {errors.slug && <div className="invalid-feedback">{errors.slug.message}</div>}
                            </div>
                          </div>
                        </Col>
                        <Col size="12">
                          <div className="form-group">
                            <label className="form-label fw-medium" htmlFor="post-excerpt">
                              <Icon name="align-left" className="me-1 text-primary" />
                              Post Excerpt
                            </label>
                            <div className="form-control-wrap">
                              <textarea
                                id="post-excerpt"
                                className={`form-control ${errors.excerpt ? 'is-invalid' : ''}`}
                                rows="4"
                                {...register('excerpt', {
                                  maxLength: { value: 500, message: "Excerpt must be less than 500 characters" }
                                })}
                                value={formData.excerpt}
                                onChange={(e) => setFormData(prev => ({ ...prev, excerpt: e.target.value }))}
                                placeholder="Write a brief description that will appear in post previews and search results"
                                style={{ borderRadius: '8px', resize: 'vertical' }}
                              />
                              {errors.excerpt && <div className="invalid-feedback">{errors.excerpt.message}</div>}
                              <div className="form-note d-flex flex-column flex-sm-row justify-content-sm-between align-items-start align-items-sm-center mt-2 gap-1">
                                <small className="text-muted">This will appear in post previews and search results</small>
                                <span className={`badge ${formData.excerpt.length > 400 ? 'badge-warning' : 'badge-light'} align-self-end align-self-sm-auto`}>
                                  {formData.excerpt.length}/500
                                </span>
                              </div>
                            </div>
                          </div>
                        </Col>
                      </Row>
                    </div>
                  </PreviewCard>

                  {/* Content Editor Section - Enhanced */}
                  <PreviewCard className="card-bordered shadow-sm mb-4">
                    <div className="card-head border-bottom pb-3">
                      <div className="d-flex align-items-center">
                        <div className="icon-circle icon-circle-sm bg-info-soft me-2 me-md-3">
                          <Icon name="edit" className="text-info" />
                        </div>
                        <div>
                          <h5 className="card-title mb-1 fs-6 fs-md-5">Post Content</h5>
                          <p className="card-text text-muted mb-0 small">Write your post content using the rich text editor</p>
                        </div>
                      </div>
                    </div>
                    <div className="card-body p-3 p-md-4">
                      <div className="form-group">
                        <div className="form-control-wrap">
                          <div style={{ border: '1px solid #e5e9f2', borderRadius: '8px', overflow: 'hidden' }}>
                            <Editor
                              licenseKey="gpl"
                              onInit={(evt, editor) => editorRef.current = editor}
                              initialValue={initialContent}
                              value={formData.content}
                              init={{
                                height: screenSize.isTablet ? 350 : 500,
                                menubar: screenSize.isTablet ? false : 'file edit view format',
                                toolbar: screenSize.isTablet ? 
                                  'undo redo | bold italic | bullist numlist | link' :
                                  'undo redo | formatselect | ' +
                                  'bold italic | alignleft aligncenter ' +
                                  'alignright alignjustify | outdent indent | ' +
                                  'bullist numlist | link image | removeformat',
                                content_style: theme.skin === 'dark' ? 
                                'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; color: #fff; background-color: #1a1a1a; }' : 
                                'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; color: #000; background-color: #fff; }',
                                branding: false,
                                directionality: 'ltr',
                              }}
                              onEditorChange={handleContentChange}
                            />
                          </div>
                          {errors.content && <div className="invalid-feedback d-block mt-2">{errors.content.message}</div>}
                        </div>
                      </div>
                    </div>
                  </PreviewCard>

                  {/* Mobile: Categories and Tags after Content */}
                  <div className="d-block d-lg-none mb-4">
                    <PreviewCard className="card-bordered shadow-sm">
                      <div className="card-head border-bottom pb-3">
                        <div className="d-flex align-items-center">
                          <div className="icon-circle icon-circle-sm bg-info-soft me-2 me-md-3">
                            <Icon name="tags" className="text-info" />
                          </div>
                          <h5 className="card-title mb-0 fs-6 fs-md-5">Categories & Tags</h5>
                        </div>
                      </div>
                      <div className="card-body p-3 p-md-4">
                        <div className="form-group mb-4">
                          <label className="form-label fw-medium">
                            <Icon name="folder" className="me-1 text-info" />
                            Category
                          </label>
                          <div className="form-control-wrap">
                            <RSelect
                              options={categoryOptions}
                              value={categoryOptions.find(opt => opt.value === String(formData.category_id))}
                              onChange={(selected) => setFormData(prev => ({ ...prev, category_id: selected?.value || null }))}
                              placeholder="Select category"
                              isClearable
                              styles={{
                                control: (base) => ({
                                  ...base,
                                  borderRadius: '8px',
                                  border: '1px solid #e5e9f2'
                                })
                              }}
                            />
                          </div>
                        </div>
                        <div className="form-group">
                          <label className="form-label fw-medium">
                            <Icon name="tag" className="me-1 text-info" />
                            Tags
                          </label>
                          <div className="form-control-wrap">
                            <RSelect
                              isMulti
                              options={tagOptions}
                              value={tagOptions.filter(opt => formData.tag_ids.includes(opt.value))}
                              onChange={(selected) => setFormData(prev => ({ 
                                ...prev, 
                                tag_ids: selected ? selected.map(s => s.value) : [] 
                              }))}
                              placeholder="Select tags"
                              styles={{
                                control: (base) => ({
                                  ...base,
                                  borderRadius: '8px',
                                  border: '1px solid #e5e9f2'
                                })
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    </PreviewCard>
                  </div>

                  {/* Mobile: Featured Image after Categories */}
                  <div className="d-block d-lg-none mb-4">
                    <PreviewCard className="card-bordered shadow-sm">
                      <div className="card-head border-bottom pb-3">
                        <div className="d-flex align-items-center">
                          <div className="icon-circle icon-circle-sm bg-success-soft me-2 me-md-3">
                            <Icon name="image" className="text-success" />
                          </div>
                          <h5 className="card-title mb-0 fs-6 fs-md-5">Featured Image</h5>
                        </div>
                      </div>
                      <div className="card-body p-3 p-md-4">
                        <div className="form-group">
                          <label className="form-label fw-medium">
                            Featured Image
                          </label>
                          <div className="form-control-wrap">
                            <Dropzone 
                              onDrop={(acceptedFiles) => {
                                const file = acceptedFiles[0];
                                if (file && file.type.startsWith('image/') && file.size <= 5 * 1024 * 1024) {
                                  setSelectedFile(file);
                                  setPreview(URL.createObjectURL(file));
                                  setFormData(prev => ({ ...prev, featured_image: '' }));
                                  toast.success('Image selected successfully');
                                } else {
                                  toast.error('Invalid file: Must be image under 5MB');
                                }
                              }} 
                              accept={{ 'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp'] }} 
                              maxFiles={1} 
                              maxSize={5 * 1024 * 1024}
                            >
                              {({ getRootProps, getInputProps, isDragActive }) => (
                                <section>
                                  <div {...getRootProps()} className={`dropzone upload-zone dz-clickable border rounded p-3 p-md-4 text-center ${isDragActive ? 'border-primary bg-primary-soft' : 'bg-light'}`}>
                                    <input {...getInputProps()} />
                                    <Icon name="upload-cloud" className="mb-2 text-primary" size="lg" />
                                    {isDragActive ? (
                                      <p className="mb-1">Drop the image here...</p>
                                    ) : (
                                      <>
                                        <p className="mb-1 d-none d-sm-block">Drag 'n' drop an image here, or click to select (max 5MB)</p>
                                        <p className="mb-1 d-block d-sm-none">Tap to select an image (max 5MB)</p>
                                      </>
                                    )}
                                    <small className="text-muted d-block">Supported formats: JPG, JPEG, PNG, GIF, WEBP</small>
                                  </div>
                                </section>
                              )}
                            </Dropzone>
                            
                            {/* Clear selection button */}
                            {(selectedFile || preview) && (
                              <div className="mt-2">
                                <Button 
                                  onClick={() => {
                                    setSelectedFile(null);
                                    setPreview('');
                                    setFormData(prev => ({ ...prev, featured_image: '' }));
                                  }}
                                  className="btn btn-dim btn-outline-danger btn-sm"
                                >
                                  <Icon name="trash" className="me-1" />
                                  Clear Image
                                </Button>
                              </div>
                            )}
                          </div>
                          
                          {/* Preview */}
                          {(preview || formData.featured_image) && (
                            <div className="form-note-group mt-3">
                              <div className="image-preview-container" style={{ 
                                border: '2px dashed #e5e9f2', 
                                borderRadius: '8px', 
                                padding: screenSize.isMobile ? '8px' : '10px',
                                textAlign: 'center'
                              }}>
                                <img 
                                  src={preview || getImageUrl(formData.featured_image, "posts")} 
                                  alt="Featured preview" 
                                  className="img-fluid rounded"
                                  style={{ maxWidth: '100%', height: 'auto', maxHeight: screenSize.isMobile ? '150px' : '200px' }}
                                  onError={(e) => {
                                    e.target.style.display = 'none';
                                    e.target.nextSibling.style.display = 'block';
                                  }}
                                />
                                <div style={{ display: 'none' }} className="text-danger">
                                  <Icon name="alert-triangle" className="me-1" />
                                  Failed to load image
                                </div>
                                {selectedFile && (
                                  <div className="mt-2">
                                    <small className="text-muted">
                                      Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                                    </small>
                                  </div>
                                )}
                                {!selectedFile && formData.featured_image && (
                                  <div className="mt-2">
                                    <small className="text-success">
                                      <Icon name="check-circle" className="me-1" />
                                      Current featured image
                                    </small>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </PreviewCard>
                  </div>

                  {/* SEO Settings Section - Enhanced */}
                  <PreviewCard className="card-bordered shadow-sm mb-4">
                    <div className="card-head border-bottom pb-3">
                      <div className="d-flex align-items-center">
                        <div className="icon-circle icon-circle-sm bg-success-soft me-2 me-md-3">
                          <Icon name="search" className="text-success" />
                        </div>
                        <div>
                          <h5 className="card-title mb-1 fs-6 fs-md-5">SEO Settings</h5>
                          <p className="card-text text-muted mb-0 small">Optimize your post for search engines</p>
                        </div>
                      </div>
                    </div>
                    <div className="card-body p-3 p-md-4">
                      <Row className="g-4">
                        <Col lg="6" md="12">
                          <div className="form-group">
                            <label className="form-label fw-medium" htmlFor="meta-title">
                              <Icon name="tag" className="me-1 text-success" />
                              Meta Title
                            </label>
                            <div className="form-control-wrap">
                              <input
                                id="meta-title"
                                type="text"
                                className={`form-control ${errors.meta_title ? 'is-invalid' : ''}`}
                                {...register('meta_title', {
                                  maxLength: { value: 200, message: "Meta title must be less than 200 characters" }
                                })}
                                value={formData.meta_title}
                                onChange={(e) => setFormData(prev => ({ ...prev, meta_title: e.target.value }))}
                                placeholder="SEO title for search engines"
                                style={{ borderRadius: '8px' }}
                              />
                              {errors.meta_title && <div className="invalid-feedback">{errors.meta_title.message}</div>}
                              <div className="form-note d-flex flex-column flex-sm-row justify-content-sm-between align-items-start align-items-sm-center mt-2 gap-1">
                                <small className="text-muted">Appears in search results</small>
                                <span className={`badge ${formData.meta_title.length > 160 ? 'badge-warning' : 'badge-light'} align-self-end align-self-sm-auto`}>
                                  {formData.meta_title.length}/200
                                </span>
                              </div>
                            </div>
                          </div>
                        </Col>
                        <Col lg="6" md="12">
                          <div className="form-group">
                            <label className="form-label fw-medium" htmlFor="meta-description">
                              <Icon name="file-text" className="me-1 text-success" />
                              Meta Description
                            </label>
                            <div className="form-control-wrap">
                              <textarea
                                id="meta-description"
                                className={`form-control ${errors.meta_description ? 'is-invalid' : ''}`}
                                rows="4"
                                {...register('meta_description', {
                                  maxLength: { value: 300, message: "Meta description must be less than 300 characters" }
                                })}
                                value={formData.meta_description}
                                onChange={(e) => setFormData(prev => ({ ...prev, meta_description: e.target.value }))}
                                placeholder="SEO description for search engines"
                                style={{ borderRadius: '8px', resize: 'vertical' }}
                              />
                              {errors.meta_description && <div className="invalid-feedback">{errors.meta_description.message}</div>}
                              <div className="form-note d-flex flex-column flex-sm-row justify-content-sm-between align-items-start align-items-sm-center mt-2 gap-1">
                                <small className="text-muted">Appears below title in search results</small>
                                <span className={`badge ${formData.meta_description.length > 250 ? 'badge-warning' : 'badge-light'} align-self-end align-self-sm-auto`}>
                                  {formData.meta_description.length}/300
                                </span>
                              </div>
                            </div>
                          </div>
                        </Col>
                      </Row>
                    </div>
                  </PreviewCard>

                  {/* Mobile: Post Statistics at the end */}
                  <div className="d-block d-lg-none mb-4">
                    <PreviewCard className="card-bordered shadow-sm">
                      <div className="card-head border-bottom pb-3">
                        <div className="d-flex align-items-center">
                          <div className="icon-circle icon-circle-sm bg-warning-soft me-2 me-md-3">
                            <Icon name="bar-chart" className="text-warning" />
                          </div>
                          <h5 className="card-title mb-0 fs-6 fs-md-5">Post Statistics</h5>
                        </div>
                      </div>
                      <div className="card-body p-3 p-md-4">
                        <div className="form-group mb-3">
                          <div className="d-flex align-items-center justify-content-between p-3 bg-light rounded-3">
                            <div className="d-flex align-items-center">
                              <Icon name="clock" className="me-2 text-warning" />
                              <span className="fw-medium">Reading Time</span>
                            </div>
                            <span className="badge badge-pill badge-warning-soft px-3 py-2">
                              {formData.reading_time || 0} min{formData.reading_time !== 1 ? 's' : ''}
                            </span>
                          </div>
                          <div className="form-note text-center mt-2">
                            <small className="text-muted">Automatically calculated from content</small>
                          </div>
                        </div>
                        
                        <div className="form-group mb-3">
                          <div className="d-flex align-items-center justify-content-between p-3 bg-light rounded-3">
                            <div className="d-flex align-items-center">
                              <Icon name="file-text" className="me-2 text-info" />
                              <span className="fw-medium">Content Length</span>
                            </div>
                            <span className="badge badge-pill badge-info-soft px-3 py-2">
                              {formData.content.replace(/<[^>]*>/g, '').split(/\s+/).filter(word => word.length > 0).length} words
                            </span>
                          </div>
                        </div>
                        
                        {/* Progress Indicators */}
                        <div className="mt-4 pt-3 border-top">
                          <h6 className="text-muted mb-3">Content Progress</h6>
                          <div className="progress-list">
                            <div className="progress-wrap mb-2">
                              <div className="progress-text">
                                <span>Title</span>
                                <span className={formData.title ? 'text-success' : 'text-muted'}>
                                  {formData.title ? '✓' : '○'}
                                </span>
                              </div>
                            </div>
                            <div className="progress-wrap mb-2">
                              <div className="progress-text">
                                <span>Content</span>
                                <span className={formData.content ? 'text-success' : 'text-muted'}>
                                  {formData.content ? '✓' : '○'}
                                </span>
                              </div>
                            </div>
                            <div className="progress-wrap mb-2">
                              <div className="progress-text">
                                <span>Category</span>
                                <span className={formData.category_id && String(formData.category_id).length > 0 ? 'text-success' : 'text-muted'}>
                                  {formData.category_id && String(formData.category_id).length > 0 ? '✓' : '○'}
                                </span>
                              </div>
                            </div>
                            <div className="progress-wrap">
                              <div className="progress-text">
                                <span>Featured Image</span>
                                <span className={(selectedFile || formData.featured_image) ? 'text-success' : 'text-muted'}>
                                  {(selectedFile || formData.featured_image) ? '✓' : '○'}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </PreviewCard>
                  </div>
                </div>
              </Col>

              {/* Sidebar Column - Enhanced - Hidden on mobile */}
              <Col xxl="4" lg="4" className="order-1 order-lg-2 d-none d-lg-block">
                <div className="gap gy-4 d-lg-sticky position-lg-sticky" style={{ top: '20px' }}>
                  {/* Quick Actions - Enhanced */}
                  <PreviewCard className="card-bordered shadow-sm mb-4">
                    <div className="card-head border-bottom pb-2">
                      <div className="d-flex align-items-center">
                        <div className="icon-circle icon-circle-sm bg-warning-soft me-2">
                          <Icon name="zap" className="text-warning" />
                        </div>
                        <h6 className="card-title mb-0">Quick Actions</h6>
                      </div>
                    </div>
                    <div className="card-body p-3">
                      <div className="d-flex flex-column flex-xl-row gap-2">
                        <Button 
                          type="submit" 
                          disabled={isLoading}
                          className="btn btn-dim btn-primary flex-fill py-2"
                        >
                          {isLoading ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                              <span className="visually-hidden">Loading...</span>
                              {isEditMode ? 'Updating...' : 'Creating...'}
                            </>
                          ) : (
                            <>
                              <Icon name={isEditMode ? "check" : "plus"} className="me-1" />
                              {isEditMode ? 'Update Post' : 'Create Post'}
                            </>
                          )}
                        </Button>
                        <Button 
                          onClick={handleCancel} 
                          disabled={isLoading}
                          className="btn btn-dim btn-primary btn-outline-primary flex-fill py-2"
                        >
                          <Icon name="arrow-left" className="me-1" />
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </PreviewCard>

                  {/* Categories and Tags - Enhanced */}
                  <PreviewCard className="card-bordered shadow-sm mb-4">
                    <div className="card-head border-bottom pb-3">
                      <div className="d-flex align-items-center">
                        <div className="icon-circle icon-circle-sm bg-info-soft me-2 me-md-3">
                          <Icon name="tags" className="text-info" />
                        </div>
                        <h5 className="card-title mb-0 fs-6 fs-md-5">Categories & Tags</h5>
                      </div>
                    </div>
                    <div className="card-body p-3 p-md-4">
                      <div className="form-group mb-4">
                        <label className="form-label fw-medium">
                          <Icon name="folder" className="me-1 text-info" />
                          Category
                        </label>
                        <div className="form-control-wrap">
  <RSelect
    options={categoryOptions}
    value={categoryOptions.find(opt => opt.value === String(formData.category_id))}
    onChange={(selected) => setFormData(prev => ({ ...prev, category_id: selected?.value || null }))}
    placeholder="Select category"
    isClearable
    styles={{
      control: (base) => ({
        ...base,
        borderRadius: '8px',
        border: '1px solid #e5e9f2'
      })
    }}
  />
                        </div>
                      </div>
                      <div className="form-group">
                        <label className="form-label fw-medium">
                          <Icon name="tag" className="me-1 text-info" />
                          Tags
                        </label>
                        <div className="form-control-wrap">
                          <RSelect
                            isMulti
                            options={tagOptions}
                            value={tagOptions.filter(opt => formData.tag_ids.includes(opt.value))}
                            onChange={(selected) => setFormData(prev => ({ 
                              ...prev, 
                              tag_ids: selected ? selected.map(s => s.value) : [] 
                            }))}
                            placeholder="Select tags"
                            styles={{
                              control: (base) => ({
                                ...base,
                                borderRadius: '8px',
                                border: '1px solid #e5e9f2'
                              })
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </PreviewCard>

                  {/* Featured Image - Enhanced */}
                  <PreviewCard className="card-bordered shadow-sm mb-4">
                    <div className="card-head border-bottom pb-3">
                      <div className="d-flex align-items-center">
                        <div className="icon-circle icon-circle-sm bg-success-soft me-2 me-md-3">
                          <Icon name="image" className="text-success" />
                        </div>
                        <h5 className="card-title mb-0 fs-6 fs-md-5">Featured Image</h5>
                      </div>
                    </div>
                    <div className="card-body p-3 p-md-4">
                      <div className="form-group">
                        <label className="form-label fw-medium">
                          Featured Image
                        </label>
                        <div className="form-control-wrap">
                          <Dropzone 
                            onDrop={(acceptedFiles) => {
                              const file = acceptedFiles[0];
                              if (file && file.type.startsWith('image/') && file.size <= 5 * 1024 * 1024) {
                                setSelectedFile(file);
                                setPreview(URL.createObjectURL(file));
                                setFormData(prev => ({ ...prev, featured_image: '' }));
                                toast.success('Image selected successfully');
                              } else {
                                toast.error('Invalid file: Must be image under 5MB');
                              }
                            }} 
                            accept={{ 'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp'] }} 
                            maxFiles={1} 
                            maxSize={5 * 1024 * 1024}
                          >
                            {({ getRootProps, getInputProps, isDragActive }) => (
                              <section>
                                <div {...getRootProps()} className={`dropzone upload-zone dz-clickable border rounded p-3 p-md-4 text-center ${isDragActive ? 'border-primary bg-primary-soft' : 'bg-light'}`}>
                                  <input {...getInputProps()} />
                                  <Icon name="upload-cloud" className="mb-2 text-primary" size="lg" />
                                  {isDragActive ? (
                                    <p className="mb-1">Drop the image here...</p>
                                  ) : (
                                    <>
                                      <p className="mb-1 d-none d-sm-block">Drag 'n' drop an image here, or click to select (max 5MB)</p>
                                      <p className="mb-1 d-block d-sm-none">Tap to select an image (max 5MB)</p>
                                    </>
                                  )}
                                  <small className="text-muted d-block">Supported formats: JPG, JPEG, PNG, GIF, WEBP</small>
                                </div>
                              </section>
                            )}
                          </Dropzone>
                          
                          {/* Clear selection button */}
                          {(selectedFile || preview) && (
                            <div className="mt-2">
                              <Button 
                                onClick={() => {
                                  setSelectedFile(null);
                                  setPreview('');
                                  setFormData(prev => ({ ...prev, featured_image: '' }));
                                }}
                                className="btn btn-dim btn-outline-danger btn-sm"
                              >
                                <Icon name="trash" className="me-1" />
                                Clear Image
                              </Button>
                            </div>
                          )}
                        </div>
                        
                        {/* Preview */}
                        {(preview || formData.featured_image) && (
                          <div className="form-note-group mt-3">
                            <div className="image-preview-container" style={{ 
                              border: '2px dashed #e5e9f2', 
                              borderRadius: '8px', 
                              padding: screenSize.isMobile ? '8px' : '10px',
                              textAlign: 'center'
                            }}>
                              <img 
                                src={preview || getImageUrl(formData.featured_image, "posts")} 
                                alt="Featured preview" 
                                className="img-fluid rounded"
                                style={{ maxWidth: '100%', height: 'auto', maxHeight: screenSize.isMobile ? '150px' : '200px' }}
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                  e.target.nextSibling.style.display = 'block';
                                }}
                              />
                              <div style={{ display: 'none' }} className="text-danger">
                                <Icon name="alert-triangle" className="me-1" />
                                Failed to load image
                              </div>
                              {selectedFile && (
                                <div className="mt-2">
                                  <small className="text-muted">
                                    Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                                  </small>
                                </div>
                              )}
                              {!selectedFile && formData.featured_image && (
                                <div className="mt-2">
                                  <small className="text-success">
                                    <Icon name="check-circle" className="me-1" />
                                    Current featured image
                                  </small>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </PreviewCard>

                  {/* Post Statistics - Enhanced */}
                  <PreviewCard className="card-bordered shadow-sm mb-4">
                    <div className="card-head border-bottom pb-3">
                      <div className="d-flex align-items-center">
                        <div className="icon-circle icon-circle-sm bg-warning-soft me-2 me-md-3">
                          <Icon name="bar-chart" className="text-warning" />
                        </div>
                        <h5 className="card-title mb-0 fs-6 fs-md-5">Post Statistics</h5>
                      </div>
                    </div>
                    <div className="card-body p-3 p-md-4">
                      <div className="form-group mb-3">
                        <div className="d-flex align-items-center justify-content-between p-3 bg-light rounded-3">
                          <div className="d-flex align-items-center">
                            <Icon name="clock" className="me-2 text-warning" />
                            <span className="fw-medium">Reading Time</span>
                          </div>
                          <span className="badge badge-pill badge-warning-soft px-3 py-2">
                            {formData.reading_time || 0} min{formData.reading_time !== 1 ? 's' : ''}
                          </span>
                        </div>
                        <div className="form-note text-center mt-2">
                          <small className="text-muted">Automatically calculated from content</small>
                        </div>
                      </div>
                      
                      <div className="form-group mb-3">
                        <div className="d-flex align-items-center justify-content-between p-3 bg-light rounded-3">
                          <div className="d-flex align-items-center">
                            <Icon name="file-text" className="me-2 text-info" />
                            <span className="fw-medium">Content Length</span>
                          </div>
                          <span className="badge badge-pill badge-info-soft px-3 py-2">
                            {formData.content.replace(/<[^>]*>/g, '').split(/\s+/).filter(word => word.length > 0).length} words
                          </span>
                        </div>
                      </div>
                      
                      {/* Progress Indicators */}
                      <div className="mt-4 pt-3 border-top">
                        <h6 className="text-muted mb-3">Content Progress</h6>
                        <div className="progress-list">
                          <div className="progress-wrap mb-2">
                            <div className="progress-text">
                              <span>Title</span>
                              <span className={formData.title ? 'text-success' : 'text-muted'}>
                                {formData.title ? '✓' : '○'}
                              </span>
                            </div>
                          </div>
                          <div className="progress-wrap mb-2">
                            <div className="progress-text">
                              <span>Content</span>
                              <span className={formData.content ? 'text-success' : 'text-muted'}>
                                {formData.content ? '✓' : '○'}
                              </span>
                            </div>
                          </div>
                          <div className="progress-wrap mb-2">
                            <div className="progress-text">
                              <span>Category</span>
                              <span className={formData.category_id && String(formData.category_id).length > 0 ? 'text-success' : 'text-muted'}>
                                {formData.category_id && String(formData.category_id).length > 0 ? '✓' : '○'}
                              </span>
                            </div>
                          </div>
                          <div className="progress-wrap">
                            <div className="progress-text">
                              <span>Featured Image</span>
                              <span className={(selectedFile || formData.featured_image) ? 'text-success' : 'text-muted'}>
                                {(selectedFile || formData.featured_image) ? '✓' : '○'}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </PreviewCard>
                </div>
              </Col>
            </Row>
          </form>
        </Block>
      </Content>
    </>
  );
};

export default PostForm;