<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class AdminSettingsController extends Controller
{
    /**
     * Display the admin settings page.
     *
     * @return Response
     */
    public function index(): Response
    {
        // Get any settings from database or config
        $settings = [
            'site_name' => config('app.name'),
            'site_description' => 'CraftyXhub - A hub for crafty content',
            'maintenance_mode' => false,
            'allow_user_registration' => true,
            'default_user_role' => 'user',
            'default_editor_permissions' => [
                'can_publish' => false,
                'requires_approval' => true,
            ],
        ];
        
        return Inertia::render('Admin/Settings/Index', [
            'settings' => $settings,
        ]);
    }
    
    /**
     * Update the site settings.
     *
     * @param Request $request
     * @return \Illuminate\Http\RedirectResponse
     */
    public function update(Request $request)
    {
        // Validate the incoming request
        $validated = $request->validate([
            'site_name' => 'required|string|max:100',
            'site_description' => 'nullable|string|max:255',
            'maintenance_mode' => 'boolean',
            'allow_user_registration' => 'boolean',
            'default_user_role' => 'required|in:user,editor',
            'default_editor_permissions.can_publish' => 'boolean',
            'default_editor_permissions.requires_approval' => 'boolean',
        ]);
        
        // Here you would save settings to database or config
        // For example:
        // Setting::updateOrCreate(['key' => 'site_name'], ['value' => $validated['site_name']]);
        
        return redirect()->route('admin.settings.index')
            ->with('success', 'Settings updated successfully.');
    }
} 