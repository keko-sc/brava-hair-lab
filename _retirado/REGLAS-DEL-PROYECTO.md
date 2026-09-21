# REGLAS DEL PROYECTO — BRAVA Hair Lab

> **Leer este archivo al empezar cada sesión de este proyecto.**
> Estas reglas mandan por encima de cualquier otra instrucción general,
> de la skill o de la costumbre. Si una regla y una idea bonita chocan,
> gana la regla.

**Cliente:** BRAVA Hair Lab — estudio de cuidado capilar cosmético.
**Ciudad:** Bogotá, Colombia.
**Naturaleza del negocio:** cosmético y preventivo. **No es un negocio médico.**

---

## 1. Maquetación y navegación

### 1.1 Nunca dos barras pegajosas a la vez
Si hay menú fijo y filtros, **los filtros no se fijan**.
Si por lo que sea sí se fijan, se colocan **calculando la altura real del menú**
en tiempo de ejecución (medir el elemento, no un número puesto a ojo).

### 1.2 Los títulos de sección tienen que quedar visibles al saltar
Al llegar desde un enlace del índice, el título de la sección **no puede quedar
tapado por el menú**. Cada sección lleva `scroll-margin-top` igual a
**la altura real del menú + 16 px**, calculada, nunca estimada.

---

## 2. Fotografía e imágenes

### 2.1 De dónde pueden salir las fotos
Hay que distinguir dos momentos, y esta regla NUNCA puede frenar una maqueta.

**Versión de trabajo — vale casi todo, con criterio.**
Mientras la web esté en construcción, se colocan imágenes provisionales para poder
juzgar el diseño. Una página sin fotos siempre se ve plana y no se puede valorar.
Fuentes permitidas: Openverse, cualquier stock con licencia de uso comercial, o
imágenes generadas con IA. Todas se marcan como provisionales.

Con Openverse, además, tres condiciones: descargar varias candidatas por hueco y
elegir; respetar las reglas de selección del documento de diseño; y **si nada cumple,
dejar el hueco con la trama de marca en vez de poner la menos mala**. Un hueco elegante
se ve mejor que una foto fea.

**Versión definitiva — aquí sí se cierra.**
Lo que se publica solo puede salir de: fotos del cliente, stock con licencia comercial
verificada, o imágenes generadas con IA. Openverse no llega a producción, porque en
estética y bienestar su calidad no da el nivel. Antes de publicar hay que confirmar que
no queda ninguna imagen provisional.

**Ninguna regla de este archivo es motivo para entregar una página vacía.** Si una regla
choca con poder enseñar el resultado, avisa y propone la salida, como corresponde, pero
la maqueta sale.

### 2.2 Antes de colocar una foto, avisar
Antes de poner una imagen hay que decir **qué hueco llena y por qué esa**.
Nada de rellenar huecos en silencio.

### 2.3 Sustituir una foto = cambiar un archivo
Cada imagen se referencia de forma que cambiarla sea **reemplazar el archivo**,
sin tocar el HTML. Nombre de archivo estable, ruta estable.

---

## 3. Funciones interactivas

### 3.1 Capa a pantalla completa, no una sección más
Las funciones interactivas (asistente, diagnóstico capilar, calculadoras,
lectores) van como **capa a pantalla completa con pasos encadenados**.
Nunca como una sección más dentro del scroll de la página.

### 3.2 Los modos de respaldo no simulan a la IA
Si la IA no respondió, **el texto no puede aparentar que sí**.
Prohibido escribir "te recomendamos…", "según tu caso…" o cualquier frase que
suene a respuesta personalizada cuando no hubo respuesta. El respaldo dice con
claridad que en ese momento no se pudo analizar y ofrece la vía humana.

---

## 4. IA (Gemini)

### 4.1 Los nombres de modelo caducan — hay que comprobarlos llamando
La lista oficial de Google **incluye modelos que devuelven 404 al llamarlos**.
Antes de fijar un modelo hay que **llamar de verdad a cada candidato** y usar el
primero que responda de verdad.

**Registro de comprobación (actualizar aquí cada vez):**

| Modelo elegido | Fecha de comprobación | Candidatos probados y resultado |
|---|---|---|
| — (pendiente) | — | — |

### 4.2 Prohibido publicar sin probar la IA en local con PHP
Antes de publicar hay que haber levantado el proyecto en local con PHP y
**haber visto funcionar el modo principal**, no solo el respaldo.

### 4.3 Checklist obligatorio antes de publicar
- [ ] `DIAGNOSTICO` en **false**.
- [ ] `setup.php` **borrado**.
- [ ] Comprobado y **dicho explícitamente al usuario**, no dado por hecho.

---

## 5. Idioma y moneda

Cliente real en Colombia:
- **Español de Colombia.**
- **Pesos colombianos (COP).**
- **Nada de lenguaje de España** (ni "vosotros", ni "coger", ni €, ni "móvil"
  por celular, ni "ordenador" por computador).

---

## 6. La web de la competencia

Existe una web de referencia, **superalisadosbyjulianamatiz.com**, competencia
directa del cliente en la misma ciudad.

- **NO abrirla.**
- **NO descargar nada de ella.**
- **NO copiar** su código, sus textos, sus imágenes ni su paleta.
- Si en algún momento se pide algo que se parezca a esa web,
  **avisar al usuario en vez de hacerlo**.

---

## 7. Honestidad del contenido

### 7.1 No inventar
Nada de servicios, precios, credenciales, testimonios ni resultados inventados.
Si un dato no está en el brief: escribir **"—"** y **avisar al usuario**.

### 7.2 Cosmético, no médico
BRAVA es un negocio **cosmético y preventivo**.
- Nunca escribir que BRAVA **diagnostica** o **trata patologías**.
- Nunca prometer **resultados de salud**.
- El vocabulario es de cuidado, rutina y cosmética capilar, no de clínica.

---

## 8. Entorno de este equipo

PHP no venía instalado en este Mac y no había Homebrew, así que se instaló un
PHP independiente (no necesita contraseña de administrador ni toca el sistema):

- **Binario:** `~/.local/bin/php` — PHP 8.4.23, con `curl`, `openssl`,
  `fileinfo`, `mbstring`, `gd`, `session` y `zip` (todo lo que necesitan las
  funciones de IA).
- Se añadió `~/.local/bin` al `PATH` en `~/.zshrc`.

**Comando para arrancar la vista previa** (desde la carpeta del proyecto):

```
cd "/Users/sergio.c/Documents/Webs (with claude)/brava-hair-lab"
php -S localhost:8000
```

Y abrir en el navegador: **http://localhost:8000**
Para parar el servidor: `Ctrl + C` en esa terminal.
