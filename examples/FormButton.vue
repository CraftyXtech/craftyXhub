<template>
  <div class="space-y-8 p-6 bg-gray-50 dark:bg-gray-900 rounded-lg">
    <h2 class="text-xl font-semibold">Form Button Examples</h2>
    
    <!-- Variants -->
    <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
      <h3 class="text-sm font-medium mb-4">Button Variants</h3>
      <div class="flex flex-wrap gap-4">
        <FormButton>Default Button</FormButton>
        <FormButton variant="primary">Primary Button</FormButton>
        <FormButton variant="secondary">Secondary Button</FormButton>
        <FormButton variant="success">Success Button</FormButton>
        <FormButton variant="danger">Danger Button</FormButton>
        <FormButton variant="warning">Warning Button</FormButton>
        <FormButton variant="info">Info Button</FormButton>
      </div>
    </div>
    
    <!-- Sizes -->
    <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
      <h3 class="text-sm font-medium mb-4">Button Sizes</h3>
      <div class="flex flex-wrap gap-4 items-center">
        <FormButton size="xs" variant="primary">Extra Small</FormButton>
        <FormButton size="sm" variant="primary">Small</FormButton>
        <FormButton size="md" variant="primary">Medium (Default)</FormButton>
        <FormButton size="lg" variant="primary">Large</FormButton>
        <FormButton size="xl" variant="primary">Extra Large</FormButton>
      </div>
    </div>
    
    <!-- States -->
    <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
      <h3 class="text-sm font-medium mb-4">Button States</h3>
      <div class="flex flex-wrap gap-4">
        <FormButton variant="primary">Normal</FormButton>
        <FormButton variant="primary" disabled>Disabled</FormButton>
        <FormButton variant="primary" :loading="true">Loading</FormButton>
        <FormButton variant="primary" :loading="true" loadingText="Submitting...">With Loading Text</FormButton>
      </div>
    </div>
    
    <!-- Icons -->
    <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
      <h3 class="text-sm font-medium mb-4">Buttons with Icons</h3>
      <div class="flex flex-wrap gap-4">
        <FormButton variant="primary" leftIcon="search">Search</FormButton>
        <FormButton variant="success" rightIcon="check">Submit</FormButton>
        <FormButton variant="danger" leftIcon="trash" rightIcon="arrow-right">Delete All</FormButton>
        <FormButton variant="secondary" iconOnly icon="settings"></FormButton>
      </div>
    </div>
    
    <!-- Full Width -->
    <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
      <h3 class="text-sm font-medium mb-4">Full Width Button</h3>
      <FormButton variant="primary" fullWidth>Full Width Button</FormButton>
    </div>
    
    <!-- Interactive Example -->
    <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
      <h3 class="text-sm font-medium mb-4">Interactive Form Example</h3>
      
      <form @submit.prevent="handleSubmit" class="max-w-md">
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1">Username</label>
          <input 
            v-model="username"
            type="text" 
            class="w-full px-4 py-2 border rounded-md"
            :disabled="isSubmitting"
          />
        </div>
        
        <div class="flex gap-4">
          <FormButton 
            type="button" 
            variant="secondary"
            :disabled="isSubmitting"
            @click="resetForm"
          >
            Reset
          </FormButton>
          
          <FormButton 
            type="submit" 
            variant="primary"
            :loading="isSubmitting"
            loadingText="Submitting..."
          >
            Submit Form
          </FormButton>
        </div>
        
        <div v-if="submitMessage" class="mt-4 p-3 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100 rounded">
          {{ submitMessage }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import FormButton from '@/Components/FormButton.vue';

const username = ref('');
const isSubmitting = ref(false);
const submitMessage = ref('');

const handleSubmit = () => {
  if (!username.value) return;
  
  isSubmitting.value = true;
  submitMessage.value = '';
  
  // Simulate API call
  setTimeout(() => {
    submitMessage.value = `Form submitted successfully for user: ${username.value}`;
    isSubmitting.value = false;
  }, 2000);
};

const resetForm = () => {
  username.value = '';
  submitMessage.value = '';
};
</script> 