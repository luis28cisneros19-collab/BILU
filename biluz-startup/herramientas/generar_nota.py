#!/usr/bin/env python3
"""Genera notas de venta de BILUZ en HTML (listas para imprimir o guardar como PDF).

Uso:
    python3 herramientas/generar_nota.py notas/datos/ejemplo.json
    python3 herramientas/generar_nota.py notas/datos/ejemplo.json --folio 15   # forzar folio

Cada nota recibe un folio consecutivo (notas/folio.txt), se guarda en notas/generadas/
y se registra en notas/registro.csv para preparar la factura global del periodo.
"""
import argparse
import csv
import html
import json
import sys
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EMPRESA = RAIZ / "empresa" / "empresa.json"
CATALOGO = RAIZ / "empresa" / "catalogo.json"
FOLIO = RAIZ / "notas" / "folio.txt"
SALIDA = RAIZ / "notas" / "generadas"
REGISTRO = RAIZ / "notas" / "registro.csv"

CENT = Decimal("0.01")
FORMAS_PAGO = {
    "01": "Efectivo",
    "03": "Transferencia electrónica",
    "04": "Tarjeta de crédito",
    "28": "Tarjeta de débito",
    "99": "Por definir",
}


def dinero(valor):
    return Decimal(str(valor)).quantize(CENT, ROUND_HALF_UP)


def fmt(valor):
    return f"${valor:,.2f}"


# --- Importe con letra -------------------------------------------------------
UNIDADES = ["", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE",
            "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISÉIS", "DIECISIETE",
            "DIECIOCHO", "DIECINUEVE", "VEINTE", "VEINTIUN", "VEINTIDÓS", "VEINTITRÉS",
            "VEINTICUATRO", "VEINTICINCO", "VEINTISÉIS", "VEINTISIETE", "VEINTIOCHO", "VEINTINUEVE"]
DECENAS = ["", "", "", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]
CENTENAS = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
            "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]


def _cientos(n):
    if n == 100:
        return "CIEN"
    c, resto = divmod(n, 100)
    partes = [CENTENAS[c]] if c else []
    if resto < 30:
        partes.append(UNIDADES[resto])
    else:
        d, u = divmod(resto, 10)
        partes.append(DECENAS[d] + (f" Y {UNIDADES[u]}" if u else ""))
    return " ".join(p for p in partes if p)


def numero_a_letras(n):
    if n == 0:
        return "CERO"
    millones, resto = divmod(n, 1_000_000)
    miles, unidades = divmod(resto, 1000)
    partes = []
    if millones:
        partes.append("UN MILLÓN" if millones == 1 else f"{numero_a_letras(millones)} MILLONES")
    if miles:
        partes.append("MIL" if miles == 1 else f"{_cientos(miles)} MIL")
    if unidades:
        partes.append(_cientos(unidades))
    return " ".join(partes)


def importe_con_letra(total, moneda):
    enteros = int(total)
    centavos = int((total - enteros) * 100)
    letras = numero_a_letras(enteros)
    sufijo = " DE" if letras.endswith(("MILLÓN", "MILLONES")) else ""
    nombre = "PESOS" if moneda == "MXN" else moneda
    return f"{letras}{sufijo} {nombre} {centavos:02d}/100 {'M.N.' if moneda == 'MXN' else ''}".strip()


# --- Lógica de la nota -------------------------------------------------------
def siguiente_folio(forzado):
    if forzado is not None:
        return forzado
    actual = int(FOLIO.read_text().strip()) if FOLIO.exists() else 0
    return actual + 1


def calcular(datos, empresa, catalogo):
    tasa = Decimal(str(empresa["tasa_iva"]))
    incluye_iva = empresa["precios_incluyen_iva"]
    conceptos = []
    for c in datos["conceptos"]:
        base = catalogo.get(c.get("clave"), {})
        precio = dinero(c.get("precio", base.get("precio", 0)))
        cantidad = Decimal(str(c["cantidad"]))
        descripcion = c.get("descripcion", base.get("descripcion"))
        if not descripcion:
            sys.exit(f"Concepto sin descripción ni clave válida: {c}")
        if c.get("personalizacion"):
            descripcion += f" — {c['personalizacion']}"
        conceptos.append({
            "clave": c.get("clave", ""),
            "cantidad": cantidad,
            "unidad": c.get("unidad", base.get("unidad", "PZA")),
            "descripcion": descripcion,
            "precio": precio,
            "importe": dinero(precio * cantidad),
        })

    bruto = sum((c["importe"] for c in conceptos), Decimal("0"))
    descuento = dinero(datos.get("descuento", 0))
    neto = bruto - descuento
    if incluye_iva:
        total = neto
        subtotal = dinero(total / (1 + tasa))
        iva = total - subtotal
    else:
        subtotal = neto
        iva = dinero(subtotal * tasa)
        total = subtotal + iva
    anticipo = dinero(datos.get("anticipo", total))
    return {
        "conceptos": conceptos, "bruto": bruto, "descuento": descuento,
        "subtotal": subtotal, "iva": iva, "total": total,
        "anticipo": anticipo, "saldo": total - anticipo,
    }


def renderizar(datos, empresa, calc, serie_folio, fecha):
    e = {k: html.escape(str(v)) for k, v in empresa.items()}
    cli = {k: html.escape(str(v)) for k, v in datos.get("cliente", {}).items()}
    moneda = empresa["moneda"]
    forma = datos.get("forma_pago", "99")
    filas = "\n".join(
        f"<tr><td>{c['cantidad'].normalize()}</td><td>{html.escape(c['unidad'])}</td>"
        f"<td>{html.escape(c['clave'])}</td><td>{html.escape(c['descripcion'])}</td>"
        f"<td class=n>{fmt(c['precio'])}</td><td class=n>{fmt(c['importe'])}</td></tr>"
        for c in calc["conceptos"]
    )
    descuento = (f"<tr><td>Descuento</td><td class=n>-{fmt(calc['descuento'])}</td></tr>"
                 if calc["descuento"] else "")
    nota_iva = "Precios con IVA incluido" if empresa["precios_incluyen_iva"] else "Precios más IVA"
    entrega = html.escape(datos.get("fecha_entrega", "Por confirmar"))
    observaciones = html.escape(datos.get("observaciones", ""))

    return f"""<!doctype html>
<html lang="es-MX"><head><meta charset="utf-8">
<title>Nota de venta {serie_folio}</title>
<style>
  body{{font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#111;max-width:780px;margin:24px auto;padding:0 16px}}
  header{{display:flex;justify-content:space-between;border-bottom:3px solid #111;padding-bottom:8px}}
  h1{{margin:0;font-size:26px;letter-spacing:2px}} h2{{margin:0;font-size:16px}}
  .folio{{text-align:right}} .folio b{{font-size:16px;color:#c00}}
  .caja{{border:1px solid #999;border-radius:4px;padding:8px;margin-top:10px}}
  table{{width:100%;border-collapse:collapse;margin-top:10px}}
  th,td{{border:1px solid #bbb;padding:5px;vertical-align:top}} th{{background:#eee;text-align:left}}
  .n{{text-align:right;white-space:nowrap}}
  .totales{{width:45%;margin-left:auto}} .totales td:first-child{{font-weight:bold}}
  .total td{{font-size:15px;background:#eee}}
  .legal{{font-size:10px;color:#333;margin-top:12px;line-height:1.4}}
  .firmas{{display:flex;gap:40px;margin-top:40px}} .firmas div{{flex:1;border-top:1px solid #111;text-align:center;padding-top:4px}}
  @media print{{body{{margin:0}}}}
</style></head><body>
<header>
  <div>
    <h1>{e['nombre_comercial']}</h1>
    <div>Tarjetas NFC personalizadas</div>
    <div>{e['razon_social']}<br>RFC: {e['rfc']} · Régimen: {e['regimen_fiscal']}</div>
    <div>{e['domicilio_fiscal']}</div>
    <div>{e['telefono']} · {e['correo']} · {e['sitio_web']}</div>
  </div>
  <div class=folio>
    <h2>NOTA DE VENTA</h2>
    <div>Folio: <b>{html.escape(serie_folio)}</b></div>
    <div>Fecha: {fecha.strftime('%Y-%m-%d')}</div>
    <div>Hora: {fecha.strftime('%H:%M:%S')}</div>
    <div>Lugar de expedición: C.P. {e['lugar_expedicion_cp']}, MX</div>
    <div>Moneda: {html.escape(moneda)}</div>
  </div>
</header>

<div class=caja>
  <b>Cliente:</b> {cli.get('nombre', 'Público en general')}
  {f"· <b>RFC:</b> {cli['rfc']}" if cli.get('rfc') else ''}<br>
  {f"<b>Tel:</b> {cli['telefono']} " if cli.get('telefono') else ''}{f"· <b>Correo:</b> {cli['correo']}" if cli.get('correo') else ''}<br>
  <b>Fecha estimada de entrega:</b> {entrega}
</div>

<table>
  <thead><tr><th>Cant.</th><th>Unidad</th><th>Clave</th><th>Descripción</th><th class=n>P. unitario</th><th class=n>Importe</th></tr></thead>
  <tbody>{filas}</tbody>
</table>

<table class=totales>
  {descuento}
  <tr><td>Subtotal</td><td class=n>{fmt(calc['subtotal'])}</td></tr>
  <tr><td>IVA {int(Decimal(str(empresa['tasa_iva'])) * 100)}%</td><td class=n>{fmt(calc['iva'])}</td></tr>
  <tr class=total><td>Total {html.escape(moneda)}</td><td class=n>{fmt(calc['total'])}</td></tr>
  <tr><td>Anticipo / pagado</td><td class=n>{fmt(calc['anticipo'])}</td></tr>
  <tr><td>Saldo pendiente</td><td class=n>{fmt(calc['saldo'])}</td></tr>
</table>

<p><b>Importe con letra:</b> ({html.escape(importe_con_letra(calc['total'], moneda))})<br>
<b>Forma de pago:</b> {forma} - {html.escape(FORMAS_PAGO.get(forma, forma))} · {nota_iva}</p>
{f"<div class=caja><b>Observaciones:</b> {observaciones}</div>" if observaciones else ''}

<div class=legal>
  <p><b>Garantía:</b> {e['garantia_dias']} días naturales a partir de la entrega contra defectos de fabricación
  y falla del chip NFC. Para hacerla válida presente esta nota en el domicilio o contacto arriba indicados;
  la reparación o reposición es sin costo. No cubre daños por mal uso, dobleces, exposición a calor, humedad o desgaste normal.</p>
  <p><b>Productos personalizados:</b> al fabricarse con el diseño aprobado por el cliente, no aplican cambios ni
  devoluciones por gusto; sí por defecto de fabricación o error imputable a {e['nombre_comercial']}.</p>
  <p><b>Datos personales:</b> la información grabada en los chips se trata conforme a nuestro aviso de privacidad:
  {e['aviso_privacidad_url']}</p>
  <p><b>{e['leyenda_no_fiscal']}</b></p>
</div>

<div class=firmas><div>Entregó ({e['nombre_comercial']})</div><div>Recibí de conformidad (cliente)</div></div>
</body></html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("datos", type=Path, help="JSON con cliente y conceptos de la venta")
    ap.add_argument("--folio", type=int, help="usar este número de folio en vez del siguiente")
    args = ap.parse_args()

    empresa = json.loads(EMPRESA.read_text(encoding="utf-8"))
    catalogo = {p["clave"]: p for p in json.loads(CATALOGO.read_text(encoding="utf-8"))["productos"]}
    datos = json.loads(args.datos.read_text(encoding="utf-8"))

    fecha = datetime.fromisoformat(datos["fecha"]) if datos.get("fecha") else datetime.now()
    numero = siguiente_folio(args.folio)
    serie_folio = f"{empresa['serie_folio']}-{numero:06d}"
    calc = calcular(datos, empresa, catalogo)

    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / f"{serie_folio}.html"
    if destino.exists():
        sys.exit(f"Ya existe la nota {destino.name}; no se sobrescribe (los folios no se reutilizan).")
    destino.write_text(renderizar(datos, empresa, calc, serie_folio, fecha), encoding="utf-8")

    if args.folio is None:
        FOLIO.write_text(f"{numero}\n")
    nuevo = not REGISTRO.exists()
    with REGISTRO.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["folio", "fecha_iso8601", "cliente", "rfc_cliente", "forma_pago",
                        "subtotal", "iva", "total", "anticipo", "saldo", "moneda"])
        w.writerow([serie_folio, fecha.isoformat(timespec="seconds"),
                    datos.get("cliente", {}).get("nombre", "Público en general"),
                    datos.get("cliente", {}).get("rfc", "XAXX010101000"),
                    datos.get("forma_pago", "99"), calc["subtotal"], calc["iva"], calc["total"],
                    calc["anticipo"], calc["saldo"], empresa["moneda"]])

    print(f"Nota generada: {destino.relative_to(RAIZ)}  Total: {fmt(calc['total'])} {empresa['moneda']}")


if __name__ == "__main__":
    main()
