# BILUZ — Tarjetas NFC personalizadas

> Rellena los campos marcados con `TODO` con los datos reales de la empresa.

## Qué hacemos

BILUZ diseña, imprime y programa **tarjetas de presentación inteligentes con chip NFC**.
El cliente acerca la tarjeta a un celular y se abre su perfil digital, vCard, WhatsApp,
redes sociales, menú, portafolio o cualquier URL, sin necesidad de apps.

## Líneas de producto

| Línea | Materiales | Chip típico | Uso |
|---|---|---|---|
| Tarjetas PVC | PVC blanco / mate / brillante | NTAG213 / NTAG215 | Tarjeta de presentación |
| Tarjetas premium | Metal, bambú/madera | NTAG215 / NTAG216 | Ejecutivos, regalos corporativos |
| Stickers y llaveros | PVC / epoxy | NTAG213 | Negocios, mesas, reseñas de Google |
| Servicios | — | — | Diseño, perfil digital, reprogramación |

Catálogo con claves y precios: [`catalogo.json`](catalogo.json).

## Estándares técnicos del producto

- **ISO/IEC 7810 ID-1** — tamaño de tarjeta: 85.60 × 53.98 mm.
- **ISO/IEC 14443-A** — protocolo de comunicación de proximidad (13.56 MHz) que usan los chips NTAG.
- **NFC Forum Type 2 Tag + NDEF** — formato de los datos grabados (URL, vCard), compatible con iPhone y Android.

## Datos fiscales y de contacto

Se configuran en [`empresa.json`](empresa.json) y alimentan automáticamente las notas de venta.

- Razón social: TODO
- RFC: TODO
- Régimen fiscal: TODO
- Domicilio fiscal: TODO
- Teléfono / correo / web: TODO

## Políticas comerciales (sugeridas)

- **Anticipo:** 50 % para iniciar producción; resto contra entrega.
- **Tiempo de producción:** 5–7 días hábiles tras aprobar el diseño.
- **Aprobación de diseño:** el cliente aprueba la prueba digital por escrito (WhatsApp/correo) antes de imprimir.
- **Garantía:** 90 días contra defectos de fabricación y falla del chip (no cubre mal uso, dobleces, calor o desgaste).
- **Devoluciones:** por ser productos personalizados no aplican cambios por gusto; sí por defecto de fabricación o error imputable a BILUZ.
- **Datos personales:** la información que se graba en el chip se trata conforme al aviso de privacidad.
