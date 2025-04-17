<?php

namespace App\Services;

use App\Models\User;
use App\Models\Post;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB; // For potential complex queries

class RecommendationService
{
    /**
     * Get personalized post recommendations for a given user.
     *
     * @param User $user The user for whom to get recommendations.
     * @param int $limit The maximum number of recommendations to return.
     * @return Collection<Post> A collection of recommended posts.
     */
    public function getRecommendations(User $user, int $limit = 3): Collection
    {
        // 1. Get posts liked by the user
        $likedPostIds = $user->likes()->pluck('post_id');

        // 2. Get posts viewed by the user
        $viewedPostIds = $user->views()->distinct()->pluck('post_id'); // Use distinct for views

        // Combine liked and viewed IDs to exclude them later
        $interactedPostIds = $likedPostIds->merge($viewedPostIds)->unique();

        // --- Placeholder for Collaborative Filtering --- 
        // This is a complex part. We'll start with a simpler version 
        // based on common tags/categories of liked/viewed posts for now.
        // A full collaborative filtering implementation might involve:
        // - Finding users with similar like/view patterns.
        // - Getting posts those similar users interacted with but the current user hasn't.
        // This often requires more advanced techniques (e.g., matrix factorization) or dedicated packages.

        // Simple Approach: Find posts with similar tags/categories to liked/viewed posts
        $recommendedPostIds = collect(); // Initialize empty collection
        if ($interactedPostIds->isNotEmpty()) {
            $similarPosts = Post::query()
                ->wherePublished()
                ->whereNotIn('id', $interactedPostIds) // Exclude already interacted posts
                ->whereHas('tags', function ($query) use ($user) {
                    $query->whereIn('id', $user->likes()->with('post.tags')->get()->pluck('post.tags.*.id')->flatten()->unique());
                })
                // ->orWhereHas('category', function ($query) use ($user) { ... }) // Could add category similarity too
                ->select('posts.id') // Select only IDs for performance
                ->inRandomOrder() // Add some randomness
                ->limit($limit * 2) // Fetch a bit more initially
                ->pluck('id');
            
             $recommendedPostIds = $similarPosts;
        }

        // --- TODO: Implement actual Collaborative Filtering --- 
        // $collaborativePostIds = $this->getCollaborativeFilteringRecommendations($user, $interactedPostIds, $limit);
        // $recommendedPostIds = $recommendedPostIds->merge($collaborativePostIds)->unique();
        

        // If not enough recommendations yet, fill with popular posts (excluding interacted)
        if ($recommendedPostIds->count() < $limit) {
            $popularPostIds = Post::query()
                ->wherePublished()
                ->whereNotIn('id', $interactedPostIds->merge($recommendedPostIds)) // Exclude interacted and already recommended
                ->withCount('views') // Or likes, or a combination
                ->orderByDesc('views_count')
                ->limit($limit - $recommendedPostIds->count())
                ->pluck('id');
            
            $recommendedPostIds = $recommendedPostIds->merge($popularPostIds);
        }

        // Ensure we don't exceed the limit
        $finalPostIds = $recommendedPostIds->take($limit);

        // 4. Fetch the actual Post models
        if ($finalPostIds->isEmpty()) {
            return collect(); // Return empty collection if no recommendations found
        }

        // Fetch posts with necessary relations for display
        return Post::query()
            ->whereIn('id', $finalPostIds)
            ->with(['author:id,name', 'category:id,name,slug'])
            ->withCount('likers') // Example: include like count
            ->get()
            ->sortBy(function($post) use ($finalPostIds) {
                 // Preserve the order if needed, though current logic doesn't guarantee specific priority order yet
                 return array_search($post->id, $finalPostIds->toArray());
            });

    }

    // Placeholder for a potentially complex collaborative filtering method
    private function getCollaborativeFilteringRecommendations(User $user, Collection $excludePostIds, int $limit): Collection
    {
        // Complex Logic: 
        // 1. Find users similar to $user based on overlapping likes/views.
        // 2. Find posts liked/viewed by these similar users.
        // 3. Filter out posts in $excludePostIds.
        // 4. Rank and return top $limit post IDs.
        // Example (very basic concept - needs refinement):
        // $similarUsers = ... find users with >= N overlapping interactions ...
        // $recs = Post::whereHas('views', fn($q) => $q->whereIn('user_id', $similarUsers))
        //               ->whereNotIn('id', $excludePostIds)
        //               ... rank and limit ...
        return collect(); // Return empty for now
    }
} 