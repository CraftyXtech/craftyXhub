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

        // Assuming User model has isAdmin() method or uses Spatie Permission pkg
        // Replace 'isAdmin' with 'hasRole('Admin')' if using Spatie pkg
        if (!$request->user()->isAdmin()) {
            Log::warning('Unauthorized admin access attempt.', [
                'user_id' => $request->user()->id,
                'email' => $request->user()->email,
                'ip_address' => $request->ip(),
                'route' => $request->path(),
            ]);
            return redirect('/')->with('error', 'Unauthorized access.');
        }

        return $next($request);
    }
} 