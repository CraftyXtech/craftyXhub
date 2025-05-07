<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Tag;
use Illuminate\Support\Str;

class TagSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $tags = [
            'Laravel',
            'Vue.js',
            'JavaScript',
            'PHP',
            'CSS',
            'HTML',
            'React',
            'NodeJS',
            'DevOps',
            'Testing',
            'Security',
            'Performance',
            'Python',
            'Machine Learning',
            'AI',
            'Frontend',
            'Backend',
            'Mobile',
            'Database',
            'Cloud',
        ];
        
        foreach ($tags as $name) {
            Tag::updateOrCreate(
                ['name' => $name],
                ['slug' => Str::slug($name)]
            );
        }
    }
}
