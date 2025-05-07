<script setup>
import { useForm } from '@inertiajs/vue3';
import InputLabel from '@/Components/InputLabel.vue';
import TextInput from '@/Components/TextInput.vue';
import InputError from '@/Components/InputError.vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';
import TextareaInput from '@/Components/TextareaInput.vue'; // Assuming you have or will create this

const props = defineProps({
    category: {
        type: Object,
        default: () => ({ name: '', slug: '', description: '' }),
    },
    isEdit: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits(['submit', 'cancel']);

const form = useForm({
    name: props.category?.name || '',
    slug: props.category?.slug || '',
    description: props.category?.description || '',
    _method: props.isEdit ? 'PUT' : 'POST',
});

const submitForm = () => {
    const routeName = props.isEdit ? 'editor.categories.update' : 'editor.categories.store';
    const params = props.isEdit ? [props.category.id] : [];
    
    form.submit(routeName, ...params, {
        // onSuccess: () => emit('submit'), // Handled by controller redirect usually
    });
};

const cancelForm = () => {
    emit('cancel');
};

</script>

<template>
    <form @submit.prevent="submitForm">
        <div class="space-y-6">
            <div>
                <InputLabel for="name" value="Category Name" />
                <TextInput
                    id="name"
                    type="text"
                    class="mt-1 block w-full"
                    v-model="form.name"
                    required
                    autofocus
                    placeholder="Enter category name"
                />
                <InputError class="mt-2" :message="form.errors.name" />
            </div>

            <div>
                <InputLabel for="slug" value="Slug (URL-friendly name)" />
                <TextInput
                    id="slug"
                    type="text"
                    class="mt-1 block w-full"
                    v-model="form.slug"
                    placeholder="Optional, auto-generated if left blank"
                />
                <InputError class="mt-2" :message="form.errors.slug" />
            </div>

            <div>
                <InputLabel for="description" value="Description (Optional)" />
                <TextareaInput
                    id="description"
                    class="mt-1 block w-full"
                    v-model="form.description"
                    rows="3"
                    placeholder="Brief description of the category"
                />
                <InputError class="mt-2" :message="form.errors.description" />
            </div>
        </div>

        <div class="mt-8 flex justify-end space-x-3">
            <SecondaryButton type="button" @click="cancelForm">
                Cancel
            </SecondaryButton>
            <PrimaryButton :class="{ 'opacity-25': form.processing }" :disabled="form.processing">
                {{ isEdit ? 'Update Category' : 'Create Category' }}
            </PrimaryButton>
        </div>
    </form>
</template> 