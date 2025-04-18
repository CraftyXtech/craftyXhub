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

class PostManagementService
{
    /**
     * Get posts with pagination and filtering
     *
     * @param Request $request
     * @param bool $userPosts Only return posts owned by current user (false allows admin to see all)
     * @return LengthAwarePaginator
     */
    public function getPosts(Request $request, bool $userPosts = true): LengthAwarePaginator
    {
        $perPage = $request->per_page ?? 10;
        
        $query = Post::query();
        
        // Filter by user
        if ($userPosts) {
            $query->where('user_id', Auth::id());
        }
        
        // Apply filters
        $query->when($request->search, function ($query, $search) {
                $query->where(function($q) use ($search) {
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
            
        // Apply sorting
        $query->when($request->sort_by, function ($query, $sortBy) use ($request) {
                $direction = $request->sort_direction ?? 'desc';
                $query->orderBy($sortBy, $direction);
            }, function ($query) {
                $query->orderBy('updated_at', 'desc');
            });
            
        // Include relationships if needed
        if ($request->with_relations) {
            $query->with(['category:id,name', 'tags:id,name', 'author:id,name']);
        }
        
        return $query->paginate($perPage)->withQueryString();
    }
    
    /**
     * Get post statistics
     *
     * @param int|null $userId Only get stats for posts by this user (null for all posts)
     * @param string $period Period for trend data (day, week, month, year)
     * @return array
     */
    public function getPostStats(?int $userId = null, string $period = 'week'): array
    {
        $cacheKey = $userId 
            ? "editor_post_stats_{$userId}_{$period}" 
            : "admin_post_stats_{$period}";
            
        return Cache::remember($cacheKey, 300, function () use ($userId, $period) {
            // Basic counts
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
            $startDate = match($period) {
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
     * Delete a post
     *
     * @param Post $post
     * @return bool
     */
    public function deletePost(Post $post): bool
    {
        // Delete tags relationship
        $post->tags()->detach();
        
        // Delete the post
        $result = $post->delete();
        
        // Clear cache
        $this->clearPostCache();
        
        return $result;
    }
    
    /**
     * Clear post-related cache
     */
    protected function clearPostCache(): void
    {
        $userId = Auth::id();
        
        // Clear editor stats
        foreach (['day', 'week', 'month', 'year'] as $period) {
            Cache::forget("editor_post_stats_{$userId}_{$period}");
            Cache::forget("admin_post_stats_{$period}");
        }
        
        // Clear dashboard data
        Cache::forget('admin_content_overview');
    }
    
    /**
     * Get categories and tags for post form
     *
     * @return array
     */
    public function getPostFormOptions(): array
    {
        return [
            'categories' => Category::orderBy('name')->get(['id', 'name']),
            'tags' => Tag::orderBy('name')->get(['id', 'name']),
        ];
    }
} 