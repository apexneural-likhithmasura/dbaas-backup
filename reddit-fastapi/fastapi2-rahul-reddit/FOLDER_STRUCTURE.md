# Output Folder Structure

## Overview

Each market analysis now gets its **own dedicated folder** with a timestamp for easy organization.

## Folder Naming Convention

```
output/
├── {market_name}_{timestamp}/
│   ├── {market}_raw_posts.json
│   ├── {market}_ranked_posts.json
│   ├── {market}_ranked_output.txt
│   ├── {market}_post_rank_1.json
│   ├── {market}_post_rank_1_structured.json
│   └── {market}_complete_analysis.json
│
├── {another_market}_{timestamp}/
│   └── ...
│
└── {third_market}_{timestamp}/
    └── ...
```

## Example Structure

```
output/
├── knee_pain_20251008_105530/
│   ├── knee_pain_raw_posts.json
│   ├── knee_pain_ranked_posts.json
│   ├── knee_pain_ranked_output.txt
│   ├── knee_pain_post_rank_1.json
│   ├── knee_pain_post_rank_1_structured.json
│   ├── knee_pain_post_rank_2.json
│   ├── knee_pain_post_rank_2_structured.json
│   └── knee_pain_complete_analysis.json
│
├── bitcoin_trading_20251008_110205/
│   ├── bitcoin_trading_raw_posts.json
│   ├── bitcoin_trading_ranked_posts.json
│   ├── bitcoin_trading_ranked_output.txt
│   └── bitcoin_trading_complete_analysis.json
│
└── remote_work_productivity_20251008_111430/
    └── ...
```

## Benefits

### ✅ **Organization**
- Each market has its own folder
- No file mixing between different analyses
- Easy to find specific market research

### ✅ **Version Control**
- Timestamp prevents overwriting
- Run same market multiple times
- Compare results over time

### ✅ **Clean Structure**
- All related files grouped together
- Easy to share specific analysis
- Simple to archive or delete

## Folder Name Format

```
{market_topic}_{YYYYMMDD}_{HHMMSS}
```

**Examples:**
- `knee_pain_20251008_105530`
- `stocks_trading_20251008_110205`
- `meal_prep_ideas_20251008_111430`

## Timestamp Format

- **YYYYMMDD**: Date (2025-10-08)
- **HHMMSS**: Time (10:55:30)
- 24-hour format
- No spaces or special characters

## Finding Your Data

### **Method 1: Check Terminal Output**
After running, the system displays:
```
✅ WORKFLOW COMPLETE!

📊 Summary:
  • Output Directory: d:/demo1 of reddit lib/output/knee_pain_20251008_105530
```

### **Method 2: Browse output/ Folder**
```bash
cd "d:/demo1 of reddit lib/output"
dir
```

### **Method 3: Use View Script**
```bash
python view_post_content.py
```
The script will show all available market folders and let you select one.

## File Organization Tips

### **Keep Multiple Analyses**
```
output/
├── bitcoin_20251008_100000/  # Morning analysis
├── bitcoin_20251008_150000/  # Afternoon analysis
└── bitcoin_20251009_100000/  # Next day analysis
```

### **Archive Old Data**
```
output/
├── archive/
│   ├── old_analysis_1/
│   └── old_analysis_2/
├── current_analysis_1/
└── current_analysis_2/
```

### **Export for Sharing**
Just zip the specific market folder:
```
knee_pain_20251008_105530.zip
```

## Viewing Content

### **View Ranked Posts**
Open: `{market}_{timestamp}/{market}_ranked_output.txt`

This is human-readable and shows:
- Top 10 ranked posts
- AI justifications
- Engagement metrics

### **View Complete Data**
Open: `{market}_{timestamp}/{market}_complete_analysis.json`

This contains:
- All URLs found
- All ranked posts
- All deep analysis results

### **View Individual Posts**
Open: `{market}_{timestamp}/{market}_post_rank_1_structured.json`

This shows:
- Full post content
- All comments with nested replies
- Metadata and scores

## Automated Cleanup (Optional)

To keep only recent analyses, you can manually delete old folders:

```bash
# Windows
cd "d:/demo1 of reddit lib/output"
rmdir /s "old_folder_name"

# Or just delete via File Explorer
```

## What Gets Created

### **Always Created:**
1. `{market}_raw_posts.json` - Scraped metadata
2. `{market}_ranked_posts.json` - Top 10 with AI scores
3. `{market}_ranked_output.txt` - Human-readable report

### **Created if Posts Selected:**
4. `{market}_post_rank_{N}.json` - Raw Reddit JSON
5. `{market}_post_rank_{N}_structured.json` - Parsed data

### **Final Summary:**
6. `{market}_complete_analysis.json` - Everything combined

---

**This structure makes it easy to:**
- Run multiple analyses without conflicts
- Compare different markets side-by-side
- Archive or share specific research
- Track changes over time
