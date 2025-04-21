<?php

namespace App\Http\Controllers\Web;

use App\Http\Controllers\Controller;
use App\Models\Post;
use Illuminate\Http\Request;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Auth;

class InteractionController extends Controller
{
    /**
     * Toggle the like status for a post for the authenticated user.
     */
    public function toggleLike(Request $request, Post $post): RedirectResponse
    {
        $user = Auth::user(); // Get authenticated user

        // Check if already liked
        $hasLiked = $post->likers()->where('user_id', $user->id)->exists();

        $message = '';
        if ($hasLiked) {
            // Unlike the post
            $post->likers()->detach($user->id);
            $message = 'Post unliked.';
        } else {
            // Like the post
            $post->likers()->attach($user->id);
            $message = 'Post liked.';
            // Optional: Dispatch notification event/job
            // event(new PostLiked($post, $user));
        }

        // Redirect back to the previous page with a status message
        // The like status prop in the view will be updated on the next render
        return redirect()->back()->with('status', $message);
    }

    /**
     * Toggle the save/bookmark status for a post for the authenticated user.
     * (Placeholder - to be implemented in the next step)
     */
    public function toggleSave(Request $request, Post $post): RedirectResponse
    { 
        // Logic will be added in the next step
        return redirect()->back()->with('status', 'Save functionality not yet implemented.');
    }
} 