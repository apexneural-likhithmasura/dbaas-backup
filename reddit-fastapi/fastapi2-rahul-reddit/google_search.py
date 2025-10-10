"""
Multi-Engine Search Module
Performs searches across multiple search engines for Reddit posts.
Uses DuckDuckGo as primary (less strict), with fallback options.
"""

import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random


class GoogleSearcher:
    """Handles searches for Reddit content across multiple search engines."""
    
    def __init__(self):
        # Rotate user agents to appear more natural
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ]
        self.session = requests.Session()
    
    def build_query(self, market_to_explore):
        """
        Builds the Google search query based on the template.
        
        Args:
            market_to_explore: The market/niche to research
            
        Returns:
            str: The formatted search query
        """
        query_template = (
            '"{market}" (site:reddit.com inurl:comments|inurl:thread | '
            'intext:"I think"|"I feel"|"I was"|"I have been"|"I experienced"|'
            '"my experience"|"in my opinion"|"IMO"|"my biggest struggle"|'
            '"my biggest fear"|"I found that"|"I learned"|"I realized"|'
            '"my advice"|"struggles"|"problems"|"issues"|"challenge"|'
            '"difficulties"|"hardships"|"pain point"|"barriers"|"obstacles"|'
            '"concerns"|"frustrations"|"worries"|"hesitations"|'
            '"what I wish I knew"|"what I regret")'
        )
        return query_template.format(market=market_to_explore)
    
    def _get_headers(self):
        """Get randomized headers to avoid bot detection."""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def search_duckduckgo(self, query, num_results=30):
        """
        Performs a DuckDuckGo search (less strict than Google).
        
        Args:
            query: The search query
            num_results: Number of results to retrieve
            
        Returns:
            list: List of Reddit URLs
        """
        print(f"\n🔍 Searching DuckDuckGo for: {query[:80]}...")
        print(f"Target: {num_results} results\n")
        
        reddit_urls = []
        encoded_query = urllib.parse.quote(query)
        
        # DuckDuckGo HTML search
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        try:
            headers = self._get_headers()
            response = self.session.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find all result links
            for result in soup.find_all('a', class_='result__a'):
                href = result.get('href', '')
                
                # DuckDuckGo uses redirect links
                if 'uddg=' in href:
                    try:
                        actual_url = urllib.parse.unquote(href.split('uddg=')[1])
                        if 'reddit.com/r/' in actual_url and '/comments/' in actual_url:
                            clean_url = actual_url.split('?')[0].split('#')[0]
                            if clean_url not in reddit_urls:
                                reddit_urls.append(clean_url)
                                print(f"  ✓ Found: {clean_url}")
                    except:
                        continue
                
                if len(reddit_urls) >= num_results:
                    break
            
            # If we need more, try additional searches with refined queries
            if len(reddit_urls) < num_results and len(reddit_urls) < 10:
                print("  ℹ Trying refined search...")
                time.sleep(2)
                refined_results = self._search_reddit_directly(query.split('"')[1] if '"' in query else query, num_results - len(reddit_urls))
                reddit_urls.extend(refined_results)
            
        except Exception as e:
            print(f"  ⚠ DuckDuckGo error: {str(e)}")
        
        print(f"\n✅ Found {len(reddit_urls)} Reddit URLs via DuckDuckGo")
        return reddit_urls
    
    def _search_reddit_directly(self, market_term, num_results=20):
        """
        Directly search Reddit's search page (no API needed).
        
        Args:
            market_term: Search term
            num_results: Number of results needed
            
        Returns:
            list: List of Reddit URLs
        """
        print(f"\n🔍 Searching Reddit directly for: {market_term}")
        
        reddit_urls = []
        
        # Search terms for pain points
        pain_keywords = [
            'struggle', 'problem', 'issue', 'pain point', 
            'frustration', 'difficult', 'challenge', 'help',
            'advice', 'experience', 'opinion'
        ]
        
        for keyword in pain_keywords:
            if len(reddit_urls) >= num_results:
                break
                
            search_query = f"{market_term} {keyword}"
            encoded_query = urllib.parse.quote(search_query)
            search_url = f"https://old.reddit.com/search?q={encoded_query}&sort=relevance&t=all"
            
            try:
                headers = self._get_headers()
                response = self.session.get(search_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Find post links - multiple selectors
                # Try different HTML structures
                links = soup.find_all('a', class_='search-title')
                if not links:
                    links = soup.find_all('a', {'data-event-action': 'title'})
                if not links:
                    # Look for any link with /comments/ in it
                    links = [a for a in soup.find_all('a', href=True) if '/comments/' in a.get('href', '')]
                
                for link in links:
                    href = link.get('href', '')
                    
                    # Handle relative URLs
                    if href.startswith('/r/') and '/comments/' in href:
                        full_url = f"https://www.reddit.com{href}"
                        clean_url = full_url.split('?')[0].split('#')[0]
                        if clean_url not in reddit_urls:
                            reddit_urls.append(clean_url)
                            print(f"  ✓ Found: {clean_url}")
                    # Handle absolute URLs
                    elif 'reddit.com/r/' in href and '/comments/' in href:
                        clean_url = href.split('?')[0].split('#')[0]
                        if clean_url not in reddit_urls:
                            reddit_urls.append(clean_url)
                            print(f"  ✓ Found: {clean_url}")
                    
                    if len(reddit_urls) >= num_results:
                        break
                
                if len(reddit_urls) > 0:
                    print(f"  ℹ Found {len(reddit_urls)} so far with keyword '{keyword}'")
                
                time.sleep(1.5)  # Be polite
                
            except Exception as e:
                print(f"  ⚠ Reddit search error for '{keyword}': {str(e)}")
                continue
        
        return reddit_urls
    
    def search_google(self, query, num_results=30):
        """
        Multi-engine search with fallbacks.
        Tries DuckDuckGo first, then direct Reddit search.
        
        Args:
            query: The search query
            num_results: Number of results to retrieve (default: 30)
            
        Returns:
            list: List of Reddit URLs
        """
        # Extract market term from query
        market_term = query.split('"')[1] if '"' in query else query.split()[0]
        
        # Try DuckDuckGo first
        reddit_urls = self.search_duckduckgo(query, num_results)
        
        # If insufficient results, use direct Reddit search
        if len(reddit_urls) < num_results:
            print(f"\n  ℹ Found {len(reddit_urls)} via DuckDuckGo, searching Reddit directly for more...")
            time.sleep(2)
            additional = self._search_reddit_directly(market_term, num_results - len(reddit_urls))
            reddit_urls.extend(additional)
        
        # Remove duplicates and trim
        reddit_urls = list(dict.fromkeys(reddit_urls))[:num_results]
        
        print(f"\n✅ Total found: {len(reddit_urls)} Reddit URLs")
        return reddit_urls
    
    def search_market(self, market_to_explore, num_results=30):
        """
        Complete search workflow for a market.
        
        Args:
            market_to_explore: The market/niche to research
            num_results: Number of results to retrieve
            
        Returns:
            list: List of Reddit URLs
        """
        query = self.build_query(market_to_explore)
        return self.search_google(query, num_results)
