import os
from src.reports.database import ViolationRepository
from src.config import settings

def main() -> None:
    """Initialize (or reset) the SQLite violations database.
    Removes any existing database file and creates a fresh schema.
    """
    db_path = settings.database_path
    # Ensure the outputs directory exists (settings.ensure_directories already called elsewhere)
    if db_path.exists():
        db_path.unlink()
        print(f"Removed existing DB at {db_path}")
    # Instantiate repository which will create the schema if missing
    _ = ViolationRepository(db_path)
    print(f"Initialized new DB at {db_path}")

if __name__ == "__main__":
    main()
