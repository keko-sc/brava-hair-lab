#!/usr/bin/env python3
"""Baja candidatas de Openverse para cada hueco y arma una hoja de contactos.

Solo licencias de uso comercial (cc0, pdm, by). Filtra por ancho minimo.
Uso:  python3 tools/buscar_candidatas.py huecos.json
"""
import json, os, sys, re, io
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from PIL import Image, ImageDraw

API = "https://api.openverse.org/v1/images/"
LIC = "cc0,pdm,by"
UA = {"User-Agent": "BRAVA-HairLab/1.0 (proyecto cliente; contacto local)", "Accept": "application/json"}
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "tools", "candidatas")

def get(url, accept="application/json", timeout=25):
    req = Request(url, headers={**UA, "Accept": accept})
    with urlopen(req, timeout=timeout) as r:
        return r.read()

def buscar(q, ancho_min, n=6):
    params = {"q": q, "license": LIC, "page_size": 24, "mature": "false",
              "extension": "jpg,jpeg,png", "size": "large"}
    try:
        data = json.loads(get(API + "?" + urlencode(params)))
    except Exception as e:
        print(f"    ! error de busqueda: {e}")
        return []
    out = []
    for r in data.get("results", []):
        w = r.get("width") or 0
        h = r.get("height") or 0
        if w < ancho_min:
            continue
        url = r.get("url") or ""
        if not re.search(r"\.(jpe?g|png)(\?|$)", url, re.I):
            continue
        out.append({"id": r.get("id"), "url": url, "w": w, "h": h,
                    "titulo": (r.get("title") or "")[:70],
                    "autor": (r.get("creator") or "—")[:40],
                    "licencia": r.get("license", "") + " " + (r.get("license_version") or ""),
                    "fuente": r.get("source", ""),
                    "pagina": r.get("foreign_landing_url", "")})
        if len(out) >= n:
            break
    return out

def bajar(c, destino):
    try:
        b = get(c["url"], accept="image/*", timeout=30)
        if len(b) < 20000:
            return None
        im = Image.open(io.BytesIO(b)).convert("RGB")
        im.save(destino, "JPEG", quality=88)
        return im
    except Exception as e:
        print(f"    ! no se pudo bajar: {str(e)[:60]}")
        return None

def hoja(imagenes, etiquetas, ruta, cols=3, celda=430):
    if not imagenes: return
    filas = (len(imagenes) + cols - 1) // cols
    alto = celda * 3 // 4
    lienzo = Image.new("RGB", (cols * celda, filas * (alto + 26)), (244, 238, 228))
    d = ImageDraw.Draw(lienzo)
    for i, im in enumerate(imagenes):
        x = (i % cols) * celda; y = (i // cols) * (alto + 26)
        t = im.copy(); t.thumbnail((celda - 8, alto - 8))
        lienzo.paste(t, (x + (celda - t.width)//2, y + (alto - t.height)//2))
        d.rectangle([x+2, y+2, x+celda-4, y+alto-2], outline=(180,146,111), width=2)
        d.text((x + 8, y + alto + 5), etiquetas[i][:62], fill=(36,28,20))
    lienzo.save(ruta, "JPEG", quality=86)

def main():
    huecos = json.load(open(sys.argv[1], encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    registro = {}
    for h in huecos:
        cod = h["codigo"]
        carpeta = os.path.join(OUT, cod)
        os.makedirs(carpeta, exist_ok=True)
        print(f"\n=== {cod} — {h['para']}")
        vistos, ims, etqs, metas = set(), [], [], []
        for q in h["consultas"]:
            print(f"  · «{q}»")
            for c in buscar(q, h["ancho_min"], n=h.get("por_consulta", 4)):
                if c["id"] in vistos: continue
                vistos.add(c["id"])
                idx = len(ims) + 1
                ruta = os.path.join(carpeta, f"{idx:02d}.jpg")
                im = bajar(c, ruta)
                if im is None: continue
                c["archivo"] = ruta; c["n"] = idx; c["consulta"] = q
                ims.append(im); metas.append(c)
                etqs.append(f"{idx:02d} · {c['w']}x{c['h']} · {c['autor']}")
                print(f"    {idx:02d}  {c['w']}x{c['h']}  {c['licencia'].strip()}  {c['titulo']}")
            if len(ims) >= h.get("maximo", 8): break
        if ims:
            hoja(ims, etqs, os.path.join(OUT, f"hoja-{cod}.jpg"))
            print(f"  -> hoja de contactos: tools/candidatas/hoja-{cod}.jpg  ({len(ims)} candidatas)")
        else:
            print("  -> sin candidatas que cumplan el minimo de tamano")
        registro[cod] = metas
    json.dump(registro, open(os.path.join(OUT, "registro.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\nregistro en tools/candidatas/registro.json")

main()
