from __future__ import annotations

from decimal import Decimal, ROUND_CEILING


TAX_RATE = Decimal("0.07")
ROUNDING_UNIT_COP = Decimal("10000")


def money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def round_up_to_10000(value: Decimal) -> Decimal:
    return (value / ROUNDING_UNIT_COP).to_integral_value(rounding=ROUND_CEILING) * ROUNDING_UNIT_COP


def calculate_item(
    product: str,
    category: str,
    price_usd: Decimal | int | float | str,
    trm: Decimal | int | float | str,
    surcharge_rate: Decimal | int | float | str,
    minimum_profit: Decimal | int | float | str,
) -> dict[str, Decimal | str]:
    price_usd = money(price_usd)
    trm = money(trm)
    surcharge_rate = money(surcharge_rate)
    minimum_profit = money(minimum_profit)

    if price_usd <= 0:
        raise ValueError("El precio en USD debe ser mayor que cero.")
    if trm <= 0:
        raise ValueError("La TRM debe ser mayor que cero.")

    tax_usd = price_usd * TAX_RATE
    total_usd = price_usd + tax_usd
    cost_cop = total_usd * trm
    price_by_rate = cost_cop * (Decimal("1") + surcharge_rate)
    price_by_minimum = cost_cop + minimum_profit
    customer_price_cop = round_up_to_10000(max(price_by_rate, price_by_minimum))
    profit_cop = customer_price_cop - cost_cop

    if profit_cop < 0:
        status = "PERDIDA"
    elif profit_cop < minimum_profit:
        status = "REVISAR"
    else:
        status = "GANANCIA"

    return {
        "product": product.strip(),
        "category": category,
        "price_usd": price_usd,
        "tax_usd": tax_usd,
        "total_usd": total_usd,
        "trm": trm,
        "cost_cop": cost_cop,
        "customer_price_cop": customer_price_cop,
        "profit_cop": profit_cop,
        "status": status,
    }
