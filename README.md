# Hacker News MCP Server

A FastMCP server that provides access to Hacker News data for Poke integration.

## 🚀 Features

- **get_top_stories**: Fetch top stories from Hacker News
- **get_story**: Get details of a specific story by ID
- **get_new_stories**: Fetch newest stories
- **search_stories**: Search for stories using Algolia API

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python src/server.py
```

## 🚢 Deployment

### Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Steps:**
1. **Fork this repository** (if you haven't already)
2. **Connect your GitHub account to Render** (if you haven't already)
3. **Click the "Deploy to Render" button above** or go to [render.com](https://render.com)
4. **Create a new Web Service:**
   - Connect your forked repository
   - **Name**: `hackernews-mcp`
   - **Environment**: `Python 3`
   - **Plan**: `Free`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/server.py`
5. **Deploy!** (No additional environment variables needed - uses public Hacker News API)

Your server will be available at `https://hackernews-mcp.onrender.com/mcp`

## 🎯 Poke Integration

1. Go to [poke.com/settings/connections](https://poke.com/settings/connections)
2. Add the MCP URL: `https://hackernews-mcp.onrender.com/mcp`
3. Give it a name like "Hacker News"
4. Test with: "Tell the subagent to use the Hacker News integration's get_top_stories tool"

## 🔧 Available Tools

- `get_top_stories(limit=10)`: Get top stories (max 30)
- `get_story(story_id)`: Get specific story details
- `get_new_stories(limit=10)`: Get newest stories (max 30)
- `search_stories(query, limit=10)`: Search stories (max 20)

## 📝 Example Usage

```python
# Get top 5 stories
get_top_stories(limit=5)

# Get story details
get_story(story_id=12345)

# Search for Python stories
search_stories(query="python", limit=5)
```
