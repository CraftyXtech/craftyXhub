<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasOne;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;

    protected $fillable = [
        'name',
        'email',
        'password',
        'avatar',
        'bio',
        'role',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected $casts = [
        'email_verified_at' => 'datetime',
    ];

    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
    }

    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    public function media()
    {
        return $this->hasMany(Media::class);
    }

    public function bookmarks()
    {
        return $this->hasMany(Bookmark::class);
    }

    public function bookmarkedPosts()
    {
        return $this->belongsToMany(Post::class, 'bookmarks')->withTimestamps();
    }

    public function followers()
    {
        return $this->belongsToMany(User::class, 'follows', 'followed_id', 'follower_id')
                    ->withTimestamps();
    }

    public function following()
    {
        return $this->belongsToMany(User::class, 'follows', 'follower_id', 'followed_id')
                    ->withTimestamps();
    }

    public function likes(): BelongsToMany
    {
        return $this->belongsToMany(Post::class, 'likes', 'user_id', 'post_id')->withTimestamps();
    }

    public function likedPosts()
    {
        return $this->morphedByMany(Post::class, 'likeable', 'likes');
    }

    public function likedComments()
    {
        return $this->morphedByMany(Comment::class, 'likeable', 'likes');
    }

    public function isAdmin()
    {
        return $this->role === 'admin';
    }

    public function isEditor()
    {
        return $this->role === 'editor' || $this->role === 'admin';
    }

    public function isFollowing(User $user)
    {
        return $this->following()->where('followed_id', $user->id)->exists();
    }

    /**
     * The posts that the user has saved.
     */
    public function savedPosts(): BelongsToMany
    {
        return $this->belongsToMany(Post::class, 'saved_posts', 'user_id', 'post_id')->withTimestamps();
    }
    
    /**
     * Get the user's reading history.
     */
    public function recentlyRead(): HasMany
    {
        return $this->hasMany(UserRead::class);
    }
    
    /**
     * Get posts that the user has recently read.
     */
    public function recentlyReadPosts(): BelongsToMany
    {
        return $this->belongsToMany(Post::class, 'user_reads', 'user_id', 'post_id')
                    ->withPivot('read_at', 'read_progress')
                    ->orderByPivot('read_at', 'desc');
    }
    
    /**
     * Get the topics (tags) that the user follows.
     */
    public function followedTopics(): BelongsToMany
    {
        return $this->belongsToMany(Tag::class, 'user_topics', 'user_id', 'tag_id')
                    ->withTimestamps();
    }
    
    /**
     * Check if a user follows a specific topic.
     */
    public function isFollowingTopic(Tag $tag): bool
    {
        return $this->followedTopics()->where('tag_id', $tag->id)->exists();
    }

    // TODO: Add relationship for preferences later
    public function preference(): HasOne
    {
        return $this->hasOne(UserPreference::class);
    }
}
