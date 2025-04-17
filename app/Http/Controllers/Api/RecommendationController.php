<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Resources\PostResource; // Assuming PostResource is suitable for recommendation output
use App\Services\RecommendationService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class RecommendationController extends Controller
{
    protected $recommendationService;

    public function __construct(RecommendationService $recommendationService)
    {
        $this->recommendationService = $recommendationService;
    }

    /**
     * Get personalized recommendations for the authenticated user.
     *
     * @param Request $request
     * @return \Illuminate\Http\Resources\Json\AnonymousResourceCollection
     */
    public function getRecommendations(Request $request)
    {
        $user = Auth::user();

        if (!$user) {
            // Handle case where user isn't authenticated, maybe return popular posts?
            // For now, return empty or an error.
            return response()->json(['message' => 'Authentication required.'], 401);
            // Or return PostResource::collection(collect()); // Empty collection
        }

        // Get recommendations using the service
        // Optionally pass a limit from the request, e.g., $request->query('limit', 3)
        $recommendations = $this->recommendationService->getRecommendations($user);

        // Return recommendations using the PostResource
        return PostResource::collection($recommendations);
    }
} 