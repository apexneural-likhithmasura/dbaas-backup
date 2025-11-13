"""
Reddit Scraper

Scrapes Reddit posts for metadata and full JSON data.
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
import logging
from typing import Dict, List, Optional, Any


logger = logging.getLogger(__name__)


class RedditScraper:
    """Handles scraping of Reddit posts for metadata and full content."""
    
    def __init__(self):
        """Initialize the Reddit scraper with default headers."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        logger.info("Initialized RedditScraper")
    
    def scrape_post_metadata(self, url: str) -> Dict[str, Any]:
        """
        Scrapes metadata from a single Reddit post using JSON API (primary) and HTML (fallback).
        
        Args:
            url: Reddit post URL
            
        Returns:
            dict: Post metadata (url, title, upvotes, comment_count)
        """
        # Convert old.reddit.com URLs to www.reddit.com for JSON compatibility
        clean_url = url.replace('old.reddit.com', 'www.reddit.com')
        
        # Try JSON API first (most reliable)
        try:
            json_data = self.get_post_json(clean_url)
            if json_data and len(json_data) >= 1:
                post_data = json_data[0]['data']['children'][0]['data']
                
                return {
                    'url': clean_url,
                    'title': post_data.get('title', 'No title found'),
                    'upvotes': post_data.get('score', 0),
                    'comment_count': post_data.get('num_comments', 0)
                }
        except Exception as e:
            logger.warning(f"JSON API failed for {url}: {str(e)}")
        
        # Fallback to HTML scraping
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Check if it's old.reddit.com
            is_old_reddit = 'old.reddit.com' in url
            
            # Extract title
            title = None
            if is_old_reddit:
                title_elem = soup.find('a', class_='title')
                if title_elem:
                    title = title_elem.get_text(strip=True)
            else:
                title_tag = soup.find('h1')
                if title_tag:
                    title = title_tag.get_text(strip=True)
            
            # Fallback: meta tag
            if not title:
                title_meta = soup.find('meta', property='og:title')
                if title_meta:
                    title = title_meta.get('content', '')
            
            # Extract upvotes (score) - try multiple approaches
            upvotes = 0
            if is_old_reddit:
                score_elem = soup.find('div', class_='score unvoted')
                if not score_elem:
                    score_elem = soup.find('div', class_='score likes')
                if not score_elem:
                    score_elem = soup.find('div', class_='score dislikes')
                if score_elem:
                    score_text = score_elem.get_text(strip=True)
                    upvotes = self._parse_number(score_text)
            else:
                # Try multiple selectors for new Reddit
                score_selectors = [
                    'div[data-click-id="upvote"]',
                    '.vote-button--up .vote-button__text',
                    '[data-testid="vote-button"]',
                    '.score'
                ]
                for selector in score_selectors:
                    score_element = soup.select_one(selector)
                    if score_element:
                        score_text = score_element.get_text(strip=True)
                        parsed_score = self._parse_number(score_text)
                        if parsed_score > 0:
                            upvotes = parsed_score
                            break
            
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
                comment_elem = soup.find('a', class_='comments')
                if comment_elem:
                    text = comment_elem.get_text(strip=True).lower()
                    comment_count = self._parse_number(text)
            else:
                # Try multiple selectors for new Reddit
                comment_selectors = [
                    'a[href*="/comments/"]',
                    '[data-testid="comment-count"]',
                    '.comment-count'
                ]
                for selector in comment_selectors:
                    comment_elements = soup.select(selector)
                    for elem in comment_elements:
                        text = elem.get_text(strip=True).lower()
                        if 'comment' in text:
                            parsed_count = self._parse_number(text)
                            if parsed_count > 0:
                                comment_count = parsed_count
                                break
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
            
            return {
                'url': clean_url,
                'title': title or 'No title found',
                'upvotes': upvotes,
                'comment_count': comment_count
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': clean_url,
                'title': 'Error loading',
                'upvotes': 0,
                'comment_count': 0
            }

    def scrape_complete_post(self, url: str) -> Dict[str, Any]:
        """
        Scrapes complete post data including full content and comments.
        
        Args:
            url: Reddit post URL
            
        Returns:
            dict: Complete post data with post content and comments
        """
        # Convert old.reddit.com URLs to www.reddit.com for JSON compatibility
        clean_url = url.replace('old.reddit.com', 'www.reddit.com')
        
        try:
            # Get JSON data which includes full post and comments
            json_data = self.get_post_json(clean_url)
            if json_data:
                # Extract complete post and comment data
                complete_data = self.extract_post_and_comments(json_data)
                if complete_data:
                    return complete_data
                else:
                    logger.warning(f"Failed to extract complete data from JSON for {url}")
            
            # Fallback: return basic metadata if complete extraction fails
            logger.warning(f"Falling back to basic metadata for {url}")
            basic_metadata = self.scrape_post_metadata(url)
            return {
                'post': {
                    'title': basic_metadata['title'],
                    'selftext': 'Content extraction failed',
                    'selftext_html': '',
                    'is_self_post': True,
                    'post_type': 'text',
                    'author': 'unknown',
                    'score': basic_metadata['upvotes'],
                    'upvote_ratio': 0.0,
                    'num_comments': basic_metadata['comment_count'],
                    'created_utc': 0.0,
                    'url': basic_metadata['url'],
                    'permalink': '',
                    'subreddit': 'unknown',
                    'link_flair_text': None,
                    'domain': 'self.unknown',
                    'is_video': False,
                    'thumbnail': 'self',
                    'preview_images': []
                },
                'comments': [],
                'total_comments': 0
            }
            
        except Exception as e:
            logger.error(f"Error scraping complete post {url}: {str(e)}")
            return {
                'post': {
                    'title': 'Error loading',
                    'selftext': 'Failed to load content',
                    'selftext_html': '',
                    'is_self_post': True,
                    'post_type': 'text',
                    'author': 'unknown',
                    'score': 0,
                    'upvote_ratio': 0.0,
                    'num_comments': 0,
                    'created_utc': 0.0,
                    'url': clean_url,
                    'permalink': '',
                    'subreddit': 'unknown',
                    'link_flair_text': None,
                    'domain': 'self.unknown',
                    'is_video': False,
                    'thumbnail': 'self',
                    'preview_images': []
                },
                'comments': [],
                'total_comments': 0
            }
    
    def scrape_multiple_posts(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrapes metadata from multiple Reddit posts.
        
        Args:
            urls: List of Reddit URLs
            
        Returns:
            list: List of post metadata dictionaries
        """
        logger.info(f"Scraping metadata from {len(urls)} posts...")
        posts_data = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"[{i}/{len(urls)}] Scraping: {url[:60]}...")
            metadata = self.scrape_post_metadata(url)
            posts_data.append(metadata)
            
            # Be polite to Reddit
            time.sleep(1)
        
        logger.info(f"Successfully scraped {len(posts_data)} posts")
        return posts_data

    def scrape_multiple_complete_posts(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrapes complete data from multiple Reddit posts including full content and comments.
        
        Args:
            urls: List of Reddit URLs
            
        Returns:
            list: List of complete post data dictionaries
        """
        logger.info(f"Scraping complete data from {len(urls)} posts...")
        posts_data = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"[{i}/{len(urls)}] Scraping complete: {url[:60]}...")
            complete_data = self.scrape_complete_post(url)
            posts_data.append(complete_data)
            
            # Be polite to Reddit
            time.sleep(1)
        
        logger.info(f"Successfully scraped complete data from {len(posts_data)} posts")
        return posts_data
    
    def get_post_json(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetches the full JSON data for a Reddit post.
        
        Args:
            url: Reddit post URL
            
        Returns:
            dict: Full JSON data from Reddit, or None if error
        """
        # Ensure URL ends with /
        clean_url = url.rstrip('/') + '/.json'
        
        try:
            logger.info(f"Fetching JSON: {clean_url}")
            response = requests.get(clean_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            logger.info("Successfully fetched JSON data")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching JSON: {str(e)}")
            return None
    
    def extract_post_and_comments(self, json_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extracts structured post and comment data from Reddit JSON.
        
        Args:
            json_data: Raw JSON from Reddit
            
        Returns:
            dict: Structured data with post and comments, or None if error
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
                'selftext_html': post_data.get('selftext_html', ''),
                'is_self_post': is_self,
                'post_type': post_hint if post_hint else ('text' if is_self else 'link'),
                'author': post_data.get('author', ''),
                'score': post_data.get('score', 0),
                'upvote_ratio': post_data.get('upvote_ratio', 0),
                'num_comments': post_data.get('num_comments', 0),
                'created_utc': post_data.get('created_utc', 0),
                'url': post_data.get('url', ''),
                'permalink': post_data.get('permalink', ''),
                'subreddit': post_data.get('subreddit', ''),
                'link_flair_text': post_data.get('link_flair_text', ''),
                'domain': post_data.get('domain', ''),
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
            logger.error(f"Error parsing JSON: {str(e)}")
            return None
    
    def _extract_preview_images(self, post_data: Dict[str, Any]) -> List[str]:
        """Extract preview image URLs if available."""
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
    
    def _extract_comment(self, comment_wrapper: Dict[str, Any], depth: int = 0) -> Optional[Dict[str, Any]]:
        """Recursively extracts comment data including nested replies."""
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
    def _parse_number(text: str) -> int:
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

