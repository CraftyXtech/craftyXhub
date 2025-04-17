<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use Carbon\Carbon;
use App\Http\Resources\TagResource;
use Illuminate\Support\Facades\Auth;
use App\Models\User;

class PostResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        // Calculate reading time (simple example)
        $wordsPerMinute = 200;
        $wordCount = str_word_count(strip_tags($this->body));
        $readingTime = ceil($wordCount / $wordsPerMinute);

        return [
            'id' => $this->id,
            'title' => $this->title,
            'slug' => $this->slug,
            'excerpt' => $this->excerpt,
            'body' => $this->body, // Include full body for single post view
            'content' => $this->when($request->routeIs('posts.show'), function () { // Conditional load for full content structure (adjust as needed)
                // Attempt to mimic the frontend structure if possible, or just send raw body
                // This example assumes body contains structured data or needs parsing.
                // A better approach might be dedicated fields or JSON column in DB.
                 return [
                    'introduction' => $this->excerpt, // Use excerpt as intro for now
                    'sections' => [ ['title' => 'Main Content', 'content' => strip_tags($this->body)] ], // Basic structure
                    'conclusion' => '' // Add conclusion if available
                 ];
            }),
            'imageUrl' => $this->image_url, // Adjust if using storage/accessors
            'category' => $this->whenLoaded('category', fn() => [
                'name' => $this->category->name,
                'slug' => $this->category->slug,
            ]),
            'author' => $this->whenLoaded('author', fn() => $this->author->name),
            'published_at' => $this->published_at ? Carbon::parse($this->published_at)->isoFormat('MMM D, YYYY') : null,
            'date' => $this->published_at ? Carbon::parse($this->published_at)->isoFormat('YYYY-MM-DD') : null, // For sorting/consistency
            'readTime' => $readingTime . ' min',
            'difficulty_level' => $this->difficulty_level,
            // Add tags if needed
             'tags' => $this->whenLoaded('tags', fn() => TagResource::collection($this->tags)),
            // Add interaction status for the *authenticated* user if available
            'is_liked' => $this->when(Auth::check(), function () {
                /** @var User $user */
                $user = Auth::user();
                return $user->likes()->where('post_id', $this->id)->exists();
            }, false), // Default to false if not logged in
            'is_saved' => $this->when(Auth::check(), function () {
                 /** @var User $user */
                $user = Auth::user();
                 return $user->savedPosts()->where('post_id', $this->id)->exists();
            }, false), // Default to false if not logged in
             'like_count' => $this->whenCounted('likers', $this->likers()->count()), // Get like count efficiently if possible
            // Add comment count if needed
            // 'comment_count' => $this->whenCounted('comments'), 
            'created_at' => $this->created_at,
            'updated_at' => $this->updated_at,
        ];
    }
}
