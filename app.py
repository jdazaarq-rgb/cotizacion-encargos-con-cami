from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.personal_shopper.calculator import calculate_item, surcharge_rate_from_percent
from src.personal_shopper.database import get_categories, initialize_database, save_quote


ROOT = Path(__file__).parent
EXCEL_PATH = ROOT / "TABLA_PERSONAL_SHOPPER_COMPLETA.xlsx"
DB_PATH = ROOT / "data" / "personal_shopper.db"

st.set_page_config(page_title="Cotización Encargos", page_icon="$", layout="wide")
initialize_database(DB_PATH, EXCEL_PATH)
categories = get_categories(DB_PATH)

header_col, logo_col = st.columns([3, 1.1])
with header_col:
    st.title("Cotización Encargos")
with logo_col:
    st.image(str(ROOT / "logo_encargos.svg"), use_container_width=True)

st.caption("Cotizador de productos comprados en Estados Unidos y vendidos en Colombia")

if not categories:
    st.error("No se encontraron categorías. Verifica el archivo Excel de configuración.")
    st.stop()

if "items" not in st.session_state:
    st.session_state["items"] = []
if "surcharge_percent" not in st.session_state:
    st.session_state["surcharge_percent"] = 20
if st.session_state.pop("reset_product_fields", False):
    st.session_state["category_input"] = "Selecciona una categoría"
    st.session_state["price_input"] = ""
    # La TRM se conserva para la siguiente cotización y solo cambia si el usuario la modifica.

st.subheader("Datos de la cotización")
trm_raw = st.text_input(
    "1. TRM manual",
    value=st.session_state.get("trm_manual_input", ""),
    placeholder="0.00",
    help="La TRM se guarda para nuevas cotizaciones y puedes cambiarla cuando tú quieras.",
    key="trm_manual_input",
)
try:
    trm = float(trm_raw.strip().replace(",", ".")) if trm_raw.strip() else 0.0
    trm_valid = trm > 0
except ValueError:
    trm = 0.0
    trm_valid = False

category_by_name = {item["name"]: item for item in categories}
product = "Producto sin nombre"
product_valid = bool(product.strip())

category_options = ["Selecciona una categoría"] + list(category_by_name)
category_name = st.selectbox(
    "2. Categoría",
    category_options,
    key="category_input",
)
category_valid = category_name != category_options[0]

price_usd_raw = st.text_input(
    "3. Precio en Estados Unidos (USD)",
    value=st.session_state.get("price_input", ""),
    placeholder="0.00",
    key="price_input",
)
try:
    price_usd = float(price_usd_raw.strip().replace(",", ".")) if price_usd_raw.strip() else 0.0
    price_valid = price_usd > 0
except ValueError:
    price_usd = 0.0
    price_valid = False

surcharge_options = list(range(10, 101, 10))
surcharge_percent = st.selectbox(
    "4. % de recargo",
    options=surcharge_options,
    index=surcharge_options.index(st.session_state.get("surcharge_percent", 20)),
    help="Selecciona el porcentaje de recargo en múltiplos de 10% hasta 100%.",
    key="surcharge_percent",
)

preview_item = None
if trm_valid and category_valid and price_valid:
    category = category_by_name[category_name]
    try:
        effective_surcharge_rate = surcharge_rate_from_percent(surcharge_percent)
        preview_item = calculate_item(
            product,
            category_name,
            price_usd,
            trm,
            effective_surcharge_rate,
            category["minimum_profit"],
        )
    except ValueError as error:
        st.error(str(error))

button_label = "Nuevo producto" if st.session_state.get("items") else "Agregar producto"
add_product = st.button(
    button_label,
    use_container_width=True,
)

if add_product:
    if not trm_valid:
        st.error("Ingresa una TRM válida mayor a cero.")
    elif not category_valid:
        st.error("Selecciona una categoría antes de continuar.")
    elif not price_valid:
        st.error("Ingresa un precio en USD válido mayor a cero.")
    elif preview_item is not None:
        st.session_state["items"].append(preview_item)
        st.session_state["reset_product_fields"] = True
        st.rerun()

if preview_item is not None:
    st.divider()
    total_columns = st.columns(3)
    total_columns[0].metric("Costo total", f"COP {preview_item['cost_cop']:,.0f}".replace(",", "."))
    total_columns[1].metric("Precio cliente", f"COP {preview_item['customer_price_cop']:,.0f}".replace(",", "."))
    total_columns[2].metric("Ganancia", f"COP {preview_item['profit_cop']:,.0f}".replace(",", "."))

    if st.button("Guardar cotización"):
        quote_id = save_quote(DB_PATH, trm, [preview_item])
        st.success(f"Cotización {quote_id} guardada correctamente.")
else:
    st.info("Completa los datos para ver la cotización actual.")
