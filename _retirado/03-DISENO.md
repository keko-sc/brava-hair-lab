# DIRECCIÓN DE DISEÑO — BRAVA Hair Lab · versión 3

**Esta versión reemplaza por completo a las dos anteriores.** Las dos primeras salieron
planas porque describían un diseño con palabras abstractas. Esta no describe: copia un
sistema que ya existe y funciona, y lo viste con la marca de BRAVA.

---

## De dónde sale este diseño

Hay una web ya construida por el mismo equipo, para un centro de masaje y estética, que
resuelve exactamente los mismos problemas que tiene BRAVA: muchos tratamientos, tres
familias, un buscador guiado, y una marca que quiere sentirse cara sin gritar.

**Ese sistema se reutiliza tal cual.** No es una referencia externa ni hay nada que
respetar: es trabajo propio. Lo que cambia es la paleta, la tipografía y el contenido.

Los elementos del sistema, uno a uno:

1. **Portada partida.** Texto grande a la izquierda, imagen a la derecha **con el borde
   superior en arco** (un semicírculo perfecto arriba, esquinas rectas abajo). Sobre la
   imagen, una tarjetita flotante que se sale del borde. Debajo del texto, una fila de
   datos con números grandes en serif.
2. **Titulares con cursiva de acento.** La última línea o la palabra clave del titular va
   en cursiva. *"Cuidado del cuerpo, **sin prisa**."* Ese contraste entre redonda y
   cursiva es la mitad del carácter de la página.
3. **Imágenes en arco** en todas las secciones de contenido, no solo en la portada.
4. **Etiquetas en versalitas muy espaciadas** encima de cada titular: `QUIÉNES SOMOS`,
   `BRAVA FIBER`. Pequeñas, en el color de acento.
5. **Filas de cifras** con el número enorme en serif y la palabra pequeña debajo.
6. **Listas con un rombo** (✦) de viñeta, título en serif y explicación debajo.
7. **Familias en píldoras** con el número de elementos en un círculo al lado, y debajo la
   rejilla de tarjetas de esa familia.
8. **Tarjetas compactas**: nombre en serif a la izquierda, los datos clave alineados a la
   derecha en la misma línea (`45 min · 48 €`), tres o cuatro líneas de descripción, una
   línea de *"Indicado si…"* y abajo un desplegable discreto con el signo más.
9. **Proceso numerado**: el número pequeño arriba, titular grande en serif, texto, y una
   línea de meta en versalitas. Las imágenes en arco, alternando y desalineadas en
   vertical entre un paso y el siguiente.
10. **Capa a pantalla completa** para el buscador: barra superior con el nombre y los
    pasos numerados, la X a la derecha, y detrás la página difuminada y atenuada, no un
    fondo negro plano.
11. **Botón flotante de WhatsApp** abajo a la derecha, siempre visible.
12. **Banda de aviso** arriba del todo mientras sea versión de trabajo.

---

## La paleta — marrón, no beige

Sale del Instagram de la marca y del logo. Es notablemente más cálida y más oscura que la
que se usó antes.

```css
:root {
  /* Marca */
  --camel:        #B4926F;   /* el color exacto del logo */
  --camel-claro:  #C9A67F;   /* sobre fondo oscuro */
  --camel-hover:  #8E6F4F;

  /* Oscuros — la marca vive aquí */
  --cafe:         #1D160E;   /* marrón profundo, casi negro. Nunca #000 */
  --cafe-alt:     #2A2118;
  --tabaco:       #3A2E22;   /* bordes y separadores en oscuro */

  /* Claros */
  --crema:        #F4EEE4;   /* el fondo claro dominante */
  --arena:        #E7DDCE;   /* bandas alternas */
  --lino:         #DCCFBC;   /* tarjetas sobre arena */

  /* Texto */
  --tinta:        #241C14;   /* sobre claro */
  --tinta-suave:  #6A5B4B;
  --crema-texto:  #F4EEE4;   /* sobre oscuro */
  --crema-suave:  #B3A493;
}
```

**Reparto:** la página alterna crema y arena en las zonas de contenido, y usa el café
profundo en la portada, la cita de marca, la sección de tecnología, el ADN y el contacto.
Ese ir y venir entre claro y oscuro es buena parte de lo que hace que se vea cara.

La zona SCALP mantiene el matiz frío, pero dentro de la misma familia: en vez del gris
azulado anterior, un lino desaturado. La diferencia entre los dos pisos se nota, pero no
rompe la unidad.

Ni negro puro ni blanco puro en ningún sitio.

---

## La trama

El Instagram usa una **trama de líneas onduladas verticales**, finas, en un tono apenas
más claro que el fondo. Es la textura de la marca y hay que traerla a la web.

Se dibuja en SVG, se repite como fondo y se usa al 6-10 % de opacidad. Va en:

- El fondo de la portada, detrás de la imagen y del texto.
- Las bandas oscuras, para que no sean rectángulos planos.
- Los huecos de foto que todavía no tienen imagen.

Es lo que impide que un fondo de color sólido se vea muerto.

---

## Tipografía

La anterior era demasiado dura y fría. Cambia:

- **Fraunces** para titulares, números y cifras. Serif de contraste moderado, cálida, con
  una cursiva excelente. Se usa `wght` 300-400 en tamaños grandes y `SOFT`/`WONK` para
  darle el punto editorial. **Su cursiva es obligatoria en el acento de cada titular.**
- **Instrument Sans** para todo lo demás: cuerpo, menú, botones, etiquetas.
  En versalitas con `letter-spacing: .2em` para las etiquetas de sección.

Nada de Bodoni Moda ni de Jost.

Escala: titulares de sección `clamp(40px, 5.5vw, 88px)`. Cuerpo de texto 17-18 px,
interlineado 1.7, línea máxima de 68 caracteres.

---

## La estructura de la página

Mismo orden que la versión 2, con las formas del sistema de arriba:

1. **Banda de aviso** de versión de trabajo.
2. **Menú**: isotipo y nombre a la izquierda, enlaces a la derecha, y el botón
   `ENCONTRAR MI PROTOCOLO` como píldora rellena en camel.
3. **Portada partida.** Izquierda: etiqueta `BRAVA HAIR LAB · FIBER X SCALP STUDIO`,
   titular *Hair,* ***Evolved*** con la segunda palabra en cursiva, la bajada, los dos
   botones y una fila de cifras: `24 protocolos · 2 pisos · WhatsApp para agendar`.
   Derecha: `FOTO-01` en arco, con una tarjetita flotante saliéndose del borde
   (`BOGOTÁ — COLINA CAMPESTRE`, y debajo el horario cuando lo tengamos).
4. **Apto para** — banda oscura con los sellos en fila, icono de línea y una frase.
5. **Dos abordajes** — dos bloques con imagen en arco, uno cálido y uno frío.
6. **The Brava Method** — los cuatro pasos con el patrón numerado, imágenes en arco
   alternando lado y desalineadas en vertical.
7. **Cita de marca** — banda café, solo tipografía, con la trama de fondo.
8. **El catálogo** — familias en píldoras con su contador, rejilla de tarjetas compactas,
   detalle en capa a pantalla completa. FIBER lleva dos subpestañas: Alineaciones y
   Rituales. Ninguna de las dos filas de pestañas se fija.
9. **Tecnología** — banda café, carrusel horizontal arrastrable.
10. **Los dos espacios** — Piso 1 en cálido y Piso 2 en frío, imágenes grandes en arco y
    una tira de detalles debajo.
11. **ADN de marca** — banda café, editorial. *"Nos dijeron bravas."*
12. **Preguntas frecuentes** — acordeón a dos columnas.
13. **Contacto** — banda café a pantalla completa.
14. **Pie.**
15. **Guion de fotos** — solo mientras sea versión de trabajo.

Más la capa del buscador y el botón flotante de WhatsApp.

---

## Las fotos

Ya no se maqueta en blanco: **la página se construye con fotografía de stock desde el
primer momento**, porque sin imagen no hay forma de juzgar si el diseño funciona. Son
provisionales y se sustituyen cuando lleguen las de la clienta.

Reglas de selección, y son innegociables porque son lo que hace que doce fotos parezcan
una sola sesión:

1. Luz natural y cálida. Nada de flash duro ni luz azulada.
2. Fondos neutros: mármol, madera, lino, arena, hormigón claro.
3. **Ningún dominante rosa.** Es el color de la competencia.
4. Sin sonrisa comercial y sin mirar a cámara. Perfil, nuca, de espaldas, ojos cerrados.
5. Sin marcas visibles.
6. Variedad real de tonos de piel y de texturas de cabello. El catálogo tiene protocolos
   para cabello rizado y afro: tiene que verse.

Cada foto colocada se reporta: qué hueco llena, de dónde salió y por qué esa.

Mientras un hueco siga vacío, se rellena con la trama de la marca sobre el color de la
sección, el isotipo en marca de agua y una etiqueta pequeña en la esquina. Nunca un
recuadro punteado vacío con un párrafo en el centro.

---

## Movimiento

El de la web de Escobar, que es el nivel correcto: se nota, no distrae.

- Aparición al entrar en pantalla: desplazamiento de 24 px hacia arriba con fundido, 700 ms.
- Escalonado en rejillas y listas: 70 ms entre elementos.
- Parallax del 8-12 % en las imágenes grandes en arco.
- Las cifras cuentan desde cero al entrar.
- El filete de acento se dibuja bajo cada titular.
- El menú se compacta al bajar y vuelve a su altura al subir.
- La capa del buscador entra con el fondo difuminándose, no con un corte a negro.
- El botón de WhatsApp aparece al pasar la portada.

GSAP con ScrollTrigger está permitido y recomendado; `lib/` existe para eso. Si GSAP no
carga, la página tiene que verse entera igualmente.

Prohibido: rebotes, giros, cursores personalizados y scroll con inercia. Y todo respeta
la preferencia de movimiento reducido del sistema.
