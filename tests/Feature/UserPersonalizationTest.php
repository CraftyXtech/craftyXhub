<?php

namespace Tests\Feature;

use App\Models\Post;
use App\Models\Tag;
use App\Models\User;
use App\Models\UserRead;
use App\Models\UserTopic;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Laravel\Sanctum\Sanctum;
use Tests\TestCase;

class UserPersonalizationTest extends TestCase
{
    public function test_user_personalization_data_exists()
    {
        // Verify that we have user reads data
        $userReadsCount = UserRead::count();
        $this->assertGreaterThan(0, $userReadsCount, 'No user reads found in the database');
        
        // Verify that we have user topics data
        $userTopicsCount = UserTopic::count();
        $this->assertGreaterThan(0, $userTopicsCount, 'No user topics found in the database');
        
        // Authenticate using Sanctum for API requests
        $user = User::where('role', 'user')->first();
        $this->assertTrue($user !== null, 'No user with role "user" found');
        $this->assertTrue($user->id > 0, 'User ID is not valid: ' . $user->id);
        
        Sanctum::actingAs($user, ['*']);
        
        // Test getting recently read articles
        $response = $this->getJson('/api/user/recently-read');
        $responseBody = $response->getContent();
        $this->assertTrue($response->status() === 200, 'Recently-read failed: ' . $responseBody);
        $response->assertStatus(200);
        $response->assertJsonStructure(['data']);
        
        // Test getting followed topics
        $response = $this->getJson('/api/user/followed-topics');
        $responseBody = $response->getContent();
        $this->assertTrue($response->status() === 200, 'Followed topics failed: ' . $responseBody);
        $response->assertStatus(200);
        $response->assertJsonStructure(['data']);
        
        // Test getting suggested topics
        $response = $this->getJson('/api/topics/suggested');
        $responseBody = $response->getContent();
        $this->assertTrue($response->status() === 200, 'Suggested topics failed: ' . $responseBody);
        $response->assertStatus(200);
        $response->assertJsonStructure(['data']);
        
        // Test recording a read
        $post = Post::first();
        $this->assertTrue($post !== null, 'No posts found in the database');
        $this->assertTrue($post->id > 0, 'Post ID is not valid: ' . $post->id);
        
        $response = $this->postJson("/api/posts/{$post->id}/read", [
            'progress' => 75
        ]);
        $responseBody = $response->getContent();
        $this->assertTrue($response->status() === 200, 'Record read failed: ' . $responseBody);
        $response->assertStatus(200);
        
        // Test following a topic
        $tag = Tag::first();
        $this->assertTrue($tag !== null, 'No tags found in the database');
        $this->assertTrue($tag->id > 0, 'Tag ID is not valid: ' . $tag->id);
        
        $response = $this->postJson('/api/topics/follow', [
            'tagId' => $tag->id,
            'follow' => true
        ]);
        $responseBody = $response->getContent();
        $this->assertTrue($response->status() === 200, 'Follow topic failed: ' . $responseBody);
        $response->assertStatus(200);
        
        // Test unfollowing a topic
        $response = $this->postJson('/api/topics/follow', [
            'tagId' => $tag->id,
            'follow' => false
        ]);
        $responseBody = $response->getContent();
        $this->assertTrue($response->status() === 200, 'Unfollow topic failed: ' . $responseBody);
        $response->assertStatus(200);
    }
} 