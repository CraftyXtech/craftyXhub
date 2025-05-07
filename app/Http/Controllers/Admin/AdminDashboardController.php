<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;
use App\Models\User;
use App\Models\Post;
use App\Models\View;
use App\Models\Comment;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use App\Services\Admin\UserManagementService;
use App\Services\Admin\ContentManagementService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Auth;
use App\Models\Category;

class AdminDashboardController extends Controller
{
    protected UserManagementService $userService;
    protected ContentManagementService $contentService;

    /**
     * Constructor with dependency injection
     *
     * @param UserManagementService $userService
     * @param ContentManagementService $contentService
     */
    public function __construct(UserManagementService $userService, ContentManagementService $contentService)
    {
        $this->userService = $userService;
        $this->contentService = $contentService;
    }

    /**
     * Display the admin dashboard.
     *
     * @param Request $request
     * @return Response
     */
    public function index(Request $request): Response
    {
        // Get current user
        $user = Auth::user();
        $isEditor = $user->role === 'editor';
        $isAdmin = $user->role === 'admin';
        
        // Get users with pagination and filtering (admin only)
        $users = $isAdmin ? $this->userService->getUsers($request) : null;
        
        // Get user statistics (admin only)
        $userStats = $isAdmin ? $this->userService->getUserStats() : null;
        
        // Get content overview - filtered for editors
        $contentOverview = $isAdmin 
            ? $this->contentService->getContentOverview() 
            : $this->contentService->getContentOverviewForUser($user->id);
        
        // Get view trends - filtered for editors
        $viewTrends = $isAdmin
            ? $this->contentService->getViewTrends($request->period ?? 'week')
            : $this->contentService->getViewTrendsForUser($user->id, $request->period ?? 'week');
        
        // Get content needing approval - admin only
        $contentNeedingApproval = $isAdmin ? $this->contentService->getContentNeedingApproval() : null;

        // Get recent posts list - filtered for editors
        $recentPostsList = $isAdmin
            ? $this->contentService->getRecentPostsList()
            : $this->contentService->getRecentPostsListForUser($user->id);

        return Inertia::render('Admin/Dashboard', [
            'userCount' => $userStats['total'] ?? 0,
            'userStats' => $userStats,
            'users' => $users,
            'filters' => [
                'search' => $request->search ?? '',
                'role' => $request->role ?? '',
                'sort_by' => $request->sort_by ?? 'created_at',
                'sort_direction' => $request->sort_direction ?? 'desc',
                'period' => $request->period ?? 'week',
            ],
            'contentOverview' => $contentOverview,
            'viewTrends' => $viewTrends,
            'contentNeedingApproval' => $contentNeedingApproval,
            'recentPostsList' => $recentPostsList,
            'isEditor' => $isEditor,
            'isAdmin' => $isAdmin,
        ]);
    }

    /**
     * Update a user's role.
     *
     * @param Request $request
     * @param User $user
     * @return JsonResponse
     */
    public function updateUserRole(Request $request, User $user): JsonResponse
    {
        // Validate the request
        $validated = $request->validate([
            'role' => 'required|string|in:admin,editor,user',
        ]);

        // Update the user's role
        $user = $this->userService->updateUserRole($user, $validated['role']);

        // Clear any cached user data
        Cache::forget('admin_user_stats');

        return response()->json([
            'message' => 'User role updated successfully',
            'user' => $user,
        ]);
    }
    
    /**
     * Delete a user.
     *
     * @param User $user
     * @return RedirectResponse
     */
    public function deleteUser(User $user): RedirectResponse
    {
        // Cannot delete yourself
        if ($user->id === Auth::id()) {
            return redirect()->back()->with('error', 'You cannot delete your own account.');
        }

        // Delete the user
        $this->userService->deleteUser($user);
        
        // Clear any cached user data
        Cache::forget('admin_user_stats');

        return redirect()->route('admin.dashboard')->with('success', 'User deleted successfully.');
    }
    
    /**
     * Display content analytics.
     *
     * @param Request $request
     * @return Response
     */
    public function contentAnalytics(Request $request): Response
    {
        // Get content overview
        $contentOverview = $this->contentService->getContentOverview();
        
        // Get view trends
        $viewTrends = $this->contentService->getViewTrends($request->period ?? 'month');
        
        return Inertia::render('Admin/ContentAnalytics', [
            'contentOverview' => $contentOverview,
            'viewTrends' => $viewTrends,
            'filters' => [
                'period' => $request->period ?? 'month',
            ],
        ]);
    }
    
    /**
     * Display content approval management.
     *
     * @return Response
     */
    public function contentApproval(): Response
    {
        // Get content needing approval
        $contentNeedingApproval = $this->contentService->getContentNeedingApproval();
        
        return Inertia::render('Admin/ContentApproval', [
            'pendingPosts' => $contentNeedingApproval['pendingPosts'],
            'pendingComments' => $contentNeedingApproval['pendingComments'],
        ]);
    }

    /**
     * Get content overview statistics for the admin dashboard.
     * This includes post counts, views, comments, etc.
     * 
     * @return array
     */
    private function getContentOverview()
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
            ];
        });
    }

    /**
     * Display users list for admin management
     * 
     * @return \Inertia\Response
     */
    public function users(Request $request)
    {
        $users = User::select('id', 'name', 'email', 'role', 'created_at')
            ->when($request->search, function($query, $search) {
                $query->where('name', 'like', "%{$search}%")
                      ->orWhere('email', 'like', "%{$search}%");
            })
            ->orderBy('created_at', 'desc')
            ->get();
            
        return Inertia::render('Admin/Users/Index', [
            'users' => $users,
            'filters' => [
                'search' => $request->search ?? '',
            ]
        ]);
    }
    
    /**
     * Display user statistics for admin
     * 
     * @return \Inertia\Response
     */
    public function userStatistics()
    {
        $userStats = [
            'total' => User::count(),
            'admins' => User::where('role', 'admin')->count(),
            'editors' => User::where('role', 'editor')->count(),
            'regular' => User::where('role', 'user')->count(),
            'recentlyJoined' => User::orderBy('created_at', 'desc')->take(5)->get(),
            'mostActive' => User::withCount('posts')->orderBy('posts_count', 'desc')->take(5)->get(),
        ];
        
        return Inertia::render('Admin/Users/Statistics', [
            'userStats' => $userStats
        ]);
    }

    // Add other methods for user management, etc., later
} 