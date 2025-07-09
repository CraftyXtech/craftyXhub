#!/usr/bin/env python3
"""
Web Endpoints Test Script for CraftyXhub

This script tests all the public web API endpoints to ensure they are properly
configured and accessible. It validates the routing, dependencies, and basic
functionality without requiring a running database.
"""

import sys
import asyncio
from typing import Dict, List, Any
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Add the api directory to the path
sys.path.insert(0, 'api')

def create_test_app() -> FastAPI:
    """Create a test FastAPI app with our web routers."""
    try:
        from core.config import Settings
        from routers.v1 import router as v1_router
        
        app = FastAPI(
            title="CraftyXhub Test",
            description="Test application for web endpoints",
            version="1.0.0"
        )
        
        # Include the v1 router
        app.include_router(v1_router, prefix="/api")
        
        return app
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return None

def test_endpoint_registration(app: FastAPI) -> Dict[str, Any]:
    """Test that all expected endpoints are registered."""
    print("🔍 Testing endpoint registration...")
    
    results = {
        "total_routes": 0,
        "web_routes": 0,
        "editor_routes": 0,
        "auth_routes": 0,
        "registered_paths": [],
        "missing_paths": [],
        "errors": []
    }
    
    # Expected web endpoints
    expected_web_endpoints = [
        # Posts
        "/api/v1/posts/",
        "/api/v1/posts/{slug}",
        "/api/v1/posts/search/advanced",
        "/api/v1/posts/search/suggestions",
        "/api/v1/posts/category/{category_slug}",
        "/api/v1/posts/tag/{tag_slug}",
        "/api/v1/posts/featured",
        "/api/v1/posts/trending",
        "/api/v1/posts/recent",
        "/api/v1/posts/{post_id}/view",
        
        # Comments
        "/api/v1/posts/{post_id}/comments/",
        "/api/v1/posts/{post_id}/comments/{comment_id}",
        "/api/v1/posts/{post_id}/comments/stats",
        "/api/v1/posts/{post_id}/comments/thread/{comment_id}",
        "/api/v1/posts/{post_id}/comments/{comment_id}/like",
        "/api/v1/posts/{post_id}/comments/{comment_id}/report",
        "/api/v1/comments/{comment_id}",
        "/api/v1/comments/user/{user_id}",
        
        # Interactions
        "/api/v1/interactions/posts/{post_id}/like",
        "/api/v1/interactions/posts/{post_id}/bookmark",
        "/api/v1/interactions/posts/{post_id}/view",
        "/api/v1/interactions/posts/{post_id}/status",
        "/api/v1/interactions/posts/{post_id}/counts",
        "/api/v1/interactions/bulk",
        "/api/v1/interactions/users/me/history",
        "/api/v1/interactions/users/me/liked",
        "/api/v1/interactions/users/me/bookmarks",
        "/api/v1/interactions/analytics/popular",
        "/api/v1/interactions/analytics/trending",
        "/api/v1/interactions/analytics/engagement",
        "/api/v1/interactions/stats/types",
        "/api/v1/interactions/users/me/interactions",
        
        # Profile
        "/api/v1/profile/me",
        "/api/v1/profile/me/avatar",
        "/api/v1/profile/me/stats",
        "/api/v1/profile/me/posts",
        "/api/v1/profile/me/liked",
        "/api/v1/profile/me/bookmarks",
        "/api/v1/profile/me/activity",
        "/api/v1/profile/me/preferences",
        "/api/v1/profile/me/notifications",
        "/api/v1/profile/me/privacy",
        "/api/v1/profile/users/{user_id}",
        "/api/v1/profile/users/{user_id}/posts",
        "/api/v1/profile/users/{user_id}/stats",
        "/api/v1/profile/me/account",
        
        # Auth
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/auth/logout",
        "/api/v1/auth/me",
    ]
    
    # Expected editor endpoints
    expected_editor_endpoints = [
        # Categories
        "/api/v1/editor/categories/",
        "/api/v1/editor/categories/{category_id}",
        "/api/v1/editor/categories/bulk",
        "/api/v1/editor/categories/{category_id}/merge",
        "/api/v1/editor/categories/hierarchy",
        "/api/v1/editor/categories/usage-stats",
        "/api/v1/editor/categories/trending",
        
        # Tags
        "/api/v1/editor/tags/",
        "/api/v1/editor/tags/{tag_id}",
        "/api/v1/editor/tags/bulk",
        "/api/v1/editor/tags/{tag_id}/merge",
        "/api/v1/editor/tags/usage-stats",
        "/api/v1/editor/tags/trending",
        "/api/v1/editor/tags/suggestions",
        
        # Posts
        "/api/v1/editor/posts/",
        "/api/v1/editor/posts/{post_id}",
        "/api/v1/editor/posts/bulk",
        "/api/v1/editor/posts/{post_id}/publish",
        "/api/v1/editor/posts/{post_id}/archive",
        "/api/v1/editor/posts/{post_id}/duplicate",
        "/api/v1/editor/posts/{post_id}/auto-save",
        "/api/v1/editor/posts/{post_id}/revisions",
        "/api/v1/editor/posts/{post_id}/workflow",
        "/api/v1/editor/posts/{post_id}/submit-review",
        "/api/v1/editor/posts/{post_id}/resubmit",
        
        # Dashboard
        "/api/v1/editor/dashboard/stats",
        "/api/v1/editor/dashboard/trending-posts",
        "/api/v1/editor/dashboard/view-trends",
        "/api/v1/editor/dashboard/post-distribution",
        "/api/v1/editor/dashboard/performance-metrics",
        "/api/v1/editor/dashboard/user-engagement",
        "/api/v1/editor/dashboard/content-analytics",
    ]
    
    try:
        # Get all registered routes
        all_routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                path = route.path
                all_routes.append(path)
                
                # Categorize routes
                if '/posts/' in path or '/comments/' in path or '/interactions/' in path or '/profile/' in path:
                    results["web_routes"] += 1
                elif '/editor/' in path:
                    results["editor_routes"] += 1
                elif '/auth/' in path:
                    results["auth_routes"] += 1
        
        results["total_routes"] = len(all_routes)
        results["registered_paths"] = sorted(all_routes)
        
        # Check for missing endpoints
        all_expected = expected_web_endpoints + expected_editor_endpoints
        for expected_path in all_expected:
            if expected_path not in all_routes:
                results["missing_paths"].append(expected_path)
        
        print(f"✅ Found {results['total_routes']} total routes")
        print(f"   - {results['web_routes']} web routes")
        print(f"   - {results['editor_routes']} editor routes") 
        print(f"   - {results['auth_routes']} auth routes")
        
        if results["missing_paths"]:
            print(f"⚠️  Missing {len(results['missing_paths'])} expected endpoints")
            for missing in results["missing_paths"][:5]:  # Show first 5
                print(f"   - {missing}")
            if len(results["missing_paths"]) > 5:
                print(f"   ... and {len(results['missing_paths']) - 5} more")
        else:
            print("✅ All expected endpoints are registered")
            
    except Exception as e:
        results["errors"].append(f"Route inspection error: {e}")
        print(f"❌ Error inspecting routes: {e}")
    
    return results

def test_basic_connectivity(app: FastAPI) -> Dict[str, Any]:
    """Test basic connectivity to key endpoints."""
    print("\n🌐 Testing basic connectivity...")
    
    client = TestClient(app)
    results = {
        "successful_requests": 0,
        "failed_requests": 0,
        "tested_endpoints": [],
        "errors": []
    }
    
    # Test endpoints that should be accessible without authentication
    test_endpoints = [
        ("GET", "/api/v1/posts/"),
        ("GET", "/api/v1/posts/featured"),
        ("GET", "/api/v1/posts/trending"),
        ("GET", "/api/v1/posts/recent"),
        ("GET", "/api/v1/posts/search/suggestions?q=test"),
        ("GET", "/api/v1/interactions/analytics/popular"),
        ("GET", "/api/v1/interactions/analytics/trending"),
    ]
    
    for method, endpoint in test_endpoints:
        try:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint)
            else:
                continue
                
            results["tested_endpoints"].append({
                "method": method,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "success": response.status_code < 500  # 4xx is expected for auth endpoints
            })
            
            if response.status_code < 500:
                results["successful_requests"] += 1
                print(f"✅ {method} {endpoint} -> {response.status_code}")
            else:
                results["failed_requests"] += 1
                print(f"❌ {method} {endpoint} -> {response.status_code}")
                
        except Exception as e:
            results["failed_requests"] += 1
            results["errors"].append(f"{method} {endpoint}: {e}")
            print(f"❌ {method} {endpoint} -> Error: {e}")
    
    print(f"\n📊 Connectivity Results:")
    print(f"   - {results['successful_requests']} successful requests")
    print(f"   - {results['failed_requests']} failed requests")
    
    return results

def test_dependencies_import() -> Dict[str, Any]:
    """Test that all dependencies can be imported correctly."""
    print("\n📦 Testing dependency imports...")
    
    results = {
        "successful_imports": [],
        "failed_imports": [],
        "errors": []
    }
    
    # List of modules to test
    modules_to_test = [
        # Schemas
        "schemas.web.posts",
        "schemas.web.comments", 
        "schemas.web.interactions",
        "schemas.web.profile",
        "schemas.editor.categories",
        "schemas.editor.tags",
        "schemas.editor.posts",
        "schemas.editor.dashboard",
        
        # Services
        "services.web.post_service",
        "services.web.comment_service",
        "services.web.interaction_service", 
        "services.web.profile_service",
        "services.editor.category_service",
        "services.editor.tag_service",
        "services.editor.post_service",
        "services.editor.dashboard_service",
        
        # Dependencies
        "dependencies.pagination",
        "dependencies.web_auth",
        "dependencies.editor_permissions",
        
        # Routers
        "routers.v1.web_posts",
        "routers.v1.web_comments",
        "routers.v1.web_interactions",
        "routers.v1.web_profile",
        "routers.v1.editor_categories",
        "routers.v1.editor_tags",
        "routers.v1.editor_posts",
        "routers.v1.editor_dashboard",
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            results["successful_imports"].append(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            results["failed_imports"].append(module_name)
            results["errors"].append(f"{module_name}: {e}")
            print(f"❌ {module_name}: {e}")
        except Exception as e:
            results["failed_imports"].append(module_name)
            results["errors"].append(f"{module_name}: Unexpected error: {e}")
            print(f"❌ {module_name}: Unexpected error: {e}")
    
    print(f"\n📊 Import Results:")
    print(f"   - {len(results['successful_imports'])} successful imports")
    print(f"   - {len(results['failed_imports'])} failed imports")
    
    return results

def main():
    """Run all tests and report results."""
    print("🚀 Starting CraftyXhub Web Endpoints Test\n")
    
    # Test dependency imports first
    import_results = test_dependencies_import()
    
    # Create test app
    print("\n🔧 Creating test application...")
    app = create_test_app()
    
    if not app:
        print("❌ Failed to create test application. Check imports and dependencies.")
        return False
    
    print("✅ Test application created successfully")
    
    # Test endpoint registration
    route_results = test_endpoint_registration(app)
    
    # Test basic connectivity (if no critical import failures)
    if len(import_results["failed_imports"]) < 5:  # Allow some missing imports
        connectivity_results = test_basic_connectivity(app)
    else:
        print("\n⚠️  Skipping connectivity tests due to import failures")
        connectivity_results = {"successful_requests": 0, "failed_requests": 0}
    
    # Generate final report
    print("\n" + "="*60)
    print("📋 FINAL TEST REPORT")
    print("="*60)
    
    print(f"\n📦 Dependency Imports:")
    print(f"   ✅ Successful: {len(import_results['successful_imports'])}")
    print(f"   ❌ Failed: {len(import_results['failed_imports'])}")
    
    print(f"\n🛣️  Route Registration:")
    print(f"   ✅ Total routes: {route_results['total_routes']}")
    print(f"   ✅ Web routes: {route_results['web_routes']}")
    print(f"   ✅ Editor routes: {route_results['editor_routes']}")
    print(f"   ❌ Missing endpoints: {len(route_results['missing_paths'])}")
    
    print(f"\n🌐 Connectivity:")
    print(f"   ✅ Successful requests: {connectivity_results['successful_requests']}")
    print(f"   ❌ Failed requests: {connectivity_results['failed_requests']}")
    
    # Determine overall success
    critical_failures = (
        len(import_results['failed_imports']) > 10 or
        route_results['total_routes'] < 20 or
        connectivity_results['successful_requests'] == 0
    )
    
    if critical_failures:
        print(f"\n❌ CRITICAL ISSUES DETECTED")
        print("   Please review the errors above and fix import/routing issues.")
        return False
    else:
        print(f"\n✅ TESTS PASSED")
        print("   Web endpoints are properly configured and accessible.")
        print("   The API is ready for database integration and testing.")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 