"""
Shared mcp instance used by all tool modules.
Importing this package registers every tool automatically.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("yt-media-kit")

# Import submodules so their @mcp.tool() decorators run and register tools.
from . import discovery, download, pipeline, transcript  # noqa: E402, F401
