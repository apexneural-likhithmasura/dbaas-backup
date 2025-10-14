"""
Reddit-Based Market Opportunity Identifier
Main application file implementing the complete workflow.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

from google_search import GoogleSearcher
from reddit_scraper import RedditScraper
from openai_ranker import PostRanker


class MarketOpportunityIdentifier:
    """Main class orchestrating the market opportunity identification workflow."""
    
    def __init__(self, openrouter_api_key):
        """
        Initialize the identifier with necessary components.
        
        Args:
            openrouter_api_key: OpenRouter API key
        """
        self.searcher = GoogleSearcher()
        self.scraper = RedditScraper()
        self.ranker = PostRanker(openrouter_api_key)
        self.base_output_dir = 'd:/redditdemo/output'
        self.market_output_dir = None  # Will be set per market
    
    def run_workflow(self, market_to_explore, num_search_results=100, top_n=20):
        """
        Execute the complete market opportunity identification workflow.
        
        Args:
            market_to_explore: The market/niche to research
            num_search_results: Number of search results to retrieve (default: 100)
            top_n: Number of top posts to rank (default: 20)
        """
        # Create market-specific output folder
        self._setup_market_folder(market_to_explore)
        
        print("\n" + "=" * 80)
        print("REDDIT-BASED MARKET OPPORTUNITY IDENTIFIER")
        print("=" * 80)
        print(f"\nMarket to Explore: {market_to_explore}")
        print(f"Search Results Target: {num_search_results}")
        print(f"Top Posts to Rank: {top_n}")
        print(f"Output Folder: {self.market_output_dir}")
        
        # Step 1: Formulate and execute search query
        print("\n" + "-" * 80)
        print("STEP 1: GOOGLE SEARCH FOR REDDIT DISCUSSIONS")
        print("-" * 80)
        
        reddit_urls = self.searcher.search_market(market_to_explore, num_search_results)
        
        if not reddit_urls:
            print("\n❌ No Reddit URLs found. Please try a different market or check your internet connection.")
            return
        
        # Step 2: Scrape initial data from search results
        print("\n" + "-" * 80)
        print("STEP 2: SCRAPING POST METADATA")
        print("-" * 80)
        
        posts_data = self.scraper.scrape_multiple_posts(reddit_urls)
        
        # Save raw scraped data
        self._save_json(posts_data, f"{market_to_explore}_raw_posts.json")
        
        # Step 3: AI-powered ranking and analysis
        print("\n" + "-" * 80)
        print("STEP 3: AI-POWERED RANKING")
        print("-" * 80)
        
        ranked_posts = self.ranker.rank_posts(posts_data, market_to_explore, top_n)
        
        if not ranked_posts:
            print("\n❌ Failed to rank posts. Please check your OpenRouter API key.")
            return
        
        # Save ranked posts
        self._save_json(ranked_posts, f"{market_to_explore}_ranked_posts.json")
        
        # Step 4: Display results and get user selection
        print("\n" + "-" * 80)
        print("STEP 4: RANKED RESULTS")
        print("-" * 80)
        
        formatted_output = self.ranker.format_ranked_output(ranked_posts, market_to_explore)
        print(formatted_output)
        
        # Save formatted output
        self._save_text(formatted_output, f"{market_to_explore}_ranked_output.txt")
        
        # User selection
        selected_posts = self._get_user_selection(ranked_posts)
        
        if not selected_posts:
            print("\n✅ Workflow complete. No posts selected for deep analysis.")
            return
        
        # Step 5: Deep data extraction via JSON
        print("\n" + "-" * 80)
        print("STEP 5: DEEP JSON EXTRACTION")
        print("-" * 80)
        
        deep_analysis_results = []
        
        for post in selected_posts:
            print(f"\nProcessing: {post['title'][:70]}...")
            
            # Fetch JSON data
            json_data = self.scraper.get_post_json(post['url'])
            
            if json_data:
                # Extract structured data
                structured_data = self.scraper.extract_post_and_comments(json_data)
                
                if structured_data:
                    deep_analysis_results.append({
                        'rank': post['rank'],
                        'title': post['title'],
                        'url': post['url'],
                        'extracted_data': structured_data
                    })
                    
                    # Save individual post JSON
                    filename = f"{market_to_explore}_post_rank_{post['rank']}.json"
                    self._save_json(json_data, filename)
                    print(f"  ✓ Saved raw JSON: {filename}")
                    
                    # Save structured extraction
                    filename_structured = f"{market_to_explore}_post_rank_{post['rank']}_structured.json"
                    self._save_json(structured_data, filename_structured)
                    print(f"  ✓ Saved structured data: {filename_structured}")
        
        # Step 6: Final output
        print("\n" + "-" * 80)
        print("STEP 6: FINAL OUTPUT")
        print("-" * 80)
        
        # Save complete analysis
        complete_output = {
            'market_to_explore': market_to_explore,
            'timestamp': datetime.now().isoformat(),
            'total_posts_found': len(reddit_urls),
            'ranked_posts': ranked_posts,
            'deep_analysis': deep_analysis_results
        }
        
        self._save_json(complete_output, f"{market_to_explore}_complete_analysis.json")
        
        # Summary
        print(f"\n✅ WORKFLOW COMPLETE!")
        print(f"\n📊 Summary:")
        print(f"  • Market Explored: {market_to_explore}")
        print(f"  • Reddit Posts Found: {len(reddit_urls)}")
        print(f"  • Posts Ranked: {len(ranked_posts)}")
        print(f"  • Posts Analyzed in Depth: {len(deep_analysis_results)}")
        print(f"  • Output Directory: {self.market_output_dir}")
        
        print(f"\n📁 Generated Files:")
        for filename in os.listdir(self.market_output_dir):
            file_path = os.path.join(self.market_output_dir, filename)
            file_size = os.path.getsize(file_path)
            print(f"  • {filename} ({self._format_size(file_size)})")
    
    def _get_user_selection(self, ranked_posts):
        """
        Prompts user to select posts for deep analysis.
        
        Args:
            ranked_posts: List of ranked posts
            
        Returns:
            list: Selected posts
        """
        print("\n" + "=" * 80)
        print("SELECT POSTS FOR DEEP ANALYSIS")
        print("=" * 80)
        print("\nEnter the rank numbers of posts you want to analyze deeply.")
        print("Examples:")
        print("  - Single post: 1")
        print("  - Multiple posts: 1,3,5")
        print("  - Range: 1-5")
        print("  - Skip: just press Enter\n")
        
        while True:
            selection = input("Your selection: ").strip()
            
            if not selection:
                return []
            
            try:
                selected_ranks = self._parse_selection(selection, len(ranked_posts))
                selected_posts = [p for p in ranked_posts if p['rank'] in selected_ranks]
                
                print(f"\n✓ Selected {len(selected_posts)} post(s):")
                for post in selected_posts:
                    print(f"  #{post['rank']}: {post['title'][:70]}...")
                
                confirm = input("\nProceed with these selections? (y/n): ").strip().lower()
                if confirm == 'y':
                    return selected_posts
                else:
                    print("\nLet's try again...")
                    continue
                    
            except ValueError as e:
                print(f"❌ Invalid selection: {e}")
                print("Please try again.\n")
    
    def _parse_selection(self, selection, max_rank):
        """
        Parses user selection string into list of rank numbers.
        
        Args:
            selection: User input string
            max_rank: Maximum valid rank number
            
        Returns:
            list: List of selected rank numbers
        """
        ranks = set()
        
        parts = selection.split(',')
        for part in parts:
            part = part.strip()
            
            if '-' in part:
                # Range
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                if start < 1 or end > max_rank:
                    raise ValueError(f"Range must be between 1 and {max_rank}")
                ranks.update(range(start, end + 1))
            else:
                # Single number
                rank = int(part)
                if rank < 1 or rank > max_rank:
                    raise ValueError(f"Rank must be between 1 and {max_rank}")
                ranks.add(rank)
        
        return sorted(list(ranks))
    
    def _setup_market_folder(self, market_to_explore):
        """
        Creates a market-specific output folder.
        
        Args:
            market_to_explore: The market/niche being researched
        """
        # Sanitize market name for folder
        safe_market_name = market_to_explore.replace(' ', '_').replace('"', '').replace('/', '_').replace('\\', '_')
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{safe_market_name}_{timestamp}"
        
        # Create full path
        self.market_output_dir = os.path.join(self.base_output_dir, folder_name)
        os.makedirs(self.market_output_dir, exist_ok=True)
        
        print(f"\n📁 Created output folder: {folder_name}")
    
    def _save_json(self, data, filename):
        """
        Saves data as JSON file.
        
        Args:
            data: Data to save
            filename: Output filename
        """
        # Sanitize filename
        filename = filename.replace(' ', '_').replace('"', '').replace('/', '_')
        filepath = os.path.join(self.market_output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_text(self, text, filename):
        """
        Saves text to file.
        
        Args:
            text: Text to save
            filename: Output filename
        """
        # Sanitize filename
        filename = filename.replace(' ', '_').replace('"', '').replace('/', '_')
        filepath = os.path.join(self.market_output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
    
    @staticmethod
    def _format_size(size):
        """
        Formats file size in human-readable format.
        
        Args:
            size: Size in bytes
            
        Returns:
            str: Formatted size
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


def main():
    """Main entry point for the application."""
    # Load environment variables
    load_dotenv()
    
    # Get OpenRouter API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in .env file")
        return
    
    print("\n" + "=" * 80)
    print("WELCOME TO THE REDDIT MARKET OPPORTUNITY IDENTIFIER")
    print("=" * 80)
    print("\nThis tool helps you discover product opportunities by analyzing")
    print("Reddit discussions for pain points and unmet needs.")
    
    # Get market to explore from user
    print("\n" + "-" * 80)
    market_to_explore = input("\nEnter the market/niche to explore: ").strip()
    
    if not market_to_explore:
        print("❌ Market cannot be empty. Exiting.")
        return
    
    # Optional parameters
    try:
        num_results = input("\nNumber of search results to retrieve (default 30): ").strip()
        num_results = int(num_results) if num_results else 30
        
        top_n = input("Number of top posts to rank (default 10): ").strip()
        top_n = int(top_n) if top_n else 10
    except ValueError:
        print("⚠ Invalid input. Using defaults (30 results, 10 top posts)")
        num_results = 30
        top_n = 10
    
    # Create identifier and run workflow
    identifier = MarketOpportunityIdentifier(api_key)
    identifier.run_workflow(market_to_explore, num_results, top_n)
    
    print("\n" + "=" * 80)
    print("Thank you for using the Market Opportunity Identifier!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
