<?php

namespace App\Http\Controllers\Editor;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;
use App\Models\Post;
use App\Services\Editor\PostManagementService;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class EditorDashboardController extends Controller
{
    protected PostManagementService $postService;

    /**
     * Constructor with dependency injection
     *
     * @param PostManagementService $postService
     */
    public function __construct(PostManagementService $postService)
    {
        $this->postService = $postService;
    }

    /**
     * Display the editor dashboard.
     *
     * @param Request $request
     * @return Response
     */
    public function index(Request $request): Response
    {
        // Get post stats
        $postStats = $this->postService->getPostStats(Auth::id());
        
        // Get recent posts (limit to 5)
        $recentPosts = Post::where('user_id', Auth::id())
            ->select('id', 'title', 'status', 'created_at', 'updated_at', 'published_at')
            ->with(['category:id,name'])
            ->orderBy('updated_at', 'desc')
            ->limit(5)
            ->get();
            
        // Get posts under review or with feedback
        $pendingReviews = Post::where('user_id', Auth::id())
            ->where('status', 'under_review')
            ->select('id', 'title', 'status', 'created_at', 'updated_at', 'feedback')
            ->orderBy('updated_at', 'desc')
            ->get();

        return Inertia::render('Editor/Dashboard', [
            'analytics' => [
                'publishedCount' => $postStats['publishedPosts'],
                'draftCount' => $postStats['draftPosts'],
                'scheduledCount' => $postStats['scheduledPosts'],
                'pendingReviewCount' => $postStats['pendingReviewPosts'],
                'totalViews' => $postStats['totalViews'],
                'recentViews' => $postStats['recentViews'],
                'totalLikes' => 0, // To be implemented
                'totalComments' => 0, // To be implemented
                'mostViewedPost' => $postStats['trendingPosts']->first(),
            ],
            'recentPosts' => $recentPosts,
            'pendingReviews' => $pendingReviews,
            'viewTrends' => $postStats['viewTrends'],
        ]);
    }

    /**
     * Display post statistics for the editor.
     *
     * @param Request $request
     * @return Response
     */
    public function stats(Request $request): Response
    {
        $userId = Auth::id();
        
        // Default to last 30 days if no time period specified
        $period = $request->period ?? 'month';
        
        // Get post stats with selected period
        $postStats = $this->postService->getPostStats($userId, $period);
        
        // Get posts with stats
        $postsRequest = new Request([
            'sort_by' => 'published_at',
            'sort_direction' => 'desc',
            'status' => 'published',
            'with_relations' => true,
            'per_page' => $request->per_page ?? 10,
        ]);
        
        $posts = $this->postService->getPosts($postsRequest);
        
        return Inertia::render('Editor/Stats', [
            'posts' => $posts,
            'trendData' => $postStats['viewTrends'],
            'summary' => [
                'totalViews' => $postStats['totalViews'],
                'recentViews' => $postStats['recentViews'],
                'publishedPosts' => $postStats['publishedPosts'],
                'trendingPosts' => $postStats['trendingPosts'],
            ],
            'period' => $period,
            'filters' => [
                'period' => $period,
            ],
        ]);
    }
    
    /**
     * Get analytics data for the editor dashboard.
     *
     * @return array
     */
    private function getEditorAnalytics()
    {
        $userId = Auth::id();
        
        // Published post count
        $publishedCount = Post::where('user_id', $userId)
            ->where('status', 'published')
            ->count();
            
        // Draft post count
        $draftCount = Post::where('user_id', $userId)
            ->where('status', 'draft')
            ->count();
            
        // Scheduled post count
        $scheduledCount = Post::where('user_id', $userId)
            ->where('status', 'scheduled')
            ->count();
            
        // Under review post count
        $pendingReviewCount = Post::where('user_id', $userId)
            ->where('status', 'under_review')
            ->count();
            
        // Total views across all posts
        $totalViews = DB::table('views')
            ->join('posts', 'views.post_id', '=', 'posts.id')
            ->where('posts.user_id', $userId)
            ->count();
            
        // Total likes across all posts
        $totalLikes = DB::table('likes')
            ->join('posts', 'likes.post_id', '=', 'posts.id')
            ->where('posts.user_id', $userId)
            ->count();
            
        // Total comments across all posts
        $totalComments = DB::table('comments')
            ->join('posts', 'comments.post_id', '=', 'posts.id')
            ->where('posts.user_id', $userId)
            ->count();
            
        // Most viewed post
        $mostViewedPost = Post::where('posts.user_id', $userId)
            ->select('posts.id', 'posts.title', 'posts.slug', DB::raw('COUNT(views.id) as view_count'))
            ->leftJoin('views', 'posts.id', '=', 'views.post_id')
            ->groupBy('posts.id', 'posts.title', 'posts.slug')
            ->orderByDesc('view_count')
            ->first();
            
        // Recent views (last 7 days)
        $recentViews = DB::table('views')
            ->join('posts', 'views.post_id', '=', 'posts.id')
            ->where('posts.user_id', $userId)
            ->where('views.viewed_at', '>=', Carbon::now()->subDays(7))
            ->count();
            
        return [
            'publishedCount' => $publishedCount,
            'draftCount' => $draftCount,
            'scheduledCount' => $scheduledCount,
            'pendingReviewCount' => $pendingReviewCount,
            'totalViews' => $totalViews,
            'totalLikes' => $totalLikes,
            'totalComments' => $totalComments,
            'mostViewedPost' => $mostViewedPost,
            'recentViews' => $recentViews,
        ];
    }
    
    /**
     * Get trend data for views over time for the editor's posts.
     *
     * @param int $userId
     * @param Carbon|null $startDate
     * @return array
     */
    private function getTrendData($userId, $startDate = null)
    {
        // Default to last 30 days if no start date provided
        $startDate = $startDate ?? Carbon::now()->subDays(30);
        $endDate = Carbon::now();
        
        // Get daily views
        $dailyViews = DB::table('views')
            ->join('posts', 'views.post_id', '=', 'posts.id')
            ->where('posts.user_id', $userId)
            ->whereBetween('views.viewed_at', [$startDate, $endDate])
            ->select(DB::raw('DATE(views.viewed_at) as date'), DB::raw('COUNT(*) as count'))
            ->groupBy('date')
            ->orderBy('date')
            ->get();
            
        // Format data for chart
        $labels = [];
        $data = [];
        
        // Create a date range for all days in the period
        $dateRange = [];
        $currentDate = clone $startDate;
        while ($currentDate <= $endDate) {
            $dateStr = $currentDate->format('Y-m-d');
            $dateRange[$dateStr] = 0;
            $currentDate->addDay();
        }
        
        // Fill in actual view counts
        foreach ($dailyViews as $view) {
            $dateRange[$view->date] = $view->count;
        }
        
        // Prepare data for chart
        foreach ($dateRange as $date => $count) {
            $labels[] = Carbon::parse($date)->format('M d');
            $data[] = $count;
        }
        
        return [
            'labels' => $labels,
            'datasets' => [
                [
                    'label' => 'Views',
                    'data' => $data,
                ]
            ]
        ];
    }
    
    /**
     * Get summary statistics for the editor's posts.
     *
     * @param int $userId
     * @param Carbon|null $startDate
     * @return array
     */
    private function getSummaryStats($userId, $startDate = null)
    {
        // Filter by start date if provided
        $postsQuery = Post::where('user_id', $userId);
        $viewsQuery = DB::table('views')
            ->join('posts', 'views.post_id', '=', 'posts.id')
            ->where('posts.user_id', $userId);
        $likesQuery = DB::table('likes')
            ->join('posts', 'likes.post_id', '=', 'posts.id')
            ->where('posts.user_id', $userId);
            
        if ($startDate) {
            $postsQuery->where('published_at', '>=', $startDate);
            $viewsQuery->where('views.viewed_at', '>=', $startDate);
            $likesQuery->where('likes.created_at', '>=', $startDate);
        }
        
        return [
            'totalPosts' => $postsQuery->count(),
            'totalViews' => $viewsQuery->count(),
            'totalLikes' => $likesQuery->count(),
            'avgViewsPerPost' => $postsQuery->count() > 0 
                ? round($viewsQuery->count() / $postsQuery->count(), 1) 
                : 0,
            'avgLikesPerPost' => $postsQuery->count() > 0 
                ? round($likesQuery->count() / $postsQuery->count(), 1) 
                : 0,
        ];
    }
    
    /**
     * Get start date based on period string.
     *
     * @param string $period
     * @return Carbon|null
     */
    private function getStartDateForPeriod($period)
    {
        switch ($period) {
            case '7days':
                return Carbon::now()->subDays(7);
            case '30days':
                return Carbon::now()->subDays(30);
            case '90days':
                return Carbon::now()->subDays(90);
            case '12months':
                return Carbon::now()->subMonths(12);
            case 'all':
                return null;
            default:
                return Carbon::now()->subDays(30);
        }
    }
} 