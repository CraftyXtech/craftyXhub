<script setup>
import { ref } from 'vue';

const email = ref('');
const isSubmitting = ref(false);
const subscribeSuccess = ref(false);

const handleSubmit = () => {
    isSubmitting.value = true;
    
    // Simulate API call
    setTimeout(() => {
        isSubmitting.value = false;
        subscribeSuccess.value = true;
        email.value = '';
        
        // Reset success message after 3 seconds
        setTimeout(() => {
            subscribeSuccess.value = false;
        }, 3000);
    }, 1000);
};
</script>

<template>
    <section class="bg-primary text-white py-12 text-center">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-2xl md:text-3xl font-semibold mb-2 flex items-center justify-center gap-2">
                <span>Join 24K+ Artisans!</span>
                <span>🚀</span> <!-- Placeholder for icon -->
            </h2>
            
            <p class="max-w-lg mx-auto opacity-90 mb-8">
                Stay inspired with the latest crafting trends, tutorials, and marketplace updates. 
                Subscribe today and never miss a creative opportunity!
            </p>
            
            <form @submit.prevent="handleSubmit" class="flex flex-col sm:flex-row justify-center items-center max-w-lg mx-auto gap-2">
                <input 
                    v-model="email"
                    type="email" 
                    placeholder="Enter your email" 
                    required
                    class="flex-grow w-full sm:w-auto px-4 py-3 rounded-full text-gray-800 focus:outline-none focus:ring-2 focus:ring-white"
                >
                <button 
                    type="submit" 
                    class="px-6 py-3 rounded-full border-2 border-white text-white font-medium bg-transparent hover:bg-white hover:text-primary transition w-full sm:w-auto"
                    :disabled="isSubmitting"
                >
                    {{ isSubmitting ? 'Subscribing...' : 'Subscribe Today' }}
                </button>
            </form>
            
            <p v-if="subscribeSuccess" class="mt-4 text-green-200 animate-pulse">
                Success! You're now subscribed to our newsletter.
            </p>
        </div>
    </section>
</template> 