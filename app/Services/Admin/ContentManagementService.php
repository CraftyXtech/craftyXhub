<?php

namespace App\Services\Admin;

use App\Models\Post;
use App\Models\View;
use App\Models\Comment;
use App\Models\User;
use App\Models\Category;
use App\Models\Tag;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class ContentManagementService
{
    /**
     * Get content overview data
     *
     * @return array
     */
    public function getContentOverview(): array
    {
        // Cache the content overview data for 10 minutes to optimize performance
        return Cache::remember('admin_content_overview', 600, function () {
            $totalPosts = Post::count();
            $publishedPosts = Post::wherePublished()->count();
            $draftPosts = Post::where('status', 'draft')->count();
            $scheduledPosts = Post::where('status', 'scheduled')->whereNotNull('published_at')->count();
            
            $totalViews = View::count();
            $uniqueViewers = View::select('ip_address')->distinct()->count();
            
            $totalComments = Comment::count();
            
            // Get posts with most views (top 5)
            $mostViewedPosts = Post::select('posts.id', 'title', 'slug', DB::raw('COUNT(views.id) as view_count'))
                ->leftJoin('views', 'posts.id', '=', 'views.post_id')
                ->groupBy('posts.id', 'title', 'slug')
                ->orderByDesc('view_count')
                ->limit(5)
                ->get();
            
            // Get most active users (top 5 by post count)
            $mostActiveUsers = User::select('users.id', 'name', 'email', DB::raw('COUNT(posts.id) as post_count'))
                ->leftJoin('posts', 'users.id', '=', 'posts.user_id')
                ->groupBy('users.id', 'name', 'email')
                ->orderByDesc('post_count')
                ->limit(5)
                ->get();
                
            // Get posts by category
            $postsByCategory = Post::select('categories.name', DB::raw('COUNT(posts.id) as post_count'))
                ->leftJoin('categories', 'posts.category_id', '=', 'categories.id')
                ->groupBy('categories.name')
                ->orderByDesc('post_count')
                ->get()
                ->map(function ($item) {
                    return [
                        'name' => $item->name ?? 'Uncategorized',
                        'count' => $item->post_count,
                    ];
                });
                
            // Recent posts (last 7 days)
            $recentPosts = Post::where('created_at', '>=', Carbon::now()->subDays(7))
                ->count();
                
            // Recent views (last 7 days)
            $recentViews = View::where('viewed_at', '>=', Carbon::now()->subDays(7))
                ->count();
                
            // Recent comments (last 7 days)
            $recentComments = Comment::where('created_at', '>=', Carbon::now()->subDays(7))
                ->count();
                
            // Most popular tags
            $popularTags = Tag::select('tags.id', 'tags.name', DB::raw('COUNT(post_tag.post_id) as usage_count'))
                ->leftJoin('post_tag', 'tags.id', '=', 'post_tag.tag_id')
                ->groupBy('tags.id', 'tags.name')
                ->orderByDesc('usage_count')
                ->limit(10)
                ->get();
            
            return [
                'totalPosts' => $totalPosts,
                'publishedPosts' => $publishedPosts,
                'draftPosts' => $draftPosts,
                'scheduledPosts' => $scheduledPosts,
                'totalViews' => $totalViews,
                'uniqueViewers' => $uniqueViewers,
                'totalComments' => $totalComments,
                'mostViewedPosts' => $mostViewedPosts,
                'mostActiveUsers' => $mostActiveUsers,
                'postsByCategory' => $postsByCategory,
                'recentPosts' => $recentPosts,
                'recentViews' => $recentViews,
                'recentComments' => $recentComments,
                'popularTags' => $popularTags,
            ];
        });
    }
    
    /**
     * Get view trends by date range
     *
     * @param string $period day|week|month|year
     * @return array
     */
    public function getViewTrends(string $period = 'week'): array
    {
        $cacheKey = "admin_view_trends_{$period}";
        
        return Cache::remember($cacheKey, 300, function () use ($period) {
            // Determine start date based on period
            $startDate = match($period) {
                'day' => Carbon::now()->subDay(),
                'week' => Carbon::now()->subWeek(),
                'month' => Carbon::now()->subMonth(),
                'year' => Carbon::now()->subYear(),
                default => Carbon::now()->subWeek(),
            };
            
            // Get views by date
            $viewsByDate = View::select(
                    DB::raw('DATE(viewed_at) as date'), 
                    DB::raw('COUNT(*) as count')
                )
                ->where('viewed_at', '>=', $startDate)
                ->groupBy('date')
                ->orderBy('date')
                ->get()
                ->pluck('count', 'date')
                ->toArray();
                
            // Fill in missing dates
            $dateRange = [];
            $currentDate = clone $startDate;
            $endDate = Carbon::now();
            
            while ($currentDate <= $endDate) {
                $dateStr = $currentDate->format('Y-m-d');
                $dateRange[$dateStr] = $viewsByDate[$dateStr] ?? 0;
                $currentDate->addDay();
            }
            
            // Format for charts
            return [
                'labels' => array_keys($dateRange),
                'data' => array_values($dateRange),
            ];
        });
    }
    
    /**
     * Get content with approval needed
     *
     * @return array
     */
    public function getContentNeedingApproval(): array
    {
        return [
            'pendingPosts' => Post::where('status', 'under_review')
                ->with(['author:id,name,email'])
                ->orderBy('updated_at', 'desc')
                ->limit(10)
                ->get(),
                
            'pendingComments' => Comment::where('approved', false)
                ->with(['user:id,name,email', 'post:id,title,slug'])
                ->orderBy('created_at', 'desc')
                ->limit(10)
                ->get(),
        ];
    }
} 