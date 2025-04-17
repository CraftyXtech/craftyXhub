<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Post;
use App\Models\User;
use Illuminate\Support\Facades\Auth;

class InteractionController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
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

    /**
     * Toggle the like status for a post.
     */
    public function toggleLike(Request $request, Post $post)
    {
        /** @var User $user */
        $user = Auth::user();

        if (!$user) {
            return response()->json(['message' => 'Unauthenticated.'], 401);
        }

        $result = $user->likes()->toggle($post->id);

        $liked = count($result['attached']) > 0;
        $likeCount = $post->likers()->count(); // Recount after toggle

        return response()->json([
            'liked' => $liked,
            'count' => $likeCount
        ]);
    }

    /**
     * Toggle the save status for a post.
     */
    public function toggleSave(Request $request, Post $post)
    {
        /** @var User $user */
        $user = Auth::user();

        if (!$user) {
            return response()->json(['message' => 'Unauthenticated.'], 401);
        }

        $result = $user->savedPosts()->toggle($post->id);

        $saved = count($result['attached']) > 0;

        return response()->json(['saved' => $saved]);
    }
}
