#!/usr/bin/env python3
"""Candidatas desde Wikimedia Commons (sin clave, licencias de uso comercial)."""
import json, os, sys, io, re, time
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from PIL import Image, ImageDraw

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "BRAVA-HairLab/1.0 (web de cliente; soysebastianrincon@gmail.com)"}
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "tools", "candidatas")
MAL = re.compile(r"non[- ]?commercial|\bnc\b|fair use|by-nc", re.I)

def get(url, timeout=30, binario=False):
    with urlopen(Request(url, headers=UA), timeout=timeout) as r:
        return r.read() if binario else json.loads(r.read())

def buscar(q, ancho_min, n=6):
    p = {"action":"query","format":"json","generator":"search","gsrsearch":f"filetype:bitmap {q}",
         "gsrnamespace":"6","gsrlimit":"30","prop":"imageinfo",
         "iiprop":"url|size|extmetadata","iiurlwidth":"1800"}
    try:
        d = get(API + "?" + urlencode(p))
    except Exception as e:
        print(f"    ! {str(e)[:70]}"); return []
    out = []
    for pg in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = (pg.get("imageinfo") or [{}])[0]
        w = ii.get("width") or 0
        if w < ancho_min: continue
        md = ii.get("extmetadata", {}) or {}
        lic = (md.get("LicenseShortName", {}).get("value") or "")
        if MAL.search(lic): continue
        if not re.search(r"cc0|public domain|cc by|cc-by|attribution", lic, re.I): continue
        url = ii.get("thumburl") or ii.get("url")
        if not url: continue
        aut = re.sub(r"<[^>]+>", "", md.get("Artist", {}).get("value") or "—")[:40].strip()
        out.append({"url": url, "w": w, "h": ii.get("height") or 0, "licencia": lic,
                    "autor": aut, "titulo": pg.get("title","")[5:75],
                    "pagina": ii.get("descriptionurl","")})
        if len(out) >= n: break
    return out

def hoja(ims, etqs, ruta, cols=3, celda=430):
    if not ims: return
    filas = (len(ims)+cols-1)//cols; alto = celda*3//4
    L = Image.new("RGB",(cols*celda, filas*(alto+26)),(244,238,228)); d = ImageDraw.Draw(L)
    for i,im in enumerate(ims):
        x=(i%cols)*celda; y=(i//cols)*(alto+26)
        t=im.copy(); t.thumbnail((celda-8,alto-8))
        L.paste(t,(x+(celda-t.width)//2, y+(alto-t.height)//2))
        d.rectangle([x+2,y+2,x+celda-4,y+alto-2],outline=(180,146,111),width=2)
        d.text((x+8,y+alto+5), etqs[i][:62], fill=(36,28,20))
    L.save(ruta,"JPEG",quality=86)

def main():
    huecos = json.load(open(sys.argv[1], encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    reg_path = os.path.join(OUT,"registro.json")
    registro = json.load(open(reg_path,encoding="utf-8")) if os.path.exists(reg_path) else {}
    for h in huecos:
        cod=h["codigo"]; carp=os.path.join(OUT,cod); os.makedirs(carp,exist_ok=True)
        print(f"\n=== {cod} — {h['para']}")
        ims,etqs,metas,vistos=[],[],[],set()
        for q in h["consultas"]:
            print(f"  · «{q}»")
            for c in buscar(q, h["ancho_min"], n=h.get("por_consulta",4)):
                if c["url"] in vistos: continue
                vistos.add(c["url"])
                idx=len(ims)+1; ruta=os.path.join(carp,f"{idx:02d}.jpg")
                try:
                    b=get(c["url"],binario=True)
                    im=Image.open(io.BytesIO(b)).convert("RGB")
                    if min(im.size)<500: continue
                    im.save(ruta,"JPEG",quality=88)
                except Exception as e:
                    print(f"    ! bajada: {str(e)[:50]}"); continue
                c["archivo"]=ruta; c["n"]=idx; c["consulta"]=q
                ims.append(im); metas.append(c)
                etqs.append(f"{idx:02d} · {c['w']}x{c['h']} · {c['licencia'][:18]}")
                print(f"    {idx:02d}  {c['w']}x{c['h']}  {c['licencia'][:26]}  {c['titulo'][:46]}")
                time.sleep(.25)
            if len(ims)>=h.get("maximo",8): break
        if ims:
            hoja(ims,etqs,os.path.join(OUT,f"hoja-{cod}.jpg"))
            print(f"  -> hoja: tools/candidatas/hoja-{cod}.jpg ({len(ims)})")
        else:
            print("  -> nada que cumpla")
        registro[cod]=metas
    json.dump(registro, open(reg_path,"w",encoding="utf-8"), ensure_ascii=False, indent=1)

main()
