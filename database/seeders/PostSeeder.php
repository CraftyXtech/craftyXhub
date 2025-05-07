<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Str;
use App\Models\Post;
use App\Models\User;
use App\Models\Category;
use App\Models\Tag;
use Carbon\Carbon;

class PostSeeder extends Seeder
{
    public function run(): void
    {
        // Get all editors
        $editors = User::where('role', 'editor')->get();
        
        if ($editors->isEmpty()) {
            $this->command->error('No editors found. Please run UserRoleSeeder first.');
            return;
        }
        
        // Get admin for approval content
        $admin = User::where('role', 'admin')->first();
        
        // Get categories and tags
        $categories = Category::all();
        if ($categories->isEmpty()) {
            $this->command->error('No categories found. Please run CategorySeeder first.');
            return;
        }
        
        $tags = Tag::all();
        if ($tags->isEmpty()) {
            $this->command->error('No tags found. Please run TagSeeder first.');
            return;
        }

        // Create published posts for each editor
        foreach ($editors as $editor) {
            // Between 3-8 published posts per editor
            $publishedCount = rand(3, 8);
            for ($i = 1; $i <= $publishedCount; $i++) {
                $title = "Published Post " . $i . " by " . $editor->name;
                
                // Use fillable attributes only to avoid issues with columns like 'embedding'
                $post = new Post([
                    'user_id' => $editor->id,
                    'category_id' => $categories->random()->id,
                    'title' => $title,
                    'slug' => Str::slug($title),
                    'excerpt' => 'This is a short excerpt for a published post.',
                    'body' => '<p>This is the full body content of the published post. It contains detailed information.</p><p>It has multiple paragraphs and might include some formatting.</p>',
                    'published_at' => Carbon::now()->subDays(rand(1, 30)),
                    'status' => 'published',
                    'featured' => (rand(1, 10) <= 2), // 20% chance to be featured
                    'comments_enabled' => true,
                ]);
                
                // Save without triggering model events that might use the embedding column
                $post->saveQuietly();
                
                // Attach 1-3 random tags - using sync instead of attach to avoid duplicates
                $randomTagIds = $tags->random(rand(1, 3))->pluck('id')->toArray();
                $post->tags()->sync($randomTagIds);
            }
            
            // Create 1-3 draft posts per editor
            $draftCount = rand(1, 3);
            for ($i = 1; $i <= $draftCount; $i++) {
                $title = "Draft Post " . $i . " by " . $editor->name;
                
                // Use new Post instead of create to avoid embedding column issue
                $post = new Post([
                    'user_id' => $editor->id,
                    'category_id' => $categories->random()->id,
                    'title' => $title,
                    'slug' => Str::slug($title),
                    'excerpt' => 'This is a draft post that is still being worked on.',
                    'body' => '<p>This draft post is not complete yet.</p><p>The editor is still working on the content.</p>',
                    'published_at' => null,
                    'status' => 'draft',
                    'featured' => false,
                    'comments_enabled' => false,
                ]);
                
                // Save without triggering model events
                $post->saveQuietly();
                
                // Attach 1-2 random tags - using sync instead of attach to avoid duplicates
                $randomTagIds = $tags->random(rand(1, 2))->pluck('id')->toArray();
                $post->tags()->sync($randomTagIds);
            }
            
            // Create 1-2 posts under review (pending approval) per editor
            $pendingCount = rand(1, 2);
            for ($i = 1; $i <= $pendingCount; $i++) {
                $title = "Review Pending Post " . $i . " by " . $editor->name;
                
                // Use new Post instead of create to avoid embedding column issue
                $post = new Post([
                    'user_id' => $editor->id,
                    'category_id' => $categories->random()->id,
                    'title' => $title,
                    'slug' => Str::slug($title),
                    'excerpt' => 'This post has been submitted for review and approval.',
                    'body' => '<p>This post needs to be reviewed by an admin before it can be published.</p><p>It contains content that might need approval.</p>',
                    'published_at' => null,
                    'status' => 'under_review',
                    'featured' => false,
                    'comments_enabled' => true,
                ]);
                
                // Save without triggering model events
                $post->saveQuietly();
                
                // Attach 1-3 random tags - using sync instead of attach to avoid duplicates
                $randomTagIds = $tags->random(rand(1, 3))->pluck('id')->toArray();
                $post->tags()->sync($randomTagIds);
            }
        }
        
        // Create related posts (for testing the related posts feature)
        // Get some published posts to create relationships between them
        $publishedPosts = Post::where('status', 'published')->get();
        
        // For the first 5 posts, make sure they have related posts (same category and tags)
        for ($i = 0; $i < 5 && $i < $publishedPosts->count(); $i++) {
            $sourcePost = $publishedPosts[$i];
            $category = $sourcePost->category;
            
            // Create 2 related posts in the same category
            for ($j = 1; $j <= 2; $j++) {
                $title = "Related Post " . $j . " to " . Str::limit($sourcePost->title, 20);
                
                // Use new Post instead of create to avoid embedding column issue
                $relatedPost = new Post([
                    'user_id' => $editors->random()->id,
                    'category_id' => $category->id, // Same category as source post
                    'title' => $title,
                    'slug' => Str::slug($title),
                    'excerpt' => 'This post is related to another post by sharing the same category.',
                    'body' => '<p>This is a related post that shares the same category as another post.</p><p>It is used to test the related posts feature.</p>',
                    'published_at' => Carbon::now()->subDays(rand(1, 20)),
                    'status' => 'published',
                    'featured' => false,
                    'comments_enabled' => true,
                ]);
                
                // Save without triggering model events
                $relatedPost->saveQuietly();
                
                // Share some tags with the source post to strengthen the relationship
                if ($sourcePost->tags->isNotEmpty()) {
                    // Get some tags from the source post
                    $sourceTagIds = $sourcePost->tags->random(min(2, $sourcePost->tags->count()))->pluck('id')->toArray();
                    
                    // Get one more random tag that's not in the source tags
                    $otherTagIds = $tags->whereNotIn('id', $sourceTagIds)->random(1)->pluck('id')->toArray();
                    
                    // Combine and ensure uniqueness
                    $tagIdsToAttach = array_unique(array_merge($sourceTagIds, $otherTagIds));
                    
                    // Use sync instead of attach to avoid duplicates
                    $relatedPost->tags()->sync($tagIdsToAttach);
                } else {
                    // Just attach random tags if the source post has no tags
                    $randomTagIds = $tags->random(rand(1, 3))->pluck('id')->toArray();
                    $relatedPost->tags()->sync($randomTagIds);
                }
            }
        }
    }
}
