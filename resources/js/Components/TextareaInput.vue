<template>
    <div>
        <label v-if="label" :for="id" class="block font-medium text-sm text-gray-700 dark:text-gray-300">
            {{ label }}
            <span v-if="required" class="text-red-500">*</span>
        </label>

        <textarea
            :id="id"
            :value="modelValue"
            :class="[
                'border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 focus:border-indigo-500 dark:focus:border-indigo-600 focus:ring-indigo-500 dark:focus:ring-indigo-600 rounded-md shadow-sm mt-1 block w-full',
                error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : '',
            ]"
            :disabled="disabled"
            :rows="rows"
            :placeholder="placeholder"
            :required="required"
            :aria-invalid="error ? 'true' : undefined"
            :aria-describedby="error ? `${id}-error` : undefined"
            @input="$emit('update:modelValue', $event.target.value)"
        ></textarea>

        <p v-if="error" :id="`${id}-error`" class="mt-1 text-sm text-red-600 dark:text-red-400">{{ error }}</p>
        <p v-if="hint && !error" class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ hint }}</p>
    </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import { uid } from '@/utils/helpers';

const props = defineProps({
    modelValue: {
        type: String,
        default: '',
    },
    label: {
        type: String,
        default: '',
    },
    placeholder: {
        type: String,
        default: '',
    },
    rows: {
        type: [Number, String],
        default: 4,
    },
    hint: {
        type: String,
        default: '',
    },
    error: {
        type: String,
        default: '',
    },
    disabled: {
        type: Boolean,
        default: false,
    },
    required: {
        type: Boolean,
        default: false,
    },
    id: {
        type: String,
        default: () => `textarea-${uid()}`,
    },
});

defineEmits(['update:modelValue']);
</script> 