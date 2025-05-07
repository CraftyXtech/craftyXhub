<?php

namespace Database\Seeders;

use App\Models\User;
// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        
        $this->call([
            UserRoleSeeder::class,      // Create admin, editors, and users
            CategorySeeder::class,      // Create categories
            TagSeeder::class,           // Create tags
            UserPreferenceSeeder::class, // Create user preferences
            PostSeeder::class,          // Create posts with different statuses
        ]);
    }
}
