<template>
  <div v-if="links.length > 3" class="flex flex-wrap -mb-1">
    <template v-for="(link, key) in links" :key="key">
      <div
        v-if="link.url === null"
        class="mr-1 mb-1 px-4 py-3 text-sm leading-4 text-gray-400 border rounded"
        v-html="link.label"
      />
      <Link
        v-else
        class="mr-1 mb-1 px-4 py-3 text-sm leading-4 border rounded hover:bg-white focus:border-primary focus:text-primary dark:hover:bg-gray-700 dark:focus:border-primary-light dark:focus:text-primary-light"
        :class="{ 'bg-white dark:bg-gray-700': link.active }"
        :href="link.url"
        v-html="link.label"
        :preserve-state="true"
        :preserve-scroll="true"
      />
    </template>
  </div>
</template>

<script setup>
import { Link } from '@inertiajs/vue3';

defineProps({
  links: {
    type: Array,
    required: true
  }
});
</script> 