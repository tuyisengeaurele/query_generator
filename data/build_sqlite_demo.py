"""Builds a SQLite copy of the demo schema and seed data at data/demo.db.
Used for local development where Docker/Postgres is not available; the API
points DATABASE_URL at this file by default. Mirrors demo_schema.sql and
demo_seed.sql, translated to SQLite syntax (SERIAL -> INTEGER PRIMARY KEY,
NUMERIC -> REAL, TIMESTAMP -> TEXT)."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "demo.db"

SCHEMA = """
CREATE TABLE cooperatives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    founded_year INTEGER NOT NULL
);

CREATE TABLE members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cooperative_id INTEGER NOT NULL REFERENCES cooperatives(id),
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    joined_at TEXT NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price REAL NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL REFERENCES members(id),
    total_amount REAL NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    amount REAL NOT NULL,
    method TEXT NOT NULL,
    paid_at TEXT NOT NULL
);
"""

SEED = """
INSERT INTO cooperatives (name, region, founded_year) VALUES
    ('Kigali Growers', 'Kigali', 2015),
    ('Musanze Highlands', 'Musanze', 2012),
    ('Huye Valley Farmers', 'Huye', 2018);

INSERT INTO members (cooperative_id, full_name, role, joined_at) VALUES
    (1, 'Alice Uwase', 'chair', '2015-03-01'),
    (1, 'Beatrice Mukamana', 'member', '2016-07-14'),
    (1, 'Claude Habimana', 'treasurer', '2017-01-20'),
    (2, 'Diane Ingabire', 'chair', '2012-05-10'),
    (2, 'Eric Nshimiyimana', 'member', '2019-09-02'),
    (3, 'Grace Umutoni', 'chair', '2018-02-11'),
    (3, 'Henri Bizimana', 'member', '2020-11-30');

INSERT INTO products (name, category, unit_price) VALUES
    ('Arabica Coffee 1kg', 'coffee', 12.50),
    ('Robusta Coffee 1kg', 'coffee', 9.00),
    ('Dried Beans 1kg', 'legumes', 3.20),
    ('Honey 500g', 'honey', 6.75),
    ('Avocado Crate', 'produce', 15.00);

INSERT INTO orders (member_id, total_amount, status, created_at) VALUES
    (1, 62.50, 'fulfilled', '2026-05-01 10:00:00'),
    (2, 27.00, 'fulfilled', '2026-05-03 14:30:00'),
    (3, 15.00, 'pending', '2026-06-10 09:15:00'),
    (4, 90.00, 'fulfilled', '2026-06-15 11:45:00'),
    (5, 6.75, 'fulfilled', '2026-06-20 16:00:00'),
    (6, 45.00, 'pending', '2026-07-01 08:30:00'),
    (7, 12.50, 'fulfilled', '2026-07-03 13:20:00');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 5, 12.50),
    (2, 2, 3, 9.00),
    (3, 5, 1, 15.00),
    (4, 1, 4, 12.50),
    (4, 3, 10, 3.20),
    (5, 4, 1, 6.75),
    (6, 1, 2, 12.50),
    (6, 3, 6, 3.20),
    (7, 1, 1, 12.50);

INSERT INTO payments (order_id, amount, method, paid_at) VALUES
    (1, 62.50, 'mobile_money', '2026-05-01 10:05:00'),
    (2, 27.00, 'cash', '2026-05-03 14:35:00'),
    (4, 60.00, 'bank_transfer', '2026-06-15 12:00:00'),
    (5, 6.75, 'mobile_money', '2026-06-20 16:05:00'),
    (7, 12.50, 'cash', '2026-07-03 13:25:00');
"""


def build() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.executescript(SEED)
    conn.commit()
    conn.close()
    print(f"wrote {DB_PATH}")


if __name__ == "__main__":
    build()
