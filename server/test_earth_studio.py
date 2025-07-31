#!/usr/bin/env python3
"""
Test Google Earth Studio Integration
Test Earth Studio functionality without requiring OpenAI API
"""

import requests
import json

def test_earth_studio_endpoints():
    """Test Earth Studio API endpoints"""
    
    print("🎬 Testing Google Earth Studio Functionality")
    print("=" * 45)
    
    base_url = "http://localhost:8000"
    
    # Test cases
    test_cases = [
        {
            "name": "Earth Studio Service Status",
            "endpoint": f"{base_url}/api/earth-studio/test",
            "method": "GET"
        },
        {
            "name": "Create Project from Locations", 
            "endpoint": f"{base_url}/api/earth-studio/create-project",
            "method": "POST",
            "data": {
                "locations": ["New York", "Paris", "Tokyo"],
                "timeline": ["Chapter 1: New York Adventure", "Chapter 2: Paris Romance", "Chapter 3: Tokyo Discovery"],
                "title": "Test Journey"
            }
        },
        {
            "name": "Preview Animation",
            "endpoint": f"{base_url}/api/earth-studio/preview", 
            "method": "POST",
            "data": {
                "locations": [
                    {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
                    {"name": "Paris", "latitude": 48.8566, "longitude": 2.3522}
                ]
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n🧪 Testing: {test['name']}")
        print("-" * 30)
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['endpoint'], timeout=10)
            else:
                response = requests.post(
                    test['endpoint'], 
                    json=test.get('data', {}),
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Success")
                
                # Try to parse JSON response
                try:
                    data = response.json()
                    
                    # Display key information
                    if 'project' in data:
                        project = data['project']
                        print(f"📽️ Project Title: {project.get('title', 'Unknown')}")
                        print(f"⏱️ Video Duration: {project.get('duration', 0):.1f} seconds")
                        print(f"🎯 Keyframe Count: {len(project.get('keyframes', []))}")
                    
                    if 'keyframes' in data:
                        keyframes = data['keyframes']
                        print(f"🎯 Keyframe Count: {len(keyframes)}")
                    
                    if 'preview' in data:
                        preview = data['preview']
                        print(f"⏱️ Estimated Duration: {preview.get('duration', 0):.1f} seconds")
                        print(f"📍 Location Count: {preview.get('locations_count', 0)}")
                
                except json.JSONDecodeError:
                    print("📄 Response is not JSON format")
                    print(f"Content preview: {response.text[:100]}...")
                    
            elif response.status_code == 500:
                print("❌ Server Error")
                try:
                    error_data = response.json()
                    print(f"Error Message: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"Error Details: {response.text[:200]}")
                    
            else:
                print(f"⚠️ Unexpected Status Code: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Failed - Make sure server is running")
            print("💡 Run: PORT=8000 python app.py")
            
        except requests.exceptions.Timeout:
            print("⏱️ Request Timeout")
            
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")

def test_earth_studio_without_ai():
    """Test Earth Studio functionality without AI dependencies"""
    
    print(f"\n🎯 Testing Independent Earth Studio Functionality")
    print("=" * 40)
    
    # Use predefined coordinates, no AI services needed
    test_locations = [
        {"name": "San Francisco", "latitude": 37.7749, "longitude": -122.4194},
        {"name": "Los Angeles", "latitude": 34.0522, "longitude": -118.2437},
        {"name": "Las Vegas", "latitude": 36.1699, "longitude": -115.1398}
    ]
    
    test_data = {
        "locations": test_locations,
        "timeline": [
            "Chapter 1: Golden Gate Bridge",
            "Chapter 2: Hollywood Hills", 
            "Chapter 3: Vegas Lights"
        ],
        "title": "California Road Trip"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/earth-studio/create-project",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Earth Studio project created successfully!")
            
            project = data.get('project', {})
            print(f"📽️ Project: {project.get('title', 'Unknown')}")
            print(f"⏱️ Duration: {project.get('duration', 0):.1f} seconds")
            print(f"🎯 Keyframes: {len(project.get('keyframes', []))}")
            
            # Check if Earth Studio JSON is generated
            if 'earth_studio_json' in data:
                print("📄 Earth Studio JSON generated")
                json_data = json.loads(data['earth_studio_json'])
                print(f"🎬 Project Name: {json_data.get('project', {}).get('name', 'Unknown')}")
            
            return True
            
        else:
            print(f"❌ Project creation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎬 Google Earth Studio Functionality Test")
    print("These tests do not require OpenAI API key")
    print("=" * 50)
    
    # First test server connection
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Server connection normal")
        else:
            print("⚠️ Server response abnormal")
    except:
        print("❌ Unable to connect to server")
        print("💡 Please start server first: PORT=8000 python app.py")
        exit(1)
    
    # Run tests
    test_earth_studio_endpoints()
    
    print(f"\n" + "=" * 50)
    print("🎯 Independent Functionality Test (No AI Required)")
    test_earth_studio_without_ai()
    
    print(f"\n💡 Next Steps:")
    print("1. If tests succeed, you can develop frontend integration")
    print("2. You can add more predefined travel routes")
    print("3. Optimize Earth Studio animation parameters")
    print("4. Add AI enhancement features after getting OpenAI key")