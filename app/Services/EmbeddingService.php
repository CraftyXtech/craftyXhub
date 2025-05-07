<?php

namespace App\Services;

use Illuminate\Support\Facades\Http; // For making API calls
use Illuminate\Support\Facades\Log; // For logging errors
use Exception;

class EmbeddingService
{
    protected $apiKey;
    protected $apiUrl;
    protected $modelName; // e.g., 'models/embedding-001' for Gemini

    public function __construct()
    {
        // Load API key and potentially URL/model from config or .env
        $this->apiKey = config('services.gemini.api_key'); 
        // Ensure you have SERVICES_GEMINI_API_KEY in your .env and config/services.php
        
        // Example Gemini API endpoint structure (confirm with official documentation)
        $this->modelName = config('services.gemini.embedding_model', 'models/embedding-001'); 
        $this->apiUrl = "https://generativelanguage.googleapis.com/v1beta/{$this->modelName}:embedContent"; 
    }

    /**
     * Generates a vector embedding for the given text using an external API.
     * 
     * TEMPORARILY DISABLED: This method is disabled until the embedding column is added to the database
     *
     * @param string $text The text content to embed.
     * @return array|null An array representing the vector embedding, or null on failure.
     */
    public function generateEmbedding(string $text): ?array
    {
        // Temporarily return null until embedding column is added
        Log::info('Embedding generation temporarily disabled');
        return null;
    }
} 