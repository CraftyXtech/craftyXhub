<script setup>
import { ref } from 'vue';
import { useForm, usePage } from '@inertiajs/vue3';
import InputLabel from '@/Components/InputLabel.vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import Checkbox from '@/Components/Checkbox.vue';
import InputError from '@/Components/InputError.vue';

// Get current preferences from shared page props (assuming they are passed)
// If not passed to Edit.vue, fetch them here or adjust logic
const currentPreferences = usePage().props.auth.user?.preferences || {}; 
// Define all possible categories (this should ideally come from the backend)
const allCategories = ref([
    { id: 'technology', name: 'Technology' },
    { id: 'finance', name: 'Finance' },
    { id: 'health', name: 'Health' },
    { id: 'education', name: 'Education' },
    { id: 'sports', name: 'Sports' },
    { id: 'travel', name: 'Travel' },
    { id: 'lifestyle', name: 'Lifestyle' },
    { id: 'community', name: 'Community' }
]);

const form = useForm({
    newsletter_enabled: currentPreferences.newsletter_enabled ?? false,
    personalization_enabled: currentPreferences.personalization_enabled ?? false,
    preferred_categories: currentPreferences.preferred_categories ?? [],
});

const submitPreferences = () => {
    form.put(route('profile.preferences.update'), {
        preserveScroll: true,
        onSuccess: () => {
            // Optionally show a temporary success message
        },
        onError: (errors) => {
            console.error('Error updating preferences:', errors);
        }
    });
};
</script>

<template>
    <section>
        <header>
            <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">User Preferences</h2>
            <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                Update your content and notification preferences.
            </p>
        </header>

        <form @submit.prevent="submitPreferences" class="mt-6 space-y-6">
            <!-- Newsletter Preference -->
            <div class="flex items-center">
                <Checkbox id="newsletter" v-model:checked="form.newsletter_enabled" />
                <InputLabel for="newsletter" value="Subscribe to Newsletter" class="ml-2" />
            </div>
            <InputError :message="form.errors.newsletter_enabled" class="mt-1 ml-8" />

            <!-- Personalization Preference -->
            <div class="flex items-center">
                <Checkbox id="personalization" v-model:checked="form.personalization_enabled" />
                <InputLabel for="personalization" value="Enable Content Personalization" class="ml-2" />
            </div>
             <InputError :message="form.errors.personalization_enabled" class="mt-1 ml-8" />

            <!-- Preferred Categories -->
            <div>
                <InputLabel value="Preferred Content Categories" class="mb-2" />
                <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div v-for="category in allCategories" :key="category.id" class="flex items-center">
                        <Checkbox 
                            :id="'category-' + category.id"
                            :value="category.id" 
                            v-model:checked="form.preferred_categories"
                        />
                        <InputLabel :for="'category-' + category.id" :value="category.name" class="ml-2" />
                    </div>
                </div>
                 <InputError :message="form.errors.preferred_categories" class="mt-2" />
            </div>

            <!-- Save Button -->
            <div class="flex items-center gap-4">
                <PrimaryButton :disabled="form.processing">Save Preferences</PrimaryButton>

                <Transition
                    enter-active-class="transition ease-in-out"
                    enter-from-class="opacity-0"
                    leave-active-class="transition ease-in-out"
                    leave-to-class="opacity-0"
                >
                    <p v-if="form.recentlySuccessful" class="text-sm text-gray-600 dark:text-gray-300">Preferences Saved.</p>
                </Transition>
            </div>
        </form>
    </section>
</template> 