import os
import logging
from typing import TypedDict
import httpx
from mcp.client.streamable_http import StreamableHTTPClient

logger = logging.getLogger(__name__)


class SearchResult(TypedDict):
    title: str
    url: str
    snippet: str


async def search_web(query: str, max_results: int = 10) -> list[SearchResult]:
    """
    Search the web using Apify's MCP-hosted rag-web-browser actor.

    Args:
        query: The search query
        max_results: Maximum number of results to return

    Returns:
        List of search results with title, url, and snippet

    Raises:
        RuntimeError: If the MCP call fails or token is missing
    """
    api_token = os.getenv("APIFY_API_TOKEN")
    mcp_url = os.getenv("MCP_SERVER_URL", "https://mcp.apify.com")

    if not api_token:
        raise RuntimeError("APIFY_API_TOKEN environment variable not set")

    try:
        async with httpx.AsyncClient() as http_client:
            client = StreamableHTTPClient(
                url=mcp_url,
                headers={"Authorization": f"Bearer {api_token}"}
            )

            async with client:
                await client.initialize()

                tool_result = await client.call_tool(
                    "call-actor",
                    {
                        "actor": "apify/rag-web-browser",
                        "input": {
                            "query": query,
                            "maxResults": max_results,
                        }
                    }
                )

                results = _parse_search_results(tool_result)
                return results

    except httpx.TimeoutException as e:
        raise RuntimeError(f"MCP request timed out: {e}")
    except httpx.HTTPError as e:
        raise RuntimeError(f"MCP HTTP error: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to execute search: {str(e)}")


def _parse_search_results(tool_result: dict) -> list[SearchResult]:
    """
    Parse the Apify MCP tool result into search results.

    Expects tool_result.content[0].text to contain structured result data.
    """
    try:
        if not tool_result.get("content"):
            return []

        content = tool_result["content"][0]
        if content.get("type") != "text":
            return []

        text = content.get("text", "")
        if not text:
            return []

        import json
        data = json.loads(text)

        results: list[SearchResult] = []
        for item in data.get("results", []):
            results.append({
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "snippet": item.get("snippet", ""),
            })

        return results

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.warning(f"Failed to parse search results: {e}")
        return []
