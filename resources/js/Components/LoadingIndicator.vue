<script setup>
defineProps({
    size: {
        type: String,
        default: 'md', // sm, md, lg
    },
    color: {
        type: String,
        default: 'primary', // primary, secondary, white
    },
});
</script>

<template>
    <div class="flex justify-center items-center">
        <div 
            class="animate-spin rounded-full border-t-2 border-b-2"
            :class="{
                'w-4 h-4': size === 'sm',
                'w-8 h-8': size === 'md',
                'w-12 h-12': size === 'lg',
                'border-primary': color === 'primary',
                'border-secondary': color === 'secondary',
                'border-white': color === 'white',
            }"
        ></div>
    </div>
</template> 