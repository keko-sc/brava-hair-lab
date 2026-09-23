# BRAVA Hair Lab · cómo está montada la web

La web es **multipágina** y sus 33 direcciones **se generan**, no se escriben a
mano. Si editas un `index.html` suelto, el siguiente generado se lo lleva por
delante.

## Cómo se organizan los servicios

Por **lo que busca la clienta**, no por las familias internas de la marca.
BRAVA FIBER y BRAVA SCALP siguen existiendo como concepto dentro de las
páginas, pero ya no son la forma de navegar.

| Categoría | Dirección | Grupo del catálogo |
|---|---|---|
| Alisados y alineación (6) | `/servicios/alisados/` | `fiber-alineacion` |
| Tratamientos y reparación (9) | `/servicios/tratamientos/` | `fiber-ritual` |
| Head Spa (2) | `/servicios/head-spa/` | `scalp-experiencia` |
| Caída y fortalecimiento (3) | `/servicios/caida/` | `scalp-rootlounge` |
| Servicios complementarios (4) | `/servicios/complementarios/` | `addon` |

Cada categoría se corresponde **exactamente** con un grupo del catálogo: mismo
contenido y mismo orden. Cada protocolo vive en
`/servicios/<categoria>/<protocolo>/`.

Tres protocolos se escriben en la dirección distinto de como se llaman en el
JSON. El `id` del catálogo sigue mandando para identificarlos; el mapa `SLUG`
de `tools/generar_paginas.py` solo traduce el trozo de la URL:

| `id` en el catálogo | trozo de la dirección |
|---|---|
| `reforce` | `re-force` |
| `reconnect` | `re-connect` |
| `split-ends` | `puntas` |

Ese mismo mapa está duplicado en `main.js` (`CATEGORIA` y `TROZO`), porque el
buscador necesita construir el enlace en el navegador. **Si tocas uno, toca el
otro**: si se separan, los resultados del buscador apuntan a páginas que no
existen.

## Las piezas

| Archivo | Qué es |
|---|---|
| `_plantilla/pagina-unica.html` | La fuente. De aquí salen todos los trozos (hero, método, galería, contacto, pie…). |
| `assets/docs/02-CATALOGO.json` | Los 24 protocolos, con su `familia`. |
| `tools/generar_paginas.py` | El generador. Escribe las 33 páginas y el menú. |
| `styles.css`, `main.js` | Compartidos por todas, con rutas absolutas (`/styles.css`). |

## Rehacer las páginas

```bash
python3 tools/generar_paginas.py
```

Imprime la lista de direcciones creadas.

## Vista previa

```bash
python3 -m http.server 8010
```

y abrir <http://127.0.0.1:8010/>. Hace falta un servidor: las páginas leen el
catálogo por `fetch` y con `file://` no funciona.

## El menú

"Servicios" despliega las cinco categorías con sus protocolos dentro.

- **Escritorio:** un panel que cae de la barra. Abre al pasar el cursor y al
  pulsar; cierra con Escape, al pulsar fuera y al salir el foco. Lo lleva
  `initDesplegable()` en `main.js`.
- **Celular:** un acordeón de `<details>` nativo, sin JS, para que siga
  funcionando aunque el JS falle.

No hay pestaña de Sedes: BRAVA tiene una sola sede, y está en Contacto.

## Reglas que el generador ya cumple

- Cada página lleva su `<title>`, su `meta description` y un solo `<h1>`.
- `noindex, nofollow` en todas, por ahora.
- Menú y pie idénticos, con las direcciones nuevas.
- El buscador está en todas y su resultado enlaza a la ficha del protocolo.
- WhatsApp y AgendaPro en todas las páginas.

## Qué queda pendiente

- Los huecos de foto vacíos: los 24 de protocolo (`FOTO-F01…`, `FOTO-R01…`,
  `FOTO-S01…`, `FOTO-A01…`), `FOTO-08`, `FOTO-09` y los cinco de la portada
  (`FOTO-21` a `FOTO-25`). Dan 404 y la página enseña la trama de marca.
- En las páginas de categoría, `FOTO-08` y `FOTO-09` están declaradas `21:9`
  pero el CSS las dibuja en `4:5`. Cuando lleguen, se les comerán los lados.
- Antes de publicar: borrar las imágenes `DEMO-*` de los comparadores y
  `PRUEBA-g0*` de la galería, y sus bloques marcados en `tools/tratar_fotos.py`.
