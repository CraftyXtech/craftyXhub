<template>
    <section class="relative overflow-hidden bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 text-white py-16 text-center">      
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="inline-block mb-6 animate-bounce-subtle">
          <div class="bg-blue-800 text-white px-4 py-1 rounded-full font-bold text-sm flex items-center gap-2 shadow-lg border border-gray-400">
            <span class="inline-block animate-pulse">●</span>
            <span>24K+ Creative Minds</span>
            <span class="inline-block animate-pulse">●</span>
          </div>
        </div>
        
        <h2 class="text-3xl md:text-4xl font-bold mb-4 flex flex-col md:flex-row items-center justify-center gap-2">
          <span class="inline-block animate-reveal-text">Join Our Creative Community</span>
          <span class="inline-block transform rotate-12 animate-wiggle text-blue-300">✦</span>
        </h2>
        
        <p class="max-w-lg mx-auto text-lg opacity-90 mb-8 leading-relaxed">
          Unlock <span class="font-bold text-blue-300">exclusive tutorials</span>, discover <span class="font-bold text-blue-300">trending crafts</span>, and connect with fellow artisans. Your next masterpiece begins with inspiration in your inbox!
        </p>
        
        <form @submit.prevent="handleSubmit" class="relative max-w-lg mx-auto">
          <div class="flex flex-col sm:flex-row justify-center items-center gap-3">
            <div class="relative w-full">
              <input 
                v-model="email" 
                type="email" 
                placeholder="Your creative email address..." 
                required 
                class="w-full px-6 py-4 rounded-full text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all duration-300 shadow-lg"
              >
            </div>
            
            <button 
              type="submit" 
              class="w-full sm:w-auto px-8 py-4 rounded-full font-bold transition-all duration-300 shadow-lg bg-blue-700 hover:bg-blue-600 text-white transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-300"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting" class="flex items-center justify-center gap-2">
                <span class="animate-spin">⚙️</span> 
                <span>Joining...</span>
              </span>
              <span v-else class="flex items-center justify-center gap-2">
                <span>Get Inspired</span> 
                <span class="animate-bounce-subtle">→</span>
              </span>
            </button>
          </div>
          
          <transition name="fade">
            <div v-if="subscribeSuccess" class="absolute -bottom-12 left-0 right-0 mt-4 text-center">
              <div class="inline-flex items-center gap-2 bg-blue-800 text-white px-4 py-2 rounded-full animate-pulse shadow-lg">
                <span>✓</span>
                <span>You're in! Creative inspiration coming your way!</span>
              </div>
            </div>
          </transition>
        </form>
        
        <!-- Social proof -->
        <div class="mt-12 flex flex-wrap justify-center gap-4 items-center opacity-90">
          <div class="flex -space-x-2">
            <div class="w-8 h-8 rounded-full bg-gray-700 border-2 border-white flex items-center justify-center text-xs">A</div>
            <div class="w-8 h-8 rounded-full bg-gray-600 border-2 border-white flex items-center justify-center text-xs">B</div>
            <div class="w-8 h-8 rounded-full bg-blue-700 border-2 border-white flex items-center justify-center text-xs">C</div>
            <div class="w-8 h-8 rounded-full bg-blue-800 border-2 border-white flex items-center justify-center text-xs">D</div>
            <div class="w-8 h-8 rounded-full bg-gray-800 border-2 border-white flex items-center justify-center text-xs">+</div>
          </div>
          <p class="text-sm"><span class="font-bold">4.9/5</span> average from <span class="font-bold">2,400+</span> creative reviews</p>
        </div>
      </div>
    </section>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const email = ref('');
  const isSubmitting = ref(false);
  const subscribeSuccess = ref(false);
  
  const handleSubmit = () => {
    isSubmitting.value = true;
    
    setTimeout(() => {
      isSubmitting.value = false;
      subscribeSuccess.value = true;
      email.value = '';
      
      setTimeout(() => {
        subscribeSuccess.value = false;
      }, 3000);
    }, 1000);
  };
  </script>
  
  <style scoped>
  @keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
  }
  
  @keyframes wiggle {
    0%, 100% { transform: rotate(12deg); }
    50% { transform: rotate(-12deg); }
  }
  
  @keyframes bounce-subtle {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
  }
  
  @keyframes reveal-text {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
  }
  
  .animate-float-slow {
    animation: float 8s ease-in-out infinite;
  }
  
  .animate-float-medium {
    animation: float 6s ease-in-out infinite;
  }
  
  .animate-float-fast {
    animation: float 4s ease-in-out infinite;
  }
  
  .animate-wiggle {
    animation: wiggle 2s ease-in-out infinite;
  }
  
  .animate-bounce-subtle {
    animation: bounce-subtle 2s ease-in-out infinite;
  }
  
  .animate-reveal-text {
    animation: reveal-text 1s ease-out forwards;
  }
  
  .craft-icon {
    position: absolute;
    font-size: 6rem;
    opacity: 0.1;
  }
  
  .fade-enter-active, .fade-leave-active {
    transition: opacity 0.5s;
  }
  .fade-enter-from, .fade-leave-to {
    opacity: 0;
  }
  </style>