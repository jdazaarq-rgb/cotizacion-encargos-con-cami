from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .excel_import import load_categories


SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    surcharge_rate NUMERIC NOT NULL,
    minimum_profit NUMERIC NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
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
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(
    db_path: str | Path,
    excel_path: str | Path | None = None,
) -> None:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as connection:
        connection.executescript(SCHEMA)
        if not connection.execute(
            "SELECT 1 FROM app_settings WHERE key = 'default_surcharge_percent'"
        ).fetchone():
            connection.execute(
                "INSERT INTO app_settings (key, value) VALUES ('default_surcharge_percent', '10')"
            )
        if excel_path and Path(excel_path).exists():
            categories = load_categories(excel_path)
            connection.execute("DELETE FROM categories")
            connection.executemany(
                "INSERT INTO categories (name, surcharge_rate, minimum_profit) VALUES (?, ?, ?)",
                [
                    (item["name"], item["surcharge_rate"], item["minimum_profit"])
                    for item in categories
                ],
            )


def get_default_surcharge_percent(db_path: str | Path) -> int:
    with connect(db_path) as connection:
        row = connection.execute(
            "SELECT value FROM app_settings WHERE key = 'default_surcharge_percent'"
        ).fetchone()
    if row is None:
        return 10
    return int(row["value"])


def set_default_surcharge_percent(db_path: str | Path, percent: int) -> None:
    if percent < 10 or percent > 100 or percent % 10 != 0:
        raise ValueError("El porcentaje debe estar entre 10% y 100% en múltiplos de 10.")
    with connect(db_path) as connection:
        connection.execute(
            "INSERT INTO app_settings (key, value) VALUES ('default_surcharge_percent', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (str(percent),),
        )


def get_categories(db_path: str | Path) -> list[dict[str, Any]]:
    with connect(db_path) as connection:
        rows = connection.execute(
            "SELECT name, surcharge_rate, minimum_profit FROM categories "
            "WHERE active = 1 ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]


def save_quote(db_path: str | Path, trm: Any, items: list[dict[str, Any]]) -> int:
    total_cost = sum((item["cost_cop"] for item in items), 0)
    total_price = sum((item["customer_price_cop"] for item in items), 0)
    total_profit = sum((item["profit_cop"] for item in items), 0)

    with connect(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO quotes (trm, total_cost_cop, total_price_cop, total_profit_cop) "
            "VALUES (?, ?, ?, ?)",
            (str(trm), str(total_cost), str(total_price), str(total_profit)),
        )
        quote_id = cursor.lastrowid
        connection.executemany(
            "INSERT INTO quote_items (quote_id, product, category, price_usd, tax_usd, "
            "total_usd, cost_cop, customer_price_cop, profit_cop, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    quote_id,
                    item["product"],
                    item["category"],
                    str(item["price_usd"]),
                    str(item["tax_usd"]),
                    str(item["total_usd"]),
                    str(item["cost_cop"]),
                    str(item["customer_price_cop"]),
                    str(item["profit_cop"]),
                    item["status"],
                )
                for item in items
            ],
        )
    return int(quote_id)
