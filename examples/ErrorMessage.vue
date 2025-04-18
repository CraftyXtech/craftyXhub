<template>
  <div class="my-6">
    <h2 class="text-xl font-semibold mb-4">Products</h2>
    
    <!-- Loading indicator while products are being fetched -->
    <LoadingIndicator v-if="loading.products" text="Loading products..." />
    
    <!-- Error message with retry functionality -->
    <ErrorMessage 
      v-if="errors.products" 
      :message="errors.products" 
      :showRetry="true"
      @retry="loadProducts" 
    />
    
    <!-- Product list (only shown when not loading and no errors) -->
    <div v-if="!loading.products && !errors.products" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div v-for="product in products" :key="product.id"
        class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
        <h3 class="font-medium">{{ product.name }}</h3>
        <p class="text-gray-600 dark:text-gray-400">{{ product.price }}</p>
      </div>
      
      <p v-if="products.length === 0" class="text-gray-500 col-span-3 text-center py-4">
        No products available.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import LoadingIndicator from '@/Components/LoadingIndicator.vue';
import ErrorMessage from '@/Components/ErrorMessage.vue';
import axios from 'axios';

const products = ref([]);
const loading = ref({ products: false });
const errors = ref({ products: null });

// Function to load products
const loadProducts = async () => {
  loading.value.products = true;
  errors.value.products = null;
  
  try {
    // Replace with your actual API endpoint
    const response = await axios.get('/api/products');
    products.value = response.data.products;
  } catch (error) {
    console.error('Failed to load products:', error);
    errors.value.products = 'Failed to load products. Please try again.';
  } finally {
    loading.value.products = false;
  }
};

// Load products when component is mounted
onMounted(() => {
  loadProducts();
});
</script> 