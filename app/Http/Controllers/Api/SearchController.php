<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Services\EmbeddingService;
use App\Models\Post;
use App\Http\Resources\PostResource;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Log;
use Pgvector\Laravel\Vector;

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

        // 1. Generate embedding for the search query
        $queryVector = $this->embeddingService->generateEmbedding($searchQuery);

        if (!$queryVector) {
            Log::error('Semantic Search: Failed to generate embedding for query', ['query' => $searchQuery]);
            // Fallback to basic keyword search or return error?
            // For now, return error
            return response()->json(['message' => 'Could not process search query.'], 500);
        }

        // 2. Perform vector search
        try {
            // Use the nearestNeighbors method from the HasNeighbors trait
            // This performs `ORDER BY embedding <=> ?` query
            // Assumes vector column is named 'embedding' and uses cosine distance by default
            $posts = Post::query()
                ->wherePublished() // Ensure we only search published posts
                ->nearestNeighbors('embedding', new Vector($queryVector), $limit)
                // ->with(...) // Eager load relationships needed by PostResource if not loaded by default
                 ->with(['author:id,name', 'category:id,name,slug', 'tags:id,name,slug'])
                 ->get();

            // Optionally, you could add a distance threshold:
            // ->whereRaw('embedding <=> ? < ?', [new Vector($queryVector), 0.5]) // Example threshold

        } catch (\Exception $e) {
             Log::error('Semantic Search: Database query failed.', [
                'query' => $searchQuery,
                 'error' => $e->getMessage()
             ]);
             return response()->json(['message' => 'Search failed.'], 500);
        }

        // 3. Return results
        return PostResource::collection($posts);
    }
} 