<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Post;
use App\Models\User;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Support\Facades\Gate;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Log;

class AdminPostController extends Controller
{
    /**
     * Display a list of posts pending review/approval.
     *
     * @return Response
     */
    public function pendingApproval(): Response
    {
        // Get posts that are under review
        $pendingPosts = Post::where('status', 'under_review')
            ->with(['author:id,name,email', 'category:id,name'])
            ->orderBy('updated_at', 'desc')
            ->paginate(10);
        
        return Inertia::render('Admin/Posts/PendingApproval', [
            'pendingPosts' => $pendingPosts,
        ]);
    }
    
    /**
     * Show a specific post for review.
     *
     * @param Post $post
     * @return Response
     */
    public function reviewPost(Post $post): Response
    {
        // Load necessary relationships
        $post->load(['author:id,name,email', 'category:id,name', 'tags:id,name']);
        
        return Inertia::render('Admin/Posts/Review', [
            'post' => $post,
        ]);
    }
    
    /**
     * Approve a post that was submitted for review.
     *
     * @param Request $request
     * @param Post $post
     * @return RedirectResponse
     */
    public function approve(Request $request, Post $post): RedirectResponse
    {
        Log::info('AdminPostController: Reached approve method for post ID: ' . $post->id, $request->all());
        // Validate the request if needed
        $validated = $request->validate([
            'feedback' => 'nullable|string|max:1000',
        ]);
        
        // Update post status to published
        $post->status = 'published';
        $post->published_at = now();
        
        // Add admin feedback if provided
        if (!empty($validated['feedback'])) {
            $post->feedback = $validated['feedback'];
        }
        
        $post->save();
        
        return redirect()->route('admin.posts.pending')
            ->with('success', 'Post has been approved and published.');
    }
    
    /**
     * Reject a post that was submitted for review.
     *
     * @param Request $request
     * @param Post $post
     * @return RedirectResponse
     */
    public function rejectPost(Request $request, Post $post): RedirectResponse
    {
        Log::info('AdminPostController: Reached rejectPost method for post ID: ' . $post->id, $request->all());
        // Validate the request
        $validated = $request->validate([
            'feedback' => 'required|string|max:1000',
        ]);
        
        // Update post status to rejected
        $post->status = 'rejected';
        $post->feedback = $validated['feedback'];
        $post->save();
        
        return redirect()->route('admin.posts.pending')
            ->with('success', 'Post has been rejected with feedback.');
    }
    
    /**
     * Display all posts (admin view with more options).
     *
     * @param Request $request
     * @return Response
     */
    public function index(Request $request): Response
    {
        $query = Post::query()
            ->with(['author:id,name', 'category:id,name']);
        
        // Apply filters if provided
        if ($request->has('status') && $request->status !== 'all') {
            $query->where('status', $request->status);
        }
        
        if ($request->has('category_id') && $request->category_id) {
            $query->where('category_id', $request->category_id);
        }
        
        if ($request->has('author_id') && $request->author_id) {
            $query->where('user_id', $request->author_id);
        }
        
        // Order posts
        $query->orderBy('updated_at', 'desc');
        
        // Paginate results
        $posts = $query->paginate(15)
            ->appends($request->all());
        
        return Inertia::render('Admin/Posts/Index', [
            'posts' => $posts,
            'filters' => $request->only(['status', 'category_id', 'author_id']),
        ]);
    }

    /**
     * Display a list of posts that have been rejected.
     *
     * @return Response
     */
    public function rejectedPosts(): Response
    {
        // Get posts that have been rejected
        $rejectedPosts = Post::where('status', 'rejected')
            ->with(['author:id,name,email', 'category:id,name'])
            ->orderBy('updated_at', 'desc')
            ->paginate(10);
        
        return Inertia::render('Admin/Posts/RejectedPosts', [
            'rejectedPosts' => $rejectedPosts,
        ]);
    }
} 