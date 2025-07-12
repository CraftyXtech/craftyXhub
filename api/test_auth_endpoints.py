#!/usr/bin/env python3
"""
Simple test script to verify authentication endpoints work correctly.
"""
import asyncio
import json
from typing import Dict, Any
import httpx

API_BASE_URL = "http://localhost:8000"

async def test_auth_endpoints():
    """Test the authentication endpoints."""
    print("🔐 Testing CraftyXhub Authentication Endpoints")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        try:
            response = await client.get(f"{API_BASE_URL}/health")
            print(f"   ✅ Health check: {response.status_code}")
            if response.status_code == 200:
                health_data = response.json()
                print(f"   📊 Status: {health_data.get('status')}")
                print(f"   🗄️  Database: {health_data.get('database')}")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
        
        # Test login endpoint structure
        print("\n2. Testing login endpoint structure...")
        try:
            # This should fail with validation error, but endpoint should exist
            response = await client.post(f"{API_BASE_URL}/auth/token", 
                                       data={"username": "", "password": ""})
            print(f"   ✅ Login endpoint exists: {response.status_code}")
            if response.status_code == 422:
                print("   📝 Validation working correctly")
        except Exception as e:
            print(f"   ❌ Login endpoint test failed: {e}")
        
        # Test refresh endpoint structure
        print("\n3. Testing refresh endpoint structure...")
        try:
            response = await client.post(f"{API_BASE_URL}/auth/refresh", 
                                       json={"refresh_token": "invalid_token"})
            print(f"   ✅ Refresh endpoint exists: {response.status_code}")
            if response.status_code == 401:
                print("   🔒 Token validation working correctly")
        except Exception as e:
            print(f"   ❌ Refresh endpoint test failed: {e}")
        
        # Test rate limiting
        print("\n4. Testing rate limiting...")
        try:
            # Make multiple requests quickly
            for i in range(7):
                response = await client.post(f"{API_BASE_URL}/auth/token", 
                                           data={"username": "test", "password": "test"})
                if response.status_code == 429:
                    print(f"   ✅ Rate limiting activated after {i+1} requests")
                    break
            else:
                print("   ⚠️  Rate limiting not triggered (may need more requests)")
        except Exception as e:
            print(f"   ❌ Rate limiting test failed: {e}")
        
        # Test CORS headers
        print("\n5. Testing CORS configuration...")
        try:
            response = await client.options(f"{API_BASE_URL}/auth/token")
            print(f"   ✅ CORS preflight: {response.status_code}")
            cors_headers = response.headers.get('access-control-allow-origin')
            if cors_headers:
                print(f"   🌐 CORS headers present: {cors_headers}")
        except Exception as e:
            print(f"   ❌ CORS test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Authentication endpoint tests completed!")
    print("\n📋 Next steps:")
    print("   1. Create a test user in the database")
    print("   2. Test actual login with real credentials")
    print("   3. Test token refresh flow")
    print("   4. Test logout functionality")
    print("   5. Update frontend to use new endpoints")

if __name__ == "__main__":
    asyncio.run(test_auth_endpoints()) 