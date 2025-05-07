<?php

namespace App\Models;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
// use Pgvector\Laravel\HasNeighbors;
// use Pgvector\Laravel\Vector;
use Illuminate\Support\Str;
use Carbon\Carbon;
use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Support\Facades\Storage;

class Post extends Model
{
    use HasFactory;
    // use HasNeighbors;

    protected $fillable = [
        'user_id',
        'category_id',
        'title',
        'slug',
        'excerpt',
        'body',
        'published_at',
        'difficulty_level',
        'status',
        'featured',
        'comments_enabled',
        'generated_image_path',
        'feedback',
    ];

    protected $casts = [
        'published_at' => 'datetime',
        'featured' => 'boolean',
        'comments_enabled' => 'boolean',
    ];

    /**
     * The accessors to append to the model's array form.
     *
     * @var array
     */
    protected $appends = ['published_at_human', 'display_image_url', 'url'];

    /**
     * Get the author of the post.
     */
    public function author(): BelongsTo
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    /**
     * Get the category of the post.
     */
    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    /**
     * Get the top-level comments for the blog post.
     */
    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class)->whereNull('parent_id')->orderBy('created_at', 'desc');
    }

    /**
     * Get all comments (including replies).
     */
    public function allComments(): HasMany
    {
        return $this->hasMany(Comment::class)->orderBy('created_at', 'desc');
    }

    /**
     * The tags that belong to the post.
     */
    public function tags(): BelongsToMany
    {
        return $this->belongsToMany(Tag::class);
    }

    /**
     * Get the views for the blog post.
     */
    public function views(): HasMany
    {
        return $this->hasMany(View::class);
    }

    /**
     * Users who liked the post (uses the 'likes' table).
     */
    public function likers(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'likes');
    }

    /**
     * Users who saved/bookmarked the post (uses the 'bookmarks' table).
     */
    public function savers(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'bookmarks');
    }

    /**
     * Check if the post is liked by a specific user.
     */
    public function isLikedBy(?User $user): bool
    {
        if (!$user) {
            return false;
        }
        return $this->likers()->where('user_id', $user->id)->exists();
    }

    /**
     * Check if the post is saved by a specific user.
     */
    public function isSavedBy(?User $user): bool
    {
        if (!$user) {
            return false;
        }
        return $this->savers()->where('user_id', $user->id)->exists();
    }

    /**
     * Users who have recently read this post.
     */
    public function readers(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'user_reads', 'post_id', 'user_id')
                    ->withPivot('read_at', 'read_progress')
                    ->orderByPivot('read_at', 'desc');
    }

    /**
     * Record a read event for a user.
     */
    public function recordRead(User $user, int $progress = 100): void
    {
        $this->readers()->syncWithoutDetaching([
            $user->id => [
                'read_at' => now(),
                'read_progress' => $progress,
            ]
        ]);
    }

    public function getRouteKeyName()
    {
        return 'slug';
    }

    public function scopeWherePublished($query)
    {
        $query->where('status', 'published')
              ->whereNotNull('published_at')
              ->where('published_at', '<=', now());
    }

    public function scopeFeatured($query)
    {
        return $query->where('featured', true);
    }

    public function isPublished()
    {
        return $this->status === 'published' && 
               $this->published_at !== null && 
               $this->published_at <= now();
    }

    /**
     * Get the published_at attribute in a human-readable format.
     *
     * @return \Illuminate\Database\Eloquent\Casts\Attribute
     */
    protected function publishedAtHuman(): Attribute
    {
        return Attribute::make(
            get: fn ($value, $attributes) => isset($attributes['published_at']) 
                ? Carbon::parse($attributes['published_at'])->diffForHumans()
                : null,
        );
    }

    /**
     * Get the URL for the image to display (prioritizes generated, falls back to featured).
     *
     * @return \Illuminate\Database\Eloquent\Casts\Attribute
     */
    protected function displayImageUrl(): Attribute
    {
        return Attribute::make(
            get: function ($value, $attributes) {
                if (!empty($attributes['generated_image_path']) && Storage::disk('public')->exists($attributes['generated_image_path'])) {
                    return asset('storage/' . $attributes['generated_image_path']);
                } elseif (!empty($attributes['featured_image_path'])) {
                    // Assuming featured_image_path might already be a full URL or relative to public path
                    // If it's stored in storage/app/public like generated ones:
                    // if (Storage::disk('public')->exists($attributes['featured_image_path'])) {
                    //     return Storage::disk('public')->url($attributes['featured_image_path']);
                    // }
                    // If it's a path relative to the public directory (e.g., stored directly in public/images):
                     return asset($attributes['featured_image_path']); 
                     // Or if it's already a full URL:
                    // return $attributes['featured_image_path'];
                }
                return asset('images/placeholder.jpg'); // Return a placeholder image
            }
        );
    }

    /**
     * Automatically generate slug from title if not provided.
     */
    protected static function boot()
    {
        parent::boot();

        static::creating(function ($post) {
            if (empty($post->slug)) {
                $post->slug = Str::slug($post->title);
                // Ensure slug uniqueness (simple approach)
                $count = static::where('slug', $post->slug)->where('id', '!=', $post->id)->count();
                if ($count > 0) {
                    $originalSlug = $post->slug;
                    $i = 1;
                    do {
                        $post->slug = $originalSlug . '-' . $i++;
                    } while (static::where('slug', $post->slug)->where('id', '!=', $post->id)->exists());
                }
            }
            if (empty($post->published_at) && $post->status === 'published') {
                 $post->published_at = now();
            }
        });
    }

    /**
     * Get related posts based on category and tags
     * 
     * @param int $limit Number of related posts to return
     * @return \Illuminate\Database\Eloquent\Collection
     */
    public function getRelatedPosts(int $limit = 3)
    {
        // Start with posts in the same category
        return static::query()
            ->where('id', '!=', $this->id) // Exclude current post
            ->where('status', 'published')
            ->whereNotNull('published_at')
            ->where(function ($query) {
                // Posts in the same category
                $query->where('category_id', $this->category_id)
                    // OR posts that share tags with the current post
                    ->orWhereHas('tags', function ($query) {
                        $tagIds = $this->tags->pluck('id');
                        if ($tagIds->isNotEmpty()) {
                            $query->whereIn('tags.id', $tagIds);
                        }
                    });
            })
            ->with(['author:id,name', 'category:id,name,slug'])
            ->latest('published_at')
            ->limit($limit)
            ->get();
    }

    /**
     * Get the URL for viewing this post
     *
     * @return string
     */
    public function getUrlAttribute(): string
    {
        return route('posts.show', $this->slug);
    }
}