#!/usr/bin/env python3
"""
Test script for the complete integrated pipeline
"""

import requests
import time
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_pipeline_status():
    """Test if pipeline is available"""
    print("=" * 80)
    print("Testing Pipeline Status")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/pipeline/status")
    data = response.json()
    
    print(f"\nStatus: {data['status']}")
    print(f"Data: {json.dumps(data['data'], indent=2)}")
    
    if not data['data']['pain_point_extractor_available']:
        print("\n❌ Pain point extractor not available!")
        return False
    
    if not data['data']['openrouter_key_configured']:
        print("\n❌ OPENROUTER_API_KEY not configured!")
        return False
    
    print("\n✅ Pipeline is ready!")
    return True


def start_pipeline(market="productivity apps"):
    """Start the complete pipeline"""
    print("\n" + "=" * 80)
    print(f"Starting Pipeline for Market: {market}")
    print("=" * 80)
    
    request_data = {
        "market": market,
        "num_results": 10,  # Small number for testing
        "top_n": 5,
        "deep_top_k": 2,    # Analyze top 2 posts only
        "ai_model": "anthropic/claude-3.5-sonnet",
        "temperature": 0.7
    }
    
    print(f"\nRequest: {json.dumps(request_data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/pipeline/complete",
        json=request_data
    )
    
    if response.status_code != 200:
        print(f"\n❌ Error: {response.status_code}")
        print(response.json())
        return None
    
    data = response.json()
    job_id = data['data']['job_id']
    
    print(f"\n✅ Pipeline started!")
    print(f"Job ID: {job_id}")
    print(f"WebSocket URL: {data['data']['websocket_url']}")
    print(f"Status URL: {data['data']['status_url']}")
    
    return job_id


def track_progress(job_id):
    """Track pipeline progress by polling"""
    print("\n" + "=" * 80)
    print("Tracking Progress")
    print("=" * 80)
    
    while True:
        response = requests.get(f"{BASE_URL}/jobs/{job_id}/status")
        data = response.json()['data']
        
        status = data['status']
        print(f"\nStatus: {status}")
        
        if status == "completed":
            print("\n✅ Pipeline completed!")
            return True
        elif status == "failed":
            print(f"\n❌ Pipeline failed: {data.get('error')}")
            return False
        elif status == "running":
            print("⏳ Running...")
        
        time.sleep(5)  # Poll every 5 seconds


def get_result(job_id):
    """Get the final result"""
    print("\n" + "=" * 80)
    print("Getting Results")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/result")
    
    if response.status_code != 200:
        print(f"\n❌ Error: {response.status_code}")
        print(response.json())
        return None
    
    data = response.json()['data']
    
    # Display summary
    print("\n" + "=" * 80)
    print("PIPELINE RESULTS SUMMARY")
    print("=" * 80)
    
    print(f"\n📊 Market: {data['market']}")
    print(f"🕐 Timestamp: {data['timestamp']}")
    
    print(f"\n🔍 Reddit Analysis:")
    reddit = data['reddit_analysis']
    print(f"  • Posts found: {reddit['total_posts_found']}")
    print(f"  • Posts ranked: {reddit['posts_ranked']}")
    print(f"  • Posts analyzed: {reddit['posts_deep_analyzed']}")
    
    print(f"\n😰 Pain Point Analysis:")
    pain = data['pain_point_analysis']
    print(f"  • Total pain points: {pain['total_pain_points']}")
    print(f"  • Categories: {pain['categories']}")
    print(f"  • Summary: {pain['summary'][:100]}...")
    
    print(f"\n💡 Market Gaps:")
    gaps = data['market_gaps']
    print(f"  • Total solutions: {gaps['total_solutions']}")
    print(f"  • Frameworks: {gaps['frameworks']}")
    print(f"  • Executive Summary: {gaps['executive_summary'][:100]}...")
    
    # Show top opportunities
    if gaps['top_opportunities']:
        print(f"\n🎯 Top Opportunities:")
        for opp in gaps['top_opportunities'][:3]:
            print(f"\n  {opp['rank']}. {opp['solution_name']}")
            print(f"     Market Size: {opp['market_size_potential'][:80]}...")
            print(f"     Advantage: {opp['competitive_advantage'][:80]}...")
    
    # Save full result
    output_file = f"pipeline_result_{job_id}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full result saved to: {output_file}")
    print(f"📁 Output directory: {data['output_dir']}")
    
    return data


def main():
    """Main test function"""
    print("\n" + "=" * 80)
    print("COMPLETE PIPELINE TEST")
    print("=" * 80)
    
    # Test 1: Check status
    if not test_pipeline_status():
        print("\n❌ Pipeline not ready. Exiting.")
        return
    
    # Test 2: Start pipeline
    market = input("\nEnter market to explore (or press Enter for default 'productivity apps'): ").strip()
    if not market:
        market = "productivity apps"
    
    job_id = start_pipeline(market)
    if not job_id:
        print("\n❌ Failed to start pipeline. Exiting.")
        return
    
    # Test 3: Track progress
    success = track_progress(job_id)
    if not success:
        print("\n❌ Pipeline failed. Exiting.")
        return
    
    # Test 4: Get results
    result = get_result(job_id)
    if not result:
        print("\n❌ Failed to get results. Exiting.")
        return
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE!")
    print("=" * 80)
    print("\n✅ Pipeline integration working successfully!")
    print(f"\n📖 See INTEGRATED_API_DOCS.md for complete documentation")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


