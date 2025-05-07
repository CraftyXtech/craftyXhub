<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\Response;

class EnsureUserIsAdmin
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        if (!Auth::check()) {
            // Should be handled by the 'auth' middleware first, but as a safeguard
            return redirect('login');
        }

        $currentRoute = $request->route()->getName();
        $user = $request->user();
        
        // Special case: Allow editors to access admin.dashboard
        if ($currentRoute === 'admin.dashboard' && $user->isEditor()) {
            return $next($request);
        }
        
        // Require admin role for all other admin routes
        if (!$user->isAdmin()) {
            Log::warning('Unauthorized admin access attempt.', [
                'user_id' => $user->id,
                'email' => $user->email,
                'ip_address' => $request->ip(),
                'route' => $request->path(),
            ]);
            
            // If it's an editor, redirect them to dashboard
            if ($user->isEditor()) {
                return redirect()->route('admin.dashboard')
                    ->with('error', 'You do not have permission to access that page.');
            }
            
            // For other users, redirect to home
            return redirect('/')->with('error', 'Unauthorized access.');
        }

        return $next($request);
    }
} 