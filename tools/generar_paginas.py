#!/usr/bin/env python3
"""Genera la web multipágina de BRAVA a partir de la página única.

Por qué existe: las 24 fichas de protocolo salen de
assets/docs/02-CATALOGO.json, no se escriben a mano. Si el catálogo cambia,
se vuelve a ejecutar esto y las páginas quedan al día. Lo mismo con el menú
y el pie, que se componen una vez y se reparten idénticos.

    python3 tools/generar_paginas.py

Las rutas internas son absolutas desde la raíz (/assets/…, /fiber/…) para
que el mismo marcado sirva a cualquier profundidad de carpeta.
"""
import json, os, re, shutil, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTE = os.path.join(RAIZ, "_plantilla", "pagina-unica.html")
CATALOGO = os.path.join(RAIZ, "assets", "docs", "02-CATALOGO.json")
# La marca que rompe la caché del navegador. ANTES era un texto fijo escrito a
# mano, y ahí estaba el problema: styles.css y main.js cambiaban, la marca no, y
# cualquier navegador que ya los tuviera guardados seguía sirviendo los viejos.
# O sea que los cambios se publicaban pero no se veían.
# Ahora sale del contenido de cada archivo: si el archivo cambia, la marca
# cambia sola, y si no cambia, se respeta la caché.
def sello(ruta):
    import hashlib
    try:
        return hashlib.sha1(open(ruta, "rb").read()).hexdigest()[:10]
    except IOError:
        return "0"


VERSION_CSS = sello(os.path.join(RAIZ, "styles.css"))
VERSION_JS = sello(os.path.join(RAIZ, "main.js"))

# La dirección del estudio y su enlace a Google Maps. Va como constante y se
# sustituye al final: la URL lleva %23 y %20, y las plantillas de este archivo
# se arman con el operador %, así que incrustarla dentro reventaría el formateo.
MAPS = "https://www.google.com/maps/search/?api=1&amp;query=Calle%20134A%20%23%2055A-20%2C%20local%205%2C%20Colina%20Campestre%2C%20Bogot%C3%A1%2C%20Colombia"

# ══════════════════════════════════════════════════════════════════════════
#  LAS CINCO CATEGORÍAS
#  Los servicios se agrupan por lo que busca la clienta, no por las familias
#  internas de la marca. Cada categoría se corresponde exactamente con un grupo
#  del catálogo —mismo contenido y mismo orden—, así que los 24 protocolos
#  siguen siendo los mismos y no queda ninguno suelto.
#  BRAVA FIBER y BRAVA SCALP siguen existiendo como concepto de marca dentro de
#  las páginas (campo "marca"), pero ya no son la forma de navegar.
# ══════════════════════════════════════════════════════════════════════════
CATEGORIAS = [
    dict(slug="alisados", familia="fiber-alineacion", marca="BRAVA FIBER",
         nombre="Alisados y alineación", corto="Alisados y alineación",
         titular="Alisados y alineación.<br><em>Sin plastificar la fibra.</em>",
         bajada="Alisados y alineación molecular sin formol, en Colina Campestre, "
                "Bogotá. Seis sistemas distintos: cuál te toca depende de la condición "
                "de tu fibra, no del precio.",
         titulo="Alisados sin formol en Bogotá · BRAVA Hair Lab",
         desc="Los 6 protocolos de alisado y alineación molecular de BRAVA Hair Lab, "
              "en Bogotá. Alineación real sin sacrificar la fuerza de la fibra.",
         ratio="4:5"),
    dict(slug="tratamientos", familia="fiber-ritual", marca="BRAVA FIBER",
         nombre="Tratamientos y reparación", corto="Tratamientos y reparación",
         titular="Tratamientos y reparación.<br><em>De medios a puntas.</em>",
         bajada="Tratamientos de reparación e hidratación de la fibra, en Colina "
                "Campestre, Bogotá. Nueve rituales para devolverle a la hebra lo que "
                "el desgaste le quitó.",
         titulo="Tratamientos capilares en Bogotá · BRAVA Hair Lab",
         desc="Los 9 rituales de tratamiento y reparación capilar de BRAVA Hair Lab, "
              "en Bogotá. Hidratación, nutrición, brillo y fuerza para la fibra.",
         ratio="1:1"),
    dict(slug="head-spa", familia="scalp-experiencia", marca="BRAVA SCALP",
         nombre="Spa capilar", corto="Spa capilar",
         titular="Spa capilar.<br><em>Cuidado desde la raíz.</em>",
         bajada="Spa capilar y cuidado del cuero cabelludo, en Colina Campestre, Bogotá. "
                "Dos experiencias de noventa minutos en el Piso 2, cosméticas y no "
                "médicas.",
         titulo="Spa capilar en Bogotá · BRAVA Hair Lab",
         desc="Las 2 experiencias de spa capilar de BRAVA Hair Lab, en Bogotá. "
              "Cuidado cosmético del cuero cabelludo y desconexión profunda.",
         ratio="3:2"),
    dict(slug="caida", familia="scalp-rootlounge", marca="BRAVA SCALP",
         nombre="Caída y fortalecimiento", corto="Caída y fortalecimiento",
         titular="Caída y fortalecimiento.<br><em>Desde la raíz.</em>",
         bajada="La salud, la fuerza y la calidad del cabello nacen en el folículo. "
                "Bioestimulación cosmética no invasiva para su entorno.",
         titulo="Caída del cabello en Bogotá · BRAVA Hair Lab",
         desc="Los 3 protocolos de BRAVA Hair Lab para caída y fortalecimiento, en "
              "Bogotá. Bioestimulación cosmética del cuero cabelludo, no médica.",
         ratio="4:5"),
    dict(slug="complementarios", familia="addon", marca="",
         nombre="Servicios complementarios", corto="Complementarios",
         titular="Servicios complementarios.<br><em>Suman a tu protocolo.</em>",
         bajada="Se añaden a cualquier protocolo para elevar tu experiencia y "
                "personalizar aún más tu resultado.",
         titulo="Servicios complementarios · BRAVA Hair Lab",
         desc="Los 4 servicios complementarios de BRAVA Hair Lab, en Bogotá. "
              "Se suman a cualquier protocolo para personalizar el resultado.",
         ratio="1:1"),
]
POR_FAMILIA = {c["familia"]: c for c in CATEGORIAS}
RUTA_CAT = {c["slug"]: "/servicios/%s/" % c["slug"] for c in CATEGORIAS}

# Tres protocolos se escriben en la dirección distinto de como se llaman en el
# JSON. El id del catálogo sigue mandando para identificarlos; esto solo cambia
# el trozo de la URL. Si algún día hay que volver atrás, se borra la entrada.
SLUG = {
    "reforce": "re-force",
    "reconnect": "re-connect",
    "split-ends": "puntas",
}


def slug(p):
    return SLUG.get(p["id"], p["id"])


def categoria(p):
    return POR_FAMILIA[p["familia"]]


def ruta_protocolo(p):
    return "/servicios/%s/%s/" % (categoria(p)["slug"], slug(p))


# ─────────────────────────── troceado de la fuente ───────────────────────────
def trozos(html):
    """Devuelve las secciones de la página única, por su id."""
    out = {}
    for m in re.finditer(r'<section class="[^"]*" id="([a-z-]+)">', html):
        ini = m.start()
        fin = html.index("</section>", ini) + len("</section>")
        out[m.group(1)] = html[ini:fin]
    # piezas que no son <section>
    for clave, (a, b) in {
        "marquesina": ('<!-- Marquesina con los nombres', '</div>\n'),
        "pie": ('<footer class="pie">', '</footer>'),
        "wa": ('<a class="wa-flotante"', '</a>\n'),
        "contexto": ('<div class="contexto-fuente"', '\n  </div>'),
    }.items():
        i = html.find(a)
        if i == -1:
            continue
        j = html.index(b, i) + len(b)
        out[clave] = html[i:j].rstrip()
    return out


# ══════════════════════════════════════════════════════════════════════════
#  RUTAS RELATIVAS
#  Nada apunta a "/": el sitio tiene que funcionar igual en la raíz de un
#  dominio que dentro de una subcarpeta (GitHub Pages lo publica en
#  /brava-hair-lab/, y ahí "/styles.css" se sale del sitio y da 404).
#  Todo se escribe con el marcador @@BASE@@ delante, y escribe() lo sustituye
#  por los "../" que haga falta según lo hondo que esté cada página.
# ══════════════════════════════════════════════════════════════════════════
def enlace(r):
    """Una ruta del sitio ("/servicios/alisados/") a href relativo."""
    return "@@BASE@@" + r.lstrip("/")


def relativas(t):
    """assets/… → @@BASE@@assets/…  ·  styles.css → @@BASE@@styles.css"""
    t = re.sub(r'(href|src|data-archivo|data-video)="(?!https?:|/|#|mailto:|@@)([^"]+)"',
               lambda m: '%s="@@BASE@@%s"' % (m.group(1), m.group(2)), t)
    return t


# ─────────────────────────────── menú y pie ───────────────────────────────
# El resto del menú, al lado de "Servicios". No hay pestaña de Sedes: BRAVA
# tiene una sola sede, y está en Contacto.
ENLACES = [
    # "Inicio" va primero y explícito: el logotipo también lleva a la portada,
    # pero mucha gente no lo da por hecho.
    ("/", "Inicio", "Inicio"),
    ("/el-lab/", "El Lab", "El Lab por dentro"),
    ("/resultados/", "Resultados", "Resultados del Lab"),
    ("/blog/", "Blog", "Blog"),
    ("/contacto/", "Contacto", "Contacto"),
]


# El catálogo, para que el menú pueda listar los protocolos sin que haya que
# ir pasándolo por cada función. Lo rellena main().
PROTOS = []


def columnas_servicios(protos):
    """Las cinco categorías con sus protocolos dentro. El mismo contenido sirve
    para el panel de escritorio y para el acordeón de celular."""
    cols = []
    for c in CATEGORIAS:
        ps = [p for p in protos if p["familia"] == c["familia"]]
        items = "\n".join(
            '            <li><a href="%s">%s</a></li>' % (enlace(ruta_protocolo(p)), esc(p["nombre"]))
            for p in ps)
        cols.append((c, len(ps), items))
    return cols


def nav(actual):
    def cls(u):
        return ' aria-current="page"' if u == actual else ""

    cols = columnas_servicios(PROTOS)
    # ¿Estamos dentro de servicios? Entonces la entrada del menú va marcada.
    en_servicios = actual.startswith("/servicios/")

    # El panel enseña solo las cinco categorías con su número. Listar dentro los
    # 24 protocolos lo convertía en una pantalla entera; para verlos está la
    # página de cada categoría.
    panel = "\n".join(
        '            <a class="nav-cat-t" href="%s">%s<span>%d</span></a>'
        % (enlace(RUTA_CAT[c["slug"]]), esc(c["nombre"]), n)
        for c, n, _ in cols)

    acordeon = "\n".join(
        '''    <details class="menu-cat"%s>
      <summary>%s<span>%d</span></summary>
      <a class="menu-cat-todo" href="%s">Ver toda la categoría</a>
      <ul>
%s
      </ul>
    </details>''' % (" open" if actual == RUTA_CAT[c["slug"]] else "",
                     esc(c["nombre"]), n, enlace(RUTA_CAT[c["slug"]]), items)
        for c, n, items in cols)

    # "Inicio" se imprime aparte porque va DELANTE del desplegable de Servicios,
    # que está escrito a mano en la plantilla del menú.
    links_inicio = '      <a href="@@BASE@@"%s>Inicio</a>' % cls("/")
    links = "\n".join(
        '      <a href="%s"%s>%s</a>' % (enlace(u), cls(u), corto)
        for u, corto, _ in ENLACES if u != "/")
    # En celular "Inicio" va delante del bloque de Servicios, para que sea la
    # primera entrada igual que en escritorio; el resto va detrás.
    movil_inicio = '    <a href="@@BASE@@"%s>Inicio</a>' % cls("/")
    movil = "\n".join(
        '    <a href="%s"%s>%s</a>' % (enlace(u), cls(u), largo)
        for u, _, largo in ENLACES if u != "/")

    return '''<header class="nav" data-nav>
  <div class="nav-in">
    <a class="logo" href="@@BASE@@" aria-label="BRAVA Hair Lab, inicio">
      <img src="@@BASE@@assets/img/marca/isotipo.webp" alt="" width="320" height="275">
      <span class="logo-txt">BRAVA<em>Hair Lab</em></span>
    </a>
    <nav class="nav-links" aria-label="Principal">
%s
      <!-- Servicios abre el panel de las cinco categorías. Es un botón, no un
           enlace, porque su función es desplegar; a la página de servicios se
           llega desde el propio panel. -->
      <div class="nav-desp" data-desplegable>
        <button class="nav-desp-b%s" type="button" data-desp-boton
                aria-expanded="false" aria-controls="panel-servicios">Servicios</button>
        <div class="nav-desp-panel" id="panel-servicios" data-desp-panel hidden>
          <div class="nav-desp-in">
%s
            <a class="nav-desp-todo" href="@@BASE@@servicios/">Ver todos los servicios</a>
          </div>
        </div>
      </div>
%s
    </nav>
    <button class="btn btn-sm nav-cta" type="button" data-abre-capa>Encontrar mi protocolo</button>
    <button class="burger" type="button" data-burger aria-label="Abrir menú" aria-expanded="false" aria-controls="menu-movil">
      <span></span><span></span>
    </button>
  </div>
</header>

<div class="menu" id="menu-movil" data-menu hidden>
  <nav aria-label="Menú móvil">
%s
    <p class="menu-et">Servicios</p>
%s
    <a class="menu-cat-todo menu-cat-todos" href="@@BASE@@servicios/">Ver todos los servicios</a>
%s
  </nav>
  <button class="btn menu-cta" type="button" data-abre-capa>Encontrar mi protocolo</button>
  <p class="menu-pie"><a href="@@MAPS@@" target="_blank" rel="noopener">Calle 134A # 55A-20, local 5<br>Colina Campestre · Bogotá</a></p>
</div>''' % (links_inicio, " es-actual" if en_servicios else "", panel, links,
       movil_inicio, acordeon, movil)


def pie(pie_fuente):
    """El pie de la página única, con su navegación apuntando a las rutas nuevas."""
    # El pie repite la navegación, con las cinco categorías desplegadas: es el
    # único sitio donde se ven todas sin desplegar nada.
    cats = [(RUTA_CAT[c["slug"]], c["nombre"]) for c in CATEGORIAS]
    nuevo = "\n".join('        <a href="%s">%s</a>' % (enlace(u), largo)
                      for u, largo in cats + [(u, l) for u, _, l in ENLACES])
    return re.sub(r'(<nav class="pie-nav" aria-label="Pie">\n)(.*?)(\n *</nav>)',
                  lambda m: m.group(1) + nuevo + m.group(3), pie_fuente, flags=re.S)


# ─────────────────────────────── el armazón ───────────────────────────────
def titular(cuerpo):
    """Cada página necesita su propio h1. Los trozos heredados de la versión de
    una sola página llevan h2, porque allí el h1 era el del hero. Aquí se
    asciende el primer titular de la página a h1, elemento entero de apertura a
    cierre: el diseño no cambia y la jerarquía queda bien."""
    if "<h1" in cuerpo:
        return cuerpo
    return re.sub(r'<h2(\s+class="titulo[^>]*)>([\s\S]*?)</h2>',
                  r'<h1\1>\2</h1>', cuerpo, count=1)


def pagina(titulo, descripcion, cuerpo, actual="", precarga=None):
    cuerpo = titular(cuerpo)
    pre = ('<link rel="preload" as="image" href="%s" type="image/webp" fetchpriority="high">\n'
           % precarga) if precarga else ""
    return '''<!DOCTYPE html>
<html lang="es-CO" data-base="@@BASE@@">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%s</title>
<meta name="description" content="%s">
<meta name="theme-color" content="#1D160E">
<meta name="robots" content="noindex, nofollow">

<link rel="icon" href="@@BASE@@assets/img/marca/favicon.ico" sizes="any">
<link rel="icon" href="@@BASE@@assets/img/marca/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="@@BASE@@assets/img/marca/apple-touch-icon.png">

%s<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<link rel="stylesheet" href="@@BASE@@styles.css?v=%s">

<!-- Marca "hay JS". Todo lo que el CSS esconde para animarlo depende de esta
     clase: sin ella no se esconde nada y la página se lee entera. -->
<script>document.documentElement.className += " js";</script>
</head>
<body>

<a class="skip" href="#contenido">Saltar al contenido</a>

%s

<main id="contenido">

%s

</main>

%s

%s

<!-- La capa del buscador de protocolo, en todas las páginas. -->
<div class="capa" id="capa-buscador" data-capa hidden role="dialog" aria-modal="true" aria-label="Buscador de protocolo"></div>

<script defer src="@@BASE@@lib/gsap.min.js"></script>
<script defer src="@@BASE@@lib/ScrollTrigger.min.js"></script>
<script defer src="@@BASE@@main.js?v=%s"></script>
</body>
</html>
''' % (esc(titulo), esc(descripcion), pre, VERSION_CSS, nav(actual), cuerpo,
       T["pie_nuevo"], T["wa"], VERSION_JS)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def escribe(ruta, html):
    destino = os.path.join(RAIZ, ruta.strip("/"), "index.html") if ruta != "/" \
        else os.path.join(RAIZ, "index.html")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    # Los huecos opcionales del catálogo (incluye, avisoEspecial) dejan líneas
    # vacías al no existir: se colapsan para que el HTML salga limpio.
    html = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", html)
    html = html.replace("@@MAPS@@", MAPS)
    # Cuántos "../" hay que subir desde este index.html hasta la raíz del sitio.
    # "/" → 0 · "/contacto/" → 1 · "/servicios/alisados/silkfusion/" → 3.
    hondura = len([x for x in ruta.strip("/").split("/") if x])
    html = html.replace("@@BASE@@", "../" * hondura)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(html)
    CREADAS.append((ruta, os.path.relpath(destino, RAIZ)))


CREADAS = []


# ──────────────────────────── contenidos nuevos ────────────────────────────
def banda_reserva(texto):
    """Las dos vías de reserva, en todas las páginas que no son la de contacto.
    Aquí viven los dos botones que el navegador arma en main.js (data-agenda y
    data-wa-simple); el href escrito es el de respaldo por si el JS no corre."""
    return '''<!-- ══════════════════════════ RESERVA ══════════════════════════ -->
<section class="seccion banda-reserva oscuro">
  <span class="trama trama-fondo" aria-hidden="true"></span>
  <div class="wrap">
    <div class="reserva-in">
      <div>
        <p class="eyebrow reveal">Tu cita</p>
        <h2 class="reserva-t">%s</h2>
      </div>
      <div class="hero-ctas reveal">
        <a class="btn btn-acento" href="https://bravahairlab.site.agendapro.com/co" data-agenda>Agendar en línea</a>
        <a class="btn btn-wa" href="https://wa.me/573205830720" data-wa-simple>Agendar por WhatsApp</a>
        <a class="btn btn-claro" href="@@BASE@@contacto/">Cómo llegar</a>
      </div>
    </div>
  </div>
</section>
''' % esc(texto)


# Los tres bloques de familia de la portada. El texto sale de
# assets/docs/01-CONTENIDO.md (§6 FIBER, §9 SCALP, §12 Add-Ons), recortado a las
# frases que aguantan solas; no se reescribe nada aquí.
# Los bloques de categoría de la portada. El texto sale del catálogo y de
# assets/docs/01-CONTENIDO.md; no se reescribe nada aquí.
PORTADA = {
    "alisados": dict(sobre="Lo que más nos piden", cod="FOTO-21",
                     texto="No plastificamos tu cabello: lo alineamos desde su salud "
                           "molecular. Seis sistemas, y la diferencia entre ellos no es "
                           "el precio: es tu cabello.",
                     foto="Alisados: plano ancho del Piso 1 en uso, trabajo sobre la hebra."),
    "tratamientos": dict(sobre="De medios a puntas", cod="FOTO-22",
                         texto="La belleza y la salud visible de tu cabello se defienden "
                               "de medios a puntas. En BRAVA nos especializamos en la "
                               "arquitectura, nutrición y preservación de la fibra.",
                         foto="Tratamientos: plano ancho de un ritual en ejecución."),
    "head-spa": dict(sobre="Cuidado desde la raíz", cod="FOTO-23",
                     texto="Un cabello extraordinario comienza desde la raíz. Experiencias "
                           "largas de cuidado del cuero cabelludo, en el silencio del Piso 2.",
                     foto="Spa capilar: plano ancho del Piso 2, cabina privada, luz tenue."),
    "caida": dict(sobre="Desde el folículo", cod="FOTO-24",
                  texto="La salud, la fuerza y la calidad del cabello nacen en el folículo, "
                        "y es allí donde centramos nuestra innovación. Cuidado cosmético, "
                        "nunca médico.",
                  foto="Caída: plano ancho de una sesión de bioestimulación."),
    "complementarios": dict(sobre="Suman a tu protocolo", cod="FOTO-25",
                            texto="Servicios complementarios para elevar tu experiencia y "
                                  "personalizar aún más tu resultado.",
                            foto="Complementarios: plano ancho de un add-on en ejecución."),
}


def banda_familias(protos):
    """Lo primero tras la banda de sellos: las cinco categorías, que se relevan
    al bajar, una por pantalla.

    El movimiento es el mismo que el cruce de pisos: position:sticky para que el
    scroll siga siendo el del navegador —no se bloquea ni se secuestra— y GSAP
    solo encima, enganchado al scroll. En celular no hay relevo.

    Los huecos FOTO-21 a FOTO-25 son de banda ancha (3:2) y están vacíos: hasta
    que lleguen las fotos, el marco enseña la trama de la marca."""
    bloques = []
    for i, c in enumerate(CATEGORIAS, 1):
        d = PORTADA[c["slug"]]
        n = len([p for p in protos if p["familia"] == c["familia"]])
        unidad = "servicios" if c["slug"] == "complementarios" else "protocolos"
        bloques.append(
            '''      <article class="fam-bloque reveal">
        <figure class="fam-bloque-fig" data-foto="%(cod)s" data-ratio="3:2"
                data-archivo="@@BASE@@assets/img/%(arch)s.webp" data-alt="%(foto)s">
          <span class="trama" aria-hidden="true"></span><span class="foto-tag">%(cod)s</span>
        </figure>
        <div class="fam-bloque-txt">
          <p class="fam-bloque-et">%(orden)02d · %(sobre)s</p>
          <h3 class="fam-bloque-t">%(nombre)s</h3>
          <p class="parrafo">%(texto)s</p>
          <p class="fam-bloque-n"><strong>%(n)d</strong> %(unidad)s</p>
          <a class="btn btn-acento" href="%(ruta)s">Ver %(nombre)s</a>
        </div>
      </article>''' % dict(d, arch=d["cod"].lower(), foto=esc(d["foto"]), orden=i,
                            nombre=esc(c["nombre"]), n=n, unidad=unidad,
                            ruta=enlace(RUTA_CAT[c["slug"]])))

    return '''<!-- ══════════════════════════ LAS CINCO CATEGORÍAS ══════════════════════════ -->
<section class="seccion familias" id="catalogo">
  <div class="wrap">
    <header class="seccion-cab">
      <p class="eyebrow reveal">Servicios</p>
      <h2 class="titulo titulo-c" data-split="lines">Alisados, tratamientos y head spa.<br><em>Veinticuatro protocolos.</em></h2>
      <p class="parrafo centro reveal">Agrupados por lo que vienes a resolver. Entra en la categoría que te interese y ahí están sus protocolos, uno a uno.</p>
    </header>

    <div class="fam-bloques" data-familias>
%s

      <!-- Recorrido para que el último bloque llegue a su posición fija y se
           quede ahí. Tiene que ser un elemento de verdad: un margen o un
           padding no le dan recorrido al sticky. -->
      <span class="fam-cola" aria-hidden="true"></span>
    </div>

    <p class="familias-todos reveal"><a href="@@BASE@@servicios/">Ver todos los servicios →</a></p>
  </div>
</section>
''' % "\n\n".join(bloques)


def fila_protocolo(p):
    return ('        <li><a class="prot-fila" href="%s">'
            '<span class="prot-nombre">%s</span>'
            '<span class="prot-sub">%s</span>'
            '<span class="prot-mas">Ver el protocolo</span></a></li>'
            % (enlace(ruta_protocolo(p)), esc(p["nombre"]), esc(p.get("subtitulo") or "")))


def lista_protocolos(c, protos):
    """La lista de una categoría, partida por una llamada a agendar.

    La llamada va hacia la mitad, no solo al final: en las listas largas la de
    abajo queda muy lejos. Usa los colores de esta zona de la página —fondo
    claro, botón camel— y no la tarjeta café oscuro del cierre."""
    ps = [p for p in protos if p["familia"] == c["familia"]]
    return "\n".join(fila_protocolo(p) for p in ps)


def llamada_agendar():
    """La llamada a agendar de las páginas de servicio. Va ANTES del titular
    del listado, no dentro: metida en mitad de la lista partía la información.
    Usa los colores de esta zona, no la tarjeta café del cierre."""
    return '''    <div class="prot-llamada">
      <p>¿Dudas de cuál te toca? Lo vemos en la valoración, sin compromiso.</p>
      <span class="prot-llamada-btns">
        <a class="btn btn-acento btn-sm" href="https://bravahairlab.site.agendapro.com/co" data-agenda>Agendar en línea</a>
        <a class="btn btn-ghost btn-sm" href="https://wa.me/573205830720" data-wa-simple>Escribir por WhatsApp</a>
      </span>
    </div>'''


def pagina_categoria(c, protos, contexto):
    ps = [p for p in protos if p["familia"] == c["familia"]]
    # BRAVA FIBER y BRAVA SCALP siguen vivos como concepto de marca: aquí
    # aparecen como antetítulo, no como forma de navegar.
    et = c["marca"] or "El catálogo"
    cuerpo = '''<!-- ══════════════════════════ CATEGORÍA ══════════════════════════ -->
<section class="seccion fam-cab-pag oscuro" id="categoria">
  <span class="trama trama-fondo" aria-hidden="true"></span>
  <div class="wrap">
    <nav class="migas migas-o" aria-label="Dónde estás">
      <a href="@@BASE@@">Inicio</a><span aria-hidden="true">·</span>
      <a href="@@BASE@@servicios/">Servicios</a><span aria-hidden="true">·</span>
      <span aria-current="page">%s</span>
    </nav>
    <header class="seccion-cab">
      <p class="eyebrow reveal">%s</p>
      <h2 class="titulo titulo-c" data-split="lines">%s</h2>
      <p class="parrafo centro reveal">%s</p>
    </header>
  </div>
</section>

<!-- El contexto del grupo y el listado van en UNA sola sección. Separados eran
     dos, y cada una cargaba sus 72px arriba y abajo: se acumulaban 144 más el
     margen del encabezado, y en complementarios la primera sección existía
     solo para un título y una frase. -->
<section class="seccion fam-listado" id="protocolos">
  <div class="wrap">
    <div class="fam-contexto">
%s
    </div>
%s
    <header class="seccion-cab">
      <h2 class="titulo titulo-c" data-split="lines">Los <em>%d protocolos.</em></h2>
    </header>
    <ul class="prot-lista">
%s
    </ul>
  </div>
</section>

%s
''' % (esc(c["nombre"]), esc(et), c["titular"], esc(c["bajada"]), contexto,
       llamada_agendar(), len(ps), lista_protocolos(c, protos),
       banda_reserva("¿No sabes cuál es el tuyo? Lo vemos en la valoración."))
    return pagina(c["titulo"], c["desc"], cuerpo, RUTA_CAT[c["slug"]])


# Los dos abordajes de marca, que en la portada llevan aquí por anclaje.
# Complementarios queda fuera a propósito: no es ni fibra ni cuero cabelludo, y
# por eso va aparte y sin anclaje.
ABORDAJES = [
    dict(ancla="fiber", marca="BRAVA FIBER", titulo="La fibra capilar",
         bajada="De medios a puntas: preservar, reparar y elevar la calidad "
                "cosmética de la hebra.",
         slugs=["alisados", "tratamientos"]),
    dict(ancla="scalp", marca="BRAVA SCALP", titulo="El cuero cabelludo",
         bajada="La raíz y el entorno donde nace el cabello. Cuidado cosmético "
                "avanzado, nunca médico.",
         slugs=["head-spa", "caida"]),
]


def pagina_servicios(protos):
    """El índice de las cinco categorías, agrupadas por los dos abordajes de
    marca. Es adonde llevan "Ver todos los servicios" del menú y del pie, y los
    dos botones de "Dos abordajes" de la portada, cada uno a su anclaje."""
    por_slug = {c["slug"]: c for c in CATEGORIAS}
    n = 0

    def fila(c):
        nonlocal n
        n += 1
        ps = [p for p in protos if p["familia"] == c["familia"]]
        nombres = " · ".join(esc(p["nombre"]) for p in ps)
        return ('''        <a class="serv-fila" href="%s">
          <span class="serv-n">%02d</span>
          <span class="serv-cuerpo">
            <span class="serv-t">%s<em>%d</em></span>
            <span class="serv-x">%s</span>
          </span>
          <span class="serv-mas">Ver la categoría</span>
        </a>''' % (enlace(RUTA_CAT[c["slug"]]), n, esc(c["nombre"]), len(ps), nombres))

    grupos = []
    for a in ABORDAJES:
        cats = [por_slug[sl] for sl in a["slugs"]]
        total = sum(len([p for p in protos if p["familia"] == c["familia"]]) for c in cats)
        grupos.append(
            '''    <section class="serv-grupo" id="%s" aria-labelledby="t-%s">
      <header class="serv-grupo-cab">
        <p class="serv-grupo-et">%s</p>
        <h2 class="serv-grupo-t" id="t-%s">%s<span>%d protocolos</span></h2>
        <p class="parrafo">%s</p>
      </header>
      <div class="serv-lista">
%s
      </div>
    </section>''' % (a["ancla"], a["ancla"], esc(a["marca"]), a["ancla"],
                     esc(a["titulo"]), total, esc(a["bajada"]),
                     "\n".join(fila(c) for c in cats)))

    # El quinto grupo: los complementarios, aparte y sin anclaje.
    suelto = por_slug["complementarios"]
    ns = len([p for p in protos if p["familia"] == suelto["familia"]])
    grupos.append(
        '''    <section class="serv-grupo serv-grupo-aparte" aria-labelledby="t-aparte">
      <header class="serv-grupo-cab">
        <p class="serv-grupo-et">Y además</p>
        <h2 class="serv-grupo-t" id="t-aparte">Servicios complementarios<span>%d servicios</span></h2>
        <p class="parrafo">No son ni fibra ni cuero cabelludo: se suman a cualquier protocolo para personalizar tu resultado.</p>
      </header>
      <div class="serv-lista">
%s
      </div>
    </section>''' % (ns, fila(suelto)))

    cuerpo = '''<!-- ══════════════════════════ SERVICIOS ══════════════════════════ -->
<section class="seccion servicios" id="servicios">
  <div class="wrap">
    <header class="seccion-cab">
      <p class="eyebrow reveal">Servicios</p>
      <h1 class="titulo titulo-c" data-split="lines">Veinticuatro protocolos.<br><em>Cinco categorías.</em></h1>
      <p class="parrafo centro reveal">Agrupados por lo que vienes a resolver. Entra en la categoría que te interese y ahí están sus protocolos, uno a uno.</p>
    </header>

%s
  </div>
</section>

%s
''' % ("\n\n".join(grupos),
       banda_reserva("¿No sabes cuál es el tuyo? Lo vemos en la valoración."))
    return pagina("Servicios capilares en Bogotá · BRAVA Hair Lab",
                  "Los 24 protocolos de BRAVA Hair Lab en Bogotá, agrupados por fibra "
                  "capilar y cuero cabelludo, más los servicios complementarios.",
                  cuerpo, "/servicios/")


# ── /resultados/ ────────────────────────────────────────────────────────────
# Ocho tarjetas con los huecos que antes ocupaba la galería de la portada:
# FOTO-G01 a FOTO-G08. No se inventan códigos nuevos, esta página es su sitio.
# El pie tiene dos líneas: el protocolo, que sí es un dato real del catálogo, y
# qué se hizo, que va marcado como pendiente porque contar el resultado de una
# clienta concreta sin tener el caso delante sería inventárselo.
RESULTADOS = [
    dict(cod="FOTO-G01", protocolo="SilkFusion",        video=False),
    dict(cod="FOTO-G02", protocolo="Velvet",            video=True),
    dict(cod="FOTO-G03", protocolo="Ultra Resolute",    video=False),
    dict(cod="FOTO-G04", protocolo="Crystal",           video=False),
    dict(cod="FOTO-G05", protocolo="(Re)-Connect Head Spa", video=True),
    dict(cod="FOTO-G06", protocolo="Bio-Cellular",      video=False),
    dict(cod="FOTO-G07", protocolo="Genesis",           video=True),
    dict(cod="FOTO-G08", protocolo="Sleek Control",     video=False),
]


def pagina_resultados():
    tarjetas = []
    for r in RESULTADOS:
        arch = r["cod"].lower()
        vid = (' data-video="@@BASE@@assets/video/reel-%s.mp4"' % arch[5:]) if r["video"] else ""
        marca = '<span class="res-play" aria-hidden="true"></span>' if r["video"] else ""
        tarjetas.append(
            '''      <figure class="res-tarjeta%s">
        <div class="res-foto" data-foto="%s" data-ratio="4:5"
             data-archivo="@@BASE@@assets/img/%s.webp"%s
             data-alt="Resultado real del Lab: protocolo %s.">
          <span class="trama" aria-hidden="true"></span><span class="foto-tag">%s</span>%s
        </div>
        <figcaption class="res-pie">
          <span class="res-protocolo">%s</span>
          <span class="res-que"><span class="pendiente pendiente-mini">PENDIENTE: qué se hizo</span></span>
        </figcaption>
      </figure>''' % (" es-video" if r["video"] else "", r["cod"], arch, vid,
                      esc(r["protocolo"]), r["cod"], marca, esc(r["protocolo"])))

    cuerpo = '''<!-- ══════════════════════════ RESULTADOS ══════════════════════════ -->
<section class="seccion resultados-pag" id="resultados">
  <div class="wrap">
    <header class="seccion-cab">
      <p class="eyebrow reveal">Resultados</p>
      <h1 class="titulo titulo-c" data-split="lines">El trabajo del Lab,<br><em>caso a caso.</em></h1>
      <p class="parrafo centro reveal">Cabellos reales de clientas de BRAVA, en Colina Campestre, Bogotá. Cada caso indica el protocolo que se aplicó.</p>
    </header>

    <div class="res-rejilla" data-resultados>
%s
    </div>
  </div>
</section>

<!-- El vídeo se abre aquí, a pantalla completa, al pulsar una tarjeta de vídeo. -->
<div class="capa" id="capa-video" data-capa hidden role="dialog" aria-modal="true" aria-label="Vídeo del resultado"></div>

%s
''' % ("\n\n".join(tarjetas),
       banda_reserva("¿Quieres un resultado así? Empezamos por tu valoración."))
    return pagina("Resultados reales · BRAVA Hair Lab",
                  "Resultados reales de BRAVA Hair Lab en Colina Campestre, Bogotá: "
                  "alisados, tratamientos de fibra y head spa, caso a caso.",
                  cuerpo, "/resultados/")


# ══════════════════════════════════════════════════════════════════════════
#  EL BLOG
#  Cinco entradas. La regla de cada una: la respuesta va en el primer párrafo,
#  no al final. Terreno general y comprobable; ni un dato del Lab inventado ni
#  una promesa de resultado. Cada entrada enlaza a su página de servicio.
# ══════════════════════════════════════════════════════════════════════════
ENTRADAS = [
 dict(slug="alisado-sin-formol", seo="Alisado sin formol: cómo saber si lo tiene", foto="FOTO-B01",
   titulo="Alisado sin formol: cómo saber si el que te hacen lo tiene",
   resumen="Cómo reconocer el formol en un salón y qué preguntar antes de sentarte en la silla.",
   desc="Cómo reconocer si un alisado lleva formol: el olor, los ojos que lloran, el humo al planchar. Y qué preguntar antes de empezar.",
   servicios=[("/servicios/alisados/", "Ver los alisados de BRAVA")],
   cuerpo=[
    ("p", "Si durante el alisado te arden los ojos, sale humo blanco al pasar la plancha o en el salón abren ventanas y te pasan un tapabocas, lo más probable es que el producto lleve formol o algún ingrediente que lo libera al calentarse. Esas tres señales juntas son la pista más clara, y las puedes notar sin saber nada de química."),
    ("h2", "Qué es el formol y por qué se usaba"),
    ("p", "El formol —o formaldehído— es un conservante y fijador que se usa en muchas industrias. En peluquería llegó porque funciona: al aplicarlo y pasar la plancha a alta temperatura, sella la fibra en la forma lisa y el efecto dura meses. Era barato, rápido y muy efectivo."),
    ("destacado", "Que un alisado sea «sin formol» no lo convierte automáticamente en inofensivo. Lo importante es que te digan con qué te están trabajando."),
    ("p", "El problema es que al calentarse se evapora y se respira. La Agencia Internacional para la Investigación sobre el Cáncer, que depende de la Organización Mundial de la Salud, lo clasifica como cancerígeno para las personas, y es un irritante conocido de ojos, nariz y garganta. Por eso su uso en cosméticos está restringido en buena parte del mundo y en Colombia los productos cosméticos deben tener registro sanitario del INVIMA."),
    ("h2", "Cómo reconocerlo en un salón"),
    ("ul", ["Un olor penetrante y punzante, distinto del olor a producto de peluquería.",
            "Ojos que lloran o arden, tuyos o de quien te atiende.",
            "Humo blanco o vapor denso al pasar la plancha.",
            "Que te pidan ponerte tapabocas, o que abran ventanas y prendan ventiladores.",
            "Garganta raspada o tos durante o después del servicio."]),
    ("p", "Ninguna de estas señales prueba nada por sí sola: un salón puede ventilar por costumbre. Pero varias juntas sí dicen algo."),
    ("h2", "Qué preguntar antes de empezar"),
    ("ul", ["¿Qué producto van a usar y puedo ver el envase y la etiqueta?",
            "¿Tiene registro sanitario del INVIMA?",
            "¿Libera formaldehído al calentarse? Algunos ingredientes no se llaman formol pero lo liberan con el calor.",
            "Si estás embarazada o lactando, dilo antes y pregunta si ese producto es apto.",
            "¿Con qué temperatura se plancha y cuánto dura el servicio?"]),
    ("p", "Y una advertencia honesta: que un alisado sea «sin formol» no lo convierte automáticamente en inofensivo. Hay alternativas sin formol que también tienen sus cuidados. Lo importante es que te digan con qué te están trabajando y por qué."),
    ("aviso", "Esta entrada es informativa y no sustituye la valoración de un profesional. Si tienes una condición médica o dudas sobre un producto, consúltalo con tu médico."),
   ]),

 dict(slug="que-es-un-head-spa", seo="Qué es un head spa o spa capilar", foto="FOTO-B02",
   titulo="Qué es un head spa o spa capilar, y en qué se diferencia de un lavado",
   resumen="La diferencia está en el tiempo, el masaje y en dónde se pone el foco: el cuero cabelludo, no el largo.",
   desc="Qué es un head spa o spa capilar, de dónde viene y en qué se diferencia de un lavado de salón. Duración, masaje y foco en el cuero cabelludo.",
   servicios=[("/servicios/head-spa/", "Ver los head spa de BRAVA")],
   cuerpo=[
    ("p", "Un head spa —o spa capilar, que es el mismo servicio con nombre en español— es un tratamiento largo centrado en el cuero cabelludo, no en el largo del pelo. Un lavado de salón dura unos minutos y busca dejarte el pelo limpio; un head spa dura entre cuarenta y cinco y noventa minutos, incluye masaje y trabaja sobre la piel de la cabeza."),
    ("h2", "De dónde viene"),
    ("p", "La práctica se popularizó en Japón, donde el cuidado del cuero cabelludo es una categoría propia dentro de la peluquería, y de ahí salió el nombre «head spa». En los últimos años se extendió a salones de toda América Latina, a veces con el nombre traducido y a veces no."),
    ("destacado", "Un lavado atiende el largo y las puntas. Un spa capilar atiende la piel de donde nace el pelo."),
    ("h2", "En qué se diferencia de un lavado"),
    ("ul", ["<strong>El tiempo.</strong> Un lavado son minutos. Un head spa se mide en decenas de minutos, porque el producto necesita reposar y el masaje necesita ritmo.",
            "<strong>El masaje.</strong> No es el enjabonado rápido: es un trabajo manual sobre el cuero cabelludo, con presión y recorrido.",
            "<strong>El foco.</strong> Un lavado atiende el largo y las puntas. Un head spa atiende la piel de donde nace el pelo.",
            "<strong>El diagnóstico previo.</strong> Suele empezar mirando el estado del cuero cabelludo para decidir qué se aplica."]),
    ("h2", "Para quién tiene sentido"),
    ("p", "Suele buscarlo quien siente el cuero cabelludo graso o tenso, quien carga mucho estrés en la cabeza y el cuello, o quien simplemente quiere una hora de desconexión. También quien usa mucho producto de peinado y acumula residuo."),
    ("aviso", "Un head spa es un servicio cosmético y de bienestar, no un tratamiento médico. No diagnostica ni trata enfermedades del cuero cabelludo. Si tienes picor persistente, heridas, descamación fuerte o caída marcada, eso lo tiene que ver un dermatólogo."),
   ]),

 dict(slug="cada-cuanto-alisado", seo="Cada cuánto hacerse un alisado", foto="FOTO-B03",
   titulo="Cada cuánto puedes hacerte un alisado sin maltratar el pelo",
   resumen="No lo marca el calendario: lo marca la raíz nueva que te va creciendo.",
   desc="Cada cuánto repetir un alisado sin maltratar el pelo: lo marca la raíz nueva, no el calendario. Qué hacer entre una vez y la siguiente.",
   servicios=[("/servicios/alisados/", "Ver los alisados de BRAVA"),
              ("/servicios/tratamientos/", "Ver los tratamientos de fibra")],
   cuerpo=[
    ("p", "No lo marca el calendario, lo marca tu raíz. El pelo crece alrededor de un centímetro al mes, así que lo que define cuándo repetir no es «cada tantos meses», sino cuánta raíz nueva sin tratar tienes. Cuando llevas dos o tres centímetros de crecimiento —entre dos y tres meses para la mayoría— es cuando tiene sentido volver a mirarlo."),
    ("h2", "Por qué la raíz manda"),
    ("p", "Un alisado actúa sobre el pelo que toca. El pelo que ya salió tratado sigue tratado: no «se le va» el efecto de forma pareja, sino que va quedando atrás mientras la raíz empuja pelo nuevo con su forma original. Por eso a los dos meses se ve el contraste entre la raíz y el largo."),
    ("destacado", "No lo marca el calendario: lo marca cuánta raíz nueva sin tratar tienes."),
    ("h2", "El riesgo de volver a aplicar sobre pelo ya tratado"),
    ("p", "Si se aplica producto de nuevo sobre todo el largo, el pelo que ya estaba tratado recibe una segunda pasada que no necesitaba. Eso es lo que se llama sobreprocesar: la fibra acumula tratamiento y calor, y puede volverse quebradiza, perder elasticidad y romperse, sobre todo en las puntas."),
    ("p", "La forma de evitarlo es trabajar sobre todo la raíz nueva y dejar el largo con lo que necesite, que casi nunca es lo mismo. Eso exige mirar el pelo antes, no aplicar por rutina."),
    ("h2", "Qué hacer entre una vez y la siguiente"),
    ("ul", ["Espaciar el calor. La plancha y el secador a temperatura alta desgastan la fibra que ya pasó por un proceso.",
            "Usar protector térmico siempre que vayas a aplicar calor.",
            "Lavar con productos suaves y sin exceso de fricción.",
            "Tratamientos de hidratación y nutrición entre servicios, que es justo lo que sostiene la fibra mientras esperas.",
            "No encadenar procesos químicos sin dejar descansar el pelo entre uno y otro."]),
    ("aviso", "Los tiempos de esta entrada son orientativos. Cuánto crece tu pelo y cómo lo tolera depende de cada persona."),
   ]),

 dict(slug="caida-del-pelo-que-es-normal", seo="Caída del pelo: qué es normal", foto="FOTO-B04",
   titulo="Se te está cayendo el pelo: qué es normal y qué no",
   resumen="Perder entre 50 y 100 cabellos al día entra dentro de lo normal. Lo que importa es el patrón.",
   desc="Cuánta caída de pelo es normal y qué señales merecen atención. Causas frecuentes no médicas y cuándo consultar a un dermatólogo.",
   servicios=[("/servicios/caida/", "Ver los protocolos de caída y fortalecimiento")],
   cuerpo=[
    ("p", "Perder entre cincuenta y cien cabellos al día es normal: el pelo tiene un ciclo y siempre hay una parte que se está cayendo para dar paso a pelo nuevo. Ver pelos en el cepillo, en la almohada o en la ducha no significa por sí solo que tengas un problema. Lo que importa no es la cantidad suelta, sino el patrón."),
    ("h2", "Señales que sí merecen atención"),
    ("ul", ["Pérdida a mechones, no pelo suelto repartido.",
            "La coronilla que se ve más clara o el cuero cabelludo que empieza a transparentarse.",
            "Picor persistente, descamación fuerte, enrojecimiento o heridas.",
            "Entradas que avanzan rápido en pocas semanas o meses.",
            "Zonas sin pelo con bordes definidos."]),
    ("p", "Si te reconoces en alguna de estas, lo que toca no es un tratamiento cosmético: toca una consulta."),
    ("destacado", "Lo que importa no es la cantidad de pelo suelto, sino el patrón."),
    ("h2", "Causas frecuentes que no son médicas"),
    ("ul", ["<strong>Estrés.</strong> Un pico fuerte de estrés puede disparar una caída que aparece semanas después del episodio, no el mismo día.",
            "<strong>Posparto.</strong> Es muy común y suele ser pasajero: el embarazo retiene pelo que después se cae todo junto.",
            "<strong>Alimentación.</strong> Dietas muy restrictivas o carencias pueden reflejarse en el pelo.",
            "<strong>Peinados muy tensos.</strong> Colas, trenzas o extensiones que tiran de la raíz de forma sostenida pueden dañar el folículo con el tiempo."]),
    ("h2", "Cuándo ver a un dermatólogo"),
    ("p", "Siempre que la caída sea repentina, por zonas, acompañada de molestias en la piel, o simplemente cuando te preocupe y quieras una respuesta. Un dermatólogo o un tricólogo puede examinar el cuero cabelludo, pedir exámenes si hace falta y decirte qué está pasando. Ningún servicio de peluquería puede hacer eso."),
    ("aviso", "BRAVA es un estudio de cuidado capilar cosmético y preventivo. No diagnosticamos ni tratamos enfermedades, y no prometemos frenar la caída. Nuestros protocolos de esta categoría trabajan el entorno del cuero cabelludo desde lo cosmético. Si hay una causa médica detrás, el sitio correcto es la consulta."),
   ]),

 dict(slug="alisado-keratina-botox-capilar", seo="Alisado, keratina y botox capilar", foto="FOTO-B05",
   titulo="Alisado, keratina y botox capilar: en qué se diferencian",
   resumen="Uno cambia la forma del pelo. Los otros dos cambian cómo se ve y cómo se siente.",
   desc="Diferencias reales entre alisado, keratina y botox capilar: cuál cambia la forma del pelo, cuál solo su apariencia y cuánto dura cada uno.",
   servicios=[("/servicios/alisados/", "Ver los alisados de BRAVA"),
              ("/servicios/tratamientos/", "Ver los tratamientos de fibra")],
   cuerpo=[
    ("p", "La diferencia de fondo es una: el alisado cambia la forma del pelo; la keratina y el llamado botox capilar no. Estos dos rellenan y sellan la fibra, así que el pelo se ve más liso porque pesa más y tiene menos frizz, pero conserva su forma natural. En cuanto se va el producto, vuelve a ondularse."),
    ("h2", "El alisado"),
    ("p", "Trabaja sobre la estructura del pelo para relajar o eliminar la onda, y el efecto se mantiene en el pelo tratado hasta que crece raíz nueva. Es el único de los tres que transforma la forma, y por eso es el que más cuidado exige al elegirlo y al repetirlo."),
    ("destacado", "El alisado cambia la forma del pelo. La keratina y el botox capilar cambian cómo se ve."),
    ("h2", "La keratina"),
    ("p", "La keratina es la proteína de la que está hecho el pelo. Un tratamiento de keratina aporta proteína y sella la cutícula: deja el pelo más manejable, con brillo y menos frizz. No rompe ni reconstruye la forma; la disimula. Se va poco a poco, lavado a lavado."),
    ("h2", "El botox capilar"),
    ("p", "Aquí hay que aclarar algo: el botox capilar no tiene absolutamente nada que ver con la toxina botulínica ni con las inyecciones estéticas. Es un nombre comercial. Se trata de una mascarilla de alta concentración que rellena las zonas dañadas de la fibra con activos hidratantes y reparadores. El pelo queda más grueso al tacto y más liso a la vista, pero por relleno, no por transformación."),
    ("h2", "Cuánto dura cada uno"),
    ("ul", ["<strong>Alisado:</strong> meses, y lo que marca el final es el crecimiento de la raíz, no el desgaste.",
            "<strong>Keratina:</strong> de unas semanas a un par de meses, y se va de forma gradual con los lavados.",
            "<strong>Botox capilar:</strong> parecido a la keratina, también gradual."]),
    ("p", "Por eso no compiten entre sí: un alisado resuelve la forma y un tratamiento de fibra resuelve el estado. Muchas veces lo que hace falta no es alisar, sino reparar."),
    ("aviso", "Los nombres comerciales varían mucho entre salones y marcas. Antes de decidir, pregunta qué hace el producto concreto que te van a aplicar, no solo cómo se llama."),
   ]),
]


def ancla(t):
    """Un id legible a partir del título, para que el índice pueda enlazarlo."""
    import unicodedata
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def bloques_html(cuerpo):
    out = []
    for tipo, val in cuerpo:
        if tipo == "p":
            out.append("      <p>%s</p>" % val)
        elif tipo == "h2":
            out.append('      <h2 class="post-h2" id="%s">%s</h2>' % (ancla(val), esc(val)))
        elif tipo == "ul":
            out.append("      <ul class=\"post-lista\">\n%s\n      </ul>"
                       % "\n".join("        <li>%s</li>" % x for x in val))
        elif tipo == "destacado":
            # Sale de la columna de lectura hacia el margen: es el respiro
            # visual de la entrada.
            out.append('      <blockquote class="post-destacado"><p>%s</p></blockquote>' % esc(val))
        elif tipo == "aviso":
            out.append('      <p class="post-aviso">%s</p>' % val)
    return "\n".join(out)


def pagina_post(e):
    indice = "\n".join(
        '          <li><a href="#%s">%s</a></li>' % (ancla(v), esc(v))
        for t, v in e["cuerpo"] if t == "h2")
    # La tarjeta cierra con los dos botones de agendar, como el resto de la
    # web, y debajo un enlace de texto al servicio del que habla la entrada.
    servicios = " · ".join(
        '<a href="%s">%s</a>' % (enlace(x), esc(y)) for x, y in e["servicios"])
    arch = e["foto"].lower()

    cuerpo = '''<!-- ══════════════════════════ ENTRADA ══════════════════════════ -->
<section class="seccion post" id="post">
  <div class="wrap">
    <nav class="migas" aria-label="Dónde estás">
      <a href="@@BASE@@">Inicio</a><span aria-hidden="true">·</span>
      <a href="@@BASE@@blog/">Blog</a><span aria-hidden="true">·</span>
      <span aria-current="page">%s</span>
    </nav>

    <header class="post-cab">
      <h1 class="post-t">%s</h1>
      <p class="post-entradilla">%s</p>
    </header>

    <figure class="post-portada" data-foto="%s" data-ratio="3:2"
            data-archivo="@@BASE@@assets/img/%s.webp"
            data-alt="Ilustración de la entrada: %s">
      <span class="trama" aria-hidden="true"></span><span class="foto-tag">%s</span>
    </figure>

    <div class="post-marco">
      <aside class="post-indice" aria-label="Secciones de la entrada">
        <p class="post-indice-t">En esta entrada</p>
        <ol>
%s
        </ol>
      </aside>

      <article class="post-cuerpo">
%s
      </article>
    </div>

    <aside class="post-servicio">
      <span class="trama trama-fondo" aria-hidden="true"></span>
      <div class="post-servicio-in">
        <p class="eyebrow">Si esto te suena</p>
        <h2 class="post-servicio-t">Lo vemos en tu valoración</h2>
        <p class="post-servicio-x">Miramos la condición real de tu fibra y tu cuero cabelludo antes de proponerte nada.</p>
        <div class="post-servicio-btns">
          <a class="btn btn-acento" href="https://bravahairlab.site.agendapro.com/co" data-agenda>Agendar en línea</a>
          <a class="btn btn-wa" href="https://wa.me/573205830720" data-wa-simple>Escribir por WhatsApp</a>
        </div>
        <p class="post-servicio-enlace">%s</p>
      </div>
    </aside>

    <p class="volver-fam"><a href="@@BASE@@blog/">← Todas las entradas</a></p>
  </div>
</section>
''' % (esc(e["titulo"]), esc(e["titulo"]), esc(e["resumen"]),
       e["foto"], arch, esc(e["titulo"]), e["foto"],
       indice, bloques_html(e["cuerpo"]), servicios)
    titulo = "%s · BRAVA Hair Lab" % e["seo"]
    return pagina(titulo, e["desc"], cuerpo, "/blog/")


def pagina_blog():
    """El índice del blog: una tarjeta por entrada, con la foto arriba y debajo
    el título y la entradilla. Los huecos FOTO-B01 a FOTO-B05 son propios del
    blog y van marcados como el resto de la web hasta que lleguen las fotos."""
    tarjetas = []
    for e in ENTRADAS:
        arch = e["foto"].lower()
        tarjetas.append(
            '''      <a class="post-tarjeta" href="%s">
        <span class="post-foto" data-foto="%s" data-ratio="3:2"
              data-archivo="@@BASE@@assets/img/%s.webp"
              data-alt="Ilustración de la entrada: %s">
          <span class="trama" aria-hidden="true"></span><span class="foto-tag">%s</span>
        </span>
        <span class="post-cuerpo-t">
          <span class="post-fila-t">%s</span>
          <span class="post-fila-x">%s</span>
          <span class="post-fila-mas">Leer</span>
        </span>
      </a>''' % (enlace("/blog/%s/" % e["slug"]), e["foto"], arch,
                 esc(e["titulo"]), e["foto"], esc(e["titulo"]), esc(e["resumen"])))
    cuerpo = '''<!-- ══════════════════════════ BLOG ══════════════════════════ -->
<section class="seccion blog" id="blog">
  <div class="wrap">
    <header class="seccion-cab">
      <p class="eyebrow reveal">Blog</p>
      <h1 class="titulo titulo-c" data-split="lines">Cuidado del cabello,<br><em>explicado sin humo.</em></h1>
      <p class="parrafo centro reveal">Lo que nos preguntan en el salón, respondido de frente y sin vender nada.</p>
    </header>
    <div class="post-rejilla reveal">
%s
    </div>
  </div>
</section>

%s
''' % ("\n\n".join(tarjetas), banda_reserva("¿Te quedó una duda? La resolvemos en la valoración."))
    return pagina("Blog de cuidado capilar · BRAVA Hair Lab",
                  "Alisados sin formol, head spa, caída del pelo y tratamientos de fibra, "
                  "explicados de frente por BRAVA Hair Lab, en Bogotá.",
                  cuerpo, "/blog/")


def pagina_protocolo(p):
    c = categoria(p)
    d = p.get("datos") or {}
    filas = ""
    if p.get("resultado"):
        filas += "<div><dt>Resultado</dt><dd>%s</dd></div>" % esc(p["resultado"])
    if p.get("idealPara"):
        filas += "<div><dt>Indicado si</dt><dd>%s</dd></div>" % esc(p["idealPara"])
    for k, v in d.items():
        filas += "<div><dt>%s</dt><dd>%s</dd></div>" % (esc(k), esc(v))
    # Sin precio no se enseña la fila: antes salía una etiqueta "PENDIENTE:
    # precio" que es una nota interna, no algo que deba ver una clienta.
    precio = p.get("precio")
    if precio:
        filas += '<div><dt>Precio</dt><dd>%s</dd></div>' % esc(precio)

    incluye = ""
    if p.get("incluye"):
        incluye = ('<p class="detalle-sub">Incluye</p><ul class="detalle-lista">%s</ul>'
                   % "".join("<li>%s</li>" % esc(i) for i in p["incluye"]))
    # Los avisos que empiezan por "PENDIENTE:" son notas internas para la
    # clienta del proyecto, no texto para una visitante: no se publican. Se
    # quedan en el catálogo, que es donde tienen que seguir haciendo de
    # recordatorio.
    av = (p.get("avisoEspecial") or "").strip()
    aviso = '<p class="detalle-aviso">%s</p>' % esc(av) if av and not av.upper().startswith("PENDIENTE") else ""
    # porQue es la frase editorial que explica la elección; en la ficha va
    # etiquetada para que no parezca una línea suelta.
    porque = ('<p class="detalle-porque"><strong>Por qué este protocolo:</strong> %s</p>'
              % esc(p["porQue"])) if p.get("porQue") else ""

    cod = p.get("foto") or ""
    figura = ('<figure class="arco detalle-fig" data-foto="%s" data-ratio="%s"'
              ' data-archivo="@@BASE@@assets/img/%s.webp"'
              ' data-alt="Protocolo %s. %s">'
              '<span class="trama" aria-hidden="true"></span>'
              '<span class="foto-tag">%s</span></figure>'
              % (esc(cod), c["ratio"], cod.lower(), esc(p["nombre"]),
                 esc(c["nombre"]), esc(cod)))
    # La marca (FIBER / SCALP) sigue apareciendo, ahora como apunte dentro de la
    # ficha y no como ruta de navegación.
    marca = ('<p class="detalle-marca">%s</p>' % esc(c["marca"])) if c["marca"] else ""

    cuerpo = '''<!-- ══════════════════════════ PROTOCOLO ══════════════════════════ -->
<section class="seccion protocolo" id="protocolo">
  <div class="wrap">
    <nav class="migas" aria-label="Dónde estás">
      <a href="@@BASE@@">Inicio</a><span aria-hidden="true">·</span>
      <a href="@@BASE@@servicios/">Servicios</a><span aria-hidden="true">·</span>
      <a href="%s">%s</a><span aria-hidden="true">·</span>
      <span aria-current="page">%s</span>
    </nav>

    <article class="detalle detalle-pag">
      %s
      <div class="detalle-cuerpo">
        <p class="eyebrow reveal">%s</p>
        <h1 class="detalle-t">%s</h1>
        <p class="detalle-sub">%s</p>
        %s
        <p>%s</p>
        <dl class="detalle-datos">%s</dl>
        %s
        %s
        %s
        <div class="hero-ctas reveal">
          <a class="btn btn-acento" href="https://bravahairlab.site.agendapro.com/co" data-agenda>Agendar en línea</a>
          <a class="btn btn-wa" href="https://wa.me/573205830720" data-wa-simple>Escribir por WhatsApp</a>
        </div>
        <p class="volver-fam"><a href="%s">← Todos los protocolos de %s</a></p>
      </div>
    </article>
  </div>
</section>
''' % (enlace(RUTA_CAT[c["slug"]]), esc(c["nombre"]), esc(p["nombre"]),
       figura, esc(c["nombre"]), esc(p["nombre"]),
       esc(p.get("subtitulo") or ""), marca, esc(p.get("descripcion") or ""),
       filas, incluye, porque, aviso,
       enlace(RUTA_CAT[c["slug"]]), esc(c["nombre"]))

    # Por debajo de 60 caracteres: si el nombre y la categoría no caben, se
    # deja solo el nombre del protocolo, que es lo que se busca.
    titulo = "%s · %s · BRAVA Hair Lab" % (p["nombre"], c["nombre"])
    if len(titulo) > 60:
        titulo = "%s · BRAVA Hair Lab" % p["nombre"]
    desc = (p.get("subtitulo") or "") + ". " + primera_frase(p.get("descripcion") or "")
    return pagina(titulo, desc.strip(" ."), cuerpo, RUTA_CAT[c["slug"]])


def primera_frase(t):
    i = t.find(". ")
    return t[:i + 1] if i > 0 else t


# ──────────────────── textos propios de cada página ────────────────────
def main():
    if not os.path.exists(FUENTE):
        sys.exit("Falta la plantilla: %s" % FUENTE)
    html = open(FUENTE, encoding="utf-8").read()
    global T, PROTOS
    T = trozos(html)
    T = {k: relativas(v) for k, v in T.items()}
    T["pie_nuevo"] = pie(T["pie"])

    cat = json.load(open(CATALOGO, encoding="utf-8"))
    protos = cat["protocolos"]
    PROTOS[:] = protos

    # Los bloques de contexto editorial. En la fuente van marcados con la
    # familia del catálogo, y cada familia es hoy una categoría, así que el
    # texto de cada una entra tal cual en su página.
    ctx = {}
    for m in re.finditer(r'<div data-contexto="([a-z-]+)">([\s\S]*?)\n      </div>', T.get("contexto", "")):
        ctx[m.group(1)] = m.group(2)

    # ── portada ──
    escribe("/", pagina(
        "Alisados sin formol y spa capilar en Bogotá · BRAVA Hair Lab",
        "Estudio de cuidado capilar cosmético en Bogotá. 24 protocolos agrupados en cinco categorías, adaptados a la condición real de tu fibra y tu cuero cabelludo.",
        # El orden manda: tras la banda de sellos, las cinco categorías. "Dos
        # abordajes" va detrás del antes y después, como explicación de fondo.
        "\n\n".join([T["inicio"], T["apto"], banda_familias(protos), T["marquesina"],
                     T["resultados"], T["abordajes"], T["faq"]]),
        "/", precarga="@@BASE@@assets/img/banner-1.webp"))

    # ── el índice de servicios ──
    escribe("/servicios/", pagina_servicios(protos))

    # ── las cinco categorías ──
    for c in CATEGORIAS:
        escribe(RUTA_CAT[c["slug"]], pagina_categoria(c, protos, ctx.get(c["familia"], "")))

    # ── las 24 fichas, cada una dentro de su categoría ──
    for p in protos:
        escribe(ruta_protocolo(p), pagina_protocolo(p))

    # ── el blog ──
    escribe("/blog/", pagina_blog())
    for e in ENTRADAS:
        escribe("/blog/%s/" % e["slug"], pagina_post(e))

    # ── resultados ──
    escribe("/resultados/", pagina_resultados())

    # ── el lab ──
    escribe("/el-lab/", pagina(
        "El Lab y el método BRAVA · BRAVA Hair Lab",
        "Los dos pisos de BRAVA en Colina Campestre y los cuatro pasos del método: evaluamos, tratamos, transformamos y mantenemos.",
        # La galería "El Lab, por dentro" NO se publica por ahora. No está
        # borrada: su HTML sigue en _plantilla/pagina-unica.html y su CSS y su
        # JS (initReel) siguen en su sitio. Para volver a sacarla, se añade
        # T["galeria"] a esta lista, en el orden que se quiera.
        "\n\n".join([T["espacios"], T["metodo"], T["adn"],
                     banda_reserva("Ven a conocer el Lab. Empezamos por tu valoración.")]),
        "/el-lab/"))

    # ── contacto ──
    escribe("/contacto/", pagina(
        "Contacto y reservas en Bogotá · BRAVA Hair Lab",
        "Agenda tu valoración en BRAVA Hair Lab: reserva en línea o escríbenos por WhatsApp. Bogotá, Colina Campestre.",
        T["contacto"], "/contacto/"))

    print("%d direcciones generadas\n" % len(CREADAS))
    for ruta, archivo in CREADAS:
        print("  %-42s %s" % (ruta, archivo))


if __name__ == "__main__":
    main()
