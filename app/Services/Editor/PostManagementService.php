<?php

namespace App\Services\Editor;

use App\Models\Post;
use App\Models\View;
use App\Models\Comment;
use App\Models\Tag;
use App\Models\Category;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Cache;
use Illuminate\Http\Request;
use Carbon\Carbon;
use Illuminate\Support\Str;
use Illuminate\Support\Collection;

class PostManagementService
{

    public function getPosts(Request $request, bool $userPosts = true): Collection
    {
        $query = Post::query();

        if ($userPosts) {
            $query->where('user_id', Auth::id());
        } else if ($request->user_id) {
            $query->where('user_id', $request->user_id);
        }

        $query->when($request->search, function ($query, $search) {
            $query->where(function ($q) use ($search) {
                $q->where('title', 'like', "%{$search}%")
                    ->orWhere('body', 'like', "%{$search}%");
            });
        })
            ->when($request->status, function ($query, $status) {
                $query->where('status', $status);
            })
            ->when($request->category_id, function ($query, $categoryId) {
                $query->where('category_id', $categoryId);
            })
            ->when($request->tag_id, function ($query, $tagId) {
                $query->whereHas('tags', function ($q) use ($tagId) {
                    $q->where('tags.id', $tagId);
                });
            });

        $query->when($request->sort_by, function ($query, $sortBy) use ($request) {
            $direction = $request->sort_direction ?? 'desc';
            $query->orderBy($sortBy, $direction);
        }, function ($query) {
            $query->orderBy('updated_at', 'desc');
        });

        if ($request->with_relations) {
            $query->with(['category:id,name', 'tags:id,name', 'author:id,name']);
        }

        return $query->get();
    }


    public function getPostStats(?int $userId = null, string $period = 'week'): array
    {
        $cacheKey = $userId
            ? "editor_post_stats_{$userId}_{$period}"
            : "admin_post_stats_{$period}";

        return Cache::remember($cacheKey, 300, function () use ($userId, $period) {
            $query = Post::query();
            if ($userId) {
                $query->where('user_id', $userId);
            }

            $totalPosts = $query->count();
            $publishedPosts = (clone $query)->wherePublished()->count();
            $draftPosts = (clone $query)->where('status', 'draft')->count();
            $scheduledPosts = (clone $query)->where('status', 'scheduled')->count();
            $pendingReviewPosts = (clone $query)->where('status', 'under_review')->count();

            // Determine start date for trends
            $startDate = match ($period) {
                'day' => Carbon::now()->subDay(),
                'week' => Carbon::now()->subWeek(),
                'month' => Carbon::now()->subMonth(),
                'year' => Carbon::now()->subYear(),
                default => Carbon::now()->subWeek(),
            };

            // View statistics
            $viewsQuery = View::query()
                ->when($userId, function ($query) use ($userId) {
                    $query->whereHas('post', function ($q) use ($userId) {
                        $q->where('user_id', $userId);
                    });
                });

            $totalViews = $viewsQuery->count();
            $recentViews = (clone $viewsQuery)
                ->where('viewed_at', '>=', $startDate)
                ->count();

            // Get trending posts (most viewed)
            $trendingPosts = Post::select('posts.id', 'title', 'slug', DB::raw('COUNT(views.id) as view_count'))
                ->leftJoin('views', 'posts.id', '=', 'views.post_id')
                ->when($userId, function ($query) use ($userId) {
                    $query->where('posts.user_id', $userId);
                })
                ->where('views.viewed_at', '>=', $startDate)
                ->groupBy('posts.id', 'title', 'slug')
                ->orderByDesc('view_count')
                ->limit(5)
                ->get();

            // Get view trends by date
            $viewsByDate = View::select(DB::raw('DATE(viewed_at) as date'), DB::raw('COUNT(*) as count'))
                ->when($userId, function ($query) use ($userId) {
                    $query->whereHas('post', function ($q) use ($userId) {
                        $q->where('user_id', $userId);
                    });
                })
                ->where('viewed_at', '>=', $startDate)
                ->groupBy('date')
                ->orderBy('date')
                ->get()
                ->pluck('count', 'date')
                ->toArray();

            // Fill in missing dates
            $viewTrends = [];
            $currentDate = clone $startDate;
            $endDate = Carbon::now();

            while ($currentDate <= $endDate) {
                $dateStr = $currentDate->format('Y-m-d');
                $viewTrends[$dateStr] = $viewsByDate[$dateStr] ?? 0;
                $currentDate->addDay();
            }

            return [
                'totalPosts' => $totalPosts,
                'publishedPosts' => $publishedPosts,
                'draftPosts' => $draftPosts,
                'scheduledPosts' => $scheduledPosts,
                'pendingReviewPosts' => $pendingReviewPosts,
                'totalViews' => $totalViews,
                'recentViews' => $recentViews,
                'trendingPosts' => $trendingPosts,
                'viewTrends' => [
                    'labels' => array_keys($viewTrends),
                    'data' => array_values($viewTrends),
                ],
            ];
        });
    }

    /**
     * Create a new post
     *
     * @param array $data Validated post data
     * @return Post
     */
    public function createPost(array $data): Post
    {
        // Generate slug if not provided
        if (!isset($data['slug']) || empty($data['slug'])) {
            $data['slug'] = Str::slug($data['title']);
            // Ensure uniqueness
            $count = Post::where('slug', $data['slug'])->count();
            if ($count > 0) {
                $data['slug'] .= '-' . Str::random(5);
            }
        }

        // Set user ID
        $data['user_id'] = Auth::id();

        // Set published_at if status is published
        if ($data['status'] === 'published' && !isset($data['published_at'])) {
            $data['published_at'] = now();
        }

        // Create the post
        $post = Post::create($data);

        // Sync tags if provided
        if (isset($data['tags']) && is_array($data['tags'])) {
            $post->tags()->sync($data['tags']);
        }

        // Clear cache
        $this->clearPostCache();

        return $post;
    }

    /**
     * Update an existing post
     *
     * @param Post $post
     * @param array $data Validated post data
     * @return Post
     */
    public function updatePost(Post $post, array $data): Post
    {
        // Handle slug updates
        if (isset($data['title']) && $post->title !== $data['title'] && $post->status !== 'published') {
            if (!isset($data['slug']) || empty($data['slug'])) {
                $data['slug'] = Str::slug($data['title']);
                // Ensure uniqueness
                $count = Post::where('slug', $data['slug'])->where('id', '!=', $post->id)->count();
                if ($count > 0) {
                    $data['slug'] .= '-' . Str::random(5);
                }
            }
        }

        // Handle published_at changes based on status
        if (isset($data['status'])) {
            if ($data['status'] === 'published' && ($post->status !== 'published' || !$post->published_at)) {
                $data['published_at'] = now();
            } elseif ($data['status'] === 'draft' && !isset($data['published_at'])) {
                $data['published_at'] = null;
            }
        }

        // Update the post
        $post->fill($data);
        $post->save();

        // Sync tags if provided
        if (isset($data['tags']) && is_array($data['tags'])) {
            $post->tags()->sync($data['tags']);
        }

        // Clear cache
        $this->clearPostCache();

        return $post;
    }

    /**
     * Apply a bulk action to specified posts.
     *
     * @param string $action The action to perform (e.g., 'delete', 'publish', 'draft').
     * @param array $postIds Array of Post IDs to apply the action to.
     * @return string Success message.
     */
    public function applyBulkAction(string $action, array $postIds): string
    {
        if (empty($postIds)) {
            return 'No posts selected for bulk action.';
        }

        $message = '';
        $count = count($postIds);

        switch ($action) {
            case 'delete':
                Post::whereIn('id', $postIds)->delete(); // Consider soft deletes if enabled
                $message = "Successfully deleted {$count} post(s).";
                break;

            case 'publish':
                Post::whereIn('id', $postIds)->update([
                    'status' => 'published',
                    'published_at' => now()
                ]);
                $message = "Successfully published {$count} post(s).";
                break;

            case 'draft':
                Post::whereIn('id', $postIds)->update([
                    'status' => 'draft',
                    'published_at' => null
                ]);
                $message = "Successfully moved {$count} post(s) to drafts.";
                break;

            case 'review':
                Post::whereIn('id', $postIds)->update(['status' => 'under_review']);
                $message = "Successfully submitted {$count} post(s) for review.";
                break;

            case 'reject': // Example for a rejection workflow
                Post::whereIn('id', $postIds)->update(['status' => 'rejected']);
                $message = "Successfully rejected {$count} post(s).";
                break;

            default:
                throw new \InvalidArgumentException("Invalid bulk action: {$action}");
        }

        // Clear relevant caches after bulk actions
        $this->clearPostCache();

        return $message;
    }

    /**
     * Delete a post
     *
     * @param Post $post
     * @return bool
     */
    public function deletePost(Post $post): bool
    {
        $deleted = $post->delete(); // Use delete() for soft deletes

        if ($deleted) {
            $this->clearPostCache();
        }

        return $deleted;
    }

    /**
     * Clear relevant post caches.
     */
    protected function clearPostCache(): void
    {
        // Example: Clear stats caches or specific post caches
        Cache::forget('admin_content_overview');
        // Potentially clear user-specific stats if needed
        // Cache::forget("editor_post_stats_" . Auth::id() . "_week");
        // ... add other cache keys to forget ...
    }

    /**
     * Get common options needed for post forms (categories, tags).
     *
     * @return array
     */
    public function getPostFormOptions(): array
    {
        $categories = Category::select('id', 'name')->orderBy('name')->get();
        $tags = Tag::select('id', 'name')->orderBy('name')->get();

        return [
            'categories' => $categories,
            'tags' => $tags,
        ];
    }
}
