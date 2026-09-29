from __future__ import annotations

from sqlalchemy import text

# Current directory se database import karne ke liye
from restaurant_booking import engine, init_db


def run_sql(query: str):
    """Raw SQL query chalane ke liye function"""
    init_db()  # Database aur tables initialize karega
    with engine.begin() as conn:
        result = conn.execute(text(query))
        return result.fetchall() if result.returns_rows else result.rowcount


if __name__ == "__main__":
    # Test query
    query = "SELECT * FROM booking"
    rows = run_sql(query)
    print("Database Result:", rows)
