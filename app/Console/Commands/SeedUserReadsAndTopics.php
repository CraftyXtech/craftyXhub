<?php

namespace App\Console\Commands;

use App\Models\Post;
use App\Models\Tag;
use App\Models\User;
use Carbon\Carbon;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class SeedUserReadsAndTopics extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'seed:user-personalization {--users=10 : Number of users to seed for}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Seed mock data for user_reads and user_topics for testing personalization features';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $userCount = $this->option('users');
        
        $this->info("Seeding user personalization data for {$userCount} users...");
        
        // Get sample users (not admin/editor roles)
        $users = User::where('role', 'user')
            ->inRandomOrder()
            ->limit($userCount)
            ->get();
            
        if ($users->count() == 0) {
            $this->error('No users found to seed data for.');
            return 1;
        }
        
        $posts = Post::where('status', 'published')->get();
        $tags = Tag::all();
        
        if ($posts->count() == 0) {
            $this->error('No published posts found to seed read data for.');
            return 1;
        }
        
        if ($tags->count() == 0) {
            $this->error('No tags found to seed topic follows for.');
            return 1;
        }
        
        $this->info("Found {$posts->count()} posts and {$tags->count()} tags for seeding.");
        
        $bar = $this->output->createProgressBar($users->count());
        $bar->start();
        
        foreach ($users as $user) {
            // Seed recently read articles (random selection of 3-10 posts)
            $readCount = rand(3, min(10, $posts->count()));
            $randomPosts = $posts->random($readCount);
            
            foreach ($randomPosts as $post) {
                DB::table('user_reads')->updateOrInsert(
                    [
                        'user_id' => $user->id, 
                        'post_id' => $post->id
                    ],
                    [
                        'read_at' => Carbon::now()->subMinutes(rand(1, 60 * 24 * 7)), // Up to a week ago
                        'read_progress' => rand(60, 100), // 60-100% read progress
                    ]
                );
            }
            
            // Seed followed topics (random selection of 2-5 tags)
            $topicCount = rand(2, min(5, $tags->count()));
            $randomTags = $tags->random($topicCount);
            
            foreach ($randomTags as $tag) {
                DB::table('user_topics')->updateOrInsert(
                    [
                        'user_id' => $user->id,
                        'tag_id' => $tag->id,
                    ],
                    [
                        'created_at' => Carbon::now()->subDays(rand(1, 30)),
                        'updated_at' => Carbon::now(),
                    ]
                );
            }
            
            $bar->advance();
        }
        
        $bar->finish();
        $this->newLine();
        
        $this->info('User personalization data seeded successfully!');
        
        return 0;
    }
} 