<?php

namespace App\Http\Controllers\Editor;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;
use App\Services\Editor\PostManagementService;
use Illuminate\Support\Facades\Auth;

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
} 