-- Cooperative sales domain used by the demo app. Written for Postgres;
-- data/build_sqlite_demo.py creates the same shape in SQLite for local
-- development where Postgres is not available.

CREATE TABLE cooperatives (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    founded_year INTEGER NOT NULL
);

CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    cooperative_id INTEGER NOT NULL REFERENCES cooperatives(id),
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    joined_at DATE NOT NULL
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id),
    total_amount NUMERIC(10, 2) NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    amount NUMERIC(10, 2) NOT NULL,
    method TEXT NOT NULL,
    paid_at TIMESTAMP NOT NULL
);
