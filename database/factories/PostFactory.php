<?php

namespace Database\Factories;

use App\Models\User;
use App\Models\Post;
use App\Models\Category;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Str;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Post>
 */
class PostFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        $title = fake()->sentence();
        $status = fake()->randomElement(['draft', 'published', 'scheduled', 'under_review']);
        
        return [
            'title' => $title,
            'slug' => Str::slug($title),
            'excerpt' => fake()->paragraph(),
            'body' => fake()->paragraphs(5, true),
            'user_id' => User::factory(),
            'category_id' => Category::factory(),
            'status' => $status,
            'feedback' => $status === 'under_review' ? fake()->paragraph() : null,
            'published_at' => $status === 'published' ? now() : ($status === 'scheduled' ? now()->addDays(rand(1, 10)) : null),
            'image_url' => fake()->imageUrl(1200, 800),
            'generated_image_path' => null,
            'featured' => fake()->boolean(10),
            'comments_enabled' => fake()->boolean(90),
            'embedding' => null,
        ];
    }

    /**
     * Indicate that the post is published.
     */
    public function published(): static
    {
        return $this->state(fn (array $attributes) => [
            'status' => 'published',
            'published_at' => now()->subDays(rand(1, 30)),
            'feedback' => null,
        ]);
    }

    /**
     * Indicate that the post is a draft.
     */
    public function draft(): static
    {
        return $this->state(fn (array $attributes) => [
            'status' => 'draft',
            'published_at' => null,
            'feedback' => null,
        ]);
    }

    /**
     * Indicate that the post is under review.
     */
    public function underReview(): static
    {
        return $this->state(fn (array $attributes) => [
            'status' => 'under_review',
            'published_at' => null,
            'feedback' => fake()->boolean(30) ? fake()->paragraph() : null,
        ]);
    }

    /**
     * Indicate that the post is scheduled for future publication.
     */
    public function scheduled(): static
    {
        return $this->state(fn (array $attributes) => [
            'status' => 'scheduled',
            'published_at' => now()->addDays(rand(1, 10)),
            'feedback' => null,
        ]);
    }
} 