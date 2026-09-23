#!/usr/bin/env python3
"""Prepara las fotos para el marco de la portada.

El marco de la portada es apaisado (6:5) y las fotos pueden llegar de
cualquier forma, así que el encuadre NO se deja al automático: cada foto
trae su modo, su zoom y su punto de foco. Reglas:

  1. MÍNIMO. Si el lado corto no llega a 800 px, la foto NO entra en la
     rotación. Una foto puede saltarse la regla a propósito
     ("salta_minimo"), y entonces se avisa de a cuánto se está ampliando.
  2. MODO "recorte". Se amplía lo justo para llenar el marco (zoom 1.0 es
     el mínimo necesario) y la ventana se coloca con el foco declarado.
     Subir el zoom recorta más; es una decisión por foto.
  3. MODO "completa". La imagen entra ENTERA, sin perder nada —para piezas
     de marca o para fotos que no encajan en la forma del marco—. Detrás
     va la misma imagen ampliada, desenfocada y oscurecida; delante, la
     nítida, centrada y al mayor tamaño que aguante: nunca se amplía por
     encima de "max_ampliacion" respecto a sus píxeles reales. Los bordes
     de la capa nítida se difuminan contra el fondo por los lados donde
     sobra sitio, para que no parezca una foto pegada encima.

Las piezas que ya traen el tono de la marca no se viran.
"""
import os, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFilter

SRC = "assets/photos/source"
DST = "assets/img"
LADO_MINIMO = 800

# Peso máximo del archivo terminado. La portada puede permitirse más: es lo
# primero que se ve y se carga con prioridad. El resto va diferido, así que
# se aprieta. Si a calidad 88 no cabe, se baja de cinco en cinco hasta que
# quepa, nunca por debajo de 70.
TOPE_KB = {"portada": 400}
TOPE_KB_POR_DEFECTO = 150
TOPE_KB_DURO = 250
CALIDAD = 88
CALIDAD_MINIMA = 70

# Cada hueco de la página tiene su forma. Aquí van los lienzos a los que se
# prepara cada foto: siempre la proporción REAL del hueco, para que el
# navegador no vuelva a recortar por encima del encuadre ya decidido.
MARCOS = {
    "portada": (6, 5, 1000),   # el marco apaisado del hero
    "piso":    (4, 5, 1200),   # la tarjeta vertical de "Los dos espacios"
    "cuadro":  (1, 1, 1100),   # los marcos cuadrados de "Dos abordajes"
    "paso":    (3, 4, 1200),   # los cuatro pasos verticales de "El Método"
    "compara": (3, 4, 1200),   # las dos caras de cada comparador
    "reel":    (9, 16, 1600),  # los marcos verticales de la galería
    "banda":   (3, 2, 1400),   # las bandas anchas de los bloques de familia
}
# La portada se puede probar con otra proporción desde la línea de comandos:
#   python3 tools/tratar_fotos.py 6:5
if len(sys.argv) > 1 and ":" in sys.argv[1]:
    _a, _b = (int(v) for v in sys.argv[1].split(":"))
    MARCOS["portada"] = (_a, _b, MARCOS["portada"][2])


def lienzo(nombre):
    a, b, alto = MARCOS[nombre]
    return int(alto * a / b), alto, f"{a}:{b}"

FOTOS = [
    # Las cuatro de la portada. Llegan a 1536x1024 (3:2) y el marco es 6:5,
    # así que se recorta solo por los lados: se pierde un 20 % del ancho y
    # no hace falta ampliar nada. El foco de cada una evita que el recorte
    # se lleve lo que importa.
    dict(cod="FOTO-01", arch="foto-01.jpg", virar=True, modo="recorte", fx=.50, fy=.50,
         nota="melena ondulada de espaldas, luz cálida de ventana; va centrada"),
    dict(cod="FOTO-18", arch="foto-02.jpg", virar=True, modo="recorte", fx=.50, fy=.50,
         nota="macro de la raíz y la partidura; la cabeza ocupa todo el ancho"),
    dict(cod="FOTO-19", arch="foto-03.jpg", virar=True, modo="recorte", fx=.60, fy=.50,
         nota="bodegón de repisa: frascos ámbar y toalla; foco a la derecha para "
              "que la toalla entre entera y quede algo del cuenco a la izquierda"),
    dict(cod="FOTO-20", arch="foto-04.jpg", virar=True, modo="recorte", fx=.62, fy=.50,
         nota="rizos definidos de espaldas; la masa de rizo cae a la derecha, "
              "así que el foco se corre para no cortarla"),

    # ── Portada · los cinco bloques de categoría ──
    # Huecos nuevos y vacíos: aún no hay original. El marco de la página es una
    # banda ancha 3:2, así que cuando lleguen las fotos basta con descomentar
    # estas cinco líneas y dejar los archivos en assets/photos/source/.
    # dict(cod="FOTO-21", arch="foto-21.jpg", virar=False, marco="banda",
    #      modo="recorte", fx=.50, fy=.50,
    #      nota="Alisados: plano ancho del Piso 1 en uso, trabajo sobre la hebra"),
    # dict(cod="FOTO-22", arch="foto-22.jpg", virar=False, marco="banda",
    #      modo="recorte", fx=.50, fy=.50,
    #      nota="Tratamientos: plano ancho de un ritual en ejecución"),
    # dict(cod="FOTO-23", arch="foto-23.jpg", virar=False, marco="banda",
    #      modo="recorte", fx=.50, fy=.50,
    #      nota="Head Spa: plano ancho del Piso 2, cabina privada, luz tenue"),
    # dict(cod="FOTO-24", arch="foto-24.jpg", virar=False, marco="banda",
    #      modo="recorte", fx=.50, fy=.50,
    #      nota="Caída: plano ancho de una sesión de bioestimulación"),
    # dict(cod="FOTO-25", arch="foto-25.jpg", virar=False, marco="banda",
    #      modo="recorte", fx=.50, fy=.50,
    #      nota="Complementarios: plano ancho de un add-on en ejecución"),

    # ── "Los dos espacios": la tarjeta vertical de cada piso ──
    # Llegan a 1024x1200 (0,85) y el hueco es 4:5, así que se recorta solo un
    # 6 % por los lados. No se viran aquí: las fotos de la página ya pasan por
    # el tratamiento común de color en el CSS (.arco img).
    dict(cod="FOTO-12", arch="foto-12.jpg", virar=False, marco="piso",
         modo="recorte", fx=.50, fy=.50,
         nota="Piso 1, Retreat en el Desierto: plano general del salón; la fuga "
              "va centrada y el recorte no toca ni la estantería ni las sillas"),
    dict(cod="FOTO-13", arch="foto-13.jpg", virar=False, marco="piso",
         modo="recorte", fx=.50, fy=.50,
         nota="Piso 2, El Santuario: cabina privada con la camilla centrada y "
              "simétrica; centrado es el único encuadre que respeta la simetría"),

    # ── "Dos abordajes": los dos marcos cuadrados ──
    # Llegan cuadradas (1254x1254) y el hueco es 1:1: no se recorta nada,
    # solo se reducen. Tampoco se viran: el color común lo pone el CSS.
    dict(cod="FOTO-02", arch="foto-02-fiber.jpg", virar=False, marco="cuadro",
         modo="recorte", fx=.50, fy=.50,
         nota="BRAVA FIBER: melena de medios a puntas con brillo, luz cálida"),
    dict(cod="FOTO-03", arch="foto-03-scalp.jpg", virar=False, marco="cuadro",
         modo="recorte", fx=.50, fy=.50,
         nota="BRAVA SCALP: nuca y raíz con recogido, luz fría y tenue"),

    # ── "El Método": los cuatro pasos ──
    # Llegan a 1024x1536 (2:3) y el hueco es 3:4, así que se recorta un 11 %
    # por arriba y por abajo, repartido. En las cuatro el motivo está
    # centrado, así que el encuadre centrado es el correcto.
    dict(cod="FOTO-04", arch="foto-04-assess.jpg", virar=False, marco="paso",
         modo="recorte", fx=.50, fy=.50,
         nota="01 ASSESS: la mano levanta la melena para ver la raíz"),
    dict(cod="FOTO-05", arch="foto-05-treat.jpg", virar=False, marco="paso",
         modo="recorte", fx=.50, fy=.50,
         nota="02 TREAT: aplicación del producto con guante sobre la hebra mojada"),
    dict(cod="FOTO-06", arch="foto-06-transform.jpg", virar=False, marco="paso",
         modo="recorte", fx=.50, fy=.50,
         nota="03 TRANSFORM: melena seca con movimiento y brillo"),
    dict(cod="FOTO-07", arch="foto-07-maintain.jpg", virar=False, marco="paso",
         modo="recorte", fx=.50, fy=.50,
         nota="04 MAINTAIN: peine de madera y toalla, el cuidado en casa"),

    # ── Comparadores de "Antes y después" ──
    # ⚠ DEMO: imágenes generadas con IA, solo para probar que el tirador
    # funciona. NO son casos reales. Estas cuatro entradas y sus archivos se
    # borran antes de publicar; la etiqueta de PENDIENTE de la sección se
    # queda hasta que lleguen los casos reales con autorización.
    # Las dos caras de un comparador llevan EXACTAMENTE el mismo encuadre:
    # si una se recortara distinto, al mover el tirador saltaría la imagen.
    dict(cod="FOTO-AB1A", arch="DEMO-antes.jpg",     virar=False, marco="compara",
         modo="recorte", fx=.50, fy=.50, nota="DEMO caso 1, antes"),
    dict(cod="FOTO-AB1B", arch="DEMO-despues.jpg",   virar=False, marco="compara",
         modo="recorte", fx=.50, fy=.50, nota="DEMO caso 1, después"),
    dict(cod="FOTO-AB2A", arch="DEMO-antes-2.jpg",   virar=False, marco="compara",
         modo="recorte", fx=.50, fy=.50, nota="DEMO caso 2, antes"),
    dict(cod="FOTO-AB2B", arch="DEMO-despues-2.jpg", virar=False, marco="compara",
         modo="recorte", fx=.50, fy=.50, nota="DEMO caso 2, después"),

    # ── Galería "El Lab, por dentro" ──
    # ⚠ PRUEBA: imágenes numeradas del 1 al 8, solo para ver la transición.
    # Estas ocho entradas y sus archivos se borran antes de publicar.
    # Llegan a 1080x1920, que ya es 9:16 exacto: no se recorta nada.
] + [
    dict(cod="FOTO-G%02d" % n, arch="PRUEBA-g%02d.jpg" % n, virar=False, marco="reel",
         modo="recorte", fx=.50, fy=.50, nota="PRUEBA galería, número %d" % n)
    for n in range(1, 9)
]


def ajustar(im):
    im = ImageEnhance.Color(im).enhance(.80)
    im = ImageEnhance.Brightness(im).enhance(.94)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.045)))
    b = b.point(lambda v: int(v * 0.965))
    return Image.merge("RGB", (r, g, b))


def cubrir(im, zoom, fx, fy, ANCHO, ALTO):
    """Amplía lo justo para llenar el marco (por zoom) y coloca la ventana."""
    w, h = im.size
    escala = max(ANCHO / w, ALTO / h) * zoom
    im = im.resize((max(ANCHO, int(w * escala)), max(ALTO, int(h * escala))), Image.LANCZOS)
    x = int((im.width - ANCHO) * fx)
    y = int((im.height - ALTO) * fy)
    return im.crop((x, y, x + ANCHO, y + ALTO))


def completa(im, fx, fy, max_ampliacion, ANCHO, ALTO):
    """La imagen entera y centrada sobre una copia ampliada y desenfocada."""
    fondo = cubrir(im, 1.18, .5, .5, ANCHO, ALTO)
    fondo = fondo.filter(ImageFilter.GaussianBlur(30))
    fondo = ImageEnhance.Brightness(fondo).enhance(.50)
    fondo = ImageEnhance.Color(fondo).enhance(.65)

    # El mayor tamaño que cabe, sin pasar del tope de ampliación de la foto.
    cabe = min(ANCHO / im.width, ALTO / im.height)
    escala = min(cabe, max_ampliacion)
    frente = im.resize((int(im.width * escala), int(im.height * escala)), Image.LANCZOS)
    if escala > 1.02:                       # devuelve algo de nitidez a lo ampliado
        frente = frente.filter(ImageFilter.UnsharpMask(radius=1.6, percent=85, threshold=3))

    # Borde difuminado solo por donde queda fondo a la vista.
    pluma = 30
    mx = pluma if frente.width < ANCHO else 0
    my = pluma if frente.height < ALTO else 0
    mascara = Image.new("L", frente.size, 0)
    ImageDraw.Draw(mascara).rectangle(
        [mx, my, frente.width - 1 - mx, frente.height - 1 - my], fill=255)
    if mx or my:
        mascara = mascara.filter(ImageFilter.GaussianBlur(pluma * .55))

    fondo.paste(frente, (int((ANCHO - frente.width) * fx),
                         int((ALTO - frente.height) * fy)), mascara)
    return fondo, escala, frente.size


os.makedirs(DST, exist_ok=True)
dentro, fuera = [], []
for f in FOTOS:
    ruta = os.path.join(SRC, f["arch"])
    if not os.path.exists(ruta):
        fuera.append((f["cod"], f["arch"], "no está en la carpeta")); continue
    im = ImageOps.exif_transpose(Image.open(ruta).convert("RGB"))
    corto = min(im.size)
    if corto < LADO_MINIMO and not f.get("salta_minimo"):
        fuera.append((f["cod"], f["arch"], f"lado corto {corto} px < {LADO_MINIMO}")); continue
    if f["virar"]:
        im = ajustar(im)
    ANCHO, ALTO, prop = lienzo(f.get("marco", "portada"))
    if f["modo"] == "recorte":
        out = cubrir(im, f.get("zoom", 1.0), f["fx"], f["fy"], ANCHO, ALTO)
        detalle = f"zoom {f.get('zoom', 1.0):.2f}  {ANCHO}x{ALTO} ({prop})"
    else:
        out, escala, tam = completa(im, f["fx"], f["fy"], f.get("max_ampliacion", 1.0), ANCHO, ALTO)
        detalle = (f"x{escala:.2f} → {tam[0]}x{tam[1]} de {ANCHO}x{ALTO} ({prop})"
                   + ("  ⚠ salta el mínimo" if f.get("salta_minimo") else ""))
    ruta_out = os.path.join(DST, f["cod"].lower() + ".webp")
    tope = TOPE_KB.get(f.get("marco", "portada"), TOPE_KB_POR_DEFECTO)
    calidad = CALIDAD
    while True:
        out.save(ruta_out, "WEBP", quality=calidad, method=6)
        kb = os.path.getsize(ruta_out) / 1024
        if kb <= tope or calidad <= CALIDAD_MINIMA:
            break
        calidad -= 5
    if calidad < CALIDAD:
        detalle += "  · %d KB a calidad %d (tope %d)" % (round(kb), calidad, tope)
    else:
        detalle += "  · %d KB" % round(kb)
    if kb > TOPE_KB_DURO:
        detalle += "  ⚠ PASA DEL TOPE DURO de %d KB" % TOPE_KB_DURO
    dentro.append((f["cod"], f["arch"], f["modo"], detalle, f["nota"]))

print("EN ROTACIÓN")
for cod, arch, modo, detalle, nota in dentro:
    print(f"  {cod}  {arch:<30} {modo:<9} {detalle}\n           · {nota}")
if fuera:
    print("\nFUERA")
    for cod, arch, por in fuera:
        print(f"  {cod}  {arch:<30} {por}")
print(f"\n{len(dentro)} fotos preparadas")
