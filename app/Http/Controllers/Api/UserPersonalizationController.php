<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Resources\PostResource;
use App\Http\Resources\TagResource;
use App\Models\Post;
use App\Models\Tag;
use App\Models\UserRead;
use App\Models\UserTopic;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Cache;

class UserPersonalizationController extends Controller
{
    /**
     * Get the user's recently read articles.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function getRecentlyRead(Request $request)
    {
        $limit = $request->limit ?? 5;
        $user = $request->user();

        // Get recently read posts with eager loading
        $recentlyRead = $user->recentlyReadPosts()
            ->with(['author', 'category'])
            ->take($limit)
            ->get();

        return response()->json([
            'data' => PostResource::collection($recentlyRead),
        ]);
    }

    /**
     * Record a post as read by the current user.
     *
     * @param Request $request
     * @param Post $post
     * @return \Illuminate\Http\JsonResponse
     */
    public function recordRead(Request $request, Post $post)
    {
        $validated = $request->validate([
            'progress' => 'nullable|integer|between:0,100',
        ]);

        $progress = $validated['progress'] ?? 100;
        $post->recordRead($request->user(), $progress);

        return response()->json([
            'message' => 'Read status recorded successfully',
        ]);
    }

    /**
     * Get the topics followed by the user.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function getFollowedTopics(Request $request)
    {
        $user = $request->user();
        $topics = $user->followedTopics()->get();

        return response()->json([
            'data' => TagResource::collection($topics),
        ]);
    }

    /**
     * Follow or unfollow a topic.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function toggleFollowTopic(Request $request)
    {
        $validated = $request->validate([
            'tagId' => 'required|exists:tags,id',
            'follow' => 'required|boolean',
        ]);

        $user = $request->user();
        $tag = Tag::findOrFail($validated['tagId']);

        if ($validated['follow']) {
            // Follow the topic
            $user->followedTopics()->syncWithoutDetaching([$tag->id]);
            $message = "You are now following '{$tag->name}'";
        } else {
            // Unfollow the topic
            $user->followedTopics()->detach($tag->id);
            $message = "You have unfollowed '{$tag->name}'";
        }

        // Clear any cache related to topics
        Cache::forget("user_{$user->id}_topics");

        return response()->json([
            'message' => $message,
            'isFollowing' => (bool) $validated['follow'],
            'topic' => new TagResource($tag),
        ]);
    }

    /**
     * Get suggested topics for the user.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function getSuggestedTopics(Request $request)
    {
        $limit = $request->limit ?? 10;
        $user = $request->user();
        
        // Get IDs of topics the user already follows
        $followedTopicIds = $user->followedTopics()->pluck('tags.id')->toArray();
        
        // Get popular topics that the user isn't following yet
        $suggestedTopics = Tag::whereNotIn('id', $followedTopicIds)
            ->withCount('posts')
            ->orderByDesc('posts_count')
            ->take($limit)
            ->get();
            
        return response()->json([
            'data' => TagResource::collection($suggestedTopics),
        ]);
    }
} 