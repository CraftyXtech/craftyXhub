<?php

namespace App\Http\Controllers\Web;

use App\Http\Controllers\Controller;
use App\Models\Category;
use App\Models\Post;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Support\Facades\Auth;

class PostController extends Controller
{
 
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

        $posts = $query->paginate(9)->withQueryString();
        $categories = Category::withCount(['posts' => function ($query) {
            $query->whereNotNull('published_at');
        }])->get();
        
        $allCount = Post::whereNotNull('published_at')->count();
        
        $categories->prepend((object)[
            'id' => null,
            'name' => 'All',
            'slug' => 'all',
            'posts_count' => $allCount
        ]);
        

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
            'categories' => $categories,
            'filters' => $request->only(['query', 'category']),
            ...$userSpecificProps
        ]);
    }


    public function show(Request $request, Post $post): Response
    {
        if ($post->published_at === null) { 
            abort(404);
        }

        $post->load([
            'author:id,name,avatar', 
            'category:id,name,slug', 
            'tags:id,name,slug', 
            'comments' => function ($query) {
                $query->whereNull('parent_id') 
                      ->with(['user:id,name,avatar', 'replies' => function($q) {
                          $q->with('user:id,name,avatar')
                            ->orderBy('created_at', 'asc'); 
                      }])
                      ->orderBy('created_at', 'desc'); 
            }
        ]);

        $relatedPosts = $post->getRelatedPosts();

        $user = $request->user();
        $isLiked = false;
        $isSaved = false;
        if ($user) {
            $isLiked = $post->likers()->where('user_id', $user->id)->exists();
            $isSaved = $user->bookmarkedPosts()->where('post_id', $post->id)->exists(); 
        }
        
        return Inertia::render('Blog/BlogPostView', [
            'post' => $post, 
            'commentsProp' => $post->comments, 
            'isLikedProp' => $isLiked,
            'isSavedProp' => $isSaved,
            'relatedPosts' => $relatedPosts,
        ]);
    }
} 