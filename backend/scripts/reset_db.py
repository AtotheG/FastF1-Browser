"""Skeleton script to reset in-memory database state."""

IN_MEMORY_DB = {}

def reset_db():
    """Clear any in-memory data structures representing the DB."""
    IN_MEMORY_DB.clear()

if __name__ == "__main__":
    reset_db()
    print("In-memory DB cleared")

