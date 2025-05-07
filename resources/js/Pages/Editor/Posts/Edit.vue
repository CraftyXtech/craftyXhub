<script setup>
import { Head, router, usePage } from '@inertiajs/vue3';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import Form from './Form.vue';
import { computed } from 'vue';

const props = defineProps({
    post: Object,
    categories: Array,
    canPublish: Boolean
});

// Get user role for conditional rendering
const page = usePage();
const currentUserRole = computed(() => page.props.auth.user.role);
const isAdmin = computed(() => currentUserRole.value === 'admin');

const pageTitle = computed(() => 
    isAdmin.value ? `Admin | Edit Post: ${props.post.title}` : `Editor | Edit Post: ${props.post.title}`
);
const headerTitle = computed(() => 
    isAdmin.value ? `Edit Post (Admin): ${props.post.title}` : `Edit Post: ${props.post.title}`
);

const handleCancel = () => {
    router.visit(route('editor.posts.index'));
};
</script>

<template>
    <Head :title="pageTitle" />

    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
                {{ headerTitle }}
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6 text-gray-900 dark:text-gray-100">
                        <Form
                            :post="post"
                            :categories="categories"
                            :can-publish="canPublish"
                            :is-edit="true"
                            @cancel="handleCancel"
                        />
                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template> 