<?php

namespace App\Http\Controllers\Editor;

use App\Http\Controllers\Controller;
use App\Models\Post;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Gate;
use App\Services\Editor\PostManagementService;
use Illuminate\Http\RedirectResponse;

class PostController extends Controller
{
    protected PostManagementService $postService;

    /**
     * Constructor with dependency injection
     *
     * @param PostManagementService $postService
     */
    public function __construct(PostManagementService $postService)
    {
        $this->postService = $postService;
    }

    /**
     * Display a listing of posts.
     *
     * @param Request $request
     * @return Response
     */
    public function index(Request $request): Response
    {
        $posts = $this->postService->getPosts($request);
        
        // Get form options for filters
        $formOptions = $this->postService->getPostFormOptions();

        return Inertia::render('Editor/Posts/Index', [
            'posts' => $posts,
            'filters' => [
                'search' => $request->search ?? '',
                'status' => $request->status ?? '',
                'category_id' => $request->category_id ?? null,
                'tag_id' => $request->tag_id ?? null,
                'sort_by' => $request->sort_by ?? 'created_at',
                'sort_direction' => $request->sort_direction ?? 'desc',
            ],
            'categories' => $formOptions['categories'],
            'tags' => $formOptions['tags'],
        ]);
    }

    /**
     * Show the form for creating a new post.
     *
     * @return Response
     */
    public function create(): Response
    {
        $formOptions = $this->postService->getPostFormOptions();
        
        return Inertia::render('Editor/Posts/Create', [
            'categories' => $formOptions['categories'],
            'tags' => $formOptions['tags'],
        ]);
    }

    /**
     * Store a newly created post in storage.
     *
     * @param Request $request
     * @return RedirectResponse
     */
    public function store(Request $request): RedirectResponse
    {
        // Validate the request
        $validated = $request->validate([
            'title' => 'required|string|max:255',
            'body' => 'required|string',
            'excerpt' => 'nullable|string|max:500',
            'featured_image_path' => 'nullable|string',
            'category_id' => 'nullable|exists:categories,id',
            'status' => 'required|in:draft,published,scheduled,under_review',
            'published_at' => 'nullable|date|required_if:status,scheduled',
            'tags' => 'nullable|array',
            'tags.*' => 'exists:tags,id',
            'comments_enabled' => 'boolean',
        ]);

        // Create the post
        $post = $this->postService->createPost($validated);

        return redirect()->route('editor.posts.edit', $post)
            ->with('success', 'Post created successfully!');
    }

    /**
     * Display the specified post.
     *
     * @param Post $post
     * @return Response
     */
    public function show(Post $post): Response
    {
        // Authorize the request (only post owner or admin can view)
        if (Gate::denies('view', $post)) {
            abort(403, 'Unauthorized action.');
        }
        
        // Load relationships
        $post->load(['category:id,name', 'tags:id,name', 'author:id,name']);

        return Inertia::render('Editor/Posts/Show', [
            'post' => $post,
        ]);
    }

    /**
     * Show the form for editing the specified post.
     *
     * @param Post $post
     * @return Response
     */
    public function edit(Post $post): Response
    {
        // Authorize the request (only post owner or admin can edit)
        if (Gate::denies('update', $post)) {
            abort(403, 'Unauthorized action.');
        }
        
        // Load relationships
        $post->load(['category:id,name', 'tags:id,name']);
        
        // Get form options
        $formOptions = $this->postService->getPostFormOptions();

        return Inertia::render('Editor/Posts/Edit', [
            'post' => $post,
            'categories' => $formOptions['categories'],
            'tags' => $formOptions['tags'],
            'selectedTags' => $post->tags->pluck('id')->toArray(),
        ]);
    }

    /**
     * Update the specified post in storage.
     *
     * @param Request $request
     * @param Post $post
     * @return RedirectResponse
     */
    public function update(Request $request, Post $post): RedirectResponse
    {
        // Authorize the request (only post owner or admin can update)
        if (Gate::denies('update', $post)) {
            abort(403, 'Unauthorized action.');
        }

        // Validate the request
        $validated = $request->validate([
            'title' => 'required|string|max:255',
            'body' => 'required|string',
            'excerpt' => 'nullable|string|max:500',
            'featured_image_path' => 'nullable|string',
            'category_id' => 'nullable|exists:categories,id',
            'status' => 'required|in:draft,published,scheduled,under_review',
            'published_at' => 'nullable|date|required_if:status,scheduled',
            'tags' => 'nullable|array',
            'tags.*' => 'exists:tags,id',
            'comments_enabled' => 'boolean',
        ]);

        // Update the post
        $this->postService->updatePost($post, $validated);

        return redirect()->route('editor.posts.edit', $post)
            ->with('success', 'Post updated successfully!');
    }

    /**
     * Remove the specified post from storage.
     *
     * @param Post $post
     * @return RedirectResponse
     */
    public function destroy(Post $post): RedirectResponse
    {
        // Authorize the request (only post owner or admin can delete)
        if (Gate::denies('delete', $post)) {
            abort(403, 'Unauthorized action.');
        }
        
        $this->postService->deletePost($post);

        return redirect()->route('editor.posts.index')
            ->with('success', 'Post deleted successfully!');
    }

    /**
     * Apply a bulk action to multiple posts.
     *
     * @param Request $request
     * @return RedirectResponse
     */
    public function bulkAction(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'action' => 'required|string|in:delete,publish,draft,review,reject', // Add other valid actions
            'ids'    => 'required|array',
            'ids.*'  => 'integer|exists:posts,id',
        ]);

        $action = $validated['action'];
        $postIds = $validated['ids'];

        // Ensure user can update/delete these posts (maybe check ownership or admin role)
        $posts = Post::whereIn('id', $postIds)->where('user_id', Auth::id())->get(); // Basic ownership check
        // More robust check using Gates:
        // $posts = Post::findMany($postIds);
        // foreach ($posts as $post) {
        //     if (Gate::denies('update', $post) && $action !== 'delete') {
        //         abort(403, 'Unauthorized action on some posts.');
        //     }
        //     if (Gate::denies('delete', $post) && $action === 'delete') {
        //         abort(403, 'Unauthorized action on some posts.');
        //     }
        // }

        if ($posts->isEmpty() && count($postIds) > 0) {
            return redirect()->back()->with('error', 'Could not perform action on specified posts. Check permissions.');
        }

        $actualIds = $posts->pluck('id')->all(); // Get IDs the user is authorized for

        // Delegate the actual action to the service
        $message = $this->postService->applyBulkAction($action, $actualIds);

        return redirect()->route('editor.posts.index')->with('success', $message ?? 'Bulk action applied successfully.');
    }
} 