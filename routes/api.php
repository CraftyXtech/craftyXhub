<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\PostController;
use App\Http\Controllers\Api\CommentController;
use App\Http\Controllers\Api\InteractionController;
use App\Http\Controllers\Api\UserProfileController;
use App\Http\Controllers\Api\AiController;
use App\Http\Controllers\Api\RecommendationController;
use App\Http\Controllers\Api\SearchController;

// Public routes
Route::get('/posts', [PostController::class, 'index']);
Route::get('/posts/{post:slug}', [PostController::class, 'show']);
Route::get('/posts/{post}/comments', [CommentController::class, 'index']);
Route::get('/search', [SearchController::class, 'index']);

// Authenticated routes (using Sanctum)
Route::middleware('auth:sanctum')->group(function () {
    Route::get('/user', function (Request $request) {
        return $request->user();
    });

    // Comments
    Route::post('/posts/{post}/comments', [CommentController::class, 'store']);

    // Interactions
    Route::post('/posts/{post}/like', [InteractionController::class, 'toggleLike']);
    Route::post('/posts/{post}/save', [InteractionController::class, 'toggleSave']);

    // User Profile & Preferences
    Route::get('/user/profile', [UserProfileController::class, 'show']); // Includes saved posts etc.
    Route::get('/user/preferences', [UserProfileController::class, 'getPreferences']);
    Route::put('/user/preferences', [UserProfileController::class, 'updatePreferences']);
    Route::get('/user/likes', [UserProfileController::class, 'getLikedPosts']);
    Route::get('/user/bookmarks', [UserProfileController::class, 'getBookmarkedPosts']);

    // AI Features
    Route::post('/ai/summarize', [AiController::class, 'summarize']);
    Route::post('/ai/ask', [AiController::class, 'ask']);

    // Recommendations
    Route::get('/posts/recommendations', [RecommendationController::class, 'getRecommendations']);
}); 