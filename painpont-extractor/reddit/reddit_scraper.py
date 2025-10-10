"""
Reddit Scraper Module
Scrapes Reddit posts for metadata and full JSON data.
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re


class RedditScraper:
    """Handles scraping of Reddit posts."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
    
    def scrape_post_metadata(self, url):
        """
        Scrapes metadata from a single Reddit post.
        
        Args:
            url: Reddit post URL
            
        Returns:
            dict: Post metadata (url, title, upvotes, comment_count)
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            try:
                soup = BeautifulSoup(response.text, 'lxml')
            except Exception:
                soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if it's old.reddit.com
            is_old_reddit = 'old.reddit.com' in url
            
            # Extract title
            title = None
            if is_old_reddit:
                # old.reddit.com uses .title class
                title_elem = soup.find('a', class_='title')
                if title_elem:
                    title = title_elem.get_text(strip=True)
            else:
                # New reddit uses h1
                title_tag = soup.find('h1')
                if title_tag:
                    title = title_tag.get_text(strip=True)
            
            # Fallback: meta tag
            if not title:
                title_meta = soup.find('meta', property='og:title')
                if title_meta:
                    title = title_meta.get('content', '')
            
            # Extract upvotes (score)
            upvotes = 0
            
            if is_old_reddit:
                # old.reddit.com score
                score_elem = soup.find('div', class_='score unvoted')
                if not score_elem:
                    score_elem = soup.find('div', class_='score likes')
                if not score_elem:
                    score_elem = soup.find('div', class_='score dislikes')
                if score_elem:
                    score_text = score_elem.get_text(strip=True)
                    upvotes = self._parse_number(score_text)
            else:
                # New reddit score
                score_element = soup.find('div', {'data-click-id': 'upvote'})
                if score_element:
                    score_text = score_element.get_text(strip=True)
                    upvotes = self._parse_number(score_text)
            
            # Fallback: JSON in scripts
            if upvotes == 0:
                for script in soup.find_all('script'):
                    if script.string and 'score' in script.string:
                        match = re.search(r'"score":(\d+)', script.string)
                        if match:
                            upvotes = int(match.group(1))
                            break
            
            # Extract comment count
            comment_count = 0
            
            if is_old_reddit:
                # old.reddit.com comments
                comment_elem = soup.find('a', class_='comments')
                if comment_elem:
                    text = comment_elem.get_text(strip=True).lower()
                    comment_count = self._parse_number(text)
            else:
                # New reddit comments
                comment_elements = soup.find_all('a', href=re.compile(r'/comments/'))
                for elem in comment_elements:
                    text = elem.get_text(strip=True).lower()
                    if 'comment' in text:
                        comment_count = self._parse_number(text)
                        if comment_count > 0:
                            break
            
            # Fallback: JSON in scripts
            if comment_count == 0:
                for script in soup.find_all('script'):
                    if script.string and 'numComments' in script.string:
                        match = re.search(r'"numComments":(\d+)', script.string)
                        if match:
                            comment_count = int(match.group(1))
                            break
            
            # Convert old.reddit.com URLs to www.reddit.com for JSON compatibility
            clean_url = url.replace('old.reddit.com', 'www.reddit.com')
            
            return {
                'url': clean_url,
                'title': title or 'No title found',
                'upvotes': upvotes,
                'comment_count': comment_count
            }
            
        except Exception as e:
            print(f"  ⚠ Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'title': 'Error loading',
                'upvotes': 0,
                'comment_count': 0
            }
    
    def scrape_multiple_posts(self, urls):
        """
        Scrapes metadata from multiple Reddit posts.
        
        Args:
            urls: List of Reddit URLs
            
        Returns:
            list: List of post metadata dictionaries
        """
        print(f"\n📊 Scraping metadata from {len(urls)} posts...")
        posts_data = []
        
        for i, url in enumerate(urls, 1):
            print(f"  [{i}/{len(urls)}] Scraping: {url[:60]}...")
            metadata = self.scrape_post_metadata(url)
            posts_data.append(metadata)
            
            # Be polite to Reddit
            time.sleep(1)
        
        print(f"\n✅ Scraped {len(posts_data)} posts")
        return posts_data
    
    def get_post_json(self, url):
        """
        Fetches the full JSON data for a Reddit post.
        
        Args:
            url: Reddit post URL
            
        Returns:
            dict: Full JSON data from Reddit
        """
        # Ensure URL ends with /
        clean_url = url.rstrip('/') + '/.json'
        
        try:
            print(f"\n📥 Fetching JSON: {clean_url}")
            response = requests.get(clean_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            print(f"  ✓ Successfully fetched JSON data")
            return data
            
        except Exception as e:
            print(f"  ✗ Error fetching JSON: {str(e)}")
            return None
    
    def extract_post_and_comments(self, json_data):
        """
        Extracts structured post and comment data from Reddit JSON.
        
        Args:
            json_data: Raw JSON from Reddit
            
        Returns:
            dict: Structured data with post and comments
        """
        if not json_data or len(json_data) < 2:
            return None
        
        try:
            # Post data is in first element
            post_data = json_data[0]['data']['children'][0]['data']
            
            # Comments are in second element
            comments_data = json_data[1]['data']['children']
            
            # Extract post information
            selftext = post_data.get('selftext', '')
            
            # Check if post was removed or deleted
            if selftext == '[removed]':
                selftext = '[CONTENT REMOVED BY MODERATORS]'
            elif selftext == '[deleted]':
                selftext = '[CONTENT DELETED BY USER]'
            
            # Determine post type and content
            is_self = post_data.get('is_self', False)
            post_hint = post_data.get('post_hint', '')
            
            post = {
                'title': post_data.get('title', ''),
                'selftext': selftext,
                'selftext_html': post_data.get('selftext_html', ''),  # HTML version
                'is_self_post': is_self,
                'post_type': post_hint if post_hint else ('text' if is_self else 'link'),
                'author': post_data.get('author', ''),
                'score': post_data.get('score', 0),
                'upvote_ratio': post_data.get('upvote_ratio', 0),
                'num_comments': post_data.get('num_comments', 0),
                'created_utc': post_data.get('created_utc', 0),
                'url': post_data.get('url', ''),  # External URL if link post
                'permalink': post_data.get('permalink', ''),  # Reddit post URL
                'subreddit': post_data.get('subreddit', ''),
                'link_flair_text': post_data.get('link_flair_text', ''),
                'domain': post_data.get('domain', ''),  # Source domain for links
                'is_video': post_data.get('is_video', False),
                'thumbnail': post_data.get('thumbnail', ''),
                'preview_images': self._extract_preview_images(post_data)
            }
            
            # Extract comments recursively
            comments = []
            for comment_wrapper in comments_data:
                comment = self._extract_comment(comment_wrapper)
                if comment:
                    comments.append(comment)
            
            return {
                'post': post,
                'comments': comments,
                'total_comments': len(comments)
            }
            
        except Exception as e:
            print(f"  ⚠ Error parsing JSON: {str(e)}")
            return None
    
    def _extract_preview_images(self, post_data):
        """
        Extracts preview image URLs if available.
        
        Args:
            post_data: Post data dictionary
            
        Returns:
            list: List of image URLs
        """
        try:
            preview = post_data.get('preview', {})
            if not preview:
                return []
            
            images = preview.get('images', [])
            if not images:
                return []
            
            # Get the source image from first preview
            source = images[0].get('source', {})
            return [source.get('url', '')] if source.get('url') else []
        except:
            return []
    
    def _extract_comment(self, comment_wrapper, depth=0):
        """
        Recursively extracts comment data including nested replies.
        
        Args:
            comment_wrapper: Comment data wrapper
            depth: Current nesting depth
            
        Returns:
            dict: Comment data with nested replies
        """
        if comment_wrapper.get('kind') != 't1':
            return None
        
        comment_data = comment_wrapper.get('data', {})
        
        comment = {
            'author': comment_data.get('author', ''),
            'body': comment_data.get('body', ''),
            'score': comment_data.get('score', 0),
            'created_utc': comment_data.get('created_utc', 0),
            'depth': depth,
            'replies': []
        }
        
        # Extract nested replies
        replies = comment_data.get('replies', '')
        if isinstance(replies, dict):
            replies_children = replies.get('data', {}).get('children', [])
            for reply_wrapper in replies_children:
                nested_comment = self._extract_comment(reply_wrapper, depth + 1)
                if nested_comment:
                    comment['replies'].append(nested_comment)
        
        return comment
    
    @staticmethod
    def _parse_number(text):
        """
        Parses a number from text, handling 'k' and 'm' suffixes.
        
        Args:
            text: Text containing a number
            
        Returns:
            int: Parsed number
        """
        if not text:
            return 0
        
        try:
            text = text.lower().strip()
            
            # Remove non-numeric characters except k, m, and .
            text = re.sub(r'[^\d.km]', '', text)
            
            # Return 0 if empty after cleaning
            if not text or text in ['k', 'm', '.', 'km']:
                return 0
            
            if 'k' in text:
                number = float(text.replace('k', ''))
                return int(number * 1000)
            elif 'm' in text:
                number = float(text.replace('m', ''))
                return int(number * 1000000)
            else:
                return int(float(text))
        except (ValueError, AttributeError):
            return 0
