"""Fabric Pattern Library Service - serves patterns for local LLM execution."""

import os
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from pattern_loader import PatternLoader

# Setup templates
templates = Jinja2Templates(directory="templates")


def categorize_pattern(name: str, is_custom: bool = False) -> tuple[str, str]:
    """Categorize a pattern and return (category, badge_type).

    Categories:
    - custom: User-defined patterns (Gavin's personal patterns)
    - extract: Patterns that extract information
    - analyze: Patterns that analyze content
    - create: Patterns that create new content
    - summarize: Patterns that summarize content
    - improve: Patterns that improve/enhance content
    - write: Patterns that write content
    - utility: Everything else
    """
    # Custom patterns get their own category
    if is_custom:
        return 'custom', 'custom'

    name_lower = name.lower()
    if 'extract' in name_lower:
        return 'extract', 'ai'
    elif 'analyze' in name_lower or 'rate' in name_lower:
        return 'analyze', 'retro'
    elif 'create' in name_lower:
        return 'create', 'circuit'
    elif 'summarize' in name_lower or 'summary' in name_lower:
        return 'summarize', 'ai'
    elif 'improve' in name_lower or 'enhance' in name_lower:
        return 'improve', 'retro'
    elif 'write' in name_lower:
        return 'write', 'circuit'
    else:
        return 'utility', 'ai'


def get_pattern_preview(content: str, max_length: int = 100) -> str:
    """Get a preview of the pattern content."""
    # Extract first meaningful line after IDENTITY or PURPOSE
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'IDENTITY' in line or 'PURPOSE' in line:
            # Get the next non-empty line
            for next_line in lines[i+1:]:
                stripped = next_line.strip()
                if stripped and not stripped.startswith('#'):
                    preview = stripped[:max_length]
                    if len(stripped) > max_length:
                        preview += '...'
                    return preview
    # Fallback: first non-header line
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            preview = stripped[:max_length]
            if len(stripped) > max_length:
                preview += '...'
            return preview
    return "No preview available"

app = FastAPI(
    title="Fabric Pattern Library",
    description="Pattern storage and sync service for Fabric AI patterns",
    version="2.0.0"
)

pattern_loader = PatternLoader()


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key from request header."""
    expected_key = os.getenv("FABRIC_API_KEY", "")
    if expected_key and x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "fabric-pattern-library",
        "version": "2.0.0",
        "patterns_loaded": len(pattern_loader.list_patterns())
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Web UI - Pattern browser."""
    pattern_names = pattern_loader.list_patterns()
    patterns = []

    for name in sorted(pattern_names):
        content = pattern_loader.get_pattern(name)
        is_custom = pattern_loader.is_custom_pattern(name)
        category, badge_type = categorize_pattern(name, is_custom=is_custom)
        preview = get_pattern_preview(content) if content else "No preview available"
        patterns.append({
            "name": name,
            "category": category,
            "badge_type": badge_type,
            "preview": preview,
            "is_custom": is_custom
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "patterns": patterns,
        "pattern_count": len(patterns),
        "custom_count": len(pattern_loader.get_custom_patterns())
    })


@app.get("/view/{pattern_name}", response_class=HTMLResponse)
async def view_pattern(request: Request, pattern_name: str):
    """Web UI - Pattern detail view."""
    content = pattern_loader.get_pattern(pattern_name)
    if not content:
        raise HTTPException(status_code=404, detail=f"Pattern '{pattern_name}' not found")

    return templates.TemplateResponse("pattern.html", {
        "request": request,
        "pattern_name": pattern_name,
        "content": content,
        "pattern_count": len(pattern_loader.list_patterns())
    })


@app.get("/patterns")
async def list_patterns(x_api_key: Optional[str] = Header(None)):
    """List all available pattern names."""
    verify_api_key(x_api_key)
    patterns = pattern_loader.list_patterns()
    return {
        "count": len(patterns),
        "patterns": patterns
    }


@app.get("/patterns/{pattern_name}")
async def get_pattern(pattern_name: str, x_api_key: Optional[str] = Header(None)):
    """Get pattern content by name."""
    verify_api_key(x_api_key)
    pattern = pattern_loader.get_pattern(pattern_name)
    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern '{pattern_name}' not found")
    return {
        "name": pattern_name,
        "content": pattern
    }


@app.post("/sync")
async def sync_patterns(x_api_key: Optional[str] = Header(None)):
    """Sync patterns from Fabric GitHub repository."""
    verify_api_key(x_api_key)

    patterns_dir = Path("/root/.config/fabric/patterns")
    repo_url = "https://github.com/danielmiessler/fabric.git"

    try:
        if patterns_dir.exists():
            # Update existing patterns
            result = subprocess.run(
                ["git", "-C", str(patterns_dir.parent.parent), "pull", "--depth=1"],
                capture_output=True,
                text=True,
                timeout=120
            )
        else:
            # Clone fresh
            patterns_dir.parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(
                ["git", "clone", "--depth=1", "--filter=blob:none", "--sparse", repo_url, str(patterns_dir.parent.parent)],
                capture_output=True,
                text=True,
                timeout=120
            )
            # Sparse checkout just patterns
            subprocess.run(
                ["git", "-C", str(patterns_dir.parent.parent), "sparse-checkout", "set", "patterns"],
                capture_output=True,
                text=True
            )

        # Reload patterns
        pattern_loader._load_patterns()

        return {
            "status": "success",
            "message": "Patterns synced from GitHub",
            "patterns_loaded": len(pattern_loader.list_patterns()),
            "output": result.stdout or result.stderr
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Sync timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.post("/youtube/transcript")
async def get_youtube_transcript(
    request: Request,
    x_api_key: Optional[str] = Header(None)
):
    """Extract transcript from YouTube video (utility endpoint)."""
    verify_api_key(x_api_key)

    try:
        body = await request.json()
        url = body.get("url", "")

        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        from youtube import extract_transcript
        transcript = await extract_transcript(url)

        return {"transcript": transcript, "url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
