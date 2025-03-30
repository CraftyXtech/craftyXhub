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
    return Inertia::render('Blog/HomeView', [
        'categoryFilter' => $category
    ]);
})->name('category');

Route::get('/category/technology', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'technology']);
})->name('technology');

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

Route::get('/category/community', function () {
    return Inertia::render('Blog/HomeView', ['categoryFilter' => 'community']);
})->name('community');

Route::get('/dashboard', function () {
    return Inertia::render('Dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

require __DIR__.'/auth.php';
