# Project Structure

## Overview

```
d:/demo1 of reddit lib/
│
├── main.py                      # Main application entry point
├── google_search.py             # Google search functionality
├── reddit_scraper.py            # Reddit scraping and JSON extraction
├── openai_ranker.py             # AI-powered post ranking
├── example_usage.py             # Usage examples and demonstrations
│
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (API key)
├── .gitignore                   # Git ignore rules
│
├── README.md                    # Full documentation
├── QUICKSTART.md                # Quick start guide
├── PROJECT_STRUCTURE.md         # This file
│
├── run.bat                      # Windows launcher script
│
└── output/                      # Generated output files
    ├── {market}_raw_posts.json
    ├── {market}_ranked_posts.json
    ├── {market}_ranked_output.txt
    ├── {market}_post_rank_N.json
    ├── {market}_post_rank_N_structured.json
    └── {market}_complete_analysis.json
```

## Core Modules

### 1. `main.py`
**Purpose**: Orchestrates the complete workflow

**Key Classes**:
- `MarketOpportunityIdentifier`: Main workflow controller

**Key Methods**:
- `run_workflow()`: Executes the 6-step process
- `_get_user_selection()`: Interactive post selection
- `_parse_selection()`: Parses user input (e.g., "1,3,5-8")
- `_save_json()`: Saves JSON output
- `_save_text()`: Saves text output

**Usage**:
```python
identifier = MarketOpportunityIdentifier(api_key)
identifier.run_workflow("remote work", num_results=30, top_n=10)
```

---

### 2. `google_search.py`
**Purpose**: Searches Google for Reddit discussions

**Key Classes**:
- `GoogleSearcher`: Handles Google search operations

**Key Methods**:
- `build_query()`: Builds search query from template
- `search_google()`: Performs Google search
- `search_market()`: Complete search workflow

**Search Query Template**:
```
"{market}" (site:reddit.com inurl:comments|inurl:thread | 
intext:"I think"|"I feel"|"my biggest struggle"|"pain point"...)
```

**Features**:
- Extracts Reddit URLs from Google results
- Handles pagination (10 results per page)
- Polite delays (2 seconds between pages)
- URL cleaning and deduplication

**Usage**:
```python
searcher = GoogleSearcher()
urls = searcher.search_market("learning guitar", num_results=30)
```

---

### 3. `reddit_scraper.py`
**Purpose**: Scrapes Reddit posts and extracts JSON data

**Key Classes**:
- `RedditScraper`: Handles all Reddit interactions

**Key Methods**:
- `scrape_post_metadata()`: Extracts title, upvotes, comments
- `scrape_multiple_posts()`: Batch scraping
- `get_post_json()`: Fetches Reddit's JSON endpoint
- `extract_post_and_comments()`: Parses JSON structure
- `_extract_comment()`: Recursively extracts nested comments
- `_parse_number()`: Handles "1.2k" → 1200 conversion

**Data Extraction**:
1. **Metadata** (via web scraping):
   - Post title
   - Upvote count
   - Comment count

2. **Full JSON** (via .json endpoint):
   - Post content (selftext)
   - Author information
   - All comments with nested replies
   - Timestamps and scores

**Features**:
- No Reddit API required
- Handles deleted posts gracefully
- Preserves comment thread structure
- Rate limiting (1 second per request)

**Usage**:
```python
scraper = RedditScraper()

# Get metadata
metadata = scraper.scrape_post_metadata(url)

# Get full JSON
json_data = scraper.get_post_json(url)
structured = scraper.extract_post_and_comments(json_data)
```

---

### 4. `openai_ranker.py`
**Purpose**: AI-powered ranking using OpenAI GPT-4

**Key Classes**:
- `PostRanker`: Ranks posts by product potential

**Key Methods**:
- `rank_posts()`: Main ranking function
- `_create_ranking_prompt()`: Builds AI prompt
- `_fallback_ranking()`: Backup ranking (if API fails)
- `format_ranked_output()`: Creates human-readable output

**Ranking Criteria**:
1. **Product Development Potential (70%)**:
   - Clarity of problem articulation
   - Strength of pain point
   - Community validation (upvotes/comments)

2. **Relevance (30%)**:
   - Direct relation to target market
   - Central theme vs. passing mention

**AI Model**: GPT-4 Turbo Preview

**Output Format**:
```json
{
  "ranked_posts": [
    {
      "rank": 1,
      "index": 5,
      "justification": "...",
      "product_potential_score": 9
    }
  ]
}
```

**Features**:
- Structured JSON output
- Automatic fallback on API errors
- Engagement-based scoring backup

**Usage**:
```python
ranker = PostRanker(api_key)
ranked = ranker.rank_posts(posts_data, "remote work", top_n=10)
output = ranker.format_ranked_output(ranked, "remote work")
```

---

### 5. `example_usage.py`
**Purpose**: Demonstrates programmatic usage

**Examples**:
1. **Automated Analysis**: No user interaction, auto-analyze top 3
2. **Custom Workflow**: Manual control over each step
3. **Single Post Analysis**: Analyze specific URL

**Usage**:
```bash
python example_usage.py
```

---

## Data Flow

```
User Input (market topic)
    ↓
[GoogleSearcher] → Search Google → Extract Reddit URLs
    ↓
[RedditScraper] → Scrape metadata → Post data
    ↓
[PostRanker] → OpenAI ranking → Top 10 posts
    ↓
User selection
    ↓
[RedditScraper] → Fetch JSON → Complete post data
    ↓
Output files (JSON + text)
```

## Configuration

### Environment Variables (`.env`)
```
OPENROUTER_API_KEY=your-api-key-here
```

### Dependencies (`requirements.txt`)
- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `lxml`: Fast XML/HTML parser
- `openai`: OpenAI API client
- `python-dotenv`: Environment management
- `googlesearch-python`: Google search helper

## Output Structure

### Raw Posts (`{market}_raw_posts.json`)
```json
[
  {
    "url": "...",
    "title": "...",
    "upvotes": 1234,
    "comment_count": 456
  }
]
```

### Ranked Posts (`{market}_ranked_posts.json`)
```json
[
  {
    "rank": 1,
    "title": "...",
    "url": "...",
    "upvotes": 1234,
    "comment_count": 456,
    "justification": "...",
    "product_potential_score": 9
  }
]
```

### Structured Data (`{market}_post_rank_N_structured.json`)
```json
{
  "post": {
    "title": "...",
    "selftext": "...",
    "author": "...",
    "score": 1234,
    "num_comments": 456
  },
  "comments": [
    {
      "author": "...",
      "body": "...",
      "score": 78,
      "depth": 0,
      "replies": [...]
    }
  ],
  "total_comments": 456
}
```

## Extension Points

### Custom Search Queries
Modify `build_query()` in `google_search.py`:
```python
def build_query(self, market_to_explore):
    return f'{market_to_explore} site:reddit.com "your custom terms"'
```

### Custom Ranking Criteria
Modify `_create_ranking_prompt()` in `openai_ranker.py`:
```python
def _create_ranking_prompt(self, posts_summary, market_to_explore, top_n):
    # Add your custom ranking criteria
    prompt = """Your custom ranking instructions..."""
    return prompt
```

### Alternative AI Models
Change model in `openai_ranker.py`:
```python
response = self.client.chat.completions.create(
    model="gpt-3.5-turbo",  # or "gpt-4", etc.
    ...
)
```

## Best Practices

1. **Rate Limiting**: Built-in delays prevent overwhelming servers
2. **Error Handling**: Graceful degradation on failures
3. **Data Persistence**: All intermediate results saved
4. **Modularity**: Each component can be used independently
5. **No Mock Data**: All results are real, live data

## Testing Workflow

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test Google search
python -c "from google_search import GoogleSearcher; s = GoogleSearcher(); print(s.search_market('test', 5))"

# 3. Test scraping
python -c "from reddit_scraper import RedditScraper; s = RedditScraper(); print(s.scrape_post_metadata('https://reddit.com/r/Python/comments/...'))"

# 4. Run full workflow
python main.py
```

## Troubleshooting

**Import Errors**:
```bash
pip install -r requirements.txt
```

**API Errors**:
- Check `.env` file has correct API key
- Verify OpenAI account credits

**Scraping Failures**:
- Normal for some posts (deleted/private)
- Tool will skip and continue

**Empty Results**:
- Try more specific market topic
- Increase `num_results` parameter

---

**For detailed usage instructions, see README.md**
**For quick setup, see QUICKSTART.md**
