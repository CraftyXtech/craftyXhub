<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\User;
use App\Models\UserPreference;
use App\Models\Category;

class UserPreferenceSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Get all regular users and some editors to set preferences for
        $users = User::where('role', 'user')
            ->orWhere('role', 'editor')
            ->get();
            
        // Get categories for preferences
        $categories = Category::pluck('id')->toArray();
        
        foreach ($users as $user) {
            // Randomize newsletter subscription (70% subscribed)
            $newsletterEnabled = (rand(1, 10) <= 7);
            
            // Randomize preferred categories (1-4 categories per user)
            $numCategories = rand(1, min(4, count($categories)));
            $shuffledCategories = $categories;
            shuffle($shuffledCategories);
            $preferredCategories = array_slice($shuffledCategories, 0, $numCategories);
            
            // Create or update preferences
            UserPreference::updateOrCreate(
                ['user_id' => $user->id],
                [
                    'newsletter_enabled' => $newsletterEnabled,
                    'preferred_categories' => $preferredCategories,
                ]
            );
        }
    }
} 