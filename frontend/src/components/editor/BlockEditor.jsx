import { memo, useRef, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

// MUI
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

// EditorJS
import EditorJS from '@editorjs/editorjs';
import Header from '@editorjs/header';
import List from '@editorjs/list';
import Quote from '@editorjs/quote';
import Code from '@editorjs/code';
import ImageTool from '@editorjs/image';
import Delimiter from '@editorjs/delimiter';
import InlineCode from '@editorjs/inline-code';
import Marker from '@editorjs/marker';
import Underline from '@editorjs/underline';
import LinkTool from '@editorjs/link';
import Embed from '@editorjs/embed';

// Utilities
import { editorJsToHtml, htmlToEditorJs, extractPlainText, sanitizeEditorData } from '@/utils/editorUtils';

// API
import { axiosPrivate } from '@/api/axios';

/**
 * BlockEditor - EditorJS-based rich content editor
 * 
 * @param {object} props
 * @param {object} props.value - Initial EditorJS data or HTML string
 * @param {function} props.onChange - Callback when content changes
 * @param {string} props.placeholder - Editor placeholder text
 * @param {number|string} props.minHeight - Minimum editor height
 * @param {boolean} props.fullHeight - Use full available height
 * @param {boolean} props.error - Show error state
 * @param {string} props.helperText - Helper/error text to display
 * @param {boolean} props.readOnly - Read-only mode
 */
const BlockEditor = ({
  value,
  onChange,
  placeholder = 'Start writing your content...',
  minHeight = 400,
  fullHeight = false,
  error = false,
  helperText,
  readOnly = false,
}) => {
  const theme = useTheme();
  const editorRef = useRef(null);
  const holderRef = useRef(null);
  const isInitializedRef = useRef(false);
  const instanceId = useRef(`editorjs-${Date.now()}`);

  // Image uploader for EditorJS
  const imageUploader = useCallback(() => ({
    uploadByFile: async (file) => {
      // Validate file
      if (!file.type.startsWith('image/')) {
        throw new Error('Please select a valid image file');
      }
      if (file.size > 10 * 1024 * 1024) {
        throw new Error('Image size must be less than 10MB');
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('folder', 'posts');

      try {
        const response = await axiosPrivate.post('media/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        if (response.data?.url) {
          return {
            success: 1,
            file: { url: response.data.url }
          };
        }
        throw new Error('Upload failed');
      } catch (error) {
        console.error('Image upload error:', error);
        throw new Error('Image upload failed: ' + (error.message || 'Unknown error'));
      }
    },
    uploadByUrl: async (url) => {
      return {
        success: 1,
        file: { url }
      };
    }
  }), []);

  // Handle editor content changes
  const handleEditorChange = useCallback(async () => {
    if (!editorRef.current || !onChange) return;

    try {
      const editorData = await editorRef.current.save();
      const sanitizedData = sanitizeEditorData(editorData);
      
      onChange({
        blocks: sanitizedData,
        html: editorJsToHtml(sanitizedData),
        plainText: extractPlainText(sanitizedData)
      });
    } catch (error) {
      console.error('Error saving editor content:', error);
    }
  }, [onChange]);

  // Initialize EditorJS
  useEffect(() => {
    if (isInitializedRef.current || !holderRef.current) return;

    const initEditor = async () => {
      try {
        let initialData = {
          time: Date.now(),
          blocks: [],
          version: '2.28.0'
        };

        // Load initial content
        if (value) {
          if (value.blocks) {
            initialData = value;
          } else if (typeof value === 'string' && value.trim()) {
            initialData = htmlToEditorJs(value);
          }
        }

        const editor = new EditorJS({
          holder: instanceId.current,
          placeholder,
          minHeight: typeof minHeight === 'number' ? minHeight : 400,
          data: initialData,
          readOnly,
          
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
                captionPlaceholder: 'Quote author'
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
                uploader: imageUploader(),
                captionPlaceholder: 'Image caption (optional)',
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
                endpoint: '/api/v1/fetch-url'
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
        });

        await editor.isReady;
        editorRef.current = editor;
        isInitializedRef.current = true;

      } catch (error) {
        console.error('Error initializing BlockEditor:', error);
      }
    };

    initEditor();

    return () => {
      if (editorRef.current?.destroy) {
        editorRef.current.destroy();
        editorRef.current = null;
      }
      isInitializedRef.current = false;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Calculate height
  const height = fullHeight ? 'calc(100vh - 280px)' : minHeight;

  return (
    <Box>
      <Box
        ref={holderRef}
        id={instanceId.current}
        sx={{
          minHeight: typeof height === 'number' ? `${height}px` : height,
          border: '1px solid',
          borderColor: error ? 'error.main' : 'divider',
          borderRadius: 1,
          p: 2,
          bgcolor: 'background.paper',
          transition: 'border-color 0.2s',
          '&:focus-within': {
            borderColor: error ? 'error.main' : 'primary.main',
          },
          // EditorJS styling overrides
          '& .codex-editor': {
            fontSize: '1rem',
          },
          '& .codex-editor__redactor': {
            paddingBottom: '100px !important',
          },
          '& .ce-block__content': {
            maxWidth: '100%',
          },
          '& .ce-toolbar__content': {
            maxWidth: '100%',
          },
          '& .ce-paragraph': {
            lineHeight: 1.8,
            color: theme.palette.text.primary,
          },
          '& h1, & h2, & h3': {
            fontFamily: theme.typography.fontFamily,
            color: theme.palette.text.primary,
          },
          '& .cdx-quote__text': {
            borderLeftColor: theme.palette.primary.main,
          },
          '& .ce-code__textarea': {
            backgroundColor: theme.palette.mode === 'dark' 
              ? theme.palette.grey[900] 
              : theme.palette.grey[100],
            color: theme.palette.text.primary,
          },
          '& .image-tool__image-picture': {
            borderRadius: 1,
          },
        }}
      />
      {helperText && (
        <Typography
          variant="caption"
          color={error ? 'error' : 'text.secondary'}
          sx={{ mt: 0.5, display: 'block' }}
        >
          {helperText}
        </Typography>
      )}
    </Box>
  );
};

BlockEditor.propTypes = {
  value: PropTypes.oneOfType([PropTypes.object, PropTypes.string]),
  onChange: PropTypes.func,
  placeholder: PropTypes.string,
  minHeight: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  fullHeight: PropTypes.bool,
  error: PropTypes.bool,
  helperText: PropTypes.string,
  readOnly: PropTypes.bool,
};

export default memo(BlockEditor);
