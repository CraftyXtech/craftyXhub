<script setup>
import { useForm } from '@inertiajs/vue3';
import InputLabel from '@/Components/InputLabel.vue';
import TextInput from '@/Components/TextInput.vue';
import InputError from '@/Components/InputError.vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';

const props = defineProps({
    tag: {
        type: Object,
        default: () => ({ name: '', slug: '' }),
    },
    isEdit: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits(['submit', 'cancel']);

const form = useForm({
    name: props.tag?.name || '',
    slug: props.tag?.slug || '',
    _method: props.isEdit ? 'PUT' : 'POST',
});

const submitForm = () => {
    const routeName = props.isEdit ? 'editor.tags.update' : 'editor.tags.store';
    const params = props.isEdit ? [props.tag.id] : [];
    
    form.submit(routeName, ...params, {});
};

const cancelForm = () => {
    emit('cancel');
};

</script>

<template>
    <form @submit.prevent="submitForm">
        <div class="space-y-6">
            <div>
                <InputLabel for="name" value="Tag Name" />
                <TextInput
                    id="name"
                    type="text"
                    class="mt-1 block w-full"
                    v-model="form.name"
                    required
                    autofocus
                    placeholder="Enter tag name"
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
        </div>

        <div class="mt-8 flex justify-end space-x-3">
            <SecondaryButton type="button" @click="cancelForm">
                Cancel
            </SecondaryButton>
            <PrimaryButton :class="{ 'opacity-25': form.processing }" :disabled="form.processing">
                {{ isEdit ? 'Update Tag' : 'Create Tag' }}
            </PrimaryButton>
        </div>
    </form>
</template> 