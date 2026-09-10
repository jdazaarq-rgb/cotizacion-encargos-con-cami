from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.personal_shopper.calculator import calculate_item
from src.personal_shopper.database import get_categories, initialize_database, save_quote


ROOT = Path(__file__).parent
EXCEL_PATH = ROOT / "TABLA_PERSONAL_SHOPPER_COMPLETA.xlsx"
DB_PATH = ROOT / "data" / "personal_shopper.db"

st.set_page_config(page_title="Cotización Encargos", page_icon="$", layout="wide")
initialize_database(DB_PATH, EXCEL_PATH)
categories = get_categories(DB_PATH)

st.title("Cotización Encargos")
st.caption("Cotizador de productos comprados en Estados Unidos y vendidos en Colombia")

if not categories:
    st.error("No se encontraron categorías. Verifica el archivo Excel de configuración.")
    st.stop()

if "items" not in st.session_state:
    st.session_state["items"] = []
if st.session_state.pop("reset_product_fields", False):
    st.session_state["product_input"] = ""
    st.session_state["category_input"] = "Selecciona una categoría"
    st.session_state["price_input"] = 0.0

st.subheader("Datos de la cotización")
trm = st.number_input(
    "1. TRM manual",
    min_value=0.0,
    value=0.0,
    step=1.0,
    format="%.2f",
    help="Ingresa la tasa representativa del mercado antes de continuar.",
)
trm_valid = trm > 0

category_by_name = {item["name"]: item for item in categories}
product = st.text_input("2. Producto", key="product_input", disabled=not trm_valid)
product_valid = bool(product.strip())

category_options = ["Selecciona una categoría"] + list(category_by_name)
category_name = st.selectbox(
    "3. Categoría",
    category_options,
    key="category_input",
    disabled=not product_valid,
)
category_valid = category_name != category_options[0]

price_usd = st.number_input(
    "4. Precio en Estados Unidos (USD)",
    min_value=0.0,
    value=0.0,
    step=0.01,
    format="%.2f",
    key="price_input",
    disabled=not category_valid,
)
price_valid = price_usd > 0
add_product = st.button(
    "Agregar producto",
    disabled=not (trm_valid and product_valid and category_valid and price_valid),
)

if add_product:
    category = category_by_name[category_name]
    try:
        item = calculate_item(
            product,
            category_name,
            price_usd,
            trm,
            category["surcharge_rate"],
            category["minimum_profit"],
        )
        st.session_state["items"].append(item)
        st.session_state["reset_product_fields"] = True
        st.rerun()
    except ValueError as error:
        st.error(str(error))

if st.session_state["items"]:
    st.subheader("Productos de la cotización")
    for index, item in enumerate(st.session_state["items"]):
        columns = st.columns([3, 2, 1, 2, 2, 2, 1])
        columns[0].write(item["product"])
        columns[1].write(item["category"])
        columns[2].write(f"USD {item['price_usd']:.2f}")
        columns[3].write(f"COP {item['cost_cop']:,.0f}")
        columns[4].write(f"COP {item['customer_price_cop']:,.0f}")
        columns[5].write(item["status"])
        if columns[6].button("Quitar", key=f"remove_{index}"):
            st.session_state["items"].pop(index)
            st.rerun()

    total_cost = sum((item["cost_cop"] for item in st.session_state["items"]), 0)
    total_price = sum((item["customer_price_cop"] for item in st.session_state["items"]), 0)
    total_profit = sum((item["profit_cop"] for item in st.session_state["items"]), 0)

    st.divider()
    total_columns = st.columns(3)
    total_columns[0].metric("Costo total", f"COP {total_cost:,.0f}")
    total_columns[1].metric("Precio cliente", f"COP {total_price:,.0f}")
    total_columns[2].metric("Ganancia", f"COP {total_profit:,.0f}")

    if st.button("Guardar cotización"):
        quote_id = save_quote(DB_PATH, trm, st.session_state["items"])
        st.success(f"Cotización {quote_id} guardada correctamente.")
else:
    st.info("Agrega uno o varios productos para construir la cotización.")
