<?php

namespace Tests\Feature;

use App\Models\Post;
use App\Models\Tag;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class UserPersonalizationMiddlewareTest extends TestCase
{
    /**
     * Test that user personalization API endpoints require authentication.
     */
    public function test_user_personalization_endpoints_require_authentication()
    {
        // Test recently read articles endpoint
        $response = $this->getJson('/api/user/recently-read');
        $response->assertStatus(401);
        
        // Test followed topics endpoint
        $response = $this->getJson('/api/user/followed-topics');
        $response->assertStatus(401);
        
        // Test suggested topics endpoint
        $response = $this->getJson('/api/topics/suggested');
        $response->assertStatus(401);
        
        // Test record post read endpoint
        $post = Post::first();
        if ($post) {
            $response = $this->postJson("/api/posts/{$post->id}/read", [
                'progress' => 75
            ]);
            $response->assertStatus(401);
        }
        
        // Test follow/unfollow topic endpoint
        $tag = Tag::first();
        if ($tag) {
            $response = $this->postJson('/api/topics/follow', [
                'tagId' => $tag->id,
                'follow' => true
            ]);
            $response->assertStatus(401);
        }
    }
    
    /**
     * Test that authenticated users can access personalization endpoints.
     */
    public function test_authenticated_users_can_access_personalization_endpoints()
    {
        $user = User::where('role', 'user')->first();
        
        if (!$user) {
            $this->markTestSkipped('No user found for testing.');
        }
        
        $this->actingAs($user);
        
        // Test recently read articles endpoint
        $response = $this->getJson('/api/user/recently-read');
        $response->assertStatus(200);
        $response->assertJsonStructure(['data']);
        
        // Test followed topics endpoint
        $response = $this->getJson('/api/user/followed-topics');
        $response->assertStatus(200);
        $response->assertJsonStructure(['data']);
        
        // Test suggested topics endpoint
        $response = $this->getJson('/api/topics/suggested');
        $response->assertStatus(200);
        $response->assertJsonStructure(['data']);
    }
} 