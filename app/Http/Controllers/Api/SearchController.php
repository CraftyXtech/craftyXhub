<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Services\EmbeddingService;
use App\Models\Post;
use App\Http\Resources\PostResource;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Log;
// use Pgvector\Laravel\Vector;

class SearchController extends Controller
{
    protected $embeddingService;

    public function __construct(EmbeddingService $embeddingService)
    {
        $this->embeddingService = $embeddingService;
    }

    /**
     * Handle semantic search requests.
     *
     * @param Request $request
     * @return \Illuminate\Http\Resources\Json\AnonymousResourceCollection|\Illuminate\Http\JsonResponse
     */
    public function index(Request $request)
    {
        // Validate request
        $validator = Validator::make($request->all(), [
            'query' => 'required|string|min:3|max:255',
            'limit' => 'integer|min:1|max:50' // Optional limit
        ]);

        if ($validator->fails()) {
            return response()->json($validator->errors(), 422);
        }

        $searchQuery = $validator->validated()['query'];
        $limit = $validator->validated()['limit'] ?? 10; // Default limit

        // TEMPORARILY DISABLED: Vector-based semantic search
        // Using keyword-based search as fallback until vector column is added
        Log::info('Semantic Search disabled - falling back to keyword search', ['query' => $searchQuery]);
        
        try {
            // Fallback to basic keyword search
            $posts = Post::query()
                ->wherePublished()
                ->where(function($query) use ($searchQuery) {
                    $query->where('title', 'like', "%{$searchQuery}%")
                        ->orWhere('body', 'like', "%{$searchQuery}%")
                        ->orWhere('excerpt', 'like', "%{$searchQuery}%");
                })
                ->with(['author:id,name', 'category:id,name,slug', 'tags:id,name,slug'])
                ->limit($limit)
                ->get();
                
        } catch (\Exception $e) {
            Log::error('Search: Database query failed.', [
                'query' => $searchQuery,
                'error' => $e->getMessage()
            ]);
            return response()->json(['message' => 'Search failed.'], 500);
        }

        // Return results
        return PostResource::collection($posts);
    }
} 