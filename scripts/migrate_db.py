"""Database migration script for PostgreSQL setup."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

from database.models import Base
from config import get_settings


def create_tables(engine):
    """Create all tables."""
    Base.metadata.create_all(engine)
    print("✅ Tables created successfully")


def migrate(database_url: str = None):
    """Run database migration."""
    settings = get_settings()
    url = database_url or settings.database_url
    
    print(f"Connecting to: {url.split('@')[-1] if '@' in url else url}")
    
    engine = create_engine(url)
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    create_tables(engine)
    return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else None
    success = migrate(url)
    sys.exit(0 if success else 1)
