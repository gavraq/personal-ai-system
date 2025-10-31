# Personal Knowledge Service - Obsidian Integration

Integration layer for accessing and managing Gavin's personal knowledge base stored in Obsidian vault.

## Overview

Provides AI agents with read/write access to the Obsidian vault containing:
- Daily notes and journaling
- GTD task management
- Meeting notes and action items
- Personal knowledge base
- Project documentation

## Obsidian Vault Location

**Mac**: `/Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault/`

**Pi (SMB Mount)**: `/mnt/gavin-obsidian/GavinsiCloudVault/`

## Integration Type

**MCP Server**: Uses Obsidian MCP server for vault access

## Key Capabilities

- Create daily notes with standardized templates
- Search vault contents (notes, tags, filenames)
- Read and edit existing notes
- Manage tags and frontmatter
- GTD task management via Obsidian Tasks plugin

## Usage

See [knowledge-manager-agent.md](/.claude/agents/knowledge-manager-agent.md) for agent usage examples.

## Configuration

The Obsidian MCP server is configured in Claude Code's MCP settings and provides direct vault access without requiring additional wrapper code.
