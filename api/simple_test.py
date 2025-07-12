import httpx
import asyncio
import json

async def test_api():
    base_url = "http://127.0.0.1:8000"
    
    async with httpx.AsyncClient() as client:
        try:
            # Test health endpoint
            print("🧪 Testing health endpoint...")
            response = await client.get(f"{base_url}/health")
            print(f"Health Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Health Response: {response.json()}")
            else:
                print(f"Health Error: {response.text}")
            
            # Test registration
            print("\n🧪 Testing registration endpoint...")
            registration_data = {
                "name": "John Doe",
                "email": "john.doe@test.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "terms_accepted": True,
                "newsletter_enabled": True
            }
            
            response = await client.post(
                f"{base_url}/v1/auth/register",
                json=registration_data
            )
            print(f"Registration Status: {response.status_code}")
            if response.status_code == 201:
                print(f"Registration Success: {response.json()}")
            else:
                print(f"Registration Error: {response.text}")
                
            # Test login
            print("\n🧪 Testing login endpoint...")
            login_data = {
                "username": "john.doe@test.com",
                "password": "SecurePass123!"
            }
            
            response = await client.post(
                f"{base_url}/v1/auth/token",
                data=login_data  # Form data for OAuth2PasswordRequestForm
            )
            print(f"Login Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Login Success: {response.json()}")
                token = response.json().get("access_token")
                
                # Test protected endpoint
                if token:
                    print("\n🧪 Testing protected endpoint...")
                    headers = {"Authorization": f"Bearer {token}"}
                    response = await client.get(
                        f"{base_url}/v1/auth/users/me",
                        headers=headers
                    )
                    print(f"Protected Endpoint Status: {response.status_code}")
                    if response.status_code == 200:
                        print(f"User Data: {response.json()}")
                    else:
                        print(f"Protected Endpoint Error: {response.text}")
            else:
                print(f"Login Error: {response.text}")
                
        except Exception as e:
            print(f"Test Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api()) 