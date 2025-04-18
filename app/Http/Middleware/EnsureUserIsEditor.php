<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\Response;

class EnsureUserIsEditor
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        if (!Auth::check()) {
            return redirect('login');
        }

        // Allow access if the user is an Editor OR an Admin
        // Replace with hasAnyRole(['Editor', 'Admin']) if using Spatie pkg
        if (!$request->user()->isEditor() && !$request->user()->isAdmin()) {
             Log::warning('Unauthorized editor access attempt.', [
                'user_id' => $request->user()->id,
                'email' => $request->user()->email,
                'ip_address' => $request->ip(),
                'route' => $request->path(),
            ]);
            // Redirect non-editors/non-admins to home
            return redirect('/')->with('error', 'You do not have permission to access this page.');
        }

        return $next($request);
    }
} 