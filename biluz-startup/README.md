# BILUZ Startup — Tarjetas NFC personalizadas

```
biluz-startup/
├── empresa/
│   ├── perfil.md          # Qué hace BILUZ, productos, estándares, políticas
│   ├── empresa.json       # Datos fiscales/contacto que salen en cada nota  ← EDITAR
│   └── catalogo.json      # Productos, claves y precios                      ← EDITAR
├── notas/
│   ├── requisitos-legales.md      # Qué exige la ley (SAT / PROFECO) y normas ISO aplicables
│   ├── datos/ejemplo.json         # Plantilla de una venta
│   ├── ejemplo-nota-BLZ-000001.html
│   └── generadas/                 # Aquí se guardan las notas reales (no se suben a git)
└── herramientas/generar_nota.py   # Generador de notas (Python 3, sin dependencias)
```

## Generar una nota para un cliente

1. Edita una sola vez `empresa/empresa.json` (RFC, razón social, domicilio, régimen…) y `empresa/catalogo.json`.
2. Copia `notas/datos/ejemplo.json`, cambia cliente, conceptos (por `clave` del catálogo), anticipo y forma de pago.
3. Ejecuta:

   ```bash
   python3 herramientas/generar_nota.py notas/datos/mi-venta.json
   ```

4. Abre `notas/generadas/BLZ-00000X.html` en el navegador → **Imprimir → Guardar como PDF** y envíala al cliente.

El generador:

- Asigna **folio consecutivo** (`BLZ-000001`, `BLZ-000002`…) y nunca sobrescribe uno existente.
- Desglosa **subtotal + IVA 16 %** (precios con IVA incluido por defecto, configurable).
- Escribe el **importe con letra**, anticipo y saldo pendiente.
- Incluye garantía por escrito, política de personalizados, aviso de privacidad y la leyenda de que **no es CFDI**.
- Usa fechas **ISO 8601** y moneda **ISO 4217** (`MXN`).
- Registra cada nota en `notas/registro.csv` para armar la **factura global** del periodo.

Formas de pago (catálogo SAT): `01` Efectivo, `03` Transferencia, `04` T. crédito, `28` T. débito, `99` Por definir.

Detalle de los requisitos legales: [`notas/requisitos-legales.md`](notas/requisitos-legales.md).
