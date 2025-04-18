<?php

namespace Database\Seeders;

use App\Models\Category;
use App\Models\Post;
use App\Models\Tag;
use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Str;

class TestPostsSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Create categories
        $categories = [
            'Technology' => 'technology',
            'Finance' => 'finance',
            'Health' => 'health',
            'Education' => 'education',
            'Sports' => 'sports',
            'Travel' => 'travel',
            'Lifestyle' => 'lifestyle',
            'Community' => 'community',
        ];
        
        foreach ($categories as $name => $slug) {
            Category::firstOrCreate(
                ['slug' => $slug],
                [
                    'name' => $name,
                    'description' => "Articles about {$name}",
                ]
            );
        }
        
        // Create tags
        $tags = [
            'Programming' => 'programming',
            'Web Development' => 'web-development',
            'AI' => 'ai',
            'Machine Learning' => 'machine-learning',
            'Investing' => 'investing',
            'Personal Finance' => 'personal-finance',
            'Fitness' => 'fitness',
            'Mental Health' => 'mental-health',
            'Online Learning' => 'online-learning',
            'Basketball' => 'basketball',
            'Football' => 'football',
            'Destinations' => 'destinations',
            'Adventure' => 'adventure',
            'Cooking' => 'cooking',
            'Home Decor' => 'home-decor',
            'Local News' => 'local-news',
            'Events' => 'events',
        ];
        
        foreach ($tags as $name => $slug) {
            Tag::firstOrCreate(
                ['slug' => $slug],
                ['name' => $name]
            );
        }
        
        // Get editors for creating posts
        $editor = User::where('role', 'editor')->first();
        if (!$editor) {
            $this->command->error('No editor found. Please run TestUsersSeeder first.');
            return;
        }
        
        $allCategories = Category::all();
        $allTags = Tag::all();
        
        // Create 15 sample posts
        for ($i = 1; $i <= 15; $i++) {
            $title = "Sample Post {$i}: " . $this->getRandomTitle();
            $slug = Str::slug($title);
            
            $post = Post::firstOrCreate(
                ['slug' => $slug],
                [
                    'user_id' => $editor->id,
                    'category_id' => $allCategories->random()->id,
                    'title' => $title,
                    'excerpt' => "This is a sample excerpt for post {$i}. " . $this->getRandomSentence(),
                    'body' => $this->generateDummyContent(),
                    'published_at' => now()->subDays(rand(1, 30)),
                    'status' => 'published',
                    'difficulty_level' => ['beginner', 'intermediate', 'advanced'][rand(0, 2)],
                    'featured' => (rand(1, 10) > 8), // 20% chance of being featured
                    'comments_enabled' => true,
                ]
            );
            
            // Attach 2-4 random tags to each post
            $randomTags = $allTags->random(rand(2, 4));
            $post->tags()->sync($randomTags->pluck('id')->toArray());
        }
        
        $this->command->info('Test posts and tags seeded successfully!');
    }
    
    /**
     * Generate random title.
     */
    private function getRandomTitle(): string
    {
        $titles = [
            'The Ultimate Guide to Modern Tech',
            'How to Master Your Finances',
            'Top Health Tips Everyone Should Know',
            'Revolutionizing Education in 2025',
            'Sports Trends That Are Changing Everything',
            'Unexplored Travel Destinations',
            'Lifestyle Changes for Better Living',
            'Building Stronger Communities',
            'Understanding Blockchain Technology',
            'Sustainable Living Practices',
        ];
        
        return $titles[array_rand($titles)];
    }
    
    /**
     * Generate random sentence.
     */
    private function getRandomSentence(): string
    {
        $sentences = [
            'Discover the latest innovations in the field.',
            'Learn how experts are approaching this challenge.',
            'Find out why this matters more than ever.',
            'See how this is transforming our daily lives.',
            'Understand the impact on society and culture.',
            'Explore the possibilities for future developments.',
            'Get insights from leading professionals.',
            'Practical advice for implementing these ideas.',
        ];
        
        return $sentences[array_rand($sentences)];
    }
    
    /**
     * Generate dummy content for post body.
     */
    private function generateDummyContent(): string
    {
        $paragraphs = [];
        
        for ($i = 0; $i < rand(5, 10); $i++) {
            $sentences = [];
            $sentenceCount = rand(4, 8);
            
            for ($j = 0; $j < $sentenceCount; $j++) {
                $sentences[] = $this->getRandomSentence();
            }
            
            $paragraphs[] = implode(' ', $sentences);
        }
        
        return '<p>' . implode('</p><p>', $paragraphs) . '</p>';
    }
} 