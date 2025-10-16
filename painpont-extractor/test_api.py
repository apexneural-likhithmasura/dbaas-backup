#!/usr/bin/env python3
"""
Test script for Topics API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_root():
    """Test root endpoint"""
    print_section("Testing Root Endpoint")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_health():
    """Test health check endpoint"""
    print_section("Testing Health Check Endpoint")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_stats():
    """Test statistics endpoint"""
    print_section("Testing Statistics Endpoint")
    response = requests.get(f"{BASE_URL}/topics/stats")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_all_topics():
    """Test get all topics with limit"""
    print_section("Testing Get All Topics (Limit 5)")
    response = requests.get(f"{BASE_URL}/topics?limit=5")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Total Topics: {data['total']}")
    print(f"Showing: {len(data['data'])} topics")
    for topic in data['data']:
        print(f"  - {topic['topic']} | Volume: {topic['volume']} | Growth: {topic['growth']}")

def test_filter_by_year():
    """Test filtering by time period"""
    print_section("Testing Filter by Time Period (2 Years)")
    response = requests.get(f"{BASE_URL}/topics?time_period=2 Years&limit=5")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Total Topics (2 Years): {data['total']}")
    print(f"Time Period Filter: {data['time_period_filter']}")
    print(f"Showing: {len(data['data'])} topics")
    for topic in data['data']:
        print(f"  - {topic['topic']} | Growth: {topic['growth']} | Period: {topic['time_period']}")
    
    print("\n" + "-"*70)
    print_section("Testing Filter by Time Period (10 Years)")
    response = requests.get(f"{BASE_URL}/topics?time_period=10 Years&limit=5")
    data = response.json()
    print(f"Total Topics (10 Years): {data['total']}")
    print(f"Showing: {len(data['data'])} topics")
    for topic in data['data']:
        print(f"  - {topic['topic']} | Growth: {topic['growth']} | Period: {topic['time_period']}")

def test_search():
    """Test search functionality"""
    print_section("Testing Search (AI related topics)")
    response = requests.get(f"{BASE_URL}/topics?search=AI")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Total AI Topics: {data['total']}")
    print(f"Topics found:")
    for topic in data['data']:
        print(f"  - {topic['topic']} | Volume: {topic['volume']} | Growth: {topic['growth']}")

def test_get_by_id():
    """Test get topic by ID"""
    print_section("Testing Get Topic by ID (ID: 1)")
    response = requests.get(f"{BASE_URL}/topics/1")
    print(f"Status Code: {response.status_code}")
    topic = response.json()
    print(f"Topic: {topic['topic']}")
    print(f"Volume: {topic['volume']}")
    print(f"Growth: {topic['growth']}")
    print(f"Time Period: {topic['time_period']}")
    print(f"Description: {topic['description'][:100]}...")

def test_pagination():
    """Test pagination"""
    print_section("Testing Pagination (Limit 3, Offset 5)")
    response = requests.get(f"{BASE_URL}/topics?limit=3&offset=5")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Total Topics: {data['total']}")
    print(f"Showing topics 6-8:")
    for topic in data['data']:
        print(f"  ID {topic['id']}: {topic['topic']}")

def main():
    """Run all tests"""
    print("\n" + "#"*70)
    print("#  TOPICS API TEST SUITE")
    print("#"*70)
    
    try:
        test_root()
        test_health()
        test_stats()
        test_all_topics()
        test_filter_by_year()
        test_search()
        test_get_by_id()
        test_pagination()
        
        print("\n" + "#"*70)
        print("#  ALL TESTS COMPLETED SUCCESSFULLY!")
        print("#"*70)
        print("\nAPI Documentation available at: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server.")
        print("Make sure the API is running: python3 pgmain.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()

