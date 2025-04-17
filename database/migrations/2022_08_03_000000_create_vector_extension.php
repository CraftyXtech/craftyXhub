<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

return new class extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        try {
            DB::statement('CREATE EXTENSION IF NOT EXISTS vector');
            Log::info('Successfully created vector extension.');
        } catch (\Exception $e) {
            // Just log the error and continue with the migration
            Log::warning('Unable to create vector extension. Vector search features will be disabled: ' . $e->getMessage());
        }
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        try {
            // Check if the extension exists before trying to drop it
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
