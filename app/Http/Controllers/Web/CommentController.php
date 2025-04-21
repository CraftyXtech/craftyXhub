<?php

namespace App\Http\Controllers\Web;

use App\Http\Controllers\Controller;
use App\Models\Post;
use Illuminate\Http\Request;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Auth;

class CommentController extends Controller
{
    /**
     * Store a newly created comment in storage.
     */
    public function store(Request $request, Post $post): RedirectResponse
    {
        // Ensure user is authenticated (already handled by middleware, but good practice)
        if (!Auth::check()) {
            // This shouldn't be reached if middleware is applied correctly
            return redirect()->route('login');
        }

        // Validate the request data
        $validated = $request->validate([
            'body' => 'required|string|max:2500', // Adjust max length as needed
            'parent_id' => 'nullable|integer|exists:comments,id', // Validate parent comment ID if replying
        ]);

        // Create the comment
        $comment = $post->comments()->create([
            'user_id' => Auth::id(), // Use the authenticated user's ID
            'body' => $validated['body'],
            'parent_id' => $validated['parent_id'] ?? null,
            // Add any other necessary fields, e.g., status if comments need approval
            // 'status' => 'pending', 
        ]);

        // Optional: Dispatch events/notifications (e.g., notify post author)
        // event(new CommentPosted($comment));

        // Redirect back to the post page with a success message
        // Inertia will automatically pick up the flashed message
        return redirect()->back()->with('success', 'Comment submitted successfully!');
    }
} 