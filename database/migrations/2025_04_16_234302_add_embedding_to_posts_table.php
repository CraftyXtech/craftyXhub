<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB; // Import DB facade for raw statements
use Illuminate\Support\Facades\Log; // Import Log facade

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        return; // Temporarily disable this migration

        // First check if pgvector extension is available
        try {
            // Try to create the extension and catch any exceptions
            DB::statement('CREATE EXTENSION IF NOT EXISTS vector;');
            $pgvectorAvailable = true;
        } catch (\Exception $e) {
            // Extension is not available, we'll proceed without vector features
            $pgvectorAvailable = false;
            // Log that vector extension is not available
            Log::warning('pgvector extension is not available. Vector search features will be disabled.');
        }

        if ($pgvectorAvailable) {
            // If pgvector is available, add the vector column
            Schema::table('posts', function (Blueprint $table) {
                // Add the vector column. Adjust dimensions (768) if your model differs.
                $table->addColumn('vector', 'embedding', ['dimensions' => 768])->nullable()->after('body');
            });
            
            // Add index using raw SQL if the Blueprint method isn't supported for vectors
            try {
                DB::statement('CREATE INDEX IF NOT EXISTS posts_embedding_idx ON posts USING hnsw (embedding vector_cosine_ops);');
            } catch (\Exception $e) {
                // Log that index creation failed
                Log::warning('Failed to create vector index: ' . $e->getMessage());
            }
        } else {
            // If pgvector is not available, add a simple JSON column instead
            Schema::table('posts', function (Blueprint $table) {
                // Add a JSON column to store the embedding as a regular JSON array
                $table->json('embedding')->nullable()->after('body');
            });
        }
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        return; // Temporarily disable this migration

        // Check if pgvector extension is available
        try {
            DB::statement('SELECT count(*) FROM pg_extension WHERE extname = \'vector\';');
            $pgvectorAvailable = true;
        } catch (\Exception $e) {
            $pgvectorAvailable = false;
        }

        if ($pgvectorAvailable) {
            // Drop the index first if it was created
            try {
                DB::statement('DROP INDEX IF EXISTS posts_embedding_idx;');
            } catch (\Exception $e) {
                // Index might not exist, just log and continue
                Log::warning('Failed to drop vector index: ' . $e->getMessage());
            }
        }

        // Drop the embedding column regardless of its type
        Schema::table('posts', function (Blueprint $table) {
            $table->dropColumn('embedding');
        });
    }
};
