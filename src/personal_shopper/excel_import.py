from __future__ import annotations

from pathlib import Path

import openpyxl


def load_categories(excel_path: str | Path) -> list[dict[str, object]]:
    workbook = openpyxl.load_workbook(excel_path, data_only=True, read_only=True)
    worksheet = workbook["CONFIGURACIÓN"]
    categories: list[dict[str, object]] = []

    for name, surcharge_rate, minimum_profit in worksheet.iter_rows(min_row=2, values_only=True):
        if not name:
            continue
        categories.append(
            {
                "name": str(name).strip(),
                "surcharge_rate": surcharge_rate,
                "minimum_profit": minimum_profit,
            }
        )

    return categories
