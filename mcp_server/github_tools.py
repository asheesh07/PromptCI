import asyncio
from asyncio import streams
import os
import json
import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS ={
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

app = Server("promptci-github-tools")

@app.list_tools()
async def list_tools():
    return [
        types.Tool(
            name = "get_pr_diff",
            description = "Fetch the raw unified diff for a GitHub pull request",
            inputSchema = {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in owner/repo format e.g. asheesh07/demo-ai-app"
                    },
                    "pr_number": {
                        "type": "integer",
                        "description": "Pull request number"
                    }
                },
                "required": ["repo", "pr_number"]
            }
        ),
        types.Tool(
            name="get_file_at_commit",
            description="Fetch the contents of a file at a specific commit SHA",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in owner/repo format"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file e.g. prompts/customer_support.txt"
                    },
                    "commit_sha": {
                        "type": "string",
                        "description": "The commit SHA to fetch the file at"
                    }
                },
                "required": ["repo", "file_path", "commit_sha"]
            }
        ),
        types.Tool(
            name="post_pr_comment",
            description="Post a comment on a GitHub pull request",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in owner/repo format"
                    },
                    "pr_number": {
                        "type": "integer",
                        "description": "Pull request number"
                    },
                    "body": {
                        "type": "string",
                        "description": "Markdown content of the comment"
                    }
                },
                "required": ["repo", "pr_number", "body"]
            }
        ),
        types.Tool(
            name="get_pr_metadata",
            description="Fetch base and head commit SHAs for a pull request",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in owner/repo format"
                    },
                    "pr_number": {
                        "type": "integer",
                        "description": "Pull request number"
                    }
                },
                "required": ["repo", "pr_number"]
            }
        ),
        types.Tool(
            name="list_prompt_files",
            description="List all prompt files in a GitHub repository's prompts folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in owner/repo format"
                    }
                },
                "required": ["repo"]
            }
        ),
        
        
    ]
    
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    async with httpx.AsyncClient() as client:
        if name == "get_pr_diff":
            repo = arguments["repo"]
            pr_number = arguments["pr_number"]
            url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
            response = await client.get(
                url,
                headers={**HEADERS, "Accept": "application/vnd.github.diff"},
            )
            response.raise_for_status()
            return [types.TextContent(type="text", text=response.text)]

        elif name == "get_file_at_commit":
            repo = arguments["repo"]
            file_path = arguments["file_path"]
            commit_sha = arguments["commit_sha"]
            url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
            response = await client.get(
                url,
                headers=HEADERS,
                params={"ref": commit_sha}
            )
            response.raise_for_status()
            data = response.json()
            import base64
            content = base64.b64decode(data["content"]).decode("utf-8")
            return [types.TextContent(type="text", text=content)]

        elif name == "post_pr_comment":
            repo = arguments["repo"]
            pr_number = arguments["pr_number"]
            body = arguments["body"]
            url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
            response = await client.post(
                url,
                headers=HEADERS,
                json={"body": body}
            )
            response.raise_for_status()
            data = response.json()
            return [types.TextContent(
                type="text",
                text=json.dumps({"comment_id": data["id"], "url": data["html_url"]})
            )]

        elif name == "get_pr_metadata":
            repo = arguments["repo"]
            pr_number = arguments["pr_number"]
            url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "base_commit_sha": data["base"]["sha"],
                    "head_commit_sha": data["head"]["sha"],
                    "base_ref": data["base"]["ref"],
                    "head_ref": data["head"]["ref"],
                    "title": data["title"],
                    "changed_files": data["changed_files"]
                })
            )]
            
        elif name == "list_prompt_files":
            repo = arguments["repo"]
            url = f"https://api.github.com/repos/{repo}/contents/prompts"
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            files = response.json()
            prompt_files = [
                f["path"] for f in files
                if f["type"] == "file" and f["name"].endswith(".txt")
            ]
            return [types.TextContent(
                type="text",
                text=json.dumps({"prompt_files": prompt_files})
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")
        
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())