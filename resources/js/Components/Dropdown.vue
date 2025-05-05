
<template>
    <div class="relative inline-block">
      <div 
        @click.stop="open = !open" 
        :class="triggerClasses"
        class="cursor-pointer"
      >
        <slot name="trigger" />
      </div>
  
      <Transition
        enter-active-class="transition duration-100 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-75 ease-in"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
      >
        <div
          v-show="open"
          class="absolute z-50 mt-2 rounded-md shadow-lg"
          :class="[widthClass, alignmentClasses]"
          @click.stop
        >
          <div
            class="rounded-md  dark:ring-gray-700 shadow-lg"
            :class="contentClasses"
          >
            <slot name="content" @click="closeDropdown" />
          </div>
        </div>
      </Transition>
  
      <div
        v-show="open"
        class="fixed inset-0 z-40 bg-black bg-opacity-10"
        @click="closeDropdown"
      />
    </div>
  </template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';

const props = defineProps({
  align: {
    type: String,
    default: 'right',
    validator: (value) => ['left', 'right', 'center'].includes(value),
  },
  width: {
    type: String,
    default: '48',
  },
  contentClasses: {
    type: String,
    default: 'py-1 bg-white dark:bg-gray-800',
  },
  triggerClasses: {
    type: String,
    default: '',
  },
});

const open = ref(false);

const closeOnEscape = (e) => {
  if (open.value && e.key === 'Escape') {
    open.value = false;
  }
};

onMounted(() => document.addEventListener('keydown', closeOnEscape));
onUnmounted(() => document.removeEventListener('keydown', closeOnEscape));

const widthClass = computed(() => {
  return {
    '48': 'w-48',
    '56': 'w-56',
    '64': 'w-64',
  }[props.width.toString()] || 'w-48';
});

const alignmentClasses = computed(() => {
  if (props.align === 'left') {
    return 'ltr:origin-top-left rtl:origin-top-right start-0';
  }
  if (props.align === 'right') {
    return 'ltr:origin-top-right rtl:origin-top-left end-0';
  }
  return 'origin-top';
});

const closeDropdown = () => {
  open.value = false;
};
</script>
