CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    surcharge_rate NUMERIC NOT NULL,
    minimum_profit NUMERIC NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trm NUMERIC NOT NULL,
    total_cost_cop NUMERIC NOT NULL,
    total_price_cop NUMERIC NOT NULL,
    total_profit_cop NUMERIC NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quote_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id INTEGER NOT NULL REFERENCES quotes(id),
    product TEXT NOT NULL,
    category TEXT NOT NULL,
    price_usd NUMERIC NOT NULL,
    tax_usd NUMERIC NOT NULL,
    total_usd NUMERIC NOT NULL,
    cost_cop NUMERIC NOT NULL,
    customer_price_cop NUMERIC NOT NULL,
    profit_cop NUMERIC NOT NULL,
    status TEXT NOT NULL
);
