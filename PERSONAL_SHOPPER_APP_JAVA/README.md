# PERSONAL_SHOPPER_APP_JAVA

Version Java de la aplicacion de cotizacion Personal Shopper.

## Requisitos

- JDK 21+
- Maven 3.9+

## Ejecutar

Desde esta carpeta:

```powershell
mvn spring-boot:run
```

Abrir http://localhost:8080.

La aplicacion usa SQLite, importa las categorias desde `TABLA_PERSONAL_SHOPPER_COMPLETA.xlsx` y permite agregar varios productos a una cotizacion.

## Pruebas

```powershell
mvn test
```
