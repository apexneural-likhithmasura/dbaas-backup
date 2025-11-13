"""
Reddit Ranker

Uses AI (via OpenRouter) to analyze and rank Reddit posts by product development potential.
"""

from openai import OpenAI
import json
import logging
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


class RedditRanker:
    """Ranks Reddit posts using AI to identify product development opportunities."""
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        """
        Initialize the ranker with OpenRouter API.
        
        Args:
            api_key: OpenRouter API key
            model: Model to use for ranking (default: Claude 3.5 Sonnet)
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model
        logger.info(f"Initialized RedditRanker with model: {model}")
    
    def rank_posts(
        self,
        posts_data: List[Dict[str, Any]],
        market_to_explore: str,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Ranks posts by product development potential using AI.
        
        Args:
            posts_data: List of post metadata dictionaries
            market_to_explore: The market being researched
            top_n: Number of top posts to return (default: 10)
            
        Returns:
            list: Ranked list of posts with justifications
        """
        logger.info(f"Ranking {len(posts_data)} posts for '{market_to_explore}'...")
        
        # Prepare the data for AI
        posts_summary = []
        for i, post in enumerate(posts_data):
            posts_summary.append({
                'index': i,
                'title': post['title'],
                'url': post['url'],
                'upvotes': post['upvotes'],
                'comment_count': post['comment_count']
            })
        
        # Create the prompt
        prompt = self._create_ranking_prompt(posts_summary, market_to_explore, top_n)
        
        try:
            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert market research analyst specializing in identifying "
                            "product opportunities from user-generated content. Your role is to analyze "
                            "Reddit discussions and identify posts that signal strong potential for new "
                            "product or service development."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            ranked_posts = result.get('ranked_posts', [])
            
            # Enrich with original data
            enriched_posts = []
            for ranked_post in ranked_posts:
                original_index = ranked_post.get('index')
                if original_index is not None and original_index < len(posts_data):
                    enriched_posts.append({
                        'rank': ranked_post.get('rank'),
                        'title': posts_data[original_index]['title'],
                        'url': posts_data[original_index]['url'],
                        'upvotes': posts_data[original_index]['upvotes'],
                        'comment_count': posts_data[original_index]['comment_count'],
                        'justification': ranked_post.get('justification', ''),
                        'product_potential_score': ranked_post.get('product_potential_score', 0)
                    })
            
            logger.info(f"Successfully ranked {len(enriched_posts)} posts")
            return enriched_posts
            
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {str(e)}")
            # Fallback: simple ranking by engagement
            return self._fallback_ranking(posts_data, top_n)
    
    def _create_ranking_prompt(
        self,
        posts_summary: List[Dict[str, Any]],
        market_to_explore: str,
        top_n: int
    ) -> str:
        """
        Creates the prompt for AI ranking.
        
        Args:
            posts_summary: List of post summaries
            market_to_explore: The market being researched
            top_n: Number of top posts to return
            
        Returns:
            str: The formatted prompt
        """
        prompt = f"""
I need you to analyze the following Reddit posts related to "{market_to_explore}" and identify the top {top_n} posts that signal the strongest potential for a new product or service.

**Ranking Criteria:**
1. **Product Development Potential (70% weight)**: How clearly does the post title articulate a problem, pain point, struggle, or strong unmet desire? High-potential posts feature discussions about frustrations, lack of good solutions, or wishes for something better. High comment_count and upvotes often correlate with widely shared problems.

2. **Relevance (30% weight)**: How directly is the post related to "{market_to_explore}"? Is it a central theme or just a passing mention?

**Posts to Analyze:**
{json.dumps(posts_summary, indent=2)}

**Required Output Format (JSON):**
{{
  "ranked_posts": [
    {{
      "rank": 1,
      "index": <original index from input>,
      "justification": "<1-2 sentence explanation of why this post was ranked highly, specifically referencing its product development potential>",
      "product_potential_score": <score from 1-10>
    }},
    ...
  ]
}}

Provide exactly {top_n} ranked posts in your response.
"""
        return prompt
    
    def _fallback_ranking(
        self,
        posts_data: List[Dict[str, Any]],
        top_n: int
    ) -> List[Dict[str, Any]]:
        """
        Fallback ranking method based on engagement metrics.
        
        Args:
            posts_data: List of post metadata
            top_n: Number of top posts to return
            
        Returns:
            list: Ranked posts
        """
        logger.info("Using fallback ranking based on engagement metrics")
        
        # Calculate engagement score
        scored_posts = []
        for post in posts_data:
            engagement_score = (post['upvotes'] * 0.5) + (post['comment_count'] * 0.5)
            scored_posts.append({
                'post': post,
                'score': engagement_score
            })
        
        # Sort by score
        scored_posts.sort(key=lambda x: x['score'], reverse=True)
        
        # Format output
        ranked_posts = []
        for i, item in enumerate(scored_posts[:top_n], 1):
            post = item['post']
            ranked_posts.append({
                'rank': i,
                'title': post['title'],
                'url': post['url'],
                'upvotes': post['upvotes'],
                'comment_count': post['comment_count'],
                'justification': f'High engagement with {post["upvotes"]} upvotes and {post["comment_count"]} comments indicates community interest.',
                'product_potential_score': min(10, int(item['score'] / 100))
            })
        
        return ranked_posts
    
    def format_ranked_output(
        self,
        ranked_posts: List[Dict[str, Any]],
        market_to_explore: str
    ) -> str:
        """
        Formats ranked posts for display.
        
        Args:
            ranked_posts: List of ranked posts
            market_to_explore: The market being researched
            
        Returns:
            str: Formatted output string
        """
        output = f"\n{'=' * 80}\n"
        output += f"Top {len(ranked_posts)} Reddit Discussions for \"{market_to_explore}\"\n"
        output += f"{'=' * 80}\n\n"
        
        for post in ranked_posts:
            output += f"#{post['rank']}: {post['title']}\n"
            output += f"  URL: {post['url']}\n"
            output += f"  Engagement: {post['upvotes']} upvotes, {post['comment_count']} comments\n"
            output += f"  Potential Score: {post.get('product_potential_score', 'N/A')}/10\n"
            output += f"  Justification: {post['justification']}\n\n"
        
        output += f"{'=' * 80}\n"
        return output

