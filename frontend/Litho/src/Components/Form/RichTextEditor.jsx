import React, { memo, useRef } from 'react'
import PropTypes from "prop-types"

// Libraries
import { useField } from 'formik'
import { Editor } from '@tinymce/tinymce-react'

// CSS
import "../../Assets/scss/components/_rich-text-editor.scss"

const RichTextEditor = ({ 
    label, 
    labelClass, 
    className, 
    showErrorMsg = true,
    height = 400,
    ...props 
}) => {
    const [field, meta, helpers] = useField(props)
    const editorRef = useRef(null)

    // Handle editor content change
    const handleEditorChange = (content) => {
        helpers.setValue(content)
    }

    return (
        <label className={`rich-text-editor-wrapper block relative${(meta.touched && meta.error) ? " errors-danger" : ""}${labelClass ? ` ${labelClass}` : ""}`}>
            {label}
            <div className={`rich-text-editor${className ? ` ${className}` : ""}${meta.touched && meta.error ? " errors-danger" : ""}`}>
                <Editor
                    apiKey="h685q3rw3rzk4surzf8xa5vj1vy6f9cpxw7yfbylcpo8g4rl"
                    onInit={(evt, editor) => editorRef.current = editor}
                    initialValue={field.value || ''}
                    init={{
                        height: height,
                        menubar: false,
                        plugins: 'anchor autolink charmap codesample emoticons image link lists media searchreplace table visualblocks wordcount',
                        toolbar: 'undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image media table | align lineheight | numlist bullist indent outdent | emoticons charmap | removeformat',
                        branding: false,
                        content_style: 'body { font-family: Roboto, sans-serif; font-size: 14px; color: #232323; }',
                        
                        // Image upload configuration
                        images_upload_handler: (blobInfo, progress) => new Promise((resolve, reject) => {
                            const formData = new FormData();
                            formData.append('file', blobInfo.blob(), blobInfo.filename());
                            formData.append('folder', 'posts');

                            fetch('/api/v1/media/upload', {
                                method: 'POST',
                                body: formData,
                                headers: {
                                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                                }
                            })
                            .then(response => response.json())
                            .then(result => {
                                if (result.success) {
                                    resolve(result.url);
                                } else {
                                    reject('Image upload failed: ' + result.message);
                                }
                            })
                            .catch(error => {
                                reject('Image upload failed: ' + error.message);
                            });
                        }),
                        
                        // Simplified image dialog
                        image_advtab: false,
                        image_caption: true,
                        image_title: false,
                        image_description: false,
                        
                        // Auto resize images
                        automatic_uploads: true,
                        images_reuse_filename: true,
                        
                        // File picker for images
                        file_picker_types: 'image',
                        file_picker_callback: (callback, value, meta) => {
                            if (meta.filetype === 'image') {
                                const input = document.createElement('input');
                                input.setAttribute('type', 'file');
                                input.setAttribute('accept', 'image/*');
                                
                                input.onchange = function () {
                                    const file = this.files[0];
                                    if (file) {
                                        const reader = new FileReader();
                                        reader.onload = function () {
                                            // Create a blob info object
                                            const id = 'blobid' + (new Date()).getTime();
                                            const blobCache = editorRef.current.editorUpload.blobCache;
                                            const base64 = reader.result.split(',')[1];
                                            const blobInfo = blobCache.create(id, file, base64);
                                            blobCache.add(blobInfo);
                                            
                                            // Call the callback with the blob URL
                                            callback(blobInfo.blobUri(), { alt: file.name });
                                        };
                                        reader.readAsDataURL(file);
                                    }
                                };
                                
                                input.click();
                            }
                        },
                        
                        // Media embed configuration (for videos)
                        media_live_embeds: true,
                        media_filter_html: false
                    }}
                    onEditorChange={handleEditorChange}
                />
            </div>
            {meta.touched && meta.error && showErrorMsg ? (
                <span className="text-sm text-error block mt-[5px]">{meta.error}</span>
            ) : null}
        </label>
    )
}

RichTextEditor.defaultProps = {
    showErrorMsg: true,
    height: 400
}

RichTextEditor.propTypes = {
    label: PropTypes.node,
    labelClass: PropTypes.string,
    className: PropTypes.string,
    showErrorMsg: PropTypes.bool,
    height: PropTypes.number,
    name: PropTypes.string.isRequired
}

export default memo(RichTextEditor)