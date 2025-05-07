<?php

use App\Http\Controllers\ProfileController;
use Illuminate\Foundation\Application;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use App\Http\Controllers\Web\PostController;
use App\Http\Controllers\Web\CommentController;
use App\Http\Controllers\Web\InteractionController;
use App\Http\Controllers\Web\UserProfileController;

// Test route for debugging - this should respond with a 200
Route::get('/route-test', function() {
    return "Routes are working!";
})->name('route.test');

Route::get('/', [PostController::class, 'index'])->name('home');

Route::get('/blog', [PostController::class, 'index'])->name('blog');

Route::get('/blog/{post:slug}', [PostController::class, 'show'])->name('posts.show');

Route::get('/category/{category}', function ($category) {
    // This generic route might still be useful if you pass slugs directly
    // Or we might want to remove it if we only use named routes below
    return Inertia::render('Blog/HomeView', [
        'categoryFilter' => $category
    ]);
})->name('category');

// --- NEW CATEGORY ROUTES ---
// Technology
Route::get('/category/technology', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'technology']);
})->name('technology');
// Finance
Route::get('/category/finance', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'finance']);
})->name('finance');
// Health
Route::get('/category/health', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'health']);
})->name('health');
// Education
Route::get('/category/education', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'education']);
})->name('education');
// Sports
Route::get('/category/sports', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'sports']);
})->name('sports');
// Travel
Route::get('/category/travel', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'travel']);
})->name('travel');
// Lifestyle
Route::get('/category/lifestyle', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'lifestyle']);
})->name('lifestyle');
// Community (Assuming this one remains relevant)
Route::get('/category/community', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'community']);
})->name('community');


// --- REMOVED OLD CATEGORY ROUTES ---
/*
Route::get('/category/crafts', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'crafts']);
})->name('crafts');

Route::get('/category/diy', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'diy']);
})->name('diy');

Route::get('/category/art', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'art']);
})->name('art');

Route::get('/category/home-decor', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'home-decor']);
})->name('home-decor');

Route::get('/category/jewelry', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'jewelry']);
})->name('jewelry');

Route::get('/category/handmade', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'handmade']);
})->name('handmade');
*/


Route::get('/dashboard', function () {
    return redirect()->route('profile.view');
})->middleware(['auth', 'verified'])->name('dashboard');

Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

require __DIR__.'/auth.php';

// Use the new UserProfileController for the profile view route
Route::get('/profile/view', [\App\Http\Controllers\Web\UserProfileController::class, 'show'])
    ->middleware(['auth'])
    ->name('profile.view');

// --- Admin Dashboard Routes ---
Route::middleware(['auth', 'verified', 'admin'])->prefix('admin')->name('admin.')->group(function () {
    Route::get('/dashboard', [\App\Http\Controllers\Admin\AdminDashboardController::class, 'index'])
        ->name('dashboard'); // -> admin.dashboard

    // User management routes
    Route::get('/users', [\App\Http\Controllers\Admin\AdminDashboardController::class, 'users'])
        ->name('users.index');
    Route::get('/users/statistics', [\App\Http\Controllers\Admin\AdminDashboardController::class, 'userStatistics'])
        ->name('users.statistics');
    Route::patch('/users/{user}/role', [\App\Http\Controllers\Admin\AdminDashboardController::class, 'updateUserRole'])
        ->name('users.update-role');
    Route::delete('/users/{user}', [\App\Http\Controllers\Admin\AdminDashboardController::class, 'deleteUser'])
        ->name('users.destroy');
    
    // Posts management routes
    Route::get('/posts', [\App\Http\Controllers\Admin\AdminPostController::class, 'index'])
        ->name('posts.index');
    Route::get('/posts/pending', [\App\Http\Controllers\Admin\AdminPostController::class, 'pendingApproval'])
        ->name('posts.pending');
    Route::get('/posts/rejected', [\App\Http\Controllers\Admin\AdminPostController::class, 'rejectedPosts'])
        ->name('posts.rejected');
    Route::get('/posts/{post}/review', [\App\Http\Controllers\Admin\AdminPostController::class, 'reviewPost'])
        ->name('posts.review');
    Route::patch('/posts/{post}/approve', [\App\Http\Controllers\Admin\AdminPostController::class, 'approve'])
        ->name('posts.approve');
    Route::patch('/posts/{post}/reject', [\App\Http\Controllers\Admin\AdminPostController::class, 'rejectPost'])
        ->name('posts.reject');
    
    // System & settings routes
    Route::get('/settings', [\App\Http\Controllers\Admin\AdminSettingsController::class, 'index'])
        ->name('settings.index');
    Route::get('/system', [\App\Http\Controllers\Admin\AdminSystemController::class, 'index'])
        ->name('system.index');
    Route::post('/system/clear-cache', [\App\Http\Controllers\Admin\AdminSystemController::class, 'clearCache'])
        ->name('system.clear-cache');
    Route::post('/system/run-migrations', [\App\Http\Controllers\Admin\AdminSystemController::class, 'runMigrations'])
        ->name('system.run-migrations');
});

// --- Editor Dashboard Routes ---
Route::middleware(['auth', 'verified', 'editor'])->prefix('editor')->name('editor.')->group(function () {
    // Main dashboard - Redirect to the admin dashboard
    Route::get('/dashboard', function() {
        return redirect()->route('admin.dashboard');
    })->name('dashboard'); // -> editor.dashboard
    
    // First define specific routes before the resource routes
    // Add drafts view route
    Route::get('posts/drafts', [\App\Http\Controllers\Editor\PostController::class, 'drafts'])
        ->name('posts.drafts');
    
    // The order is important - specific routes must come before wildcard routes
    // Add the bulk action route before any routes with {post} parameter
    Route::post('posts/bulk-action', [\App\Http\Controllers\Editor\PostController::class, 'bulkAction'])
        ->name('posts.bulk-action'); 
        
    // Add submit for review route - must come before the resource routes that use {post}
    Route::post('posts/{post}/submit', [\App\Http\Controllers\Editor\PostController::class, 'submitForReview'])
        ->name('posts.submit');
    
    // Add resubmit rejected post route
    Route::post('posts/{post}/resubmit', [\App\Http\Controllers\Editor\PostController::class, 'resubmitRejected'])
        ->name('posts.resubmit');
    
    // Then define the resource routes
    // Post management routes (CRUD)
    Route::resource('posts', \App\Http\Controllers\Editor\PostController::class);
    
    // Post statistics
    Route::get('/stats', [\App\Http\Controllers\Editor\EditorDashboardController::class, 'stats'])
        ->name('stats');
    
    // Category management routes
    Route::resource('categories', \App\Http\Controllers\Editor\CategoryController::class);
    
    // Tag management routes
    Route::resource('tags', \App\Http\Controllers\Editor\TagController::class);
});

Route::post('/posts/{post}/comments', [CommentController::class, 'store'])
    ->middleware('auth')
    ->name('posts.comments.store');

Route::post('/posts/{post}/like', [InteractionController::class, 'toggleLike'])
    ->middleware('auth')
    ->name('posts.like');

Route::post('/posts/{post}/save', [InteractionController::class, 'toggleSave'])
    ->middleware('auth')
    ->name('posts.save');

Route::put('/profile/preferences', [UserProfileController::class, 'updatePreferences'])
    ->middleware(['auth'])
    ->name('profile.preferences.update');
