<?php

namespace App\Http\Controllers\Web;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Support\Facades\Auth; // Needed for Auth::user()

class UserProfileController extends Controller
{
    /**
     * Display the user's profile page with associated data.
     */
    public function show(Request $request): Response
    {
        /** @var \App\Models\User $user */ // Add PHPDoc to hint the User model type
        $user = Auth::user(); // Get the authenticated user

        // Eager load counts or relations needed for the profile view
        $user->loadCount(['posts', 'followers', 'following']); // Example counts

        // Fetch paginated liked posts (adjust relation name and pagination as needed)
        $likedPosts = $user->likes() // Assuming 'likes' is the relationship name for liked posts
                           ->with(['category:id,name,slug']) // Eager load necessary post data
                           ->latest('pivot_created_at') // Order by when they were liked
                           ->paginate(5, ['*'], 'likes_page'); // Paginate with a specific page name

        // Fetch paginated bookmarked posts (adjust relation name and pagination as needed)
        $bookmarkedPosts = $user->bookmarkedPosts()
                ->with(['category:id,name,slug'])
                ->latest('pivot_created_at')
                ->paginate(5, ['*'], 'bookmarks_page'); 

        // Fetch user preferences (assuming a relationship or dedicated method)
        $preferences = $user->preference()->first() ?? []; // Example: get preferences

        // Add any other data needed for the profile view
        // $recentActivity = $user->recentActivity()->limit(5)->get();

        return Inertia::render('Profile/ProfileView', [
            'userProfile' => $user, // Pass the loaded user model
            'likedPosts' => $likedPosts, // Pass paginated liked posts
            'bookmarkedPosts' => $bookmarkedPosts, // Pass paginated bookmarks
            'preferences' => $preferences, // Pass user preferences
            // 'recentActivity' => $recentActivity, // Pass other data as needed
        ]);
    }

    /**
     * Update the user's preferences.
     */
    public function updatePreferences(Request $request): \Illuminate\Http\RedirectResponse
    {
        /** @var \App\Models\User $user */ // Add PHPDoc hint
        $user = Auth::user();

        // Validate the incoming request data
        $validated = $request->validate([
            'newsletter_enabled'   => 'sometimes|boolean',
            'personalization_enabled' => 'sometimes|boolean', // Example preference
            'preferred_categories' => 'sometimes|array',
            'preferred_categories.*' => 'string|exists:categories,slug', // Example: Validate category slugs
            // Add validation for other preferences...
        ]);

        // Update or create the preferences record
        // Assuming a 'preferences' relationship exists on the User model (e.g., hasOne)
        $user->preferences()->updateOrCreate(
            ['user_id' => $user->id], // Match by user_id
            $validated // Update with validated data
        );

        // Redirect back to the profile view page with a success message
        return redirect()->route('profile.view')->with('success', 'Preferences updated successfully!');
    }
} 