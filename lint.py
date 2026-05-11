#!/usr/bin/env python3
"""
Layered architecture linter for the word puzzle game.

Enforces:
1. All source files live inside layer directories
2. Imports respect the forward dependency direction
3. No file exceeds 300 lines

Layer dependency direction (forward-only):
    types -> config -> repo -> service -> runtime -> ui
    providers -> (all layers, cross-cutting)
    utils -> (leaf layer, no internal imports)

Usage:
    python lint.py
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

# Layer order defines dependency direction
LAYERS = ["types", "config", "providers", "repo", "service", "utils", "runtime", "ui"]

# Layer directories that should exist
LAYER_DIRS = set(LAYERS)

# Allowed imports per layer (internal only, forward direction)
ALLOWED_INTERNAL_IMPORTS = {
    "types": [],
    "config": [],
    "providers": ["types"],
    "repo": ["types", "config"],
    "service": ["types", "config", "providers", "repo"],
    "utils": [],
    "runtime": ["types", "config", "providers", "repo", "service"],
    "ui": ["types", "config", "providers", "repo", "service", "utils"],
}


def get_source_files(src_dir: Path) -> List[Path]:
    """Get all Python source files in src directory."""
    return list(src_dir.rglob("*.py"))


def get_file_layer(filepath: Path, src_dir: Path) -> str | None:
    """Determine which layer a file belongs to."""
    try:
        rel_path = filepath.relative_to(src_dir)
        parts = rel_path.parts
        if parts and parts[0] in LAYER_DIRS:
            return parts[0]
        return None
    except ValueError:
        return None


def get_imports(filepath: Path) -> List[Tuple[str, str]]:
    """
    Parse a Python file and extract import statements.
    Returns list of (module_name, import_type).
    import_type is 'from' or 'import'.
    """
    imports = []
    try:
        with open(filepath) as f:
            tree = ast.parse(f.read(), filename=str(filepath))

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.append((module, "from"))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((alias.name, "import"))
    except SyntaxError:
        pass
    return imports


def get_internal_imports(imports: List[Tuple[str, str]], layer: str) -> List[str]:
    """
    Extract internal src.* imports from a list of imports.
    Returns list of layer names being imported.
    """
    internal = []
    for module, _ in imports:
        if module.startswith("src."):
            parts = module.split(".")
            if len(parts) > 1:
                layer_name = parts[1]
                if layer_name in LAYER_DIRS:
                    internal.append(layer_name)
    return internal


def check_file_line_count(filepath: Path) -> List[str]:
    """Check if file exceeds 300 lines."""
    errors = []
    try:
        with open(filepath) as f:
            lines = f.readlines()
        if len(lines) > 300:
            errors.append(f"{filepath}: exceeds 300 lines ({len(lines)} lines)")
    except Exception:
        pass
    return errors


def check_imports(filepath: Path, layer: str) -> List[str]:
    """Check that imports respect layer dependency rules."""
    errors = []
    imports = get_imports(filepath)
    internal_imports = get_internal_imports(imports, layer)
    allowed = ALLOWED_INTERNAL_IMPORTS.get(layer, [])

    for imp in internal_imports:
        if imp not in allowed:
            errors.append(
                f"{filepath}: imports '{imp}' which violates layer dependency rules "
                f"(layer '{layer}' can only import: {', '.join(allowed) or 'none'})"
            )

    return errors


def check_file_location(filepath: Path, src_dir: Path) -> List[str]:
    """Check that file lives inside a layer directory."""
    errors = []
    try:
        rel_path = filepath.relative_to(src_dir)
        parts = rel_path.parts

        # Skip if file is at src root level (like main.py)
        if len(parts) == 1:
            return []

        layer = parts[0]
        if layer not in LAYER_DIRS:
            errors.append(
                f"{filepath}: file outside layer directory (should be in src/)"
            )
    except ValueError:
        errors.append(f"{filepath}: not under src directory")
    return errors


def lint(src_dir: Path) -> Tuple[int, List[str]]:
    """
    Run all linter checks.
    Returns (exit_code, list_of_errors).
    """
    errors = []
    source_files = get_source_files(src_dir)

    for filepath in source_files:
        layer = get_file_layer(filepath, src_dir)

        # Check file location
        errors.extend(check_file_location(filepath, src_dir))

        # Only check imports for files inside layers
        if layer:
            errors.extend(check_imports(filepath, layer))

        # Always check line count
        errors.extend(check_file_line_count(filepath))

    # Remove duplicates while preserving order
    unique_errors = list(dict.fromkeys(errors))
    return len(unique_errors), unique_errors


def main() -> int:
    """Main entrypoint."""
    repo_root = Path(__file__).parent
    src_dir = repo_root / "src"

    if not src_dir.exists():
        print("Error: src directory not found")
        return 1

    exit_code, errors = lint(src_dir)

    if errors:
        print("Linting failed:\n")
        for error in errors:
            print(f"  {error}")
        print(f"\n{len(errors)} error(s)")
        return 1

    print("All checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
