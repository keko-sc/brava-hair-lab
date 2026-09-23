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
         bajada="No plastificamos tu cabello: lo alineamos desde su salud molecular. "
                "Seis sistemas, y la diferencia entre ellos no es el precio: es tu cabello.",
         titulo="Alisados y alineación · 6 protocolos · BRAVA Hair Lab",
         desc="Los 6 protocolos de alisado y alineación molecular de BRAVA Hair Lab, "
              "en Bogotá. Alineación real sin sacrificar la fuerza de la fibra.",
         ratio="4:5"),
    dict(slug="tratamientos", familia="fiber-ritual", marca="BRAVA FIBER",
         nombre="Tratamientos y reparación", corto="Tratamientos y reparación",
         titular="Tratamientos y reparación.<br><em>De medios a puntas.</em>",
         bajada="Hidratación, nutrición, suavidad, brillo, fuerza y protección frente "
                "al desgaste. Nueve rituales para devolverle a la hebra lo que perdió.",
         titulo="Tratamientos y reparación · 9 protocolos · BRAVA Hair Lab",
         desc="Los 9 rituales de tratamiento y reparación capilar de BRAVA Hair Lab, "
              "en Bogotá. Hidratación, nutrición, brillo y fuerza para la fibra.",
         ratio="1:1"),
    dict(slug="head-spa", familia="scalp-experiencia", marca="BRAVA SCALP",
         nombre="Head Spa", corto="Head Spa",
         titular="Head Spa.<br><em>Rooted in Care.</em>",
         bajada="Experiencias largas de cuidado del cuero cabelludo, en el silencio "
                "del Piso 2. Desconexión profunda y cuidado cosmético avanzado.",
         titulo="Head Spa · 2 experiencias · BRAVA Hair Lab",
         desc="Las 2 experiencias de Head Spa de BRAVA Hair Lab, en Bogotá. "
              "Cuidado cosmético del cuero cabelludo y desconexión profunda.",
         ratio="3:2"),
    dict(slug="caida", familia="scalp-rootlounge", marca="BRAVA SCALP",
         nombre="Caída y fortalecimiento", corto="Caída y fortalecimiento",
         titular="Caída y fortalecimiento.<br><em>Desde la raíz.</em>",
         bajada="La salud, la fuerza y la calidad del cabello nacen en el folículo. "
                "Bioestimulación cosmética no invasiva para su entorno.",
         titulo="Caída y fortalecimiento · 3 protocolos · BRAVA Hair Lab",
         desc="Los 3 protocolos de BRAVA Hair Lab para caída y fortalecimiento, en "
              "Bogotá. Bioestimulación cosmética del cuero cabelludo, no médica.",
         ratio="4:5"),
    dict(slug="complementarios", familia="addon", marca="",
         nombre="Servicios complementarios", corto="Complementarios",
         titular="Servicios complementarios.<br><em>Suman a tu protocolo.</em>",
         bajada="Se añaden a cualquier protocolo para elevar tu experiencia y "
                "personalizar aún más tu resultado.",
         titulo="Servicios complementarios · 4 servicios · BRAVA Hair Lab",
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


def absolutas(t):
    """assets/… → /assets/…  ·  styles.css → /styles.css  ·  lib/… → /lib/…"""
    t = re.sub(r'(href|src|data-archivo|data-video)="(?!https?:|/|#|mailto:)([^"]+)"',
               lambda m: '%s="/%s"' % (m.group(1), m.group(2)), t)
    return t


# ─────────────────────────────── menú y pie ───────────────────────────────
# El resto del menú, al lado de "Servicios". No hay pestaña de Sedes: BRAVA
# tiene una sola sede, y está en Contacto.
ENLACES = [
    # "Inicio" va primero y explícito: el logotipo también lleva a la portada,
    # pero mucha gente no lo da por hecho.
    ("/", "Inicio", "Inicio"),
    ("/el-lab/", "El Lab", "El Lab por dentro"),
    ("/#resultados", "Resultados", "Antes y después"),
    ("/#faq", "Preguntas", "Preguntas frecuentes"),
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
            '            <li><a href="%s">%s</a></li>' % (ruta_protocolo(p), esc(p["nombre"]))
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
        % (RUTA_CAT[c["slug"]], esc(c["nombre"]), n)
        for c, n, _ in cols)

    acordeon = "\n".join(
        '''    <details class="menu-cat"%s>
      <summary>%s<span>%d</span></summary>
      <a class="menu-cat-todo" href="%s">Ver toda la categoría</a>
      <ul>
%s
      </ul>
    </details>''' % (" open" if actual == RUTA_CAT[c["slug"]] else "",
                     esc(c["nombre"]), n, RUTA_CAT[c["slug"]], items)
        for c, n, items in cols)

    # "Inicio" se imprime aparte porque va DELANTE del desplegable de Servicios,
    # que está escrito a mano en la plantilla del menú.
    links_inicio = '      <a href="/"%s>Inicio</a>' % cls("/")
    links = "\n".join(
        '      <a href="%s"%s>%s</a>' % (u, cls(u), corto)
        for u, corto, _ in ENLACES if u != "/")
    # En celular "Inicio" va delante del bloque de Servicios, para que sea la
    # primera entrada igual que en escritorio; el resto va detrás.
    movil_inicio = '    <a href="/"%s>Inicio</a>' % cls("/")
    movil = "\n".join(
        '    <a href="%s"%s>%s</a>' % (u, cls(u), largo)
        for u, _, largo in ENLACES if u != "/")

    return '''<header class="nav" data-nav>
  <div class="nav-in">
    <a class="logo" href="/" aria-label="BRAVA Hair Lab, inicio">
      <img src="/assets/img/marca/isotipo.webp" alt="" width="320" height="275">
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
            <a class="nav-desp-todo" href="/servicios/">Ver todos los servicios</a>
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
    <a class="menu-cat-todo menu-cat-todos" href="/servicios/">Ver todos los servicios</a>
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
    nuevo = "\n".join('        <a href="%s">%s</a>' % (u, largo)
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
<html lang="es-CO">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%s</title>
<meta name="description" content="%s">
<meta name="theme-color" content="#1D160E">
<meta name="robots" content="noindex, nofollow">

<link rel="icon" href="/assets/img/marca/favicon.ico" sizes="any">
<link rel="icon" href="/assets/img/marca/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/img/marca/apple-touch-icon.png">

%s<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<link rel="stylesheet" href="/styles.css?v=%s">

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

<script defer src="/lib/gsap.min.js"></script>
<script defer src="/lib/ScrollTrigger.min.js"></script>
<script defer src="/main.js?v=%s"></script>
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
        <a class="btn btn-claro" href="/contacto/">Cómo llegar</a>
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
    "head-spa": dict(sobre="Rooted in Care", cod="FOTO-23",
                     texto="Una melena extraordinaria comienza desde la raíz. Experiencias "
                           "largas de cuidado del cuero cabelludo, en el silencio del Piso 2.",
                     foto="Head Spa: plano ancho del Piso 2, cabina privada, luz tenue."),
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
                data-archivo="/assets/img/%(arch)s.webp" data-alt="%(foto)s">
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
                            ruta=RUTA_CAT[c["slug"]]))

    return '''<!-- ══════════════════════════ LAS CINCO CATEGORÍAS ══════════════════════════ -->
<section class="seccion familias" id="catalogo">
  <div class="wrap">
    <header class="seccion-cab">
      <p class="eyebrow reveal">Servicios</p>
      <h2 class="titulo titulo-c" data-split="lines">Veinticuatro protocolos.<br><em>Cinco categorías.</em></h2>
      <p class="parrafo centro reveal">Agrupados por lo que vienes a resolver. Entra en la categoría que te interese y ahí están sus protocolos, uno a uno.</p>
    </header>

    <div class="fam-bloques" data-familias>
%s

      <!-- Recorrido para que el último bloque llegue a su posición fija y se
           quede ahí. Tiene que ser un elemento de verdad: un margen o un
           padding no le dan recorrido al sticky. -->
      <span class="fam-cola" aria-hidden="true"></span>
    </div>

    <p class="familias-todos reveal"><a href="/servicios/">Ver todos los servicios →</a></p>
  </div>
</section>
''' % "\n\n".join(bloques)


def lista_protocolos(c, protos):
    """La lista de una categoría: una fila-enlace por protocolo."""
    ps = [p for p in protos if p["familia"] == c["familia"]]
    return "\n".join(
        '        <li><a class="prot-fila" href="%s">'
        '<span class="prot-nombre">%s</span>'
        '<span class="prot-sub">%s</span>'
        '<span class="prot-mas">Ver el protocolo</span></a></li>'
        % (ruta_protocolo(p), esc(p["nombre"]), esc(p.get("subtitulo") or ""))
        for p in ps)


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
      <a href="/">Inicio</a><span aria-hidden="true">·</span>
      <a href="/servicios/">Servicios</a><span aria-hidden="true">·</span>
      <span aria-current="page">%s</span>
    </nav>
    <header class="seccion-cab">
      <p class="eyebrow reveal">%s</p>
      <h2 class="titulo titulo-c" data-split="lines">%s</h2>
      <p class="parrafo centro reveal">%s</p>
    </header>
  </div>
</section>

<section class="seccion fam-contexto">
  <div class="wrap">
%s
  </div>
</section>

<section class="seccion fam-listado" id="protocolos">
  <div class="wrap">
    <header class="seccion-cab">
      <h2 class="titulo titulo-c" data-split="lines">Los <em>%d protocolos.</em></h2>
      <p class="nota-trabajo reveal">Precios pendientes de la clienta</p>
    </header>
    <ul class="prot-lista">
%s
    </ul>
  </div>
</section>

%s
''' % (esc(c["nombre"]), esc(et), c["titular"], esc(c["bajada"]), contexto,
       len(ps), lista_protocolos(c, protos),
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
        </a>''' % (RUTA_CAT[c["slug"]], n, esc(c["nombre"]), len(ps), nombres))

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
    return pagina("Servicios · los 24 protocolos · BRAVA Hair Lab",
                  "Los 24 protocolos de BRAVA Hair Lab en Bogotá, agrupados por fibra "
                  "capilar y cuero cabelludo, más los servicios complementarios.",
                  cuerpo, "/servicios/")


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
    precio = p.get("precio")
    filas += ('<div><dt>Precio</dt><dd>%s</dd></div>'
              % (esc(precio) if precio else '<span class="pendiente">PENDIENTE: precio</span>'))

    incluye = ""
    if p.get("incluye"):
        incluye = ('<p class="detalle-sub">Incluye</p><ul class="detalle-lista">%s</ul>'
                   % "".join("<li>%s</li>" % esc(i) for i in p["incluye"]))
    aviso = ('<p class="detalle-aviso">%s</p>' % esc(p["avisoEspecial"])) if p.get("avisoEspecial") else ""
    # porQue es la frase editorial que explica la elección; en la ficha va
    # etiquetada para que no parezca una línea suelta.
    porque = ('<p class="detalle-porque"><strong>Por qué este protocolo:</strong> %s</p>'
              % esc(p["porQue"])) if p.get("porQue") else ""

    cod = p.get("foto") or ""
    figura = ('<figure class="arco detalle-fig" data-foto="%s" data-ratio="%s"'
              ' data-archivo="/assets/img/%s.webp"'
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
      <a href="/">Inicio</a><span aria-hidden="true">·</span>
      <a href="/servicios/">Servicios</a><span aria-hidden="true">·</span>
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
''' % (RUTA_CAT[c["slug"]], esc(c["nombre"]), esc(p["nombre"]),
       figura, esc(c["nombre"]), esc(p["nombre"]),
       esc(p.get("subtitulo") or ""), marca, esc(p.get("descripcion") or ""),
       filas, incluye, porque, aviso,
       RUTA_CAT[c["slug"]], esc(c["nombre"]))

    titulo = "%s · %s · BRAVA Hair Lab" % (p["nombre"], c["nombre"])
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
    T = {k: absolutas(v) for k, v in T.items()}
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
        "BRAVA Hair Lab · Fiber x Scalp Studio · Bogotá",
        "Estudio de cuidado capilar cosmético en Bogotá. 24 protocolos agrupados en cinco categorías, adaptados a la condición real de tu fibra y tu cuero cabelludo.",
        # El orden manda: tras la banda de sellos, las cinco categorías. "Dos
        # abordajes" va detrás del antes y después, como explicación de fondo.
        "\n\n".join([T["inicio"], T["apto"], banda_familias(protos), T["marquesina"],
                     T["resultados"], T["abordajes"], T["faq"]]),
        "/", precarga="/assets/img/foto-01.webp"))

    # ── el índice de servicios ──
    escribe("/servicios/", pagina_servicios(protos))

    # ── las cinco categorías ──
    for c in CATEGORIAS:
        escribe(RUTA_CAT[c["slug"]], pagina_categoria(c, protos, ctx.get(c["familia"], "")))

    # ── las 24 fichas, cada una dentro de su categoría ──
    for p in protos:
        escribe(ruta_protocolo(p), pagina_protocolo(p))

    # ── el lab ──
    escribe("/el-lab/", pagina(
        "El Lab · Los dos pisos y The Brava Method · BRAVA Hair Lab",
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
        "Contacto y reservas · BRAVA Hair Lab · Bogotá",
        "Agenda tu valoración en BRAVA Hair Lab: reserva en línea o escríbenos por WhatsApp. Bogotá, Colina Campestre.",
        T["contacto"], "/contacto/"))

    print("%d direcciones generadas\n" % len(CREADAS))
    for ruta, archivo in CREADAS:
        print("  %-42s %s" % (ruta, archivo))


if __name__ == "__main__":
    main()
