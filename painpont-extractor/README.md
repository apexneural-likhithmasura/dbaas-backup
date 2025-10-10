# Pain Point & Market Gap Analyzer API

A FastAPI application that extracts pain points from Reddit conversations and generates business solutions and market opportunities.

## Features

- **Pain Point Extraction**: Analyzes Reddit conversations to identify user pain points, frustrations, and unmet needs
- **Market Gap Generation**: Generates business solutions and market opportunities based on extracted pain points
- **Chained Pipeline**: Automatically passes pain point analysis to solution generator
- **Flexible Input**: Accepts file uploads or existing file paths
- **JSON Output**: Returns structured JSON responses with complete analysis

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project directory:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:

```
OPENROUTER_API_KEY=your_actual_api_key_here
```

Get your API key from: https://openrouter.ai/

### 3. Run the API

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### 1. Root Endpoint
**GET /** - API information and available endpoints

```bash
curl http://localhost:8000/
```

### 2. Health Check
**GET /health** - Check API health and configuration status

```bash
curl http://localhost:8000/health
```

### 3. Analyze Uploaded Files
**POST /analyze-files** - Upload TXT files for analysis

```bash
curl -X POST "http://localhost:8000/analyze-files" \
  -F "files=@test_data.txt" \
  -F "files=@test_data2.txt" \
  -F "model=anthropic/claude-3.5-sonnet" \
  -F "temperature=0.7"
```

**Parameters:**
- `files` (required): One or more TXT files containing Reddit conversations
- `model` (optional): AI model to use (default: "anthropic/claude-3.5-sonnet")
- `temperature` (optional): Model temperature 0.0-1.0 (default: 0.7)

### 4. Analyze Existing Files
**POST /analyze-paths** - Analyze files from existing paths

```bash
curl -X POST "http://localhost:8000/analyze-paths" \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": ["/path/to/test_data.txt", "/path/to/test_data2.txt"],
    "model": "anthropic/claude-3.5-sonnet",
    "temperature": 0.7
  }'
```

**Request Body:**
```json
{
  "file_paths": ["/path/to/file1.txt", "/path/to/file2.txt"],
  "model": "anthropic/claude-3.5-sonnet",
  "temperature": 0.7
}
```

## Response Format

Both analysis endpoints return a JSON response with the following structure:

```json
{
  "pain_points": {
    "summary": "Brief overview of major pain points identified",
    "categories": [
      {
        "category_name": "Category name",
        "pain_points": [
          {
            "heading": "Clear descriptive heading",
            "summary": "1-2 sentence summary",
            "quotes": ["Quote 1", "Quote 2"],
            "frequency_intensity": "Note on frequency/intensity"
          }
        ]
      }
    ],
    "priority_ranking": [
      {
        "rank": 1,
        "pain_point": "Pain point description",
        "frequency": "high/medium/low",
        "intensity": "high/medium/low",
        "specificity": "high/medium/low",
        "solvability": "high/medium/low",
        "reasoning": "Brief explanation"
      }
    ]
  },
  "market_solutions": "Detailed business solutions and market opportunities (text format)",
  "status": "success",
  "message": "Successfully analyzed N file(s)"
}
```

## Example Usage

### Python Example

```python
import requests

# Upload files for analysis
with open('reddit_data.txt', 'rb') as f1, open('reddit_data2.txt', 'rb') as f2:
    files = [
        ('files', ('reddit_data.txt', f1, 'text/plain')),
        ('files', ('reddit_data2.txt', f2, 'text/plain'))
    ]
    
    response = requests.post(
        'http://localhost:8000/analyze-files',
        files=files,
        data={'model': 'anthropic/claude-3.5-sonnet', 'temperature': 0.7}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("Pain Points:", result['pain_points'])
        print("\nMarket Solutions:", result['market_solutions'])
    else:
        print("Error:", response.json())
```

### JavaScript/Node.js Example

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('files', fs.createReadStream('reddit_data.txt'));
form.append('files', fs.createReadStream('reddit_data2.txt'));
form.append('model', 'anthropic/claude-3.5-sonnet');
form.append('temperature', '0.7');

axios.post('http://localhost:8000/analyze-files', form, {
  headers: form.getHeaders()
})
.then(response => {
  console.log('Pain Points:', response.data.pain_points);
  console.log('Market Solutions:', response.data.market_solutions);
})
.catch(error => {
  console.error('Error:', error.response.data);
});
```

## API Documentation

Once the server is running, visit these URLs for interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## File Requirements

- Input files must be in `.txt` format
- Files should contain Reddit conversations, comments, or discussions
- Multiple files can be processed in a single request
- Each file is analyzed together to identify common pain points

## Logging

The application generates detailed logs:
- `pain_point_analyzer.log` - Pain point extraction logs
- `solution_generator.log` - Market solution generation logs

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `400` - Bad request (invalid file type, missing parameters)
- `404` - File not found (for path-based analysis)
- `500` - Internal server error (API key issues, processing errors)

## Models Available

The API uses OpenRouter, which provides access to various models:
- `anthropic/claude-3.5-sonnet` (default, recommended)
- `anthropic/claude-3-opus`
- `openai/gpt-4-turbo`
- And many more available on OpenRouter

## Architecture

The application follows a two-stage pipeline:

1. **Pain Point Extraction** (`pain_point_extractor.py`)
   - Analyzes Reddit conversations
   - Identifies pain points, frustrations, and unmet needs
   - Extracts user quotes
   - Ranks pain points by priority
   - Returns structured JSON

2. **Market Gap Generation** (`market_gap_generator.py`)
   - Takes pain points as input
   - Applies strategic frameworks
   - Generates business solutions
   - Evaluates market opportunities
   - Returns detailed recommendations

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

