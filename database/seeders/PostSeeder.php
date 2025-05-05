<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Str;
use App\Models\Post;
use App\Models\User;
use App\Models\Category;

class PostSeeder extends Seeder
{
    public function run(): void
    {
        $user = User::first(); // Make sure at least one user exists

        if (!$user) {
            $user = User::factory()->create();
        }

        $categories = Category::all();

        for ($i = 1; $i <= 5; $i++) {
            $title = "Sample Post $i";
            Post::create([
                'user_id' => $user->id,
                'category_id' => $categories->random()->id ?? null,
                'title' => $title,
                'slug' => Str::slug($title),
                'excerpt' => 'This is a short excerpt of the post.',
                'body' => 'This is the full body content of the post. It contains detailed information.',
                'image_url' => null,
                'published_at' => now(),
                'difficulty_level' => 'Intermediate',
                'status' => 'published',
                'featured' => rand(0, 1),
                'comments_enabled' => true,
            ]);
        }
    }
}
