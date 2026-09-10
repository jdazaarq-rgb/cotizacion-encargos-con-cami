from decimal import Decimal

import pytest

from src.personal_shopper.calculator import calculate_item, round_up_to_10000


def test_round_up_to_next_10000():
    assert round_up_to_10000(Decimal("153200")) == Decimal("160000")
    assert round_up_to_10000(Decimal("160000")) == Decimal("160000")


def test_calculate_item_uses_fixed_seven_percent_tax_and_category_rules():
    result = calculate_item("Tenis prueba", "Tenis", "60", "3200", "0.40", "150000")

    assert result["tax_usd"] == Decimal("4.20")
    assert result["total_usd"] == Decimal("64.20")
    assert result["cost_cop"] == Decimal("205440.00")
    assert result["customer_price_cop"] == Decimal("360000")
    assert result["profit_cop"] == Decimal("154560.00")
    assert result["status"] == "GANANCIA"


def test_invalid_price_is_rejected():
    with pytest.raises(ValueError, match="precio"):
        calculate_item("Producto", "Ropa", 0, 3200, "0.40", 80000)
