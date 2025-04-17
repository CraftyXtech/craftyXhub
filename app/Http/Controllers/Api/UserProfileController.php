<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Http\Resources\UserProfileResource;
use App\Models\UserPreference; // Assuming a model exists or create one
use App\Models\User;

class UserProfileController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the authenticated user's profile.
     */
    public function show(Request $request)
    {
        /** @var User $user */
        $user = Auth::user();
        $user->load(['savedPosts.category', 'savedPosts.author']); // Eager load saved posts details

        return new UserProfileResource($user);
    }

    /**
     * Get the authenticated user's preferences.
     */
    public function getPreferences(Request $request)
    {
        /** @var User $user */
        $user = Auth::user();
        $preferences = UserPreference::firstOrCreate(
            ['user_id' => $user->id],
            // Default values handled by model or database defaults if set
            // ['preferred_categories' => []] 
        );

        return response()->json($preferences);
    }

    /**
     * Update the authenticated user's preferences.
     */
    public function updatePreferences(Request $request)
    {
        /** @var User $user */
        $user = Auth::user();
        
        $validated = $request->validate([
            'newsletter_enabled' => 'sometimes|boolean',
            'preferred_categories' => 'sometimes|array', 
        ]);

        $preferences = UserPreference::updateOrCreate(
            ['user_id' => $user->id],
            $validated // Use validated data directly
        );
        
        return response()->json($preferences);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }
}
