# Requisitos legales y normas para notas de venta / tickets

> Guía orientativa para México. **No sustituye la asesoría de tu contador**: confirma
> con él tu régimen fiscal y las reglas vigentes de la Resolución Miscelánea Fiscal (RMF) del año.

## 1. ¿Existe una ISO para notas o tickets?

**No hay una norma ISO que defina el contenido de una nota de venta o ticket.** Lo que
manda el contenido es la ley de cada país (en México: SAT y PROFECO). Sí hay normas ISO
que conviene usar para que el documento sea claro y sin ambigüedades, y el generador las aplica:

| Norma | Para qué se usa en la nota |
|---|---|
| ISO 8601 | Fecha y hora: `2026-10-08T14:30:00` (sin confusión día/mes) |
| ISO 4217 | Código de moneda: `MXN` |
| ISO 3166-1 | Código de país: `MX` |
| ISO 9001 (opcional) | Control de documentos: folios consecutivos, sin huecos, archivados |

Para facturas electrónicas existen estándares internacionales (UBL / ISO/IEC 19845, EN 16931 en
la UE), pero en México el formato obligatorio es el **CFDI 4.0 del SAT**, no una ISO.

## 2. Nota de venta vs. factura (CFDI)

- La **nota de venta / ticket** es un comprobante de compra para el cliente. **No es deducible** ni sustituye al CFDI.
- Si el cliente **pide factura**, debes emitir un **CFDI 4.0** (art. 29 y 29-A del Código Fiscal de la Federación).
- Las ventas con nota/ticket a público en general deben ampararse después en una **factura global**
  (RFC genérico `XAXX010101000`) por periodo (diario, semanal, mensual o bimestral según régimen).
- Las notas deben tener **folio consecutivo** para poder relacionarlas con la factura global.

## 3. Datos que debe contener la nota (los incluye el generador)

**Ley Federal de Protección al Consumidor (art. 12):** el proveedor debe entregar comprobante con los
datos específicos de la compraventa. **Práctica SAT para comprobantes a público en general:**

1. Nombre / razón social del emisor ✅
2. RFC del emisor ✅ y régimen fiscal ✅
3. Domicilio fiscal y lugar de expedición (C.P.) ✅
4. Serie y folio consecutivo ✅
5. Fecha y hora de expedición ✅
6. Cantidad, unidad y descripción de cada producto/servicio ✅
7. Valor unitario e importe de cada concepto ✅
8. Subtotal, **IVA trasladado desglosado** e importe total ✅
9. Importe total con letra (práctica comercial mexicana) ✅
10. Forma de pago (efectivo, transferencia, tarjeta) ✅
11. Leyenda "no es comprobante fiscal" y cómo solicitar factura ✅

## 4. Requisitos de PROFECO aplicables a productos personalizados

- **Precio total visible** con impuestos incluidos (art. 7 bis LFPC). ✅
- **Garantía por escrito**: plazo, qué cubre, cómo hacerla válida y dónde (arts. 77–78 LFPC). ✅
- **Anticipos**: indicar monto pagado y saldo pendiente. ✅
- **Fecha estimada de entrega** del pedido. ✅
- Las condiciones de no devolución por personalización deben informarse **antes** de la compra (y quedar por escrito). ✅

## 5. Protección de datos personales

Las tarjetas NFC graban nombre, teléfono, correo, etc. del cliente. Conforme a la
**Ley Federal de Protección de Datos Personales en Posesión de los Particulares** debes tener un
**aviso de privacidad** y referenciarlo en la nota. ✅ (campo `aviso_privacidad_url`)

## 6. Conservación

Guarda copia de las notas emitidas (el generador las deja en `notas/generadas/`) al menos
**5 años** (art. 30 CFF), junto con las facturas globales correspondientes.
