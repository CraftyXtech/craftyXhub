<?php

namespace App\Observers;

use App\Models\Post;
use App\Services\EmbeddingService;
use App\Services\ImageGenerationService;
use Illuminate\Support\Facades\Log;
use Pgvector\Laravel\Vector; // Import the Vector class
use Illuminate\Support\Facades\Storage;

class PostObserver
{
    protected $embeddingService;
    protected $imageGenerationService;

    public function __construct(
        EmbeddingService $embeddingService,
        ImageGenerationService $imageGenerationService
    )
    {
        $this->embeddingService = $embeddingService;
        $this->imageGenerationService = $imageGenerationService;
    }

    /**
     * Handle the Post "saving" event.
     *
     * This event fires before the model is saved (both creating and updating).
     * We generate the embedding here.
     *
     * @param  \App\Models\Post  $post
     * @return void
     */
    public function saving(Post $post): void
    {
        // Combine title and excerpt for embedding content
        $contentToEmbed = $post->title . "\n\n" . $post->excerpt; 
        // Consider adding body or tags if needed, but keep it concise initially.
        
        // Only generate if content is meaningful and embedding is missing or content changed
        if (!empty($contentToEmbed) && ($post->isDirty('title') || $post->isDirty('excerpt') || is_null($post->embedding))) {
             Log::info("Generating embedding for post ID: {$post->id}");
            $embedding = $this->embeddingService->generateEmbedding($contentToEmbed);

            if ($embedding) {
                // Cast the array to the Vector object if using pgvector/laravel package
                $post->embedding = new Vector($embedding); 
                // If not using the package, ensure the array is formatted correctly for direct DB insertion
                // $post->embedding = "[" . implode(",", $embedding) . "]"; // Example raw format
            } else {
                // Handle failure: maybe set embedding to null or log a persistent error
                Log::error("Failed to generate embedding for post ID: {$post->id}");
                 $post->embedding = null; // Ensure it's null if generation fails
            }
        }

        // --- Image Generation --- 
        // Generate image if title/excerpt changed, it's a new post, or no image exists yet,
        // and if the post is being published (or already published).
        // Avoid generating for drafts unless explicitly intended.
        $shouldGenerateImage = !empty($post->title) && 
                               ($post->isDirty('title') || $post->isDirty('excerpt') || is_null($post->generated_image_path)) &&
                               ($post->status === 'published' || $post->wasRecentlyCreated);

        if ($shouldGenerateImage) {
            Log::info("Generating image for post ID: {$post->id}");
            // Create a prompt based on title and excerpt
            $prompt = "Create a blog post header image representing the concept: " . $post->title . ". Style: vibrant, digital art. Content hint: " . $post->excerpt;
            
            // Pass post ID for unique filename generation
            $imagePath = $this->imageGenerationService->generateAndSaveImage($prompt, $post->id ?? 'new');

            if ($imagePath) {
                $post->generated_image_path = $imagePath;
                Log::info("Generated image path saved for post ID: {$post->id}");
            } else {
                 Log::error("Failed to generate image for post ID: {$post->id}");
                 // Decide if we should clear the path if generation fails on update?
                 // $post->generated_image_path = null;
            }
        }
    }

    /**
     * Handle the Post "created" event.
     */
    public function created(Post $post): void
    {
        // Embedding is handled in 'saving'
    }

    /**
     * Handle the Post "updated" event.
     */
    public function updated(Post $post): void
    {
        // Embedding is handled in 'saving'
    }

    /**
     * Handle the Post "deleted" event.
     */
    public function deleted(Post $post): void
    {
        // Optionally delete the generated image file from storage
        if ($post->generated_image_path) {
            Log::info("Deleting generated image for post ID: {$post->id}", ['path' => $post->generated_image_path]);
            Storage::disk('public')->delete($post->generated_image_path);
        }
    }

    /**
     * Handle the Post "restored" event.
     */
    public function restored(Post $post): void
    {
        // Re-generate embedding if needed upon restore?
        // $this->saving($post); // Maybe just call saving logic again
    }

    /**
     * Handle the Post "force deleted" event.
     */
    public function forceDeleted(Post $post): void
    {
        // Optionally delete the generated image file from storage
         if ($post->generated_image_path) {
            Log::info("Force deleting generated image for post ID: {$post->id}", ['path' => $post->generated_image_path]);
            Storage::disk('public')->delete($post->generated_image_path);
        }
    }
}
