<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\Post;
use App\Services\EmbeddingService; // Although observer handles it, good practice to have access if needed
use Illuminate\Support\Facades\Log;
use Exception;

class GeneratePostEmbeddings extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'app:generate-post-embeddings {--chunk=100 : Process posts in chunks of this size} {--force : Force regeneration even if embedding exists}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Generate and save vector embeddings for existing posts using the configured service.';

    protected $embeddingService; // Keep for potential direct use if needed

    // Inject service, though the observer does the heavy lifting via save()
    public function __construct(EmbeddingService $embeddingService) 
    {   
        parent::__construct();
        $this->embeddingService = $embeddingService;
    }

    /**
     * Execute the console command.
     */
    public function handle(): int
    {
        $this->info('Starting embedding generation for posts...');
        $chunkSize = (int) $this->option('chunk');
        $forceRegenerate = $this->option('force');
        $totalProcessed = 0;
        $totalFailed = 0;

        // Use chunkById to avoid memory issues with large tables
        Post::query()
            ->when(!$forceRegenerate, function ($query) {
                // Only process posts where embedding is null if not forcing
                $query->whereNull('embedding');
            })
            ->select('id', 'title', 'excerpt') // Select only needed fields initially
            ->chunkById($chunkSize, function ($posts) use (&$totalProcessed, &$totalFailed, $forceRegenerate) {
                $this->info("Processing chunk of " . $posts->count() . " posts...");
                $bar = $this->output->createProgressBar($posts->count());
                $bar->start();

                foreach ($posts as $post) {
                    try {
                        // Re-fetch the full model for the observer to work correctly
                        // Or modify observer to accept partial data / directly call service
                        // Let's try re-fetching, simpler for now.
                        $fullPost = Post::find($post->id); 
                        
                        if (!$fullPost) continue; // Should not happen in chunkById, but safety check
                        
                        // We rely on the PostObserver's 'saving' method.
                        // The observer checks if title/excerpt changed or embedding is null.
                        // If --force is used, we should ideally skip the observer's check.
                        // For now, saving will trigger the observer which handles the logic.
                        // If --force is needed for already embedded posts, the observer logic needs adjustment or direct service call here.
                        
                        // Just calling save() triggers the observer which has the generation logic.
                        // The observer already checks if generation is needed unless --force.
                        // To truly force, we might need to manually set embedding to null first or call service directly.
                         
                        // If force is specified, nullify embedding first to ensure observer runs generation
                        if($forceRegenerate && !is_null($fullPost->embedding)) {
                            $this->warn("Forcing regeneration for Post ID: {$fullPost->id}");
                            $fullPost->embedding = null; 
                            // Note: This requires a save, then the actual save triggers observer again. Not ideal.
                            // Better: Modify observer or call service directly here if forcing.
                            // Let's stick to the simpler approach for now: save will trigger observer.
                        }

                        // Trigger the 'saving' event via save()
                        $fullPost->save(); 
                        
                        $totalProcessed++;
                    } catch (Exception $e) {
                        $this->error(" Failed processing Post ID: {$post->id} - " . $e->getMessage());
                        Log::error("Embedding generation command failed for Post ID: {$post->id}", ['error' => $e->getMessage()]);
                        $totalFailed++;
                    }
                    $bar->advance();
                }
                $bar->finish();
                $this->newLine(2);
                 // Small delay between chunks if hitting API rate limits
                // sleep(1); 
            });

        $this->info("Embedding generation complete.");
        $this->info("Total Posts Processed: {$totalProcessed}");
        $this->warn ("Total Posts Failed: {$totalFailed}");

        return Command::SUCCESS;
    }
}
