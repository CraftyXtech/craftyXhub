<script setup>
import { Head, router, usePage } from '@inertiajs/vue3';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import TagForm from './Form.vue';
import { computed } from 'vue';

const props = defineProps({
    tag: Object, // The tag object to edit
});

const page = usePage();
const currentUserRole = computed(() => page.props.auth.user.role);
const isAdmin = computed(() => currentUserRole.value === 'admin');

const pageTitle = computed(() =>
    isAdmin.value ? `Admin | Edit Tag: ${props.tag.name}` : `Editor | Edit Tag: ${props.tag.name}`
);
const headerTitle = computed(() =>
    isAdmin.value ? `Edit Tag (Admin): ${props.tag.name}` : `Edit Tag: ${props.tag.name}`
);

const handleCancel = () => {
    router.visit(route('editor.tags.index'));
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
            <div class="max-w-3xl mx-auto sm:px-6 lg:px-8">
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6 md:p-8">
                        <TagForm
                            :tag="props.tag"
                            :is-edit="true"
                            @cancel="handleCancel"
                            />
                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template> 