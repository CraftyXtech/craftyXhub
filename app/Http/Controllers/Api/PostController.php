<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Post;
use App\Models\Category;
use Illuminate\Http\Request;
use App\Http\Resources\PostResource;
use App\Models\View;
use Illuminate\Support\Facades\Auth;

class PostController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $query = Post::query()
            ->with(['author:id,name', 'category:id,name,slug', 'tags:id,name,slug']) // Eager load relationships
            ->where('status', 'published') // Only show published posts
            ->whereNotNull('published_at')
            ->orderBy('published_at', 'desc');

        // Filtering by Category
        if ($request->has('category')) {
            $categorySlug = $request->input('category');
            $query->whereHas('category', function ($q) use ($categorySlug) {
                $q->where('slug', $categorySlug);
            });
        }

        // Filtering by Search Query
        if ($request->has('search')) {
            $search = $request->input('search');
            $query->where(function ($q) use ($search) {
                $q->where('title', 'like', "%{$search}%")
                  ->orWhere('excerpt', 'like', "%{$search}%")
                  ->orWhereHas('tags', function ($tagQuery) use ($search) {
                      $tagQuery->where('name', 'like', "%{$search}%");
                  })
                  ->orWhereHas('category', function ($catQuery) use ($search) {
                        $catQuery->where('name', 'like', "%{$search}%");
                    });
                  // Maybe search body too? ->orWhere('body', 'like', "%{$search}%")
            });
        }

        // Pagination
        $posts = $query->paginate(9); // Adjust page size as needed

        return PostResource::collection($posts);
    }

    /**
     * Display the specified resource.
     */
    public function show(Post $post, Request $request)
    {
        // Ensure the post is published
        if ($post->status !== 'published' || is_null($post->published_at)) {
            abort(404);
        }

        // --- Log the view ---
        // Avoid logging views for the post author or multiple times in quick succession if desired (optional complexity)
        // For now, just log every valid view access
        View::create([
            'post_id' => $post->id,
            'user_id' => Auth::id(), // Will be null if user is not authenticated
            'ip_address' => $request->ip(),
            'user_agent' => $request->userAgent(),
            'viewed_at' => now(),
        ]);
        // --- End log view ---

        // Eager load necessary relationships for the single post view
        $post->load(['author:id,name', 'category:id,name,slug', 'tags:id,name,slug'])
             ->loadCount('likers'); // Load like count efficiently

        // TODO: Load related posts logic
        
        // Note: We don't need to explicitly load the user's like/save status here,
        // as the PostResource handles checking the authenticated user directly.

        return new PostResource($post);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }
}
