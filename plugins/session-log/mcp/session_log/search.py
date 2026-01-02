"""ChromaDB semantic search for session summaries."""

from pathlib import Path

import chromadb
from chromadb.config import Settings


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

    settings = Settings(
        persist_directory=str(db_path),
        anonymized_telemetry=False,
    )
    client = chromadb.PersistentClient(path=str(db_path), settings=settings)
    return client.get_or_create_collection(name="sessions")


def embed_session(
    session_id: str,
    content: str,
    metadata: dict | None = None,
    db_path: Path | None = None,
) -> bool:
    """Embed and store a session summary.

    Args:
        session_id: Unique session identifier (used as ChromaDB ID).
        content: Session summary text to embed.
        metadata: Optional metadata dict (project, branch, date, etc.).
        db_path: Optional override for ChromaDB storage path (for testing).

    Returns:
        True if successful, False otherwise.
    """
    try:
        collection = get_collection(db_path)
        collection.upsert(
            ids=[session_id],
            documents=[content],
            metadatas=[metadata] if metadata else None,
        )
        return True
    except Exception:
        return False
