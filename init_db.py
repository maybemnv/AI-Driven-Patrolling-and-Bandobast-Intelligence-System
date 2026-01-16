"""Database initialization script."""

from pathlib import Path
from config import setup_logging, get_logger

setup_logging("INFO", log_to_file=False)
log = get_logger(__name__)


def main():
    log.info("Initializing database...")
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize SQLite database
    from database import create_db_engine, init_db
    
    db_path = data_dir / "patrolling.db"
    engine = create_db_engine(f"sqlite:///{db_path}")
    init_db(engine)
    log.info(f"SQLite database created: {db_path}")
    
    # Initialize vector database
    from database import get_vectordb
    
    vectordb = get_vectordb(str(data_dir / "vectordb"))
    
    # Create collections
    for collection in ["patrol_logs", "alert_history", "location_context"]:
        vectordb.get_collection(collection)
        log.info(f"ChromaDB collection ready: {collection}")
    
    log.info("Database initialization complete!")


if __name__ == "__main__":
    main()
