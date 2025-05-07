<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Artisan;

class AdminSystemController extends Controller
{
    /**
     * Display the system information and maintenance page.
     *
     * @return Response
     */
    public function index(): Response
    {
        // Get system information
        $systemInfo = [
            'php_version' => phpversion(),
            'laravel_version' => app()->version(),
            'database_type' => DB::connection()->getPdo()->getAttribute(\PDO::ATTR_DRIVER_NAME),
            'server_software' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown',
            'memory_limit' => ini_get('memory_limit'),
            'max_execution_time' => ini_get('max_execution_time') . ' seconds',
            'upload_max_filesize' => ini_get('upload_max_filesize'),
            'post_max_size' => ini_get('post_max_size'),
        ];
        
        // Get application statistics
        $stats = [
            'cache_driver' => config('cache.default'),
            'session_driver' => config('session.driver'),
            'queue_connection' => config('queue.default'),
        ];
        
        return Inertia::render('Admin/System/Index', [
            'systemInfo' => $systemInfo,
            'stats' => $stats,
        ]);
    }
    
    /**
     * Clear various application caches.
     *
     * @param Request $request
     * @return \Illuminate\Http\RedirectResponse
     */
    public function clearCache(Request $request)
    {
        // Validate the type of cache to clear
        $validated = $request->validate([
            'type' => 'required|in:application,view,route,config,all',
        ]);
        
        $message = 'Cache cleared successfully.';
        
        switch ($validated['type']) {
            case 'application':
                Artisan::call('cache:clear');
                break;
            case 'view':
                Artisan::call('view:clear');
                break;
            case 'route':
                Artisan::call('route:clear');
                break;
            case 'config':
                Artisan::call('config:clear');
                break;
            case 'all':
                Artisan::call('cache:clear');
                Artisan::call('view:clear');
                Artisan::call('route:clear');
                Artisan::call('config:clear');
                $message = 'All caches cleared successfully.';
                break;
        }
        
        return redirect()->route('admin.system.index')
            ->with('success', $message);
    }
    
    /**
     * Run database migrations.
     *
     * @return \Illuminate\Http\RedirectResponse
     */
    public function runMigrations()
    {
        try {
            Artisan::call('migrate', ['--force' => true]);
            $output = Artisan::output();
            
            return redirect()->route('admin.system.index')
                ->with('success', 'Migrations completed successfully.')
                ->with('output', $output);
        } catch (\Exception $e) {
            return redirect()->route('admin.system.index')
                ->with('error', 'Migration failed: ' . $e->getMessage());
        }
    }
} 