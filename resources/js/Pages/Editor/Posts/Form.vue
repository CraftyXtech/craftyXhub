<script setup>
import { ref, computed, watch } from 'vue';
import { useForm, router } from '@inertiajs/vue3';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';
import DangerButton from '@/Components/DangerButton.vue';
import InputLabel from '@/Components/InputLabel.vue';
import TextInput from '@/Components/TextInput.vue';
import InputError from '@/Components/InputError.vue';
import Modal from '@/Components/Modal.vue';
import RichEditor from '@/Components/RichEditor.vue';
import TagInput from '@/Components/TagInput.vue';
import FileUpload from '@/Components/FileUpload.vue';

const props = defineProps({
    post: {
        type: Object,
        default: () => ({})
    },
    categories: {
        type: Array,
        required: true
    },
    tags: {
        type: Array,
        default: () => []
    },
    canPublish: {
        type: Boolean,
        default: false
    },
    isEdit: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['cancel']);

// Create form
const form = useForm({
    title: props.post?.title || '',
    slug: props.post?.slug || '',
    body: props.post?.content || props.post?.body || '',
    excerpt: props.post?.excerpt || '',
    category_id: props.post?.category_id || '',
    tags: props.post?.tags?.map(tag => tag.id) || [],
    featured_image: null,
    status: props.post?.status || 'draft',
    published_at: props.post?.published_at || null,
    meta_title: props.post?.meta_title || '',
    meta_description: props.post?.meta_description || '',
    _method: props.isEdit ? 'PUT' : 'POST',
});

// Selected tags for display
const selectedTags = ref(props.post?.tags || []);

// Preview image URL
const previewImage = ref(props.post?.featured_image_url || null);

// Modal states
const showDeleteModal = ref(false);
const showPublishModal = ref(false);
const showScheduleModal = ref(false);
const scheduledDate = ref(props.post?.published_at || '');

// Auto-generate slug from title
watch(() => form.title, (newTitle) => {
    if (!props.post?.slug) {
        form.slug = newTitle
            .toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim();
    }
});

// Handle image upload
const handleImageUpload = (file) => {
    form.featured_image = file;
    
    // Create preview URL
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.value = e.target.result;
        };
        reader.readAsDataURL(file);
    }
};

// Remove featured image
const removeImage = () => {
    form.featured_image = null;
    previewImage.value = null;
};

// Handle tag selection
const handleTagSelect = (selectedItems) => {
    form.tags = selectedItems.map(tag => tag.id);
    selectedTags.value = selectedItems;
};

// Handle form submission based on context (create or edit)
const submitForm = (status = 'draft') => {
    form.status = status;
    
    if (status === 'published' && !form.published_at) {
        form.published_at = new Date().toISOString();
    }
    
    // Make sure required fields are handled properly
    if (!form.title) {
        alert('Title is required');
        return;
    }
    
    if (!form.body) {
        alert('Content is required');
        return;
    }
    
    if (!form.slug) {
        // Auto-generate slug from title if empty
        form.slug = form.title
            .toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim();
    }
    
    const routeName = props.isEdit 
        ? 'editor.posts.update'
        : 'editor.posts.store';
    
    const url = props.isEdit 
        ? route(routeName, { post: props.post.slug })
        : route(routeName);
        
    form.post(url, {
        preserveScroll: true,
        onSuccess: () => {
            // Redirect to the posts index after successful submission
            if (!props.isEdit) {
                router.visit(route('editor.posts.index'));
            }
        },
        onError: (errors) => {
            console.error('Form submission failed:', errors);
        }
    });
};

// Save as draft
const saveDraft = () => submitForm('draft');

// Submit for review
const submitForReview = () => submitForm('under_review');

// Open publish modal
const openPublishModal = () => {
    showPublishModal.value = true;
};

// Publish post
const publishPost = () => {
    showPublishModal.value = false;
    submitForm('published');
};

// Open schedule modal
const openScheduleModal = () => {
    showScheduleModal.value = true;
};

// Schedule post
const schedulePost = () => {
    form.status = 'scheduled';
    form.published_at = new Date(scheduledDate.value).toISOString();
    
    const routeToSubmit = props.isEdit
        ? route('editor.posts.update', { post: props.post.slug })
        : route('editor.posts.store');
        
    form.post(routeToSubmit, {
        preserveScroll: true,
        onSuccess: () => {
            showScheduleModal.value = false;
        },
    });
};

// Open delete modal
const openDeleteModal = () => {
    showDeleteModal.value = true;
};

// Delete post
const deletePost = () => {
    useForm({}).delete(route('editor.posts.destroy', { post: props.post.slug }), {
        onSuccess: () => {
            showDeleteModal.value = false;
            window.location = route('editor.posts.index');
        },
    });
};

// Cancel form
const handleCancel = () => {
    emit('cancel');
};

// Status badges
const getStatusBadge = (status) => {
    const statusMap = {
        'published': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        'draft': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        'scheduled': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
        'rejected': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
        'under_review': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
    };
    return statusMap[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
};

// Format status text
const formatStatus = (status) => {
    return status
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
};

// Computed property to check if form has been modified
const formHasChanges = computed(() => {
    if (!props.isEdit) return true;
    
    return Object.keys(form).some(key => {
        if (key === '_method' || key === 'featured_image') return false;
        if (key === 'tags') {
            const originalTags = props.post?.tags?.map(tag => tag.id) || [];
            return JSON.stringify(form[key].sort()) !== JSON.stringify(originalTags.sort());
        }
        return form[key] !== props.post?.[key];
    });
});
</script>

<template>
    <form @submit.prevent>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Main content area -->
            <div class="lg:col-span-2 space-y-6">
                <!-- Title -->
                <div>
                    <InputLabel for="title" value="Title" />
                    <TextInput
                        id="title"
                        type="text"
                        class="mt-1 block w-full"
                        v-model="form.title"
                        required
                        autofocus
                        placeholder="Post title"
                    />
                    <InputError :message="form.errors.title" class="mt-2" />
                </div>

                <!-- Slug -->
                <div>
                    <InputLabel for="slug" value="Slug" />
                    <TextInput
                        id="slug"
                        type="text"
                        class="mt-1 block w-full"
                        v-model="form.slug"
                        required
                        placeholder="post-url-slug"
                    />
                    <InputError :message="form.errors.slug" class="mt-2" />
                </div>

                <!-- Content -->
                <div>
                    <InputLabel for="body" value="Content" />
                    <RichEditor
                        id="body"
                        v-model="form.body"
                        class="mt-1 block w-full min-h-[400px]"
                        placeholder="Write your post content here..."
                    />
                    <InputError :message="form.errors.body" class="mt-2" />
                </div>

                <!-- Excerpt -->
                <div>
                    <InputLabel for="excerpt" value="Excerpt" />
                    <textarea
                        id="excerpt"
                        v-model="form.excerpt"
                        class="mt-1 block w-full border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 focus:border-indigo-500 dark:focus:border-indigo-600 focus:ring-indigo-500 dark:focus:ring-indigo-600 rounded-md shadow-sm"
                        rows="3"
                        placeholder="Brief summary of your post"
                    ></textarea>
                    <InputError :message="form.errors.excerpt" class="mt-2" />
                </div>
            </div>

            <!-- Sidebar -->
            <div class="space-y-6">
                <!-- Status badge for edit mode -->
                <div v-if="isEdit && post.status" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Status</h3>
                    <span 
                        class="px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="getStatusBadge(post.status)"
                    >
                        {{ formatStatus(post.status) }}
                    </span>
                </div>
                
                <!-- Actions -->
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-3">
                    <h3 class="text-sm font-medium text-gray-900 dark:text-gray-100">Actions</h3>
                    
                    <div class="flex flex-wrap gap-2">
                        <PrimaryButton @click="saveDraft" :disabled="form.processing">
                            Save Draft
                        </PrimaryButton>
                        
                        <SecondaryButton @click="submitForReview" :disabled="form.processing">
                            Submit for Review
                        </SecondaryButton>
                        
                        <SecondaryButton 
                            v-if="canPublish && (!isEdit || post.status !== 'published')"
                            @click="openPublishModal" 
                            :disabled="form.processing"
                        >
                            Publish Now
                        </SecondaryButton>
                        
                        <SecondaryButton 
                            v-if="canPublish"
                            @click="openScheduleModal" 
                            :disabled="form.processing"
                        >
                            Schedule
                        </SecondaryButton>
                        
                        <SecondaryButton @click="handleCancel" :disabled="form.processing">
                            Cancel
                        </SecondaryButton>
                        
                        <DangerButton 
                            v-if="isEdit"
                            @click="openDeleteModal" 
                            :disabled="form.processing" 
                            class="mt-2"
                        >
                            Delete
                        </DangerButton>
                    </div>
                </div>

                <!-- Category -->
                <div>
                    <InputLabel for="category" value="Category" />
                    <select
                        id="category"
                        v-model="form.category_id"
                        class="mt-1 block w-full border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 focus:border-indigo-500 dark:focus:border-indigo-600 focus:ring-indigo-500 dark:focus:ring-indigo-600 rounded-md shadow-sm"
                    >
                        <option value="">Select a category</option>
                        <option v-for="category in categories" :key="category.id" :value="category.id">
                            {{ category.name }}
                        </option>
                    </select>
                    <InputError :message="form.errors.category_id" class="mt-2" />
                </div>

                <!-- Tags -->
                <div v-if="tags.length > 0">
                    <InputLabel for="tags" value="Tags" />
                    <TagInput 
                        id="tags"
                        :available-tags="tags"
                        :selected-tags="selectedTags"
                        @update:selected="handleTagSelect"
                    />
                    <InputError :message="form.errors.tags" class="mt-2" />
                </div>

                <!-- Featured Image -->
                <div>
                    <InputLabel for="featured_image" value="Featured Image" />
                    <div class="mt-1">
                        <div v-if="previewImage" class="mb-2">
                            <img :src="previewImage" alt="Preview" class="w-full h-auto rounded-md" />
                            <button 
                                type="button" 
                                @click="removeImage" 
                                class="mt-2 text-red-500 text-sm"
                            >
                                Remove Image
                            </button>
                        </div>
                        <FileUpload 
                            v-else
                            @file-selected="handleImageUpload" 
                            accept="image/*" 
                        />
                    </div>
                    <InputError :message="form.errors.featured_image" class="mt-2" />
                </div>

                <!-- Meta Title -->
                <div>
                    <InputLabel for="meta_title" value="Meta Title (SEO)" />
                    <TextInput
                        id="meta_title"
                        type="text"
                        class="mt-1 block w-full"
                        v-model="form.meta_title"
                        placeholder="SEO title (optional)"
                    />
                    <InputError :message="form.errors.meta_title" class="mt-2" />
                </div>

                <!-- Meta Description -->
                <div>
                    <InputLabel for="meta_description" value="Meta Description (SEO)" />
                    <textarea
                        id="meta_description"
                        v-model="form.meta_description"
                        class="mt-1 block w-full border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 focus:border-indigo-500 dark:focus:border-indigo-600 focus:ring-indigo-500 dark:focus:ring-indigo-600 rounded-md shadow-sm"
                        rows="3"
                        placeholder="SEO description (optional)"
                    ></textarea>
                    <InputError :message="form.errors.meta_description" class="mt-2" />
                </div>
            </div>
        </div>

        <!-- Delete Confirmation Modal -->
        <Modal :show="showDeleteModal" @close="showDeleteModal = false">
            <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                    Delete Post
                </h2>

                <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    Are you sure you want to delete this post? This action cannot be undone.
                </p>

                <div class="mt-6 flex justify-end">
                    <SecondaryButton @click="showDeleteModal = false" class="mr-2">
                        Cancel
                    </SecondaryButton>

                    <DangerButton @click="deletePost" :disabled="form.processing">
                        Delete Post
                    </DangerButton>
                </div>
            </div>
        </Modal>

        <!-- Publish Confirmation Modal -->
        <Modal :show="showPublishModal" @close="showPublishModal = false">
            <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                    Publish Post
                </h2>

                <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    Are you sure you want to publish this post now? It will be immediately visible to all visitors.
                </p>

                <div class="mt-6 flex justify-end">
                    <SecondaryButton @click="showPublishModal = false" class="mr-2">
                        Cancel
                    </SecondaryButton>

                    <PrimaryButton @click="publishPost" :disabled="form.processing">
                        Publish Now
                    </PrimaryButton>
                </div>
            </div>
        </Modal>

        <!-- Schedule Modal -->
        <Modal :show="showScheduleModal" @close="showScheduleModal = false">
            <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                    Schedule Post
                </h2>

                <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    Choose when to publish this post.
                </p>

                <div class="mt-4">
                    <InputLabel for="scheduled_date" value="Publication Date & Time" />
                    <TextInput
                        id="scheduled_date"
                        type="datetime-local"
                        class="mt-1 block w-full"
                        v-model="scheduledDate"
                        required
                    />
                </div>

                <div class="mt-6 flex justify-end">
                    <SecondaryButton @click="showScheduleModal = false" class="mr-2">
                        Cancel
                    </SecondaryButton>

                    <PrimaryButton @click="schedulePost" :disabled="form.processing || !scheduledDate">
                        Schedule
                    </PrimaryButton>
                </div>
            </div>
        </Modal>
    </form>
</template> 