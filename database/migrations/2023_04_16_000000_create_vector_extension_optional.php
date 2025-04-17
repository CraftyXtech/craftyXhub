<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        try {
            // Try to create the vector extension and catch any exceptions
            DB::statement('CREATE EXTENSION IF NOT EXISTS vector');
            Log::info('Successfully created vector extension.');
        } catch (\Exception $e) {
            // Just log the error and continue with the migration
            Log::warning('Unable to create vector extension. Vector search features will be disabled: ' . $e->getMessage());
        }
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        try {
            // Try to drop the vector extension if it exists
            $result = DB::select("SELECT extname FROM pg_extension WHERE extname = 'vector'");
            if (!empty($result)) {
                DB::statement('DROP EXTENSION vector');
                Log::info('Successfully dropped vector extension.');
            }
        } catch (\Exception $e) {
            // Just log the error and continue
            Log::warning('Unable to drop vector extension: ' . $e->getMessage());
        }
    }
}; 