import React, { memo, useRef, useEffect, useCallback } from 'react'
import PropTypes from "prop-types"

// Libraries
import { useField } from 'formik'
import EditorJS from '@editorjs/editorjs'
import Header from '@editorjs/header'
import List from '@editorjs/list'
import Quote from '@editorjs/quote'
import Code from '@editorjs/code'
import ImageTool from '@editorjs/image'
import Delimiter from '@editorjs/delimiter'
import InlineCode from '@editorjs/inline-code'
import Marker from '@editorjs/marker'
import Underline from '@editorjs/underline'
import LinkTool from '@editorjs/link'
import Embed from '@editorjs/embed'

// Utilities
import {
    editorJsToHtml,
    htmlToEditorJs,
    extractPlainText,
    sanitizeEditorData,
    isEditorEmpty
} from '../../utils/editorUtils'

// CSS
import "../../Assets/scss/components/_block-editor.scss"

const BlockEditor = ({ 
    label, 
    labelClass, 
    className, 
    placeholder, 
    showErrorMsg,
    height,
    ...props 
}) => {
    const [field, meta, helpers] = useField(props)
    const editorRef = useRef(null)
    const holderRef = useRef(null)
    const isInitializedRef = useRef(false)
    
    // Set defaults
    const actualPlaceholder = placeholder ?? "Start writing or type '/' for commands..."
    const actualShowErrorMsg = showErrorMsg ?? true
    const actualHeight = height ?? 400

    // Custom image uploader for EditorJS
    const imageUploader = useCallback({
        uploadByFile: async (file) => {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                throw new Error('Please select a valid image file');
            }
            
            // Validate file size - 10MB limit
            if (file.size > 10 * 1024 * 1024) {
                throw new Error('Image size must be less than 10MB');
            }

            const formData = new FormData();
            formData.append('file', file);
            formData.append('folder', 'posts');

            try {
                const response = await fetch('/api/v1/media/upload', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                    }
                });

                const result = await response.json();
                
                if (result.success) {
                    return {
                        success: 1,
                        file: {
                            url: result.url
                        }
                    };
                } else {
                    throw new Error(result.message || 'Image upload failed');
                }
            } catch (error) {
                console.error('Image upload error:', error);
                throw new Error('Image upload failed: ' + error.message);
            }
        }
    }, []);

    // Handle editor content changes
    const handleEditorChange = useCallback(async () => {
        if (!editorRef.current) return;

        try {
            const editorData = await editorRef.current.save();
            
            // Sanitize the data
            const sanitizedData = sanitizeEditorData(editorData);
            
            // Update content_blocks field with native JSON
            helpers.setValue(sanitizedData);
            
            // Also update a separate content field with HTML if it exists in the form
            // This will be handled by the parent form component
            const html = editorJsToHtml(sanitizedData);
            
            // Trigger a custom event that the parent form can listen to
            if (props.onContentChange) {
                props.onContentChange({
                    blocks: sanitizedData,
                    html: html,
                    plainText: extractPlainText(sanitizedData)
                });
            }
        } catch (error) {
            console.error('Error saving editor content:', error);
        }
    }, [helpers, props]);

    // Initialize EditorJS
    useEffect(() => {
        if (isInitializedRef.current) return;
        if (!holderRef.current) {
            console.error('BlockEditor: holderRef is not set');
            return;
        }

        const initEditor = async () => {
            console.log('BlockEditor: Initializing editor...');
            try {
                let initialData = {
                    time: Date.now(),
                    blocks: [],
                    version: '2.28.0'
                };

                // Load initial content
                if (field.value) {
                    // If field.value is already EditorJS format (has blocks property)
                    if (field.value.blocks) {
                        initialData = field.value;
                    }
                    // If it's HTML string, convert it
                    else if (typeof field.value === 'string' && field.value.trim()) {
                        initialData = htmlToEditorJs(field.value);
                    }
                }

                // Initialize EditorJS
                const editor = new EditorJS({
                    holder: `editorjs-${props.name}`,
                    placeholder: actualPlaceholder,
                    minHeight: actualHeight,
                    data: initialData,
                    
                    tools: {
                        header: {
                            class: Header,
                            config: {
                                levels: [1, 2, 3],
                                defaultLevel: 2
                            },
                            inlineToolbar: true
                        },
                        list: {
                            class: List,
                            inlineToolbar: true,
                            config: {
                                defaultStyle: 'unordered'
                            }
                        },
                        quote: {
                            class: Quote,
                            inlineToolbar: true,
                            config: {
                                quotePlaceholder: 'Enter a quote',
                                captionPlaceholder: 'Quote\'s author'
                            }
                        },
                        code: {
                            class: Code,
                            config: {
                                placeholder: 'Enter code'
                            }
                        },
                        image: {
                            class: ImageTool,
                            config: {
                                uploader: imageUploader,
                                captionPlaceholder: 'Enter image caption (optional)',
                                buttonContent: 'Select an image',
                                types: 'image/*'
                            }
                        },
                        delimiter: Delimiter,
                        inlineCode: {
                            class: InlineCode,
                            shortcut: 'CMD+SHIFT+M'
                        },
                        marker: {
                            class: Marker,
                            shortcut: 'CMD+SHIFT+H'
                        },
                        underline: {
                            class: Underline,
                            shortcut: 'CMD+U'
                        },
                        linkTool: {
                            class: LinkTool,
                            config: {
                                endpoint: '/api/v1/fetchUrl' // Optional: for link preview
                            }
                        },
                        embed: {
                            class: Embed,
                            config: {
                                services: {
                                    youtube: true,
                                    vimeo: true,
                                    twitter: true,
                                    instagram: true,
                                    codepen: true
                                }
                            }
                        }
                    },

                    onChange: handleEditorChange,

                    onReady: () => {
                        console.log('BlockEditor is ready');
                    }
                });

                await editor.isReady;
                editorRef.current = editor;
                isInitializedRef.current = true;
                console.log('BlockEditor: Editor initialized successfully');
                
                // Debug: Check if editor is receiving input
                const editorElement = document.getElementById(`editorjs-${props.name}`);
                if (editorElement) {
                    console.log('BlockEditor: Editor element found', editorElement);
                    
                    // Add event listeners to debug
                    editorElement.addEventListener('keydown', (e) => {
                        console.log('BlockEditor: Keydown event', e.key, e);
                    });
                    
                    editorElement.addEventListener('input', (e) => {
                        console.log('BlockEditor: Input event', e);
                    });
                    
                    editorElement.addEventListener('click', (e) => {
                        console.log('BlockEditor: Click event', e.target);
                    });
                    
                    // Check contenteditable
                    const editableElements = editorElement.querySelectorAll('[contenteditable]');
                    console.log('BlockEditor: Contenteditable elements found:', editableElements.length);
                    editableElements.forEach((el, index) => {
                        console.log(`BlockEditor: Element ${index}:`, el, 'contenteditable=', el.getAttribute('contenteditable'));
                    });
                } else {
                    console.error('BlockEditor: Editor element NOT found!');
                }

            } catch (error) {
                console.error('BlockEditor: Error initializing editor:', error);
                console.error('BlockEditor: Error details:', error.message, error.stack);
            }
        };

        initEditor();

        // Cleanup on unmount
        return () => {
            if (editorRef.current && editorRef.current.destroy) {
                editorRef.current.destroy();
                editorRef.current = null;
            }
            isInitializedRef.current = false;
        };
    }, []); // Empty dependency array - only initialize once

    return (
        <label className={`block-editor-wrapper block relative${(meta.touched && meta.error) ? " errors-danger" : ""}${labelClass ? ` ${labelClass}` : ""}`}>
            {label}
            <div 
                className={`block-editor${className ? ` ${className}` : ""}${meta.touched && meta.error ? " errors-danger" : ""}`}
                style={{ minHeight: `${actualHeight}px` }}
            >
                <div 
                    ref={holderRef} 
                    id={`editorjs-${props.name}`}
                    style={{ minHeight: `${actualHeight}px`, width: '100%' }}
                />
            </div>
            {meta.touched && meta.error && actualShowErrorMsg ? (
                <span className="text-sm text-error block mt-[5px]">{meta.error}</span>
            ) : null}
        </label>
    )
}

BlockEditor.propTypes = {
    label: PropTypes.node,
    labelClass: PropTypes.string,
    className: PropTypes.string,
    showErrorMsg: PropTypes.bool,
    height: PropTypes.number,
    placeholder: PropTypes.string,
    name: PropTypes.string.isRequired,
    onContentChange: PropTypes.func
}

// Set default values directly in destructuring above
BlockEditor.defaultProps = undefined

export default memo(BlockEditor)
