"""OneSignal MCP server package entry point."""
from .server import mcp


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
