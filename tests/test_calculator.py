import sqlite3
from decimal import Decimal

import pytest
from openpyxl import Workbook

from src.personal_shopper.calculator import (
    calculate_item,
    round_up_to_10000,
    surcharge_rate_from_percent,
)
from src.personal_shopper.database import (
    get_categories,
    get_default_surcharge_percent,
    initialize_database,
    set_default_surcharge_percent,
)


def test_round_up_to_next_10000():
    assert round_up_to_10000(Decimal("153200")) == Decimal("160000")
    assert round_up_to_10000(Decimal("160000")) == Decimal("160000")


def test_calculate_item_uses_fixed_seven_percent_tax_and_category_rules():
    result = calculate_item("Tenis prueba", "Tenis", "60", "3200", "0.40", "150000")

    assert result["tax_usd"] == Decimal("4.20")
    assert result["total_usd"] == Decimal("64.20")
    assert result["cost_cop"] == Decimal("205440.00")
    assert result["customer_price_cop"] == Decimal("360000")
    assert result["profit_cop"] == Decimal("160000")
    assert result["status"] == "GANANCIA"


def test_profit_rounds_up_to_next_10000():
    result = calculate_item("Camiseta", "Ropa", "50", "3900", "0.30", "80000")

    assert result["profit_cop"] == Decimal("90000")


def test_invalid_price_is_rejected():
    with pytest.raises(ValueError, match="precio"):
        calculate_item("Producto", "Ropa", 0, 3200, "0.40", 80000)


def test_surcharge_rate_from_percent_accepts_multiples_of_ten():
    assert surcharge_rate_from_percent(10) == Decimal("0.10")
    assert surcharge_rate_from_percent(50) == Decimal("0.50")
    assert surcharge_rate_from_percent(100) == Decimal("1.00")

    with pytest.raises(ValueError, match="múltiplo de 10"):
        surcharge_rate_from_percent(15)


def test_initialize_database_refreshes_category_rates_from_excel(tmp_path):
    excel_path = tmp_path / "CONFIGURACION.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "CONFIGURACIÓN"
    sheet.append(["Categoria", "surcharge_rate", "minimum_profit"])
    sheet.append(["Ropa", 0.45, 120000])
    workbook.save(excel_path)

    db_path = tmp_path / "personal_shopper.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "CREATE TABLE categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, surcharge_rate NUMERIC NOT NULL, minimum_profit NUMERIC NOT NULL, active INTEGER NOT NULL DEFAULT 1)"
        )
        connection.execute(
            "INSERT INTO categories (name, surcharge_rate, minimum_profit, active) VALUES (?, ?, ?, ?)",
            ("Ropa", 0.20, 80000, 1),
        )

    initialize_database(db_path, excel_path)

    categories = get_categories(db_path)
    assert categories[0]["name"] == "Ropa"
    assert categories[0]["surcharge_rate"] == 0.45
    assert categories[0]["minimum_profit"] == 120000


def test_default_surcharge_percent_is_persisted(tmp_path):
    db_path = tmp_path / "personal_shopper.db"
    initialize_database(db_path)

    assert get_default_surcharge_percent(db_path) == 10

    set_default_surcharge_percent(db_path, 60)
    assert get_default_surcharge_percent(db_path) == 60
