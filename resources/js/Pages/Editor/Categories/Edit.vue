<script setup>
import { Head, router, usePage } from '@inertiajs/vue3';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import CategoryForm from './Form.vue'; // Changed from Form.vue to CategoryForm.vue for clarity
import { computed } from 'vue';

const props = defineProps({
    category: Object, // The category object to edit
    // canPublish: Boolean, // Example, might be canUpdateCategory or similar
});

const page = usePage();
const currentUserRole = computed(() => page.props.auth.user.role);
const isAdmin = computed(() => currentUserRole.value === 'admin');

const pageTitle = computed(() =>
    isAdmin.value ? `Admin | Edit Category: ${props.category.name}` : `Editor | Edit Category: ${props.category.name}`
);
const headerTitle = computed(() =>
    isAdmin.value ? `Edit Category (Admin): ${props.category.name}` : `Edit Category: ${props.category.name}`
);

const handleCancel = () => {
    router.visit(route('editor.categories.index'));
};

// Form submission is handled by the Form component itself
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
            <div class="max-w-3xl mx-auto sm:px-6 lg:px-8">
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6 md:p-8">
                        <CategoryForm
                            :category="props.category"
                            :is-edit="true"
                            @cancel="handleCancel"
                            />
                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template> 