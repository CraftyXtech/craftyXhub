<script setup>
import { ref } from 'vue';

defineProps({
    tableOfContents: {
        type: Array,
        default: () => []
    },
    postTitle: {
        type: String,
        required: true
    }
});

const email = ref('');
const isSubmitting = ref(false);
const subscribeSuccess = ref(false);

const handleSubscribe = () => {
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
    <aside>
        <!-- Social Share Widget -->
        <div class="bg-primary text-white p-6 rounded-lg mb-8">
            <h4 class="text-lg font-medium mb-4 pb-2 border-b border-white/30">
                Share with your community!
            </h4>
            
            <div class="flex justify-around items-center">
                <a href="#" aria-label="Share on Facebook" class="w-10 h-10 flex items-center justify-center rounded-full bg-white/20 text-white hover:bg-white/40">
                    <i class="fab fa-facebook-f"></i>
                </a>
                <a href="#" aria-label="Share on Twitter" class="w-10 h-10 flex items-center justify-center rounded-full bg-white/20 text-white hover:bg-white/40">
                    <i class="fab fa-twitter"></i>
                </a>
                <a href="#" aria-label="Share on LinkedIn" class="w-10 h-10 flex items-center justify-center rounded-full bg-white/20 text-white hover:bg-white/40">
                    <i class="fab fa-linkedin-in"></i>
                </a>
                <a href="#" aria-label="Share on Pinterest" class="w-10 h-10 flex items-center justify-center rounded-full bg-white/20 text-white hover:bg-white/40">
                    <i class="fab fa-pinterest-p"></i>
                </a>
                <a href="#" aria-label="Share on WhatsApp" class="w-10 h-10 flex items-center justify-center rounded-full bg-white/20 text-white hover:bg-white/40">
                    <i class="fab fa-whatsapp"></i>
                </a>
                <a href="#" aria-label="Copy link" class="w-10 h-10 flex items-center justify-center rounded-full bg-white/20 text-white hover:bg-white/40">
                    <i class="fas fa-link"></i>
                </a>
            </div>
        </div>
        
        <!-- Table of Contents Widget -->
        <div v-if="tableOfContents.length > 0" class="border border-gray-200 bg-gray-50 p-6 rounded-lg mb-8">
            <h4 class="text-lg font-medium mb-4 pb-2 border-b border-gray-200">
                In this article
            </h4>
            
            <ul>
                <li v-for="(item, index) in tableOfContents" :key="index" class="mb-2">
                    <a 
                        :href="`#section-${index + 1}`" 
                        class="block py-2 text-gray-700 hover:text-primary border-b border-dashed border-gray-200 last:border-0"
                    >
                        {{ item }}
                    </a>
                </li>
            </ul>
        </div>
        
        <!-- Newsletter Widget -->
        <div class="border border-gray-200 bg-white p-6 rounded-lg">
            <h4 class="text-lg font-medium mb-4 pb-2 border-b border-gray-200">
                Newsletter
            </h4>
            
            <p class="text-sm text-gray-500 mb-4">
                Subscribe to our newsletter for the latest crafting updates, tutorials, and marketplace trends.
            </p>
            
            <form @submit.prevent="handleSubscribe">
                <label for="sidebar-email" class="block font-medium text-sm mb-2">
                    Email
                </label>
                
                <input 
                    v-model="email"
                    type="email" 
                    id="sidebar-email" 
                    placeholder="Enter your email" 
                    required
                    class="w-full p-2 border border-gray-200 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
                >
                
                <button 
                    type="submit" 
                    :disabled="isSubmitting"
                    class="w-full py-2 bg-primary text-white rounded font-medium hover:bg-primary-dark transition"
                >
                    {{ isSubmitting ? 'Subscribing...' : 'Subscribe' }}
                </button>
                
                <p v-if="subscribeSuccess" class="mt-2 text-green-600 text-sm">
                    Success! You're now subscribed to our newsletter.
                </p>
            </form>
        </div>
    </aside>
</template> 