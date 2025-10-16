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
1. **Click the "Deploy to Render" button above** or go to [render.com](https://render.com)
2. **Connect your GitHub account to Render** (if you haven't already)
3. **Create a new Web Service:**
   - Connect this repository
   - **Name**: `hackernews-mcp`
   - **Environment**: `Python 3`
   - **Plan**: `Free`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/server.py`
4. **Deploy!** (No additional environment variables needed - uses public Hacker News API)

> Note: On Render's free tier, services go idle after ~15 minutes of inactivity and may require a manual "Deploy" to wake or to pick up the latest commit. Unlike Vercel, pushes do not auto-deploy by default.

Your server will be available at `https://hackernews-mcp.onrender.com/mcp`

## 🎯 Poke Integration

1. Go to [poke.com/settings/connections](https://poke.com/settings/connections)
2. Add the MCP URL: `https://hackernews-mcp.onrender.com/mcp`
3. Give it a name like "Hacker News"
4. Try: "Can you use the Hacker News MCP to get top stories?"

## 🧩 Architecture Note (FastAPI + FastMCP Hybrid)

Note: FastMCP 2.x responses didn’t work well with Poke’s client in my testing due to response format differences. The client expects simpler JSON but errors on FastMCP’s structured content with "Cannot read properties of undefined (reading 'status')". This was reproducible with Interaction’s basic FastMCP template as well.

So for now, this server uses a hybrid architecture where:
- FastAPI endpoints deliver Poke‑compatible JSON
- `@mcp.tool()` functions exist as future‑ready wrappers
- Shared logic lives in `_http` functions to avoid duplication

To try pure FastMCP later:
1) replace the entire FastAPI main block with `mcp.run()`,
2) optionally move each `_http` function’s logic into the corresponding `@mcp.tool()` (or keep wrappers calling `_http`), and
3) remove FastAPI routes if no longer needed.

This works with Poke today while keeping a clean migration path to pure FastMCP.

## References

- Based on the Interaction MCP server template: [MCP Server Template](https://github.com/InteractionCo/mcp-server-template/tree/main)
- Discovered via Interaction’s HackMIT challenge: [Interaction HackMIT Challenge](https://interaction.co/HackMIT)

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
