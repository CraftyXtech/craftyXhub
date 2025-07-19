import React, { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "reactstrap";
import { useForm } from "react-hook-form";
import { Editor } from "@tinymce/tinymce-react";
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
import { useCreatePost, useUpdatePost, useGetPost, useGetCategories, useGetTags, useCreateCategory, useCreateTag } from "@/api/postService";
import { toast } from "react-toastify";
import { debounce } from 'lodash';

// TinyMCE imports
import 'tinymce/tinymce';
import 'tinymce/models/dom/model';
import 'tinymce/themes/silver';
import 'tinymce/icons/default';
import 'tinymce/skins/content/default/content';

const PostForm = () => {
  const navigate = useNavigate();
  const { postId } = useParams();
  const isEditMode = Boolean(postId);
  const theme = useTheme();
  const editorRef = useRef(null);
  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm();
  
  // Form state
  const [formData, setFormData] = useState({
    title: "",
    slug: "",
    content: "",
    excerpt: "",
    category_id: null,
    tag_ids: [],
    is_published: false,
    is_featured: false,
    featured_image: "",
    reading_time: null,
    meta_title: "",
    meta_description: "",
  });

  // API hooks
  const { createPost, loading: createLoading } = useCreatePost();
  const { updatePost, loading: updateLoading } = useUpdatePost();
  const { post: editPost, loading: postLoading } = useGetPost(postId);
  const { categories, refetch: refetchCategories } = useGetCategories();
  const { tags, refetch: refetchTags } = useGetTags();
  const { createCategory } = useCreateCategory();
  const { createTag } = useCreateTag();

  // Loading state
  const isLoading = createLoading || updateLoading || postLoading;

  const debouncedUpdate = useCallback(
    debounce(async (data) => {
      try {
        await updatePost(postId, data);
        toast.info('Post autosaved');
      } catch (err) {
        toast.error('Autosave failed');
      }
    }, 5000),
    [updatePost, postId]
  );

  useEffect(() => {
    if (isEditMode) {
      debouncedUpdate(formData);
    }
  }, [formData, isEditMode, debouncedUpdate]);

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
        is_published: editPost.is_published || false,
        is_featured: editPost.is_featured || false,
        featured_image: editPost.featured_image || "",
        reading_time: editPost.reading_time || null,
        meta_title: editPost.meta_title || "",
        meta_description: editPost.meta_description || "",
      };
      setFormData(postData);
      
        
      Object.keys(postData).forEach(key => {
        setValue(key, postData[key]);
      });
    }
  }, [editPost, isEditMode, setValue]);

  
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
    value: cat.id,
    label: cat.name
  }));

  const tagOptions = tags.map(tag => ({
    value: tag.id,
    label: tag.name
  }));

  
  const onSubmit = async (data) => {
    try {
      
      const content = editorRef.current?.getContent() || formData.content;
      
      const postData = {
        ...formData,
        ...data,
        content,
        tag_ids: formData.tag_ids || []
      };

      let result;
      if (isEditMode) {
        result = await updatePost(postId, postData);
        toast.success("Post updated successfully");
      } else {
        result = await createPost(postData);
        toast.success("Post created successfully");
      }

      
      navigate('/posts-list');
    } catch (error) {
      toast.error(isEditMode ? "Failed to update post" : "Failed to create post");
    }
  };

  
  const handleCancel = () => {
    navigate('/posts-list');
  };

  if (isEditMode && postLoading) {
    return (
      <Content>
        <div className="d-flex justify-content-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
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
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BlockTitle page>
                {isEditMode ? "Edit Post" : "Create New Post"}
              </BlockTitle>
              <BlockDes className="text-soft">
                <p>{isEditMode ? "Update your post content and settings" : "Create a new post for your blog"}</p>
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              <BackTo link="/posts-list" icon="arrow-left">
                Back to Posts
              </BackTo>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <form onSubmit={handleSubmit(onSubmit)}>
            <Row className="g-gs">
              {/* Main Content Column */}
              <Col xxl="8">
                <div className="gap gy-gs">
                  {/* Post Information Section */}
                  <PreviewCard className="card-bordered">
                      <div className="card-head">
                        <h5 className="card-title">Post Information</h5>
                      <p className="card-text">Basic information about your post</p>
                      </div>
                      <Row className="g-4">
                      <Col lg="8">
                          <div className="form-group">
                            <label className="form-label" htmlFor="post-title">
                              Post Title *
                            </label>
                            <div className="form-control-wrap">
                              <input
                                id="post-title"
                                type="text"
                                className="form-control form-control-lg"
                                {...register('title', {
                                  required: "Title is required",
                                  minLength: { value: 3, message: "Title must be at least 3 characters" }
                                })}
                                value={formData.title}
                                onChange={handleTitleChange}
                                placeholder="Enter an engaging post title"
                              />
                              {errors.title && <span className="invalid">{errors.title.message}</span>}
                            </div>
                          </div>
                        </Col>
                      <Col lg="4">
                          <div className="form-group">
                            <label className="form-label" htmlFor="post-slug">
                              URL Slug *
                            </label>
                            <div className="form-control-wrap">
                              <input
                                id="post-slug"
                                type="text"
                                className="form-control"
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
                              />
                              {errors.slug && <span className="invalid">{errors.slug.message}</span>}
                          </div>
                          </div>
                        </Col>
                        <Col size="12">
                          <div className="form-group">
                            <label className="form-label" htmlFor="post-excerpt">
                              Post Excerpt
                            </label>
                            <div className="form-control-wrap">
                              <textarea
                                id="post-excerpt"
                                className="form-control"
                              rows="3"
                                {...register('excerpt', {
                                  maxLength: { value: 500, message: "Excerpt must be less than 500 characters" }
                                })}
                                value={formData.excerpt}
                                onChange={(e) => setFormData(prev => ({ ...prev, excerpt: e.target.value }))}
                                placeholder="Write a brief description that will appear in post previews and search results"
                              />
                              {errors.excerpt && <span className="invalid">{errors.excerpt.message}</span>}
                              <div className="form-note">
                                {formData.excerpt.length}/500 characters
                              </div>
                            </div>
                          </div>
                        </Col>
                      </Row>
                  </PreviewCard>

                  {/* Content Editor Section */}
                  <PreviewCard className="card-bordered">
                    <div className="card-head">
                      <h5 className="card-title">Post Content</h5>
                      <p className="card-text">Write your post content using the rich text editor</p>
                      </div>
                      <div className="form-group">
                        <div className="form-control-wrap">
                          <Editor
                            licenseKey="gpl"
                            onInit={(evt, editor) => editorRef.current = editor}
                          initialValue={initialContent}
                          value={formData.content}
                            init={{
                              height: 500,
                            menubar: 'file edit view format',
                            toolbar: 'undo redo | formatselect | ' +
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
                          {errors.content && <span className="invalid">{errors.content.message}</span>}
                        </div>
                      </div>
                  </PreviewCard>

                  {/* SEO Settings Section */}
                  <PreviewCard className="card-bordered">
                      <div className="card-head">
                        <h5 className="card-title">SEO Settings</h5>
                        <p className="card-text">Optimize your post for search engines</p>
                      </div>
                      <Row className="g-4">
                      <Col lg="6">
                          <div className="form-group">
                            <label className="form-label" htmlFor="meta-title">
                              Meta Title
                            </label>
                            <div className="form-control-wrap">
                              <input
                                id="meta-title"
                                type="text"
                                className="form-control"
                                {...register('meta_title', {
                                  maxLength: { value: 200, message: "Meta title must be less than 200 characters" }
                                })}
                                value={formData.meta_title}
                                onChange={(e) => setFormData(prev => ({ ...prev, meta_title: e.target.value }))}
                                placeholder="SEO title for search engines"
                              />
                              {errors.meta_title && <span className="invalid">{errors.meta_title.message}</span>}
                              <div className="form-note">
                                {formData.meta_title.length}/200 characters
                              </div>
                            </div>
                          </div>
                        </Col>
                      <Col lg="6">
                          <div className="form-group">
                            <label className="form-label" htmlFor="meta-description">
                              Meta Description
                            </label>
                            <div className="form-control-wrap">
                              <textarea
                                id="meta-description"
                                className="form-control"
                                rows="3"
                                {...register('meta_description', {
                                  maxLength: { value: 300, message: "Meta description must be less than 300 characters" }
                                })}
                                value={formData.meta_description}
                                onChange={(e) => setFormData(prev => ({ ...prev, meta_description: e.target.value }))}
                                placeholder="SEO description for search engines"
                              />
                              {errors.meta_description && <span className="invalid">{errors.meta_description.message}</span>}
                              <div className="form-note">
                                {formData.meta_description.length}/300 characters
                              </div>
                            </div>
                          </div>
                        </Col>
                      </Row>
                  </PreviewCard>
                </div>
              </Col>

              {/* Sidebar Column */}
              <Col xxl="4">
                <div className="gap gy-gs">
                  {/* Quick Actions */}
                  <PreviewCard className="card-bordered">
                    <div className="card-head">
                      <h5 className="card-title">Quick Actions</h5>
                    </div>
                    <div className="d-flex gap-2 flex-wrap">
                      <Button color="light" size="sm" onClick={handleCancel} disabled={isLoading}>
                        <Icon name="arrow-left" className="me-1" />
                        Cancel
                      </Button>
                      <Button color="primary" size="sm" type="submit" disabled={isLoading}>
                        {isLoading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                            {isEditMode ? 'Updating...' : 'Creating...'}
                          </>
                        ) : (
                          <>
                            <Icon name={isEditMode ? "edit" : "plus"} className="me-1" />
                            {isEditMode ? 'Update Post' : 'Create Post'}
                          </>
                        )}
                      </Button>
                    </div>
                  </PreviewCard>

                  {/* Publish Settings */}
                  <PreviewCard className="card-bordered">
                      <div className="card-head">
                        <h5 className="card-title">Publish Settings</h5>
                      </div>
                      <div className="form-group">
                        <div className="custom-control custom-switch">
                          <input
                            type="checkbox"
                            className="custom-control-input"
                            id="is-published"
                            checked={formData.is_published}
                            onChange={(e) => setFormData(prev => ({ ...prev, is_published: e.target.checked }))}
                          />
                          <label className="custom-control-label" htmlFor="is-published">
                            <span className="switch-text">Published</span>
                          </label>
                        </div>
                        <div className="form-note">
                          {formData.is_published ? "Post will be visible to the public" : "Post will be saved as draft"}
                        </div>
                      </div>
                      <div className="form-group">
                        <div className="custom-control custom-switch">
                          <input
                            type="checkbox"
                            className="custom-control-input"
                            id="is-featured"
                            checked={formData.is_featured}
                            onChange={(e) => setFormData(prev => ({ ...prev, is_featured: e.target.checked }))}
                          />
                          <label className="custom-control-label" htmlFor="is-featured">
                            <span className="switch-text">Featured</span>
                          </label>
                        </div>
                        <div className="form-note">
                          Featured posts appear prominently on the homepage
                        </div>
                      </div>
                  </PreviewCard>

                  {/* Categories and Tags */}
                  <PreviewCard className="card-bordered">
                      <div className="card-head">
                        <h5 className="card-title">Categories & Tags</h5>
                      </div>
                      <div className="form-group">
                        <label className="form-label">Category</label>
                        <div className="form-control-wrap">
                          <RSelect
                            options={categoryOptions}
                            value={categoryOptions.find(opt => opt.value === formData.category_id)}
                            onChange={(selected) => setFormData(prev => ({ ...prev, category_id: selected?.value || null }))}
                            placeholder="Select category"
                            isClearable
                          />
                        </div>
                      </div>
                      <div className="form-group">
                        <label className="form-label">Tags</label>
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
                          />
                        </div>
                      </div>
                  </PreviewCard>

                  {/* Featured Image */}
                  <PreviewCard className="card-bordered">
                      <div className="card-head">
                        <h5 className="card-title">Featured Image</h5>
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="featured-image">
                          Image URL
                        </label>
                        <div className="form-control-wrap">
                          <input
                            id="featured-image"
                            type="url"
                            className="form-control"
                            {...register('featured_image')}
                            value={formData.featured_image}
                            onChange={(e) => setFormData(prev => ({ ...prev, featured_image: e.target.value }))}
                            placeholder="https://example.com/image.jpg"
                          />
                        </div>
                        {formData.featured_image && (
                          <div className="form-note-group">
                            <img 
                              src={formData.featured_image} 
                              alt="Featured preview" 
                              className="img-thumbnail mt-2"
                              style={{ maxWidth: '100%', height: 'auto' }}
                              onError={(e) => {
                                e.target.style.display = 'none';
                              }}
                            />
                          </div>
                        )}
                      </div>
                  </PreviewCard>

                  {/* Post Statistics */}
                  <PreviewCard className="card-bordered">
                    <div className="card-head">
                      <h5 className="card-title">Post Statistics</h5>
                    </div>
                    <div className="form-group">
                      <div className="d-flex justify-content-between align-items-center">
                        <span className="form-label">Reading Time</span>
                        <span className="badge badge-dim badge-outline-primary">
                          {formData.reading_time || 0} min{formData.reading_time !== 1 ? 's' : ''}
                        </span>
                      </div>
                      <div className="form-note">
                        Automatically calculated from content length
                      </div>
                      </div>
                      <div className="form-group">
                      <div className="d-flex justify-content-between align-items-center">
                        <span className="form-label">Content Length</span>
                        <span className="badge badge-dim badge-outline-info">
                          {formData.content.replace(/<[^>]*>/g, '').split(/\s+/).filter(word => word.length > 0).length} words
                            </span>
                      </div>
                    </div>
                    <div className="form-group">
                      <div className="d-flex justify-content-between align-items-center">
                        <span className="form-label">Status</span>
                        <span className={`badge badge-dim ${formData.is_published ? 'badge-success' : 'badge-warning'}`}>
                          {formData.is_published ? 'Published' : 'Draft'}
                        </span>
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