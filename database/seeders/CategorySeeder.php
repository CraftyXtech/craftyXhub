<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Category;
use Illuminate\Support\Str;

class CategorySeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $categories = [
            'Tech' => 'Tech related content.',
            'Science' => 'Science related content.',
            'Health' => 'Health and wellness content.',
            'Food' => 'Food and cooking content.',
            'Travel' => 'Travel experiences and tips.',
            'DIY' => 'Do-it-yourself projects.',
            'Education' => 'Educational materials.',
            'Entertainment' => 'Entertainment news and reviews.',
            'Business' => 'Business and entrepreneurship.',
            'Finance' => 'Personal and business finance.',
        ];
        
        foreach ($categories as $name => $description) {
            Category::updateOrCreate(
                ['name' => $name],
                [
                    'slug' => Str::slug($name),
                    'description' => $description,
                ]
            );
        }
    }
}
