"""Pattern loader for Fabric patterns."""

import os
from pathlib import Path
from typing import Optional, List, Set


class PatternLoader:
    """Loads and manages Fabric patterns from filesystem."""

    def __init__(self):
        """Initialize pattern loader with pattern directories."""
        # Pattern directories (inside container)
        # Order matters: community first, then custom (custom can override)
        self.community_dirs = [
            Path("/root/.config/fabric/patterns"),
            Path(__file__).parent.parent / "config" / "patterns",
        ]
        self.custom_dirs = [
            Path("/root/.config/fabric/custom-patterns"),
            Path(__file__).parent.parent / "custom-patterns",
        ]

        self._pattern_cache = {}
        self._custom_patterns: Set[str] = set()
        self._load_patterns()

    def _load_patterns(self):
        """Load all patterns from pattern directories."""
        self._pattern_cache = {}
        self._custom_patterns = set()

        # Load community patterns first
        for pattern_dir in self.community_dirs:
            if not pattern_dir.exists():
                continue

            for pattern_path in pattern_dir.iterdir():
                if pattern_path.is_dir():
                    system_file = pattern_path / "system.md"
                    if system_file.exists():
                        pattern_name = pattern_path.name
                        try:
                            content = system_file.read_text(encoding="utf-8")
                            self._pattern_cache[pattern_name] = content
                        except Exception as e:
                            print(f"Error loading pattern {pattern_name}: {e}")

        # Load custom patterns (can override community)
        for pattern_dir in self.custom_dirs:
            if not pattern_dir.exists():
                continue

            for pattern_path in pattern_dir.iterdir():
                if pattern_path.is_dir():
                    system_file = pattern_path / "system.md"
                    if system_file.exists():
                        pattern_name = pattern_path.name
                        try:
                            content = system_file.read_text(encoding="utf-8")
                            self._pattern_cache[pattern_name] = content
                            self._custom_patterns.add(pattern_name)
                        except Exception as e:
                            print(f"Error loading custom pattern {pattern_name}: {e}")

        print(f"Loaded {len(self._pattern_cache)} patterns ({len(self._custom_patterns)} custom)")

    def list_patterns(self) -> List[str]:
        """Return list of all available pattern names."""
        return sorted(list(self._pattern_cache.keys()))

    def get_pattern(self, name: str) -> Optional[str]:
        """
        Get pattern content by name.

        Args:
            name: Pattern name

        Returns:
            Pattern system prompt content, or None if not found
        """
        return self._pattern_cache.get(name)

    def reload_patterns(self):
        """Reload all patterns from disk."""
        self._load_patterns()

    def pattern_exists(self, name: str) -> bool:
        """Check if a pattern exists."""
        return name in self._pattern_cache

    def is_custom_pattern(self, name: str) -> bool:
        """Check if a pattern is a custom (user-defined) pattern."""
        return name in self._custom_patterns

    def get_custom_patterns(self) -> List[str]:
        """Return list of custom pattern names."""
        return sorted(list(self._custom_patterns))

    def get_pattern_count(self) -> int:
        """Return total number of loaded patterns."""
        return len(self._pattern_cache)
