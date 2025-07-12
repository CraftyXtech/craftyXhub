#!/usr/bin/env python3
"""
Test script for CraftyXhub API endpoints - Registration and Login
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

def test_registration():
    """Test user registration endpoint"""
    print("🧪 Testing Registration Endpoint...")
    
    # Test data
    registration_data = {
        "name": "John Doe",
        "email": "john.doe@test.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
        "terms_accepted": True,
        "newsletter_enabled": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            response_data = response.json()
            print(f"📊 Response: {json.dumps(response_data, indent=2)}")
            return response_data
        else:
            print("❌ Registration failed!")
            print(f"📊 Error Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: FastAPI server not running or not accessible")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_registration_validation():
    """Test registration with various validation scenarios"""
    print("\n🧪 Testing Registration Validation...")
    
    # Test cases
    test_cases = [
        {
            "name": "Weak Password",
            "data": {
                "name": "Test User",
                "email": "test@example.com",
                "password": "weak",
                "confirm_password": "weak",
                "terms_accepted": True
            },
            "expected_status": 422
        },
        {
            "name": "Password Mismatch",
            "data": {
                "name": "Test User",
                "email": "test2@example.com",
                "password": "SecurePass123!",
                "confirm_password": "DifferentPass123!",
                "terms_accepted": True
            },
            "expected_status": 422
        },
        {
            "name": "Invalid Email",
            "data": {
                "name": "Test User",
                "email": "invalid-email",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "terms_accepted": True
            },
            "expected_status": 422
        },
        {
            "name": "Terms Not Accepted",
            "data": {
                "name": "Test User",
                "email": "test3@example.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "terms_accepted": False
            },
            "expected_status": 422
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        try:
            response = requests.post(
                f"{BASE_URL}/v1/auth/register",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == test_case["expected_status"]:
                print(f"✅ Expected validation error received (Status: {response.status_code})")
                if response.status_code == 422:
                    error_details = response.json()
                    print(f"📊 Validation errors: {json.dumps(error_details.get('detail', []), indent=2)}")
            else:
                print(f"❌ Unexpected status code: {response.status_code} (expected: {test_case['expected_status']})")
                print(f"📊 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: FastAPI server not running")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def test_login():
    """Test login endpoint"""
    print("\n🧪 Testing Login Endpoint...")
    
    # Test login with OAuth2PasswordRequestForm format
    login_data = {
        "username": "john.doe@test.com",  # Most systems use email as username
        "password": "SecurePass123!"
    }
    
    try:
        # OAuth2PasswordRequestForm expects form data, not JSON
        response = requests.post(
            f"{BASE_URL}/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            response_data = response.json()
            print(f"📊 Response: {json.dumps(response_data, indent=2)}")
            return response_data.get("access_token")
        else:
            print("❌ Login failed!")
            print(f"📊 Error Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: FastAPI server not running")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_protected_endpoint(token: str):
    """Test accessing a protected endpoint with the token"""
    print("\n🧪 Testing Protected Endpoint...")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/v1/auth/users/me",
            headers=headers
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Protected endpoint access successful!")
            response_data = response.json()
            print(f"📊 User data: {json.dumps(response_data, indent=2)}")
        else:
            print("❌ Protected endpoint access failed!")
            print(f"📊 Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: FastAPI server not running")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_check():
    """Test if the API is running"""
    print("🧪 Testing API Health Check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running!")
            health_data = response.json()
            print(f"📊 Health status: {json.dumps(health_data, indent=2)}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: FastAPI server not running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test runner"""
    print("🚀 Starting CraftyXhub API Tests\n")
    
    # Check if API is running
    if not test_health_check():
        print("\n❌ Cannot proceed with tests - API server is not accessible")
        return
    
    print("\n" + "="*50)
    
    # Test registration
    registration_result = test_registration()
    
    # Test registration validation
    test_registration_validation()
    
    print("\n" + "="*50)
    
    # Test login
    token = test_login()
    
    # Test protected endpoint if login was successful
    if token:
        test_protected_endpoint(token)
    
    print("\n" + "="*50)
    print("🏁 Tests completed!")

if __name__ == "__main__":
    main() 