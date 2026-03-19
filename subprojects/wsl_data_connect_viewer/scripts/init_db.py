from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3] / "data_connect_viewer"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import models  # noqa: F401
from app.core.database import Base, engine, session_scope
from app.services.mapping_service import ensure_default_mappings


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with session_scope() as session:
        ensure_default_mappings(session)
    print("Database initialized.")


if __name__ == "__main__":
    main()
