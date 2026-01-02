"""ChromaDB semantic search for session summaries."""

from pathlib import Path

import chromadb


def get_chroma_path() -> Path:
    """Get the path to the ChromaDB storage directory."""
    db_dir = Path.home() / ".claude" / "session-log" / "chroma"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir


def get_collection(db_path: Path | None = None) -> chromadb.Collection:
    """Get or create the sessions collection.

    Args:
        db_path: Optional override for ChromaDB storage path (for testing).

    Returns:
        ChromaDB collection for session embeddings.
    """
    if db_path is None:
        db_path = get_chroma_path()

    client = chromadb.PersistentClient(path=str(db_path))
    return client.get_or_create_collection(name="sessions")
