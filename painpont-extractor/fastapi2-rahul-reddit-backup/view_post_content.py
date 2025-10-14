"""
View Post Content - Display what's extracted from Reddit posts
"""

import json
import os
from datetime import datetime

def view_post_content(json_file_path):
    """Display the post content from a structured JSON file."""
    
    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        return
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    post = data.get('post', {})
    comments = data.get('comments', [])
    
    print("\n" + "="*80)
    print("REDDIT POST CONTENT")
    print("="*80)
    
    # Post metadata
    print(f"\n📌 TITLE: {post.get('title', 'N/A')}")
    print(f"👤 AUTHOR: u/{post.get('author', 'N/A')}")
    print(f"📍 SUBREDDIT: r/{post.get('subreddit', 'N/A')}")
    print(f"🏷️  FLAIR: {post.get('link_flair_text', 'None')}")
    print(f"⬆️  SCORE: {post.get('score', 0)} ({int(post.get('upvote_ratio', 0)*100)}% upvoted)")
    print(f"💬 COMMENTS: {post.get('num_comments', 0)}")
    print(f"🔗 URL: https://reddit.com{post.get('permalink', '')}")
    
    # Post type
    print(f"\n📝 POST TYPE: {post.get('post_type', 'unknown')}")
    print(f"   Is Self Post: {post.get('is_self_post', False)}")
    print(f"   Is Video: {post.get('is_video', False)}")
    
    # Main content
    print("\n" + "-"*80)
    print("MAIN POST CONTENT:")
    print("-"*80)
    
    selftext = post.get('selftext', '').strip()
    
    if selftext:
        print(f"\n{selftext}\n")
    else:
        print("\n[NO TEXT CONTENT - This is a link/image/video post]\n")
        
        # Show linked content
        url = post.get('url', '')
        if url and not url.startswith('https://www.reddit.com'):
            print(f"🔗 External Link: {url}")
        
        domain = post.get('domain', '')
        if domain and domain != 'self.' + post.get('subreddit', ''):
            print(f"📎 Domain: {domain}")
        
        # Show images if any
        preview_images = post.get('preview_images', [])
        if preview_images:
            print(f"🖼️  Preview Images:")
            for i, img_url in enumerate(preview_images, 1):
                print(f"   {i}. {img_url}")
        
        thumbnail = post.get('thumbnail', '')
        if thumbnail and thumbnail not in ['self', 'default', 'nsfw', '']:
            print(f"🖼️  Thumbnail: {thumbnail}")
    
    # Comment summary
    print("\n" + "-"*80)
    print(f"COMMENTS ({len(comments)} top-level)")
    print("-"*80)
    
    if comments:
        print("\nTop 3 Comments:\n")
        for i, comment in enumerate(comments[:3], 1):
            body = comment.get('body', '')[:200]
            if len(comment.get('body', '')) > 200:
                body += "..."
            
            print(f"{i}. u/{comment.get('author', 'N/A')} (⬆️ {comment.get('score', 0)})")
            print(f"   {body}")
            print(f"   Replies: {len(comment.get('replies', []))}\n")
    else:
        print("\n[No comments extracted]\n")
    
    print("="*80)


def main():
    """Interactive viewer for post content."""
    
    output_dir = "d:/demo1 of reddit lib/output"
    
    if not os.path.exists(output_dir):
        print(f"❌ Output directory not found: {output_dir}")
        return
    
    # Find all market folders
    market_folders = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    
    if not market_folders:
        print("❌ No market folders found in output/")
        print("   Run main.py first to extract Reddit data")
        return
    
    # Let user select a market folder
    print("\n" + "="*80)
    print("REDDIT POST CONTENT VIEWER")
    print("="*80)
    print(f"\nAvailable Market Analyses:\n")
    
    for i, folder in enumerate(sorted(market_folders), 1):
        print(f"  {i}. {folder}")
    
    try:
        choice = int(input("\nSelect market folder (number): ").strip())
        if choice < 1 or choice > len(market_folders):
            print("❌ Invalid choice")
            return
        
        selected_folder = sorted(market_folders)[choice - 1]
        market_dir = os.path.join(output_dir, selected_folder)
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Invalid input")
        return
    
    # Find all structured JSON files in the selected folder
    structured_files = [f for f in os.listdir(market_dir) if f.endswith('_structured.json')]
    
    if not structured_files:
        print(f"❌ No structured JSON files found in {selected_folder}/")
        return
    
    print(f"\n" + "="*80)
    print(f"POSTS IN: {selected_folder}")
    print("="*80)
    print(f"\nFound {len(structured_files)} posts:\n")
    
    for i, filename in enumerate(sorted(structured_files), 1):
        print(f"  {i}. {filename}")
    
    print(f"\n  {len(structured_files) + 1}. View all posts")
    print("  0. Exit")
    
    while True:
        try:
            choice = input("\nSelect a post to view (number): ").strip()
            
            if choice == '0':
                print("\n👋 Goodbye!")
                break
            
            choice_num = int(choice)
            
            if choice_num == len(structured_files) + 1:
                # View all
                for filename in sorted(structured_files):
                    filepath = os.path.join(market_dir, filename)
                    view_post_content(filepath)
                    input("\nPress Enter to view next post...")
                break
            elif 1 <= choice_num <= len(structured_files):
                filename = sorted(structured_files)[choice_num - 1]
                filepath = os.path.join(market_dir, filename)
                view_post_content(filepath)
                
                again = input("\nView another post? (y/n): ").strip().lower()
                if again != 'y':
                    break
            else:
                print("❌ Invalid choice")
                
        except ValueError:
            print("❌ Please enter a number")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
