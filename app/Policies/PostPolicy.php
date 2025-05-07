<?php

namespace App\Policies;

use App\Models\Post;
use App\Models\User;
use Illuminate\Auth\Access\HandlesAuthorization;

class PostPolicy
{
    use HandlesAuthorization;

    /**
     * Determine whether the user can view the post.
     *
     * @param User $user
     * @param Post $post
     * @return bool
     */
    public function view(User $user, Post $post): bool
    {
        // Admin can view any post
        if ($user->isAdmin()) {
            return true;
        }
        
        // Editors can view their own posts or published posts
        if ($user->isEditor()) {
            return $post->user_id === $user->id || $post->isPublished();
        }
        
        // Regular users can only view published posts
        return $post->isPublished();
    }

    /**
     * Determine whether the user can create posts.
     *
     * @param User $user
     * @return bool
     */
    public function create(User $user): bool
    {
        // Only admins and editors can create posts
        return $user->isAdmin() || $user->isEditor();
    }

    /**
     * Determine whether the user can update the post.
     *
     * @param User $user
     * @param Post $post
     * @return bool
     */
    public function update(User $user, Post $post): bool
    {
        // Admin can update any post
        if ($user->isAdmin()) {
            return true;
        }
        
        // Editors can only update their own posts that are not published
        if ($user->isEditor()) {
            return $post->user_id === $user->id && $post->status !== 'published';
        }
        
        return false;
    }

    /**
     * Determine whether the user can delete the post.
     *
     * @param User $user
     * @param Post $post
     * @return bool
     */
    public function delete(User $user, Post $post): bool
    {
        // Admin can delete any post
        if ($user->isAdmin()) {
            return true;
        }
        
        // Editors can only delete their own posts
        return $user->isEditor() && $post->user_id === $user->id;
    }

    /**
     * Determine whether the user can restore the post.
     *
     * @param User $user
     * @param Post $post
     * @return bool
     */
    public function restore(User $user, Post $post): bool
    {
        // Only admins can restore posts
        return $user->isAdmin();
    }

    /**
     * Determine whether the user can permanently delete the post.
     *
     * @param User $user
     * @param Post $post
     * @return bool
     */
    public function forceDelete(User $user, Post $post): bool
    {
        // Only admins can force delete posts
        return $user->isAdmin();
    }
    
    /**
     * Determine whether the user can publish the post.
     *
     * @param User $user
     * @param Post $post
     * @return bool
     */
    public function publish(User $user, Post $post): bool
    {
        // Only Admin can publish directly
        if ($user->isAdmin()) {
            return true;
        }
        
        // Editors cannot publish directly, they must submit for review
        return false;
    }

    /**
     * Determine whether the user can submit the post for review.
     *
     * @param User $user
     * @param Post $post
     * @return bool
     */
    public function submitForReview(User $user, Post $post): bool
    {
        // Editors can only submit their own posts for review
        if ($user->isEditor()) {
            return $post->user_id === $user->id && $post->status !== 'published';
        }
        
        return false;
    }
} 