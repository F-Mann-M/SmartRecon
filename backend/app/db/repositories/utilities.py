
import hashlib


def compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash for a file at file_path. Returns hex digest."""
    print(f"Computing hash for file: {file_path}")
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except Exception as e:
        # Re-raise to let callers decide; callers may choose to handle remote files differently
        raise
    return h.hexdigest()
