# PERSONAL_SHOPPER_APP

Cotizador local para productos comprados en Estados Unidos y vendidos en Colombia.

## Requisitos

- Python 3.12+
- Entorno virtual recomendado

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecutar

```powershell
streamlit run app.py
```

La primera ejecucion crea `data/personal_shopper.db` y carga las categorias desde `TABLA_PERSONAL_SHOPPER_COMPLETA.xlsx`.

## Pruebas

```powershell
pytest
```

La TRM se ingresa manualmente por cotizacion. El impuesto es fijo del 7% y el precio se redondea hacia arriba al siguiente multiplo de $10.000 COP.
