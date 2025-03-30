<script setup>
import { ref, onMounted, computed } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import TheHeader from '@/Components/Layout/TheHeader.vue';
import TheFooter from '@/Components/Layout/TheFooter.vue';
import BlogPostCard from '@/Components/Blog/BlogPostCard.vue';
import BlogSidebar from '@/Components/Blog/BlogSidebar.vue';
import SubscribeBanner from '@/Components/Shared/SubscribeBanner.vue';

const props = defineProps({
    slug: {
        type: String,
        required: true
    }
});

// Mock blog post data - in real app, this would be fetched from API
const post = ref({
    id: 1,
    title: 'Essential Tips for Handmade Craft Success',
    subtitle: 'Elevate your crafting journey with these proven strategies',
    slug: 'essential-tips-for-handmade-craft-success',
    date: '2024-02-15',
    author: 'Sarah Johnson',
    category: 'Crafts',
    tags: ['Handmade', 'Business', 'Tips'],
    imageUrl: 'https://via.placeholder.com/1200x600/6A0572/FFFFFF?text=Crafting+Success',
    content: {
        introduction: 'Crafting isn\'t just a hobby—it\'s a passion that can transform into a thriving business with the right approach. Whether you\'re just starting your crafting journey or looking to take your established handmade business to the next level, these essential tips will help you succeed in the competitive world of handmade crafts.',
        sections: [
            {
                title: 'Perfect Your Craft Technique',
                content: 'The foundation of any successful craft business is mastery of your chosen technique. Dedicate time to practice, take classes, and continually improve your skills. Customers can recognize quality craftsmanship and are willing to pay premium prices for well-executed handmade items. Document your process and create a consistent workflow to ensure each piece meets your high standards.'
            },
            {
                title: 'Develop a Unique Style',
                content: 'In a crowded marketplace, a distinctive style helps your crafts stand out. Experiment with different techniques, materials, and aesthetics until you find a signature look that represents your artistic vision. Your unique style becomes your brand identity, making your creations instantly recognizable to customers and fostering loyalty among repeat buyers.'
            },
            {
                title: 'Source Quality Materials',
                content: 'The materials you use directly impact the quality and durability of your finished products. Research suppliers, request samples, and test materials before committing to large purchases. Building relationships with reliable suppliers ensures consistent quality and can sometimes lead to better pricing. Consider sustainable and ethically sourced materials, as today\'s consumers increasingly value environmental responsibility.'
            },
            {
                title: 'Price Your Work Appropriately',
                content: 'Calculating the right price for handmade items is challenging but crucial. Consider all costs: materials, labor (value your time appropriately!), overhead expenses, packaging, and shipping. Research market prices for similar items, but don\'t undervalue your work. Remember that handmade items command premium prices because they offer uniqueness and quality that mass-produced goods cannot match.'
            },
            {
                title: 'Create Professional Product Photos',
                content: 'In online selling, your photos are your storefront. Invest in good lighting, learn basic photography skills, and create a consistent visual style for your product images. Clear, well-lit photos from multiple angles show details and craftsmanship. Lifestyle photos help customers envision your products in use. Consider the background, props, and overall aesthetic to ensure your photos enhance your brand image.'
            },
            {
                title: 'Build an Online Presence',
                content: 'A strong online presence is essential for reaching customers beyond your local area. Create accounts on platforms like Instagram, Pinterest, and TikTok to showcase your work process and finished products. Establish a website or shop on marketplaces like Etsy, Amazon Handmade, or CraftyXhub. Regular posting, engaging with followers, and using relevant hashtags help build your audience and drive traffic to your shop.'
            },
            {
                title: 'Cultivate Customer Relationships',
                content: 'Building relationships with customers creates brand loyalty and generates word-of-mouth referrals. Respond promptly to inquiries, include personal notes with orders, and follow up after purchases. Consider starting an email newsletter to keep customers informed about new products and special offers. Excellent customer service, including clear policies for returns and custom orders, builds trust and enhances your reputation.'
            },
            {
                title: 'Network with Fellow Artisans',
                content: 'Connecting with other crafters provides opportunities for collaboration, knowledge sharing, and mutual support. Join craft groups, attend workshops, and participate in forums to expand your network. Collaborative projects and cross-promotion with complementary craft businesses can introduce your work to new audiences. The crafting community is generally supportive and can provide valuable advice on navigating the challenges of a handmade business.'
            }
        ],
        conclusion: 'Success in the handmade craft world requires a blend of artistic skill, business acumen, and marketing savvy. By focusing on quality craftsmanship, developing your unique style, and building strong relationships with both customers and fellow artisans, you can create a sustainable and fulfilling craft business. Remember that building a successful handcraft enterprise takes time—celebrate small victories and stay committed to continuous improvement in both your craft and business practices.'
    },
    relatedPosts: [
        {
            id: 2,
            title: 'Photography Tips for Craft Product Listings',
            slug: 'photography-tips-for-craft-product-listings',
            excerpt: 'Learn how to take professional-quality photos of your handmade items to increase sales and attract more customers to your online shop.',
            category: 'Technology',
            categoryId: 1,
            readTime: '6 min',
            imageUrl: 'https://via.placeholder.com/800x600/FF6B6B/FFFFFF?text=Craft+Photography',
            date: '2023-12-10'
        },
        {
            id: 3,
            title: 'Setting Up Your Home Craft Studio',
            slug: 'setting-up-your-home-craft-studio',
            excerpt: 'Transform any space into an efficient and inspiring craft studio with these organization tips and essential equipment recommendations.',
            category: 'DIY',
            categoryId: 3,
            readTime: '7 min',
            imageUrl: 'https://via.placeholder.com/800x600/4ECDC4/FFFFFF?text=Craft+Studio',
            date: '2024-01-15'
        },
        {
            id: 4,
            title: 'Marketing Strategies for Handmade Businesses',
            slug: 'marketing-strategies-for-handmade-businesses',
            excerpt: 'Discover effective marketing tactics specifically designed for handmade and craft businesses to increase your visibility and boost sales.',
            category: 'Business',
            categoryId: 8,
            readTime: '9 min',
            imageUrl: 'https://via.placeholder.com/800x600/1D3557/FFFFFF?text=Craft+Marketing',
            date: '2024-02-05'
        }
    ]
});

// Table of contents for the sidebar
const tableOfContents = computed(() => {
    return post.value.content.sections.map(section => section.title);
});

const isLoading = ref(true);

onMounted(() => {
    // Simulate loading the post data from an API
    setTimeout(() => {
        isLoading.value = false;
        
        // Scroll to section if there's a hash in the URL
        if (window.location.hash) {
            const targetId = window.location.hash.substring(1);
            const element = document.getElementById(targetId);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }, 500);
});
</script>

<template>
    <Head :title="`${post.title} - CraftyXhub`" />
    
    <TheHeader />
    
    <main>
        <div v-if="isLoading" class="flex justify-center items-center py-32">
            <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-primary"></div>
        </div>
        
        <template v-else>
            <!-- Article Header -->
            <section class="py-12 text-center">
                <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
                    <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
                        {{ post.title }}
                    </h1>
                    
                    <p class="text-xl text-gray-600 max-w-3xl mx-auto mb-6">
                        {{ post.subtitle }}
                    </p>
                    
                    <div class="flex justify-center items-center gap-4 text-sm text-gray-500">
                        <span class="bg-primary text-white px-3 py-1 rounded-md">{{ post.category }}</span>
                        <span class="bg-gray-800 text-white px-3 py-1 rounded-md">{{ post.author }}</span>
                        <span>Published {{ post.date }}</span>
                    </div>
                </div>
            </section>
            
            <!-- Featured Image -->
            <img 
                :src="post.imageUrl" 
                :alt="post.title" 
                class="w-full max-h-[500px] object-cover mb-12"
            >
            
            <!-- Article Content -->
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex flex-col lg:flex-row gap-12 mt-12">
                    <article class="flex-1 min-w-0">
                        <!-- Introduction -->
                        <p class="text-lg leading-relaxed mb-8 text-gray-800">
                            {{ post.content.introduction }}
                        </p>
                        
                        <!-- Numbered Sections -->
                        <ol class="mb-12">
                            <li 
                                v-for="(section, index) in post.content.sections" 
                                :key="index"
                                class="mb-12"
                                :id="`section-${index + 1}`"
                            >
                                <h2 class="text-2xl font-semibold mb-4 text-gray-900">
                                    <span class="text-primary font-bold mr-2">{{ index + 1 }}.</span>
                                    {{ section.title }}
                                </h2>
                                <p class="leading-relaxed text-gray-700">
                                    {{ section.content }}
                                </p>
                            </li>
                        </ol>
                        
                        <!-- Conclusion -->
                        <div class="border-t border-gray-200 pt-8 mt-12 italic text-gray-600">
                            <p class="mb-2">
                                <strong class="font-semibold text-gray-800 not-italic">Summary</strong>
                            </p>
                            <p>{{ post.content.conclusion }} ✈️</p>
                        </div>
                    </article>
                    
                    <!-- Sidebar -->
                    <div class="lg:w-80 flex-shrink-0">
                        <div class="sticky top-8">
                            <BlogSidebar 
                                :table-of-contents="tableOfContents" 
                                :post-title="post.title" 
                            />
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Related Articles Section -->
            <section class="py-16 mt-12 border-t border-gray-200">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <h2 class="text-3xl font-bold text-center mb-12">Related Articles</h2>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <BlogPostCard 
                            v-for="relatedPost in post.relatedPosts" 
                            :key="relatedPost.id" 
                            :post="relatedPost" 
                        />
                    </div>
                </div>
            </section>
            
            <SubscribeBanner />
        </template>
    </main>
    
    <TheFooter />
</template> 