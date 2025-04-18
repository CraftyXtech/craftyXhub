<?php

namespace App\Services\Admin;

use App\Models\User;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;
use Illuminate\Http\Request;

class UserManagementService
{
    /**
     * Get users with pagination and filtering
     *
     * @param Request $request
     * @return LengthAwarePaginator
     */
    public function getUsers(Request $request): LengthAwarePaginator
    {
        $perPage = $request->per_page ?? 10;
        
        return User::when($request->search, function ($query, $search) {
                $query->where(function($q) use ($search) {
                    $q->where('name', 'like', "%{$search}%")
                      ->orWhere('email', 'like', "%{$search}%");
                });
            })
            ->when($request->role, function ($query, $role) {
                $query->where('role', $role);
            })
            ->when($request->sort_by, function ($query, $sortBy) use ($request) {
                $direction = $request->sort_direction ?? 'asc';
                $query->orderBy($sortBy, $direction);
            }, function ($query) {
                $query->orderBy('created_at', 'desc');
            })
            ->paginate($perPage)
            ->withQueryString();
    }

    /**
     * Update user role
     *
     * @param User $user
     * @param string $role
     * @return User
     */
    public function updateUserRole(User $user, string $role): User
    {
        $oldRole = $user->role;
        $user->role = $role;
        $user->save();
        
        Log::info("User role updated", [
            'user_id' => $user->id,
            'old_role' => $oldRole,
            'new_role' => $role,
        ]);
        
        return $user;
    }

    /**
     * Delete a user
     *
     * @param User $user
     * @return bool
     */
    public function deleteUser(User $user): bool
    {
        Log::info("User deleted", [
            'user_id' => $user->id,
            'email' => $user->email,
        ]);
        
        return $user->delete();
    }

    /**
     * Get user statistics
     *
     * @return array
     */
    public function getUserStats(): array
    {
        return Cache::remember('admin_user_stats', 300, function () {
            return [
                'total' => User::count(),
                'admins' => User::where('role', 'admin')->count(),
                'editors' => User::where('role', 'editor')->count(),
                'regular_users' => User::where('role', 'user')->count(),
                'recent_signups' => User::orderBy('created_at', 'desc')
                                        ->limit(5)
                                        ->get(['id', 'name', 'email', 'created_at']),
            ];
        });
    }
} 