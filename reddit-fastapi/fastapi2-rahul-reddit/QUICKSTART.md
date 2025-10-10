# Quick Start Guide

## Installation (First Time Only)

### Option 1: Automatic (Windows)
1. Double-click `run.bat`
2. The script will automatically:
   - Create a virtual environment
   - Install all dependencies
   - Run the application

### Option 2: Manual
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Usage

### Basic Workflow

1. **Run the application**:
   ```bash
   python main.py
   ```

2. **Enter your market**:
   ```
   Enter the market/niche to explore: remote work productivity
   ```

3. **Set parameters** (or press Enter for defaults):
   ```
   Number of search results to retrieve (default 30): [Enter]
   Number of top posts to rank (default 10): [Enter]
   ```

4. **Review ranked results**:
   - The system will display top 10 posts
   - Each with a justification and potential score

5. **Select posts for deep analysis**:
   ```
   Your selection: 1,2,5
   ```
   Or use ranges: `1-5`
   Or skip: just press Enter

6. **Check output**:
   - All results saved in `output/` folder
   - JSON files contain complete data

### Example Markets to Explore

- "remote work productivity"
- "learning guitar as an adult"
- "sustainable gardening"
- "meal planning for busy parents"
- "home organization solutions"
- "freelance project management"
- "online fitness coaching"
- "pet training challenges"

### Understanding the Output

**Ranked Posts** show:
- **Rank**: Position (1-10)
- **Title**: Reddit post title
- **Engagement**: Upvotes and comments
- **Potential Score**: AI assessment (1-10)
- **Justification**: Why it's a good opportunity

**Deep Analysis** provides:
- Complete post content
- All comments with replies
- Author information
- Timestamps and scores

## Output Files

After running, check the `output/` folder:

```
output/
├── remote_work_productivity_raw_posts.json
├── remote_work_productivity_ranked_posts.json
├── remote_work_productivity_ranked_output.txt
├── remote_work_productivity_post_rank_1.json
├── remote_work_productivity_post_rank_1_structured.json
└── remote_work_productivity_complete_analysis.json
```

## Programmatic Usage

For automated workflows, see `example_usage.py`:

```bash
python example_usage.py
```

## Tips

1. **Be Specific**: "meal planning for vegetarians" works better than just "food"

2. **Check Engagement**: Posts with 100+ upvotes and 50+ comments often indicate real pain points

3. **Read Justifications**: The AI explains why each post has product potential

4. **Analyze Comments**: The deep analysis reveals how people are currently solving (or not solving) the problem

5. **Start Small**: Begin with 10-15 search results to test, then scale up

## Troubleshooting

**"No results found"**
- Try a different market
- Make it more specific
- Check internet connection

**"OpenAI API error"**
- Verify API key in `.env` file
- Check OpenAI account has credits
- Try again (temporary API issues)

**"Scraping errors"**
- Normal - some posts may be deleted or restricted
- The tool will skip them and continue

## Next Steps

1. ✅ Run your first analysis
2. 📊 Review the ranked posts
3. 🔍 Deep dive into top 3 posts
4. 💡 Identify product opportunities
5. 🚀 Build something people need!

---

**Questions?** Check the main README.md for detailed documentation.
