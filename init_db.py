"""Database initialization script."""

from pathlib import Path
from config import setup_logging, get_logger

setup_logging("INFO", log_to_file=False)
log = get_logger(__name__)


def main():
    log.info("Initializing database...")
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # SQLite
    from database import create_db_engine, init_db
    
    db_path = data_dir / "patrolling.db"
    engine = create_db_engine(f"sqlite:///{db_path}")
    init_db(engine)
    log.info(f"SQLite: {db_path}")
    
    # FAISS
    from database import get_vectordb
    
    vectordb = get_vectordb(str(data_dir / "vectordb"))
    for name in vectordb.COLLECTIONS:
        vectordb.get_collection(name)
        log.info(f"FAISS collection: {name} ({vectordb.count(name)} docs)")
    
    log.info("Done!")


if __name__ == "__main__":
    main()
