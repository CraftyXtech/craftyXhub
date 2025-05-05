<template>
  <component
    :is="as === 'button' ? 'button' : Link"
    :href="as === 'button' ? undefined : href"
    :disabled="disabled"
    class="block w-full px-4 py-2 text-left text-sm transition-colors duration-200 ease-in-out"
    :class="{
      'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:bg-gray-100 dark:focus:bg-gray-700': !active && !disabled,
      'text-gray-400 dark:text-gray-500 cursor-not-allowed': disabled,
      'bg-gray-100 dark:bg-gray-700 text-primary-600 dark:text-primary-400': active,
    }"
    :aria-disabled="disabled ? 'true' : undefined"
  >
    <slot />
  </component>
</template>

<script setup>
import { Link } from '@inertiajs/vue3';

defineProps({
  href: {
    type: String,
    required: true,
  },
  active: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  as: {
    type: String,
    default: 'link',
    validator: (value) => ['link', 'button'].includes(value),
  },
});
</script>