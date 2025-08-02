import React, { useState, useRef, memo, useCallback } from 'react'
import PropTypes from "prop-types"

// Libraries
import { Formik, Form } from 'formik'
import * as Yup from 'yup'
import { m } from "framer-motion"

// Components
import { Input, TextArea, RichTextEditor } from '../Form/Form'
import Buttons from '../Button/Buttons'

// API & Auth
import { useCategories, useTags } from '../../api/usePosts'
import useAuth from '../../api/useAuth'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

// CSS
import "../../Assets/scss/components/_post-form.scss"

// Post form validation schema
const PostFormSchema = Yup.object().shape({
    title: Yup.string()
        .min(5, 'Title must be at least 5 characters')
        .max(200, 'Title must be less than 200 characters')
        .required('Title is required'),
    content: Yup.string()
        .min(50, 'Content must be at least 50 characters')
        .required('Content is required')
        .test('content-length', 'Content must be at least 50 characters', function(value) {
            // Strip HTML tags to check actual text content length
            const textContent = value ? value.replace(/<[^>]*>/g, '').trim() : '';
            return textContent.length >= 50;
        }),
    excerpt: Yup.string()
        .max(500, 'Excerpt must be less than 500 characters'),
    category_id: Yup.number()
        .nullable(),
    tag_ids: Yup.array()
        .of(Yup.number()),
    meta_title: Yup.string()
        .max(200, 'Meta title must be less than 200 characters'),
    meta_description: Yup.string()
        .max(300, 'Meta description must be less than 300 characters'),
    reading_time: Yup.number()
        .min(1, 'Reading time must be at least 1 minute')
        .max(120, 'Reading time must be less than 120 minutes')
        .nullable()
});

const PostForm = (props) => {
    const {
        initialValues = {},
        onSubmit,
        onSaveDraft,
        submitButtonText = "Publish Post",
        draftButtonText = "Save as Draft",
        loading = false,
        className,
        showAdvancedFields = true,
        ...restProps
    } = props;

    const [featuredImage, setFeaturedImage] = useState(null);
    const [featuredImagePreview, setFeaturedImagePreview] = useState(initialValues.featured_image || null);
    const [selectedTags, setSelectedTags] = useState(initialValues.tag_ids || []);
    const [isDraftSaving, setIsDraftSaving] = useState(false);
    const fileInputRef = useRef(null);

    const { isAuthenticated } = useAuth();
    const { categories, loading: categoriesLoading } = useCategories();
    const { tags, loading: tagsLoading } = useTags();

    // Default form values
    const defaultValues = {
        title: '',
        content: '',
        excerpt: '',
        category_id: '',
        tag_ids: [],
        meta_title: '',
        meta_description: '',
        reading_time: '',
        ...initialValues
    };

    // Handle featured image selection
    const handleImageChange = useCallback((event) => {
        const file = event.target.files[0];
        if (file) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                alert('Please select a valid image file');
                return;
            }
            
            // Validate file size (10MB limit)
            if (file.size > 10 * 1024 * 1024) {
                alert('Image size must be less than 10MB');
                return;
            }

            setFeaturedImage(file);
            
            // Create preview
            const reader = new FileReader();
            reader.onload = (e) => {
                setFeaturedImagePreview(e.target.result);
            };
            reader.readAsDataURL(file);
        }
    }, []);

    // Handle tag selection
    const handleTagToggle = useCallback((tagId) => {
        setSelectedTags(prev => {
            if (prev.includes(tagId)) {
                return prev.filter(id => id !== tagId);
            } else {
                return [...prev, tagId];
            }
        });
    }, []);

    // Generate slug from title
    const generateSlug = useCallback((title) => {
        return title
            .toLowerCase()
            .replace(/[^a-z0-9 -]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim('-');
    }, []);

    // Handle form submission
    const handleSubmit = useCallback(async (values, { setSubmitting, setFieldError }) => {
        if (!isAuthenticated) {
            setFieldError('title', 'You must be logged in to create posts');
            return;
        }

        try {
            const formData = {
                ...values,
                tag_ids: selectedTags,
                featured_image: featuredImage,
                slug: values.slug || generateSlug(values.title),
                is_published: true
            };

            await onSubmit(formData);
        } catch (error) {
            console.error('Error submitting post:', error);
            setFieldError('title', error.message || 'Failed to submit post');
        } finally {
            setSubmitting(false);
        }
    }, [isAuthenticated, selectedTags, featuredImage, generateSlug, onSubmit]);

    // Handle save as draft
    const handleSaveDraft = useCallback(async (values) => {
        if (!isAuthenticated || !onSaveDraft) return;

        try {
            setIsDraftSaving(true);
            
            const formData = {
                ...values,
                tag_ids: selectedTags,
                featured_image: featuredImage,
                slug: values.slug || generateSlug(values.title),
                is_published: false
            };

            await onSaveDraft(formData);
        } catch (error) {
            console.error('Error saving draft:', error);
        } finally {
            setIsDraftSaving(false);
        }
    }, [isAuthenticated, selectedTags, featuredImage, generateSlug, onSaveDraft]);

    if (!isAuthenticated) {
        return (
            <div className="text-center py-16">
                <i className="feather-lock text-4xl text-spanishgray mb-4"></i>
                <h3 className="text-darkgray mb-4">Authentication Required</h3>
                <p className="text-spanishgray">Please log in to create or edit posts.</p>
            </div>
        );
    }

    return (
        <m.div 
            className={`post-form-container${className ? ` ${className}` : ''}`}
            {...fadeIn}
            {...restProps}
        >
            <Formik
                initialValues={defaultValues}
                validationSchema={PostFormSchema}
                onSubmit={handleSubmit}
                enableReinitialize={true}
            >
                {({ values, errors, touched, isSubmitting, setFieldValue }) => {
                    // Debug: Log form state
                    console.log('Form values:', values);
                    console.log('Form errors:', errors);
                    console.log('Form touched:', touched);
                    console.log('Form isSubmitting:', isSubmitting);
                    
                    return (
                    <Form className="post-form">
                        {/* Title Field */}
                        <div className="mb-[25px]">
                            <Input
                                name="title"
                                type="text"
                                label={
                                    <span className="text-sm font-medium text-darkgray mb-[10px] block">
                                        Post Title *
                                    </span>
                                }
                                placeholder="Enter an engaging title for your post..."
                                className="py-[15px] px-[20px] w-full border-[1px] border-solid border-[#dfdfdf] text-base rounded-[6px] focus:border-fastblue focus:outline-none transition-all duration-300"
                                onChange={(e) => {
                                    setFieldValue('title', e.target.value);
                                    // Auto-generate slug if not manually set
                                    if (!values.slug) {
                                        setFieldValue('slug', generateSlug(e.target.value));
                                    }
                                }}
                            />
                        </div>

                        {/* Content Field - Rich Text Editor */}
                        <div className="mb-[25px]">
                            <RichTextEditor
                                name="content"
                                label={
                                    <span className="text-sm font-medium text-darkgray mb-[10px] block">
                                        Content *
                                    </span>
                                }
                                height={400}
                                className="w-full"
                            />
                            <div className="text-xs text-spanishgray mt-2">
                                Tip: Use the rich text editor to format your content with headings, lists, links, and more.
                            </div>
                        </div>

                        {/* Featured Image Upload */}
                        <div className="mb-[25px]">
                            <label className="text-sm font-medium text-darkgray mb-[10px] block">
                                Featured Image
                            </label>
                            <div className="border-2 border-dashed border-[#dfdfdf] rounded-[6px] p-6 text-center hover:border-fastblue transition-colors duration-300">
                                {featuredImagePreview ? (
                                    <div className="relative">
                                        <img
                                            src={featuredImagePreview}
                                            alt="Featured preview"
                                            className="max-w-full h-48 object-cover mx-auto rounded-[4px]"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setFeaturedImage(null);
                                                setFeaturedImagePreview(null);
                                                if (fileInputRef.current) {
                                                    fileInputRef.current.value = '';
                                                }
                                            }}
                                            className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-red-600 transition-colors"
                                        >
                                            <i className="feather-x text-sm"></i>
                                        </button>
                                    </div>
                                ) : (
                                    <div
                                        className="cursor-pointer"
                                        onClick={() => fileInputRef.current?.click()}
                                    >
                                        <i className="feather-upload text-3xl text-spanishgray mb-3"></i>
                                        <p className="text-spanishgray mb-2">Click to upload featured image</p>
                                        <p className="text-xs text-spanishgray">Maximum file size: 10MB. Supported formats: JPG, PNG, GIF</p>
                                    </div>
                                )}
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    onChange={handleImageChange}
                                    className="hidden"
                                />
                            </div>
                        </div>

                        {/* Excerpt Field */}
                        <div className="mb-[25px]">
                            <TextArea
                                name="excerpt"
                                rows={3}
                                label={
                                    <span className="text-sm font-medium text-darkgray mb-[10px] block">
                                        Excerpt (Optional)
                                    </span>
                                }
                                placeholder="A brief description of your post..."
                                className="py-[12px] px-[15px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[6px] focus:border-fastblue focus:outline-none transition-all duration-300"
                            />
                        </div>

                        {/* Category Selection */}
                        <div className="mb-[25px]">
                            <label className="text-sm font-medium text-darkgray mb-[10px] block">
                                Category (Optional)
                            </label>
                            <select
                                name="category_id"
                                value={values.category_id}
                                onChange={(e) => setFieldValue('category_id', e.target.value)}
                                className="py-[12px] px-[15px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[6px] focus:border-fastblue focus:outline-none transition-all duration-300"
                                disabled={categoriesLoading}
                            >
                                <option value="">Select a category...</option>
                                {categories.map(category => (
                                    <option key={category.id} value={category.id}>
                                        {category.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Tags Selection */}
                        <div className="mb-[25px]">
                            <label className="text-sm font-medium text-darkgray mb-[10px] block">
                                Tags (Optional)
                            </label>
                            <div className="border-[1px] border-solid border-[#dfdfdf] rounded-[6px] p-4 max-h-48 overflow-y-auto">
                                {tagsLoading ? (
                                    <p className="text-spanishgray text-sm">Loading tags...</p>
                                ) : tags.length > 0 ? (
                                    <div className="flex flex-wrap gap-2">
                                        {tags.map(tag => (
                                            <button
                                                key={tag.id}
                                                type="button"
                                                onClick={() => handleTagToggle(tag.id)}
                                                className={`px-3 py-1 rounded-full text-sm border transition-all duration-300 ${
                                                    selectedTags.includes(tag.id)
                                                        ? 'bg-fastblue text-white border-fastblue'
                                                        : 'bg-white text-darkgray border-[#dfdfdf] hover:border-fastblue'
                                                }`}
                                            >
                                                {tag.name}
                                            </button>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-spanishgray text-sm">No tags available</p>
                                )}
                            </div>
                        </div>

                        {/* Advanced Fields (SEO & Reading Time) */}
                        {showAdvancedFields && (
                            <div className="advanced-fields border-t border-[#dfdfdf] pt-6 mt-6">
                                <h4 className="text-lg font-serif font-medium text-darkgray mb-4">SEO & Advanced Settings</h4>
                                
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <Input
                                            name="meta_title"
                                            type="text"
                                            label={
                                                <span className="text-sm font-medium text-darkgray mb-[8px] block">
                                                    Meta Title
                                                </span>
                                            }
                                            placeholder="SEO title for search engines..."
                                            className="py-[10px] px-[12px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-fastblue focus:outline-none"
                                        />
                                    </div>
                                    
                                    <div>
                                        <Input
                                            name="reading_time"
                                            type="number"
                                            label={
                                                <span className="text-sm font-medium text-darkgray mb-[8px] block">
                                                    Reading Time (minutes)
                                                </span>
                                            }
                                            placeholder="e.g., 5"
                                            className="py-[10px] px-[12px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-fastblue focus:outline-none"
                                        />
                                    </div>
                                </div>

                                <div className="mt-4">
                                    <TextArea
                                        name="meta_description"
                                        rows={3}
                                        label={
                                            <span className="text-sm font-medium text-darkgray mb-[8px] block">
                                                Meta Description
                                            </span>
                                        }
                                        placeholder="Brief description for search engines..."
                                        className="py-[10px] px-[12px] w-full border-[1px] border-solid border-[#dfdfdf] text-sm rounded-[4px] focus:border-fastblue focus:outline-none"
                                    />
                                </div>
                            </div>
                        )}

                        {/* Form Actions */}
                        <div className="form-actions flex flex-col sm:flex-row gap-4 pt-8 border-t border-[#dfdfdf] mt-8">
                            <Buttons
                                type="submit"
                                ariaLabel="submit post"
                                className={`font-medium font-serif uppercase text-sm flex-1 ${isSubmitting || loading ? 'loading' : ''}`}
                                themeColor={["#0038e3", "#ff7a56"]}
                                size="lg"
                                color="#fff"
                                title={isSubmitting || loading ? "Publishing..." : submitButtonText}
                                disabled={isSubmitting || loading}
                            />
                            
                            {onSaveDraft && (
                                <Buttons
                                    type="button"
                                    ariaLabel="save as draft"
                                    className={`font-medium font-serif uppercase text-sm flex-1 ${isDraftSaving ? 'loading' : ''}`}
                                    themeColor={["#6c757d", "#495057"]}
                                    size="lg"
                                    color="#fff"
                                    title={isDraftSaving ? "Saving..." : draftButtonText}
                                    onClick={() => handleSaveDraft(values)}
                                    disabled={isDraftSaving || isSubmitting || loading}
                                />
                            )}
                        </div>
                    </Form>
                    );
                }}
            </Formik>
        </m.div>
    );
};

PostForm.defaultProps = {
    initialValues: {},
    submitButtonText: "Publish Post",
    draftButtonText: "Save as Draft",
    loading: false,
    showAdvancedFields: true,
    className: ""
};

PostForm.propTypes = {
    initialValues: PropTypes.object,
    onSubmit: PropTypes.func.isRequired,
    onSaveDraft: PropTypes.func,
    submitButtonText: PropTypes.string,
    draftButtonText: PropTypes.string,
    loading: PropTypes.bool,
    showAdvancedFields: PropTypes.bool,
    className: PropTypes.string,
};

export default memo(PostForm)