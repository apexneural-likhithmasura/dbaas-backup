# Reddit-Based Market Opportunity Identifier

An advanced AI-powered tool that identifies potential product or service opportunities by analyzing user-generated content on Reddit. This system discovers genuine user pain points and unmet needs through systematic analysis of Reddit discussions.

## 🎯 Features

- **Automated Google Search**: Finds relevant Reddit discussions using sophisticated query templates
- **Web Scraping**: Extracts post metadata (title, upvotes, comments) without using Reddit API
- **AI-Powered Ranking**: Uses OpenAI GPT-4 to rank posts by product development potential
- **Deep JSON Extraction**: Retrieves complete post and comment data via Reddit's JSON endpoints
- **Interactive CLI**: User-friendly command-line interface for selecting posts to analyze
- **Structured Output**: Generates JSON files with complete analysis data

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Internet connection

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your OpenAI API key**:
   - The `.env` file already contains your API key
   - To change it, edit the `.env` file:
     ```
     OPENROUTER_API_KEY=your-api-key-here
     ```

### Running the Application

```bash
python main.py
```

## 📖 How It Works

### Workflow

The application follows a 6-step process:

#### **Step 1: Formulate and Execute Search Query**
- Takes your market topic (e.g., "learning guitar as an adult")
- Builds a sophisticated Google search query targeting Reddit discussions
- Searches for posts containing pain points, struggles, and user experiences
- Collects 20-30 relevant Reddit URLs

#### **Step 2: Scrape Post Metadata**
- Visits each Reddit URL
- Extracts: title, upvotes, comment count
- No Reddit API required - uses web scraping

#### **Step 3: AI-Powered Ranking**
- Sends post data to OpenAI GPT-4
- Analyzes posts based on:
  - **Product Development Potential (70%)**: How clearly the post articulates a problem or pain point
  - **Relevance (30%)**: How directly related to your target market
- Returns top 10 ranked posts with justifications

#### **Step 4: User Selection**
- Displays ranked results
- Allows you to select posts for deep analysis
- Flexible selection: single posts, multiple posts, or ranges

#### **Step 5: Deep JSON Extraction**
- Fetches complete JSON data from Reddit
- Extracts all comments with full nested structure
- Saves both raw and structured data

#### **Step 6: Final Output**
- Generates comprehensive JSON files
- Creates summary report
- All files saved to `output/` directory

## 📁 Output Files

All output files are saved in the `output/` directory with the following naming convention:

- `{market}_raw_posts.json` - All scraped post metadata
- `{market}_ranked_posts.json` - Top 10 ranked posts with scores
- `{market}_ranked_output.txt` - Human-readable ranked results
- `{market}_post_rank_{N}.json` - Raw Reddit JSON for selected posts
- `{market}_post_rank_{N}_structured.json` - Parsed post and comments
- `{market}_complete_analysis.json` - Complete workflow results

## 💡 Example Usage

```bash
$ python main.py

Enter the market/niche to explore: remote work productivity

Number of search results to retrieve (default 30): 25
Number of top posts to rank (default 10): 10

[System searches Google, scrapes Reddit, ranks posts...]

Top 10 Reddit Discussions for "remote work productivity"

#1: My biggest struggle with remote work is staying focused
  URL: https://reddit.com/r/...
  Engagement: 1,234 upvotes, 456 comments
  Potential Score: 9/10
  Justification: Post highlights a widespread pain point with high engagement...

[... more results ...]

SELECT POSTS FOR DEEP ANALYSIS
Your selection: 1,3,5

[System extracts complete JSON data for selected posts...]

✅ WORKFLOW COMPLETE!
```

## 🔍 Advanced Features

### Custom Query Template

The search query is designed to find posts where users express:
- Personal experiences ("I think", "I feel", "my experience")
- Struggles ("my biggest struggle", "pain point", "frustrations")
- Problems ("issues", "challenges", "difficulties")
- Wishes ("what I wish I knew", "what I regret")

### AI Ranking Criteria

OpenAI GPT-4 analyzes each post for:
1. **Clarity of problem articulation**
2. **Strength of pain point expression**
3. **Community validation** (upvotes, comments)
4. **Product opportunity signals**
5. **Market relevance**

### Data Structure

Structured JSON output includes:
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
  ]
}
```

## 🛠️ Technical Details

### Architecture

- **google_search.py**: Google search automation
- **reddit_scraper.py**: Web scraping and JSON extraction
- **openai_ranker.py**: AI-powered post ranking
- **main.py**: Workflow orchestration

### Dependencies

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `lxml`: XML/HTML parser
- `openai`: OpenAI API client
- `python-dotenv`: Environment variable management

### Rate Limiting

The application includes polite delays:
- 2 seconds between Google search pages
- 1 second between Reddit post scrapes
- Prevents overwhelming servers

## 📊 Use Cases

- **Product Managers**: Identify user pain points for new features
- **Entrepreneurs**: Discover product opportunities
- **Market Researchers**: Understand user needs in specific niches
- **UX Designers**: Find usability issues and friction points
- **Content Creators**: Understand what resonates with audiences

## ⚠️ Important Notes

1. **No Reddit API**: This tool uses web scraping and public JSON endpoints - no Reddit API key required
2. **OpenAI Costs**: GPT-4 API calls incur costs (typically $0.01-0.03 per analysis)
3. **Rate Limits**: Built-in delays prevent rate limiting
4. **Internet Required**: Active internet connection needed throughout
5. **Real Data Only**: No mock data - all results are live from Reddit

## 🔒 Security

- API keys stored in `.env` file (not committed to git)
- `.gitignore` configured to protect sensitive data
- Follow OpenAI's best practices for API key management

## 🤝 Contributing

This is a standalone tool designed for market research. Modify the query templates in `google_search.py` or ranking criteria in `openai_ranker.py` to suit your specific needs.

## 📝 License

Free to use for market research and product development purposes.

## 🆘 Troubleshooting

**Issue**: No search results found
- **Solution**: Try a different market topic or check internet connection

**Issue**: OpenAI API error
- **Solution**: Verify API key in `.env` file and check OpenAI account credits

**Issue**: Scraping errors
- **Solution**: Some Reddit posts may have restricted access; the tool will skip them

**Issue**: Empty metadata
- **Solution**: Reddit's HTML structure occasionally changes; fallback values are used

## 📧 Support

For issues or questions, review the output logs which provide detailed information about each step of the process.

---

**Built with ❤️ for discovering real user needs and building products people actually want.**
