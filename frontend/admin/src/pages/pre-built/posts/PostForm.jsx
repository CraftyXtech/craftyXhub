import React, { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Row, Col, Button, Card } from "reactstrap";
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
} from "@/components/Component";
import { useCreatePost, useUpdatePost, useGetPost, useGetCategories, useGetTags, useCreateCategory, useCreateTag } from "@/api/postService";
import { toast } from "react-toastify";

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
      
      // Set form values
      Object.keys(postData).forEach(key => {
        setValue(key, postData[key]);
      });
    }
  }, [editPost, isEditMode, setValue]);

  // Auto-generate slug from title
  const generateSlug = (title) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9 -]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  };

  // Handle title change and auto-generate slug
  const handleTitleChange = (e) => {
    const title = e.target.value;
    setFormData(prev => ({ ...prev, title }));
    
    // Auto-generate slug if not editing or if slug is empty
    if (!isEditMode || !formData.slug) {
      const slug = generateSlug(title);
      setFormData(prev => ({ ...prev, slug }));
      setValue('slug', slug);
    }
  };

  // Handle content change from TinyMCE
  const handleContentChange = (content) => {
    setFormData(prev => ({ ...prev, content }));
    setValue('content', content);
  };

  // Handle category creation
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

  // Handle tag creation
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

  // Prepare options for selects
  const categoryOptions = categories.map(cat => ({
    value: cat.id,
    label: cat.name
  }));

  const tagOptions = tags.map(tag => ({
    value: tag.id,
    label: tag.name
  }));

  // Handle form submission
  const onSubmit = async (data) => {
    try {
      // Get content from TinyMCE editor
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

      // Navigate back to posts list
      navigate('/posts-list');
    } catch (error) {
      toast.error(isEditMode ? "Failed to update post" : "Failed to create post");
    }
  };

  // Handle cancel
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
              {/* Main Content Section */}
              <Col xxl="8">
                <div className="gap gy-4">
                  {/* Basic Information */}
                  <Card className="card-bordered">
                    <div className="card-inner">
                      <div className="card-head">
                        <h5 className="card-title">Post Information</h5>
                      </div>
                      <Row className="g-4">
                        <Col size="12">
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

                        <Col size="12">
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
                              <div className="form-note">
                                This will be used in the post URL: /posts/{formData.slug}
                              </div>
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
                                rows="4"
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
                    </div>
                  </Card>

                  {/* Content Editor */}
                  <Card className="card-bordered">
                    <div className="card-inner">
                      <div className="card-head">
                        <h5 className="card-title">Post Content</h5>
                      </div>
                      <div className="form-group">
                        <div className="form-control-wrap">
                          <Editor
                            licenseKey="gpl"
                            onInit={(evt, editor) => editorRef.current = editor}
                            initialValue={formData.content}
                            init={{
                              height: 500,
                              menubar: 'file edit view insert format tools table help',
                              toolbar: 'undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | ' +
                                'link image media table mergetags | addcomment showcomments | ' +
                                'spellcheckdialog a11ycheck typography | align lineheight | ' +
                                'checklist numlist bullist indent outdent | emoticons charmap | removeformat',
                              content_style: theme.skin === 'dark' ? 
                                'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; color: #fff; background-color: #1a1a1a; }' : 
                                'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; color: #000; background-color: #fff; }',
                              plugins: [
                                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                                'insertdatetime', 'media', 'table', 'code', 'help', 'wordcount',
                                'emoticons', 'template', 'codesample'
                              ],
                              image_advtab: true,
                              link_context_toolbar: true,
                              branding: false,
                            }}
                            onEditorChange={handleContentChange}
                          />
                          {errors.content && <span className="invalid">{errors.content.message}</span>}
                        </div>
                      </div>
                    </div>
                  </Card>

                  {/* SEO Settings */}
                  <Card className="card-bordered">
                    <div className="card-inner">
                      <div className="card-head">
                        <h5 className="card-title">SEO Settings</h5>
                        <p className="card-text">Optimize your post for search engines</p>
                      </div>
                      <Row className="g-4">
                        <Col size="12">
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

                        <Col size="12">
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
                    </div>
                  </Card>
                </div>
              </Col>

              {/* Sidebar */}
              <Col xxl="4">
                <div className="gap gy-4">
                  {/* Publish Settings */}
                  <Card className="card-bordered">
                    <div className="card-inner">
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
                    </div>
                  </Card>

                  {/* Categories and Tags */}
                  <Card className="card-bordered">
                    <div className="card-inner">
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
                    </div>
                  </Card>

                  {/* Featured Image */}
                  <Card className="card-bordered">
                    <div className="card-inner">
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
                    </div>
                  </Card>

                  {/* Additional Settings */}
                  <Card className="card-bordered">
                    <div className="card-inner">
                      <div className="card-head">
                        <h5 className="card-title">Additional Settings</h5>
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor="reading-time">
                          Reading Time (minutes)
                        </label>
                        <div className="form-control-wrap">
                          <input
                            id="reading-time"
                            type="number"
                            className="form-control"
                            {...register('reading_time', {
                              min: { value: 1, message: "Reading time must be at least 1 minute" }
                            })}
                            value={formData.reading_time || ''}
                            onChange={(e) => setFormData(prev => ({ ...prev, reading_time: parseInt(e.target.value) || null }))}
                            placeholder="5"
                          />
                          {errors.reading_time && <span className="invalid">{errors.reading_time.message}</span>}
                        </div>
                      </div>
                    </div>
                  </Card>

                  {/* Action Buttons */}
                  <Card className="card-bordered">
                    <div className="card-inner">
                      <div className="d-flex justify-content-between">
                        <Button color="light" onClick={handleCancel} disabled={isLoading}>
                          Cancel
                        </Button>
                        <Button color="primary" type="submit" disabled={isLoading}>
                          {isLoading ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                              {isEditMode ? 'Updating...' : 'Creating...'}
                            </>
                          ) : (
                            <>
                              <Icon name={isEditMode ? "edit" : "plus"} />
                              <span>{isEditMode ? 'Update Post' : 'Create Post'}</span>
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </Card>
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