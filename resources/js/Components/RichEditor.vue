<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import Placeholder from '@tiptap/extension-placeholder';

const props = defineProps({
    modelValue: {
        type: String,
        default: ''
    },
    placeholder: {
        type: String,
        default: 'Start writing...'
    },
    editable: {
        type: Boolean,
        default: true
    }
});

const emit = defineEmits(['update:modelValue']);

const editor = useEditor({
    content: props.modelValue,
    editable: props.editable,
    extensions: [
        StarterKit,
        Link.configure({
            openOnClick: false,
            HTMLAttributes: {
                class: 'text-primary hover:text-primary-dark underline'
            }
        }),
        Image.configure({
            HTMLAttributes: {
                class: 'max-w-full h-auto rounded-lg shadow-lg'
            }
        }),
        Placeholder.configure({
            placeholder: props.placeholder
        })
    ],
    onUpdate: ({ editor }) => {
        emit('update:modelValue', editor.getHTML());
    }
});

const isActive = (type, attrs = {}) => {
    if (!editor.value) return false;
    return editor.value.isActive(type, attrs);
};

const toggleBold = () => editor.value?.chain().focus().toggleBold().run();
const toggleItalic = () => editor.value?.chain().focus().toggleItalic().run();
const toggleStrike = () => editor.value?.chain().focus().toggleStrike().run();
const toggleHeading = (level) => editor.value?.chain().focus().toggleHeading({ level }).run();
const toggleBulletList = () => editor.value?.chain().focus().toggleBulletList().run();
const toggleOrderedList = () => editor.value?.chain().focus().toggleOrderedList().run();
const toggleBlockquote = () => editor.value?.chain().focus().toggleBlockquote().run();
const setLink = () => {
    const url = window.prompt('URL');
    if (url) {
        editor.value?.chain().focus().setLink({ href: url }).run();
    }
};
const unsetLink = () => editor.value?.chain().focus().unsetLink().run();

onBeforeUnmount(() => {
    editor.value?.destroy();
});
</script>

<template>
    <div class="rich-editor">
        <div v-if="editable" class="toolbar flex flex-wrap gap-1 p-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-t-lg">
            <button
                v-for="(item, index) in [
                    { icon: 'format_bold', action: toggleBold, isActive: isActive('bold') },
                    { icon: 'format_italic', action: toggleItalic, isActive: isActive('italic') },
                    { icon: 'format_strikethrough', action: toggleStrike, isActive: isActive('strike') },
                    { icon: 'format_h1', action: () => toggleHeading(1), isActive: isActive('heading', { level: 1 }) },
                    { icon: 'format_h2', action: () => toggleHeading(2), isActive: isActive('heading', { level: 2 }) },
                    { icon: 'format_quote', action: toggleBlockquote, isActive: isActive('blockquote') },
                    { icon: 'format_list_bulleted', action: toggleBulletList, isActive: isActive('bulletList') },
                    { icon: 'format_list_numbered', action: toggleOrderedList, isActive: isActive('orderedList') },
                    { icon: 'link', action: setLink, isActive: isActive('link') },
                    { icon: 'link_off', action: unsetLink, isActive: false },
                ]"
                :key="index"
                @click.prevent="item.action"
                class="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                :class="{ 'bg-gray-200 dark:bg-gray-700': item.isActive }"
                type="button"
            >
                <span class="material-icons text-gray-700 dark:text-gray-300">{{ item.icon }}</span>
            </button>
        </div>
        
        <div :class="[
            'prose prose-sm sm:prose lg:prose-lg max-w-none',
            'border border-gray-200 dark:border-gray-700',
            editable ? 'rounded-b-lg' : 'rounded-lg',
            'bg-white dark:bg-gray-900'
        ]">
            <EditorContent :editor="editor" class="min-h-[200px] p-4" />
        </div>
    </div>
</template>

<style>
.rich-editor {
    .ProseMirror {
        outline: none;
        
        > * + * {
            margin-top: 0.75em;
        }
        
        ul,
        ol {
            padding: 0 1rem;
        }
        
        h1 {
            font-size: 2em;
            font-weight: bold;
        }
        
        h2 {
            font-size: 1.5em;
            font-weight: bold;
        }
        
        blockquote {
            padding-left: 1rem;
            border-left: 2px solid #e5e7eb;
            color: #6b7280;
            font-style: italic;
        }
        
        img {
            max-width: 100%;
            height: auto;
        }
        
        &.ProseMirror-focused {
            outline: none;
        }
    }
    
    .is-editor-empty:first-child::before {
        content: attr(data-placeholder);
        float: left;
        color: #adb5bd;
        pointer-events: none;
        height: 0;
    }
}
</style> 