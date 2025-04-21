<?php

namespace App\Http\Controllers\Web;

use App\Http\Controllers\Controller;
use App\Models\Post;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Support\Facades\Auth;

class PostController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request): Response
    {
        $query = Post::query()
            ->whereNotNull('published_at')
            ->with(['author:id,name', 'category:id,name,slug'])
            ->latest('published_at');

        if ($request->filled('query')) {
            $searchTerm = $request->input('query');
            $query->where(function ($q) use ($searchTerm) {
                $q->where('title', 'like', "%{$searchTerm}%")
                  ->orWhere('body', 'like', "%{$searchTerm}%");
            });
        }

        if ($request->filled('category')) {
            $query->whereHas('category', function ($q) use ($request) {
                $q->where('slug', $request->input('category'));
            });
        }

        $posts = $query->paginate(10)->withQueryString();

        $userSpecificProps = [];
        if (Auth::check()) {
            $user = Auth::user();
            $userSpecificProps = [
                // Load recently read, followed topics, suggested topics here if needed for HomeView
                // 'recentlyRead' => $user->recentlyReadPosts()->limit(3)->get(),
                // 'followedTopics' => $user->followedTopics()->limit(5)->get(),
                // 'suggestedTopics' => ..., // Add logic for suggested topics
            ];
        }

        return Inertia::render('Blog/HomeView', [
            'posts' => $posts,
            'filters' => $request->only(['query', 'category']),
            ...$userSpecificProps
        ]);
    }

    /**
     * Display the specified resource.
     */
    public function show(Request $request, Post $post): Response
    {
        // Ensure the post is published
        if ($post->published_at === null) { // Add any other status checks if needed
            abort(404);
        }

        // Eager load necessary relationships
        $post->load([
            'author:id,name,avatar', 
            'category:id,name,slug', 
            'tags:id,name,slug', 
            // Load top-level comments with their user and replies (also with user)
            'comments' => function ($query) {
                $query->whereNull('parent_id') // Only top-level comments
                      ->with(['user:id,name,avatar', 'replies' => function($q) {
                          $q->with('user:id,name,avatar') // Load user for replies
                            ->orderBy('created_at', 'asc'); 
                      }])
                      ->orderBy('created_at', 'desc'); // Order top-level comments
            }
        ]);

        // Optional: Record post view for the current user (consider throttling/queuing)
        // You might want a dedicated service or event listener for this
        // Example: RecordViewJob::dispatch($post, $request->user());

        // Get like/save status for the currently authenticated user
        $user = $request->user();
        $isLiked = false;
        $isSaved = false;
        if ($user) {
            // Assuming standard pivot table relationships (likers, savers/bookmarks)
            $isLiked = $post->likers()->where('user_id', $user->id)->exists();
            $isSaved = $user->bookmarkedPosts()->where('post_id', $post->id)->exists(); // Adjust relation name if needed
        }
        
        // Pass the post and related data as props
        return Inertia::render('Blog/BlogPostView', [
            'post' => $post, 
            // Pass comments directly (adjust structure/resource if needed)
            'commentsProp' => $post->comments, 
            'isLikedProp' => $isLiked,
            'isSavedProp' => $isSaved,
        ]);
    }
} 