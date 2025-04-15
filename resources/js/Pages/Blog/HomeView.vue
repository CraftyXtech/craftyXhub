<script setup>
import { ref, onMounted } from 'vue';
import { Head } from '@inertiajs/vue3';
import TheHeader from '@/Components/Layout/TheHeader.vue';
import TheFooter from '@/Components/Layout/TheFooter.vue';
import BlogPostCard from '@/Components/Blog/BlogPostCard.vue';
import CategoryTags from '@/Components/Blog/CategoryTags.vue';
import SearchBar from '@/Components/Shared/SearchBar.vue';
import SubscribeBanner from '@/Components/Shared/SubscribeBanner.vue';

// Updated mock data for blog posts reflecting new categories
const allPosts = [
    {
        id: 1,
        title: 'The Future of AI in Web Development',
        slug: 'future-of-ai-in-web-development',
        excerpt: 'Explore how Artificial Intelligence is revolutionizing web development workflows, from code generation to automated testing.',
        category: 'Technology',
        categoryId: 1, // Corresponds to 'Technology' in CategoryTags
        readTime: '5 min',
        imageUrl: 'https://via.placeholder.com/800x600/118AB2/FFFFFF?text=AI+Web+Dev',
        date: '2024-07-15'
    },
    {
        id: 2,
        title: "Beginner's Guide to Stock Market Investing",
        slug: 'beginners-guide-stock-market-investing',
        excerpt: 'New to investing? This guide covers the basics of the stock market, how to choose stocks, and strategies for long-term growth.',
        category: 'Finance',
        categoryId: 2, // Corresponds to 'Finance'
        readTime: '7 min',
        imageUrl: 'https://via.placeholder.com/800x600/06D6A0/FFFFFF?text=Investing+101',
        date: '2024-07-10'
    },
    {
        id: 3,
        title: 'Meal Planning for a Healthier Lifestyle',
        slug: 'meal-planning-healthier-lifestyle',
        excerpt: 'Learn effective meal planning strategies to save time, reduce stress, and make healthier food choices throughout the week.',
        category: 'Health',
        categoryId: 3, // Corresponds to 'Health'
        readTime: '4 min',
        imageUrl: 'https://via.placeholder.com/800x600/FFD166/000000?text=Meal+Plan',
        date: '2024-07-05'
    },
    {
        id: 4,
        title: 'Top Online Courses for Learning Python',
        slug: 'top-online-courses-learning-python',
        excerpt: 'Discover the best online platforms and courses to master Python programming, whether you are a beginner or looking to advance your skills.',
        category: 'Education',
        categoryId: 4, // Corresponds to 'Education'
        readTime: '6 min',
        imageUrl: 'https://via.placeholder.com/800x600/F78764/FFFFFF?text=Python+Courses',
        date: '2024-06-28'
    },
    {
        id: 5,
        title: 'Effective Workout Routines for Busy People',
        slug: 'effective-workout-routines-busy-people',
        excerpt: 'Short on time? Find efficient and effective workout routines that you can fit into even the busiest schedules to stay active and fit.',
        category: 'Health',
        categoryId: 3, // Corresponds to 'Health'
        readTime: '5 min',
        imageUrl: 'https://via.placeholder.com/800x600/4ECDC4/FFFFFF?text=Quick+Workouts',
        date: '2024-06-20'
    },
    {
        id: 6,
        title: 'Budget Travel: Tips for Seeing the World Affordably',
        slug: 'budget-travel-tips-seeing-world-affordably',
        excerpt: 'Dreaming of travel but tight on budget? Learn practical tips and tricks for exploring new destinations without breaking the bank.',
        category: 'Travel',
        categoryId: 6, // Corresponds to 'Travel'
        readTime: '8 min',
        imageUrl: 'https://via.placeholder.com/800x600/6A0572/FFFFFF?text=Budget+Travel',
        date: '2024-06-15'
    },
    {
        id: 7,
        title: 'Introduction to Personal Finance Management',
        slug: 'introduction-personal-finance-management',
        excerpt: 'Take control of your finances with this beginner-friendly guide to budgeting, saving, and managing debt effectively.',
        category: 'Finance',
        categoryId: 2, // Corresponds to 'Finance'
        readTime: '6 min',
        imageUrl: 'https://via.placeholder.com/800x600/FF6B6B/FFFFFF?text=Personal+Finance',
        date: '2024-06-10'
    },
    {
        id: 8,
        title: 'Latest Trends in Mobile App Development',
        slug: 'latest-trends-mobile-app-development',
        excerpt: 'Stay ahead of the curve by learning about the newest trends shaping the mobile app development landscape in 2024 and beyond.',
        category: 'Technology',
        categoryId: 1, // Corresponds to 'Technology'
        readTime: '7 min',
        imageUrl: 'https://via.placeholder.com/800x600/073B4C/FFFFFF?text=Mobile+Trends',
        date: '2024-06-01'
    },
    {
        id: 9, 
        title: 'Training Regimen of Top Athletes',
        slug: 'training-regimen-top-athletes',
        excerpt: 'Get a glimpse into the demanding training schedules and techniques used by professional athletes across different sports.',
        category: 'Sports',
        categoryId: 5, // Corresponds to 'Sports'
        readTime: '6 min',
        imageUrl: 'https://via.placeholder.com/800x600/EF476F/FFFFFF?text=Athlete+Training',
        date: '2024-05-25'
    },
    {
        id: 10,
        title: 'Minimalist Living: Declutter Your Life',
        slug: 'minimalist-living-declutter-your-life',
        excerpt: 'Explore the principles of minimalism and how decluttering your physical and digital spaces can lead to a more focused life.',
        category: 'Lifestyle',
        categoryId: 7, // Corresponds to 'Lifestyle'
        readTime: '5 min',
        imageUrl: 'https://via.placeholder.com/800x600/06D6A0/FFFFFF?text=Minimalism',
        date: '2024-05-18'
    },
    {
        id: 11,
        title: 'Organizing Local Community Events Successfully',
        slug: 'organizing-local-community-events-successfully',
        excerpt: 'A step-by-step guide to planning and executing successful local community events, from securing venues to engaging volunteers.',
        category: 'Community',
        categoryId: 8, // Corresponds to 'Community'
        readTime: '7 min',
        imageUrl: 'https://via.placeholder.com/800x600/FFD166/000000?text=Community+Events',
        date: '2024-05-12'
    },
    {
        id: 12,
        title: 'Healthy Eating Habits for a Balanced Lifestyle',
        slug: 'healthy-eating-habits-balanced-lifestyle',
        excerpt: 'Learn how to cultivate sustainable healthy eating habits that nourish your body and support a balanced, energetic lifestyle.',
        category: 'Lifestyle', // Another Lifestyle example
        categoryId: 7, // Corresponds to 'Lifestyle'
        readTime: '4 min',
        imageUrl: 'https://via.placeholder.com/800x600/118AB2/FFFFFF?text=Healthy+Eating',
        date: '2024-05-05'
    }
];

// Reactive state
const displayedPosts = ref([...allPosts]);
const searchQuery = ref('');
const selectedCategory = ref(0); // Default: All
const isLoading = ref(false);

// Methods
const filterByCategory = (categoryId) => {
    selectedCategory.value = categoryId;
    applyFilters();
};

const handleSearch = (query) => {
    searchQuery.value = query;
    applyFilters();
};

const applyFilters = () => {
    isLoading.value = true;
    
    // Simulate API call/loading
    setTimeout(() => {
        // First filter by category (if not "All")
        let filtered = [...allPosts];
        
        if (selectedCategory.value !== 0) {
            // Find the category name based on the ID from the CategoryTags component
            const categoryMap = {
                1: 'Technology', 2: 'Finance', 3: 'Health', 4: 'Education',
                5: 'Sports', 6: 'Travel', 7: 'Lifestyle', 8: 'Community'
            };
            const categoryName = categoryMap[selectedCategory.value];
            if (categoryName) {
                 filtered = filtered.filter(post => post.category === categoryName);
            }
        }
        
        // Then filter by search query if present
        if (searchQuery.value) {
            const query = searchQuery.value.toLowerCase();
            filtered = filtered.filter(post => 
                post.title.toLowerCase().includes(query) || 
                post.excerpt.toLowerCase().includes(query) ||
                post.category.toLowerCase().includes(query)
            );
        }
        
        displayedPosts.value = filtered;
        isLoading.value = false;
    }, 300);
};

const loadMore = () => {
    // In a real app, this would load the next page of results
    // For this demo, we'll just simulate a loading state
    isLoading.value = true;
    
    setTimeout(() => {
        isLoading.value = false;
        // You might add more posts here in a real application
    }, 1000);
};

// Initialize
onMounted(() => {
    // Simulate initial data fetch
    isLoading.value = true;
    setTimeout(() => {
        isLoading.value = false;
    }, 300);
});
</script>

<template>
    <Head title="CraftyXhub - Discover, Create & Connect" />
    
    <TheHeader />
    
    <main>
        <!-- Hero Section -->
        <section class="py-12 border-b border-gray-200 mb-8">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                <p class="text-primary text-sm font-medium mb-2">
                    <!-- Updated Hero Text -->
                    Explore Ideas, Insights & Inspiration That Matter
                </p>
                
                <h1 class="text-3xl md:text-4xl font-bold mb-2 flex items-center justify-center gap-2">
                    <span>🚀</span> <!-- Placeholder for icon -->
                    <!-- Updated Hero Title -->
                    <span>Discover Knowledge & Connect</span>
                </h1>
                
                <p class="max-w-2xl mx-auto text-gray-600 mb-8">
                    <!-- Updated Hero Description -->
                    Join thousands exploring the latest trends, expert tips, and engaging stories across various fields. 
                    Find resources, share insights, and connect with like-minded individuals.
                </p>
                
                <CategoryTags @filter="filterByCategory" />
                
                <SearchBar @search="handleSearch" />
            </div>
        </section>
        
        <!-- Blog Grid Section -->
        <section class="py-8 mb-16">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <!-- Loading indicator -->
                <div v-if="isLoading" class="flex justify-center items-center py-12">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                </div>
                
                <!-- No results message -->
                <div v-else-if="displayedPosts.length === 0" class="text-center py-12">
                    <h3 class="text-xl font-medium text-gray-700 mb-2">No results found</h3>
                    <p class="text-gray-500">
                        Try adjusting your search or filter to find what you're looking for.
                    </p>
                </div>
                
                <!-- Posts grid -->
                <div 
                    v-else 
                    class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
                >
                    <BlogPostCard 
                        v-for="post in displayedPosts" 
                        :key="post.id" 
                        :post="post" 
                    />
                </div>
                
                <!-- Load more button -->
                <div class="text-center mt-12">
                    <button 
                        @click="loadMore" 
                        class="px-6 py-3 border border-gray-300 rounded-full text-gray-700 hover:bg-gray-50 inline-flex items-center"
                        :disabled="isLoading"
                    >
                        <span>Load More</span>
                        <span class="ml-1 text-xs">▼</span>
                    </button>
                </div>
            </div>
        </section>
        
        <SubscribeBanner />
    </main>
    
    <TheFooter />
</template> 