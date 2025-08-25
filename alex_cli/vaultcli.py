#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from datetime import datetime
import yaml
from cyclopts import App

app = App(name="vaultcli")

VAULT_ROOT = Path("/Users/alexleviyev/Documents/knowledge_graph_copy/vault")          # change as needed
CONTENT_DIR = VAULT_ROOT / "content"
NOTES_DIR = VAULT_ROOT / "notes"
DB_PATH = VAULT_ROOT / "vault.db"

# ---------------------------
# DB setup and helpers
# ---------------------------
def init_db():
    """Initialize the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            md_file TEXT UNIQUE,
            content_file TEXT UNIQUE,
            title TEXT,
            author TEXT,
            tags TEXT,
            year INTEGER,
            mtime INTEGER
        )
    """)
    conn.commit()
    return conn

def create_markdown_for_content(content_file: Path) -> Path:
    """Create a markdown note file for a given content file if it doesn't exist."""
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    md_filename = content_file.stem + ".md"
    md_file = NOTES_DIR / md_filename

    if md_file.exists():
        return md_file  # skip if already exists

    frontmatter = {
        "title": content_file.stem.replace("_", " ").title(),
        "author": None,
        "tags": [],
        "year": None,
        "content_file": str(content_file.relative_to(VAULT_ROOT)),
        "created": datetime.now().isoformat()
    }

    with md_file.open("w", encoding="utf-8") as f:
        f.write("---\n")
        yaml.dump(frontmatter, f)
        f.write("---\n\n")
        f.write(f"# {frontmatter['title']}\n\n")  # template content

    return md_file

def index_content():
    """Scan content folder, create missing markdowns, and update DB."""
    conn = init_db()
    cur = conn.cursor()

    for content_file in CONTENT_DIR.iterdir():
        if not content_file.is_file():
            continue

        # Skip if already in DB
        cur.execute("SELECT id FROM notes WHERE content_file=?", (str(content_file.relative_to(VAULT_ROOT)),))
        if cur.fetchone():
            continue

        md_file = create_markdown_for_content(content_file)
        mtime = int(content_file.stat().st_mtime)

        # Insert into DB
        cur.execute("""
            INSERT INTO notes(md_file, content_file, mtime)
            VALUES (?, ?, ?)
            ON CONFLICT(content_file) DO NOTHING
        """, (str(md_file.relative_to(VAULT_ROOT)), str(content_file.relative_to(VAULT_ROOT)), mtime))

    conn.commit()
    conn.close()
    print("✅ Content indexed and markdowns created successfully.")

# ---------------------------
# Validation / testing
# ---------------------------
def validate_links():
    """Check that all content files and markdown files exist."""
    conn = init_db()
    cur = conn.cursor()
    cur.execute("SELECT md_file, content_file FROM notes")
    errors = []

    for md_rel, content_rel in cur.fetchall():
        md_path = VAULT_ROOT / md_rel
        content_path = VAULT_ROOT / content_rel

        if not md_path.exists():
            errors.append(f"Missing markdown file: {md_path}")
        if not content_path.exists():
            errors.append(f"Missing content file: {content_path}")

    conn.close()
    if errors:
        print("⚠️ Validation failed:")
        for e in errors:
            print("  -", e)
    else:
        print("✅ All links valid!")

# ---------------------------
# CLI commands
# ---------------------------
@app.command
def index():
    """Index content folder and create missing markdown files."""
    index_content()

@app.command
def validate():
    """Validate that all links between markdowns and content files exist."""
    validate_links()

# ---------------------------
if __name__ == "__main__":
    app()

