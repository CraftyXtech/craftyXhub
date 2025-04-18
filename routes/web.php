<?php

use App\Http\Controllers\ProfileController;
use Illuminate\Foundation\Application;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;

Route::get('/', function () {
    return Inertia::render('Blog/HomeView');
})->name('home');

Route::get('/blog', function () {
    return Inertia::render('Blog/HomeView');
})->name('blog');

Route::get('/blog/{slug}', function ($slug) {
    return Inertia::render('Blog/BlogPostView', [
        'slug' => $slug,
    ]);
})->name('blog.show');

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

// Add route for Profile View page
Route::get('/profile/view', function () {
    // In a real app, you might pass user data from the controller
    return Inertia::render('Profile/ProfileView'); 
})->middleware(['auth'])->name('profile.view');

// --- Admin Dashboard Routes ---
Route::middleware(['auth', 'verified', 'admin'])->prefix('admin')->name('admin.')->group(function () {
    Route::get('/dashboard', [\App\Http\Controllers\Admin\AdminDashboardController::class, 'index'])
        ->name('dashboard'); // -> admin.dashboard

    // User management routes
    Route::patch('/users/{user}/role', [\App\Http\Controllers\Admin\AdminDashboardController::class, 'updateUserRole'])
        ->name('users.update-role');
    Route::delete('/users/{user}', [\App\Http\Controllers\Admin\AdminDashboardController::class, 'deleteUser'])
        ->name('users.delete');
        
    // Content management routes
    Route::get('/content/analytics', [\App\Http\Controllers\Admin\AdminDashboardController::class, 'contentAnalytics'])
        ->name('content.analytics');
    Route::get('/content/approval', [\App\Http\Controllers\Admin\AdminDashboardController::class, 'contentApproval'])
        ->name('content.approval');
});

// --- Editor Dashboard Routes ---
Route::middleware(['auth', 'verified', 'editor'])->prefix('editor')->name('editor.')->group(function () {
    // Main dashboard
    Route::get('/dashboard', [\App\Http\Controllers\Editor\EditorDashboardController::class, 'index'])
        ->name('dashboard'); // -> editor.dashboard
    
    // Post management routes (CRUD)
    Route::resource('posts', \App\Http\Controllers\Editor\PostController::class);
    
    // Post statistics
    Route::get('/stats', [\App\Http\Controllers\Editor\EditorDashboardController::class, 'stats'])
        ->name('stats');
});
