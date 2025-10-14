#!/usr/bin/env python3
"""
Hacker News MCP Server
A FastMCP server that provides access to Hacker News data.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
import httpx
from fastmcp import FastMCP

# Create the FastMCP server
mcp = FastMCP("Hacker News MCP Server")

# Hacker News API base URL
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"

# Undecorated functions for HTTP endpoint
def get_top_stories_http(limit: int = 10) -> str:
    """Get top stories from Hacker News."""
    try:
        limit = min(max(limit, 1), 30)  # Clamp between 1 and 30
        
        # Fetch top story IDs
        response = httpx.get(f"{HN_API_BASE}/topstories.json", timeout=10.0)
        response.raise_for_status()
        story_ids = response.json()[:limit]
        
        # Fetch story details
        stories = []
        for story_id in story_ids:
            story_response = httpx.get(f"{HN_API_BASE}/item/{story_id}.json", timeout=5.0)
            story_response.raise_for_status()
            story = story_response.json()
            
            if story and story.get('type') == 'story':
                stories.append({
                    'id': story.get('id'),
                    'title': story.get('title', ''),
                    'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                    'score': story.get('score', 0),
                    'author': story.get('by', ''),
                    'comments': story.get('descendants', 0),
                    'time': story.get('time', 0),
                    'time_iso': story.get('time') and str(story.get('time')) or None
                })
        
        return json.dumps(stories, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

def get_new_stories_http(limit: int = 10) -> str:
    """Get newest stories from Hacker News."""
    try:
        limit = min(max(limit, 1), 30)  # Clamp between 1 and 30
        
        # Fetch new story IDs
        response = httpx.get(f"{HN_API_BASE}/newstories.json", timeout=10.0)
        response.raise_for_status()
        story_ids = response.json()[:limit]
        
        # Fetch story details
        stories = []
        for story_id in story_ids:
            story_response = httpx.get(f"{HN_API_BASE}/item/{story_id}.json", timeout=5.0)
            story_response.raise_for_status()
            story = story_response.json()
            
            if story and story.get('type') == 'story':
                stories.append({
                    'id': story.get('id'),
                    'title': story.get('title', ''),
                    'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                    'score': story.get('score', 0),
                    'author': story.get('by', ''),
                    'time': story.get('time', 0),
                    'time_iso': story.get('time') and str(story.get('time')) or None
                })
        
        return json.dumps(stories, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

def get_story_http(story_id: int) -> str:
    """Get details of a specific Hacker News story by ID."""
    try:
        response = httpx.get(f"{HN_API_BASE}/item/{story_id}.json", timeout=10.0)
        response.raise_for_status()
        story = response.json()
        
        if not story:
            return json.dumps({"error": f"Story {story_id} not found"}, indent=2)
        
        if story.get('type') != 'story':
            return json.dumps({"error": f"Item {story_id} is not a story"}, indent=2)
        
        formatted_story = {
            'id': story.get('id'),
            'title': story.get('title', ''),
            'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
            'score': story.get('score', 0),
            'author': story.get('by', ''),
            'comments': story.get('descendants', 0),
            'time': story.get('time', 0),
            'text': story.get('text', ''),
            'kids': story.get('kids', [])  # Comment IDs
        }
        
        return json.dumps(formatted_story, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

def search_stories_http(query: str, limit: int = 10) -> str:
    """Search for stories on Hacker News (using Algolia API)."""
    try:
        limit = min(max(limit, 1), 20)  # Clamp between 1 and 20
        
        # Use Algolia search API
        search_url = "https://hn.algolia.com/api/v1/search"
        params = {
            "query": query,
            "tags": "story",
            "hitsPerPage": limit
        }
        
        response = httpx.get(search_url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        stories = []
        for hit in data.get('hits', []):
            stories.append({
                'id': hit.get('objectID'),
                'title': hit.get('title', ''),
                'url': hit.get('url', f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                'score': hit.get('points', 0),
                'author': hit.get('author', ''),
                'comments': hit.get('num_comments', 0),
                'time': hit.get('created_at_i', 0),
                'time_iso': hit.get('created_at', '')
            })
        
        return json.dumps(stories, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

@mcp.tool()
def get_top_stories(limit: int = 10) -> str:
    """Get top stories from Hacker News.
    
    Args:
        limit: Number of stories to fetch (default: 10, max: 30)
    
    Returns:
        JSON string with top stories data
    """
    try:
        limit = min(max(limit, 1), 30)  # Clamp between 1 and 30
        
        # Fetch top story IDs
        response = httpx.get(f"{HN_API_BASE}/topstories.json", timeout=10.0)
        response.raise_for_status()
        story_ids = response.json()[:limit]
        
        # Fetch story details
        stories = []
        for story_id in story_ids:
            story_response = httpx.get(f"{HN_API_BASE}/item/{story_id}.json", timeout=5.0)
            story_response.raise_for_status()
            story = story_response.json()
            
            if story and story.get('type') == 'story':
                stories.append({
                    'id': story.get('id'),
                    'title': story.get('title', ''),
                    'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                    'score': story.get('score', 0),
                    'author': story.get('by', ''),
                    'comments': story.get('descendants', 0),
                    'time': story.get('time', 0),
                    'time_iso': story.get('time') and str(story.get('time')) or None
                })
        
        return json.dumps(stories, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

@mcp.tool()
def get_story(story_id: int) -> str:
    """Get details of a specific Hacker News story by ID.
    
    Args:
        story_id: The ID of the story to fetch
    
    Returns:
        JSON string with story details
    """
    try:
        response = httpx.get(f"{HN_API_BASE}/item/{story_id}.json", timeout=10.0)
        response.raise_for_status()
        story = response.json()
        
        if not story:
            return json.dumps({"error": f"Story {story_id} not found"}, indent=2)
        
        if story.get('type') != 'story':
            return json.dumps({"error": f"Item {story_id} is not a story"}, indent=2)
        
        formatted_story = {
            'id': story.get('id'),
            'title': story.get('title', ''),
            'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
            'score': story.get('score', 0),
            'author': story.get('by', ''),
            'comments': story.get('descendants', 0),
            'time': story.get('time', 0),
            'text': story.get('text', ''),
            'kids': story.get('kids', [])  # Comment IDs
        }
        
        return json.dumps(formatted_story, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

@mcp.tool()
def get_new_stories(limit: int = 10) -> str:
    """Get newest stories from Hacker News.
    
    Args:
        limit: Number of stories to fetch (default: 10, max: 30)
    
    Returns:
        JSON string with newest stories data
    """
    try:
        limit = min(max(limit, 1), 30)  # Clamp between 1 and 30
        
        # Fetch new story IDs
        response = httpx.get(f"{HN_API_BASE}/newstories.json", timeout=10.0)
        response.raise_for_status()
        story_ids = response.json()[:limit]
        
        # Fetch story details
        stories = []
        for story_id in story_ids:
            story_response = httpx.get(f"{HN_API_BASE}/item/{story_id}.json", timeout=5.0)
            story_response.raise_for_status()
            story = story_response.json()
            
            if story and story.get('type') == 'story':
                stories.append({
                    'id': story.get('id'),
                    'title': story.get('title', ''),
                    'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                    'score': story.get('score', 0),
                    'author': story.get('by', ''),
                    'time': story.get('time', 0),
                    'time_iso': story.get('time') and str(story.get('time')) or None
                })
        
        return json.dumps(stories, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

@mcp.tool()
def search_stories(query: str, limit: int = 10) -> str:
    """Search for stories on Hacker News (using Algolia API).
    
    Args:
        query: Search query string
        limit: Number of results to return (default: 10, max: 20)
    
    Returns:
        JSON string with search results
    """
    try:
        limit = min(max(limit, 1), 20)  # Clamp between 1 and 20
        
        # Use Algolia search API
        search_url = "https://hn.algolia.com/api/v1/search"
        params = {
            "query": query,
            "tags": "story",
            "hitsPerPage": limit
        }
        
        response = httpx.get(search_url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        stories = []
        for hit in data.get('hits', []):
            stories.append({
                'id': hit.get('objectID'),
                'title': hit.get('title', ''),
                'url': hit.get('url', f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                'score': hit.get('points', 0),
                'author': hit.get('author', ''),
                'comments': hit.get('num_comments', 0),
                'time': hit.get('created_at_i', 0),
                'time_iso': hit.get('created_at', '')
            })
        
        return json.dumps(stories, indent=2)
        
    except httpx.RequestError as e:
        return json.dumps({"error": f"Request failed: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

if __name__ == "__main__":
    # Run in HTTP mode for testing
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import json
    
    # Create FastAPI app
    app = FastAPI()
    
    # Add CORS middleware
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def health_check():
        return {"status": "ok", "server": "Hacker News MCP Server"}
    
    @app.post("/")
    @app.post("/mcp")
    async def mcp_endpoint(request: dict):
        """Handle MCP requests via HTTP POST"""
        try:
            # Log the request for debugging
            print(f"Received request: {request}")
            
            # Convert dict to JSON string for FastMCP
            request_json = json.dumps(request)
            
            # Process the MCP request using the tools directly
            if request.get("method") == "initialize":
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "Hacker News MCP Server",
                            "version": "1.0.0"
                        }
                    }
                })
            elif request.get("method") == "tools/list":
                tools = [
                    {
                        "name": "get_top_stories",
                        "description": "Get top stories from Hacker News",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "limit": {
                                    "type": "integer",
                                    "description": "Number of stories to fetch (1-30)",
                                    "minimum": 1,
                                    "maximum": 30,
                                    "default": 10
                                }
                            }
                        }
                    },
                    {
                        "name": "get_new_stories",
                        "description": "Get newest stories from Hacker News",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "limit": {
                                    "type": "integer",
                                    "description": "Number of stories to fetch (1-30)",
                                    "minimum": 1,
                                    "maximum": 30,
                                    "default": 10
                                }
                            }
                        }
                    },
                    {
                        "name": "get_story",
                        "description": "Get details of a specific Hacker News story by ID",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "story_id": {
                                    "type": "integer",
                                    "description": "The ID of the story to fetch"
                                }
                            },
                            "required": ["story_id"]
                        }
                    },
                    {
                        "name": "search_stories",
                        "description": "Search for stories on Hacker News using Algolia API",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query string"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Number of results to return (1-20)",
                                    "minimum": 1,
                                    "maximum": 20,
                                    "default": 10
                                }
                            },
                            "required": ["query"]
                        }
                    }
                ]
                
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"tools": tools}
                })
            
            elif request.get("method") == "tools/call":
                tool_name = request.get("params", {}).get("name")
                tool_args = request.get("params", {}).get("arguments", {})
                
                # Call the undecorated HTTP functions
                if tool_name == "get_top_stories":
                    result = get_top_stories_http(**tool_args)
                elif tool_name == "get_new_stories":
                    result = get_new_stories_http(**tool_args)
                elif tool_name == "get_story":
                    result = get_story_http(**tool_args)
                elif tool_name == "search_stories":
                    result = search_stories_http(**tool_args)
                else:
                    return JSONResponse(content={
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
                    })
                
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": result}]}
                })
            
            else:
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": f"Method '{request.get('method')}' not found"}
                })
                
        except Exception as e:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }, 
                status_code=500
            )
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
