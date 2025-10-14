"""
Example Usage Script
Demonstrates programmatic usage of the Market Opportunity Identifier.
"""

import os
from dotenv import load_dotenv
from main import MarketOpportunityIdentifier


def example_automated_analysis():
    """
    Example: Fully automated analysis without user interaction.
    Analyzes top 3 posts automatically.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE: AUTOMATED ANALYSIS")
    print("=" * 80)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found")
        return
    
    # Initialize identifier
    identifier = MarketOpportunityIdentifier(api_key)
    
    # Define market
    market = "sustainable gardening"
    
    print(f"\n🔍 Analyzing market: {market}")
    
    # Step 1-3: Search, scrape, and rank
    print("\n📊 Searching and ranking posts...")
    reddit_urls = identifier.searcher.search_market(market, num_results=20)
    posts_data = identifier.scraper.scrape_multiple_posts(reddit_urls)
    ranked_posts = identifier.ranker.rank_posts(posts_data, market, top_n=10)
    
    # Display top 5
    print("\n🏆 Top 5 Posts:")
    for post in ranked_posts[:5]:
        print(f"\n#{post['rank']}: {post['title']}")
        print(f"  Score: {post.get('product_potential_score', 'N/A')}/10")
        print(f"  {post['justification']}")
    
    # Automatically analyze top 3
    print("\n\n🔬 Deep analysis of top 3 posts...")
    for post in ranked_posts[:3]:
        print(f"\nAnalyzing: {post['title'][:60]}...")
        json_data = identifier.scraper.get_post_json(post['url'])
        
        if json_data:
            structured = identifier.scraper.extract_post_and_comments(json_data)
            if structured:
                print(f"  ✓ Extracted {structured['total_comments']} comments")
                
                # Save
                filename = f"{market}_auto_rank_{post['rank']}.json"
                identifier._save_json(structured, filename)
    
    print("\n✅ Automated analysis complete!")


def example_custom_workflow():
    """
    Example: Custom workflow with manual control.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE: CUSTOM WORKFLOW")
    print("=" * 80)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found")
        return
    
    # Initialize components individually
    from google_search import GoogleSearcher
    from reddit_scraper import RedditScraper
    from openai_ranker import PostRanker
    
    searcher = GoogleSearcher()
    scraper = RedditScraper()
    ranker = PostRanker(api_key)
    
    market = "learning guitar as an adult"
    
    # Custom search query
    print(f"\n🎸 Analyzing: {market}")
    print("\n1️⃣ Custom Google Search...")
    
    custom_query = f'{market} site:reddit.com "pain point" OR "struggle" OR "difficult"'
    urls = searcher.search_google(custom_query, num_results=15)
    
    # Selective scraping (only first 10)
    print("\n2️⃣ Selective Scraping...")
    posts = scraper.scrape_multiple_posts(urls[:10])
    
    # Filter posts with high engagement
    print("\n3️⃣ Filtering by engagement...")
    high_engagement = [p for p in posts if p['upvotes'] > 50 or p['comment_count'] > 20]
    print(f"  Found {len(high_engagement)} high-engagement posts")
    
    # Rank only filtered posts
    if high_engagement:
        print("\n4️⃣ Ranking high-engagement posts...")
        ranked = ranker.rank_posts(high_engagement, market, top_n=5)
        
        # Display results
        output = ranker.format_ranked_output(ranked, market)
        print(output)
    
    print("\n✅ Custom workflow complete!")


def example_single_post_analysis():
    """
    Example: Analyze a specific Reddit post URL.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE: SINGLE POST ANALYSIS")
    print("=" * 80)
    
    # Load environment
    load_dotenv()
    
    from reddit_scraper import RedditScraper
    
    scraper = RedditScraper()
    
    # Example URL (replace with actual URL)
    url = "https://www.reddit.com/r/Guitar/comments/example"
    
    print(f"\n🔍 Analyzing single post...")
    print(f"URL: {url}")
    
    # Get metadata
    print("\n1️⃣ Extracting metadata...")
    metadata = scraper.scrape_post_metadata(url)
    print(f"  Title: {metadata['title']}")
    print(f"  Upvotes: {metadata['upvotes']}")
    print(f"  Comments: {metadata['comment_count']}")
    
    # Get full JSON
    print("\n2️⃣ Fetching complete data...")
    json_data = scraper.get_post_json(url)
    
    if json_data:
        structured = scraper.extract_post_and_comments(json_data)
        
        if structured:
            print(f"\n3️⃣ Analysis Results:")
            print(f"  Post Author: {structured['post']['author']}")
            print(f"  Post Score: {structured['post']['score']}")
            print(f"  Total Comments: {structured['total_comments']}")
            
            # Show top 3 comments
            print(f"\n  Top Comments:")
            for i, comment in enumerate(structured['comments'][:3], 1):
                print(f"    {i}. {comment['author']}: {comment['body'][:80]}...")
                print(f"       Score: {comment['score']}, Replies: {len(comment['replies'])}")
    
    print("\n✅ Single post analysis complete!")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("MARKET OPPORTUNITY IDENTIFIER - USAGE EXAMPLES")
    print("=" * 80)
    
    print("\nAvailable examples:")
    print("1. Automated Analysis (no user interaction)")
    print("2. Custom Workflow (manual control)")
    print("3. Single Post Analysis")
    print("4. Run all examples")
    
    choice = input("\nSelect example (1-4): ").strip()
    
    if choice == "1":
        example_automated_analysis()
    elif choice == "2":
        example_custom_workflow()
    elif choice == "3":
        example_single_post_analysis()
    elif choice == "4":
        example_automated_analysis()
        input("\nPress Enter to continue to next example...")
        example_custom_workflow()
        input("\nPress Enter to continue to next example...")
        example_single_post_analysis()
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
