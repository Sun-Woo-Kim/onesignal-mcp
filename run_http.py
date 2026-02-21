from onesignal_refactored.server import mcp

import inspect
import logging
import os
import uvicorn

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger("onesignal-mcp")


def _run_fastmcp() -> None:
    sig = inspect.signature(mcp.run)
    params = sig.parameters
    has_var_kwargs = any(param.kind == inspect.Parameter.VAR_KEYWORD for param in params.values())

    if "transport" in sig.parameters:
        kwargs = {"transport": TRANSPORT}
        if "host" in sig.parameters and "port" in sig.parameters:
            kwargs["host"] = MCP_HOST
            kwargs["port"] = PORT
        elif has_var_kwargs:
            kwargs["host"] = MCP_HOST
            kwargs["port"] = PORT
        elif "host" in sig.parameters or "port" in sig.parameters:
            logger.info("FastMCP.run() has partial networking args only; using ASGI fallback for safe external binding.")
            raise TypeError("No full host/port support in this FastMCP.run signature")

        if "host" not in kwargs or "port" not in kwargs:
            raise TypeError("host/port not available in FastMCP.run")
        mcp.run(**kwargs)
        return

    if sig.parameters:
        mcp.run()
        return

    raise RuntimeError("Unsupported FastMCP.run signature")


def _resolve_asgi_app():
    candidates = (
        getattr(mcp, "streamable_http_app", None),
        getattr(mcp, "http_app", None),
        getattr(mcp, "asgi_app", None),
        getattr(mcp, "app", None),
        getattr(mcp, "get_asgi_app", None),
    )

    for candidate in candidates:
        if candidate is None:
            continue
        if callable(candidate):
            try:
                value = candidate()
            except TypeError:
                value = candidate
        else:
            value = candidate

        if value is not None:
            return value

    return mcp


def main() -> None:
    try:
        _run_fastmcp()
        return
    except TypeError:
        logger.info("FastMCP.run() does not accept transport/host/port in current runtime.")
    except Exception:
        logger.exception("Failed to run via FastMCP adapter.")
        return

    app = _resolve_asgi_app()
    if app is None:
        raise RuntimeError("No ASGI app available from FastMCP instance")

    uvicorn.run(
        app,
        host=MCP_HOST,
        port=PORT,
        log_level=LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
