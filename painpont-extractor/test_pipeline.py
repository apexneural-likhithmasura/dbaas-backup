#!/usr/bin/env python3
"""
Test script to validate the pipeline structure and Pydantic models.
This test doesn't require actual JSON files or API keys.
"""

import json
import tempfile
import os
import sys
from pathlib import Path
import importlib.util

# Import module with hyphen in name
spec = importlib.util.spec_from_file_location("json_extraction", "json-extraction.py")
json_extraction = importlib.util.module_from_spec(spec)
sys.modules['json_extraction'] = json_extraction
spec.loader.exec_module(json_extraction)


def create_sample_json_file(file_path: str, format_type: str = "simple"):
    """Create a sample JSON file for testing."""
    if format_type == "simple":
        data = {
            "post": {
                "title": "Test Post - Looking for productivity app recommendations",
                "selftext": "I've been struggling to find a good productivity app that works for me. Most are too complex or don't sync properly."
            },
            "comments": [
                {
                    "body": "I've tried over 10 different apps and they all have the same issue - terrible syncing between devices.",
                    "replies": [
                        {
                            "body": "Same here! I just gave up and use a simple text file now."
                        }
                    ]
                },
                {
                    "body": "The main problem is that these apps are either too simple and lack features, or too complex with features I don't need."
                }
            ]
        }
    else:  # Reddit API format
        data = [
            {
                "kind": "Listing",
                "data": {
                    "children": [
                        {
                            "kind": "t3",
                            "data": {
                                "title": "Test Post - Reddit API Format",
                                "selftext": "This is a test post in Reddit API format."
                            }
                        }
                    ]
                }
            },
            {
                "kind": "Listing",
                "data": {
                    "children": [
                        {
                            "kind": "t1",
                            "data": {
                                "body": "First comment",
                                "replies": ""
                            }
                        },
                        {
                            "kind": "t1",
                            "data": {
                                "body": "Second comment with pain point about bugs",
                                "replies": ""
                            }
                        }
                    ]
                }
            }
        ]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    return file_path


def test_pydantic_models():
    """Test Pydantic model validation."""
    print("=" * 80)
    print("TEST 1: Pydantic Model Validation")
    print("=" * 80)
    
    try:
        from json_extraction import (
            CommentModel,
            PostModel,
            ExtractedDataModel,
            ProcessedDataModel,
            PipelineResultModel
        )
        
        # Test CommentModel
        comment = CommentModel(body="This is a test comment")
        print("✅ CommentModel validated")
        
        # Test PostModel
        post = PostModel(title="Test Post", content="Test content")
        print("✅ PostModel validated")
        
        # Test ExtractedDataModel
        extracted = ExtractedDataModel(
            post=post,
            comments=[comment],
            total_comments=1,
            source_file="test.json"
        )
        print("✅ ExtractedDataModel validated")
        
        # Test ProcessedDataModel
        processed = ProcessedDataModel(
            extracted_data=[extracted],
            total_posts=1,
            total_comments_all=1
        )
        print("✅ ProcessedDataModel validated")
        
        # Test PipelineResultModel
        result = PipelineResultModel(
            extracted_data=processed,
            status="success",
            files_processed=["test.json"]
        )
        print("✅ PipelineResultModel validated")
        
        print("\n✅ All Pydantic models validated successfully!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error validating models: {str(e)}\n")
        return False


def test_json_extraction():
    """Test JSON extraction functionality."""
    print("=" * 80)
    print("TEST 2: JSON Extraction")
    print("=" * 80)
    
    try:
        from json_extraction import (
            extract_post_and_comments,
            process_multiple_json_files
        )
        
        # Create temporary test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create simple format file
            simple_file = os.path.join(temp_dir, "simple_format.json")
            create_sample_json_file(simple_file, "simple")
            print(f"📄 Created test file: {simple_file}")
            
            # Create Reddit API format file
            api_file = os.path.join(temp_dir, "api_format.json")
            create_sample_json_file(api_file, "reddit_api")
            print(f"📄 Created test file: {api_file}")
            
            # Test single file extraction - simple format
            print("\nTesting simple format extraction...")
            data1 = extract_post_and_comments(simple_file)
            print(f"✅ Extracted: '{data1['post']['title']}'")
            print(f"   Comments: {data1['total_comments']}")
            
            # Test single file extraction - API format
            print("\nTesting Reddit API format extraction...")
            data2 = extract_post_and_comments(api_file)
            print(f"✅ Extracted: '{data2['post']['title']}'")
            print(f"   Comments: {data2['total_comments']}")
            
            # Test multiple file processing
            print("\nTesting multiple file processing...")
            processed = process_multiple_json_files([simple_file, api_file])
            print(f"✅ Processed {processed.total_posts} posts")
            print(f"   Total comments: {processed.total_comments_all}")
            
            print("\n✅ JSON extraction tests passed!\n")
            return True
            
    except Exception as e:
        print(f"\n❌ Error in extraction: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_text_conversion():
    """Test conversion to text format."""
    print("=" * 80)
    print("TEST 3: Text Conversion")
    print("=" * 80)
    
    try:
        from json_extraction import (
            process_multiple_json_files,
            convert_to_text_format
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = os.path.join(temp_dir, "test.json")
            create_sample_json_file(test_file, "simple")
            
            # Process file
            processed = process_multiple_json_files([test_file])
            
            # Convert to text
            text = convert_to_text_format(processed)
            
            print(f"✅ Converted {processed.total_posts} posts to text format")
            print(f"   Text length: {len(text)} characters")
            print(f"\nText preview:")
            print("-" * 80)
            print(text[:300] + "..." if len(text) > 300 else text)
            print("-" * 80)
            
            print("\n✅ Text conversion test passed!\n")
            return True
            
    except Exception as e:
        print(f"\n❌ Error in text conversion: {str(e)}\n")
        return False


def test_file_finding():
    """Test JSON file finding functionality."""
    print("=" * 80)
    print("TEST 4: File Finding")
    print("=" * 80)
    
    try:
        from json_extraction import find_json_files
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple test files
            for i in range(3):
                file_path = os.path.join(temp_dir, f"test_{i}.json")
                create_sample_json_file(file_path, "simple")
            
            # Find files
            found_files = find_json_files(temp_dir)
            
            print(f"✅ Found {len(found_files)} JSON files")
            for f in found_files:
                print(f"   - {os.path.basename(f)}")
            
            assert len(found_files) == 3, f"Expected 3 files, found {len(found_files)}"
            
            print("\n✅ File finding test passed!\n")
            return True
            
    except Exception as e:
        print(f"\n❌ Error in file finding: {str(e)}\n")
        return False


def test_pipeline_structure():
    """Test pipeline structure without API calls."""
    print("=" * 80)
    print("TEST 5: Pipeline Structure (No API)")
    print("=" * 80)
    
    try:
        from json_extraction import (
            process_multiple_json_files,
            convert_to_text_format,
            save_text_file
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            json_files = []
            for i in range(2):
                file_path = os.path.join(temp_dir, f"post_{i}.json")
                create_sample_json_file(file_path, "simple")
                json_files.append(file_path)
            
            print(f"📄 Created {len(json_files)} test files")
            
            # Step 1: Extract
            print("\nStep 1: Extracting data...")
            processed = process_multiple_json_files(json_files)
            print(f"✅ Extracted {processed.total_posts} posts, {processed.total_comments_all} comments")
            
            # Step 2: Convert to text
            print("\nStep 2: Converting to text...")
            text = convert_to_text_format(processed)
            print(f"✅ Generated {len(text)} characters of text")
            
            # Step 3: Save text
            print("\nStep 3: Saving text file...")
            text_file = os.path.join(temp_dir, "extracted.txt")
            save_text_file(text, text_file)
            print(f"✅ Saved to {text_file}")
            
            # Verify saved file
            with open(text_file, 'r', encoding='utf-8') as f:
                saved_text = f.read()
            
            assert saved_text == text, "Saved text doesn't match"
            print("✅ Text file verified")
            
            print("\n✅ Pipeline structure test passed!\n")
            return True
            
    except Exception as e:
        print(f"\n❌ Error in pipeline structure: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("JSON EXTRACTION PIPELINE - TEST SUITE")
    print("=" * 80)
    print("\nThis test suite validates the pipeline structure without requiring")
    print("actual Reddit data or API keys.\n")
    
    results = []
    
    # Run tests
    results.append(("Pydantic Models", test_pydantic_models()))
    results.append(("JSON Extraction", test_json_extraction()))
    results.append(("Text Conversion", test_text_conversion()))
    results.append(("File Finding", test_file_finding()))
    results.append(("Pipeline Structure", test_pipeline_structure()))
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The pipeline is working correctly.")
        print("\nNext steps:")
        print("1. Add your OPENROUTER_API_KEY to .env file")
        print("2. Run: python json-extraction.py <your_json_dir> ./output")
        print("3. Check QUICK_START.md for more examples")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("=" * 80)
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

