import os
from pathlib import Path

# File where flattened code will be written
OUTPUT_FILE = "flattened_code_review.txt"

# Directories to ignore
IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
    ".idea",
    ".vscode",
    "dist",
    "build"
}

# Code file extensions to include
VALID_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".c",
    ".go",
    ".rs",
    ".html",
    ".css",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".txt"
}


def flatten_codebase(root_dir="."):
    root = Path(root_dir).resolve()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip ignored directories
            if any(part in IGNORE_DIRS for part in file_path.parts):
                continue

            # Skip non-code files
            if file_path.suffix.lower() not in VALID_EXTENSIONS:
                continue

            header = (
                "\n"
                + "=" * 90
                + f"\nFILE: {file_path}\n"
                + "=" * 90
                + "\n\n"
            )

            out.write(header)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    out.write(f.read())
                    out.write("\n")
            except Exception as e:
                out.write(f"[Could not read file: {e}]\n")

    print(f"\nFlattened code written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    flatten_codebase()