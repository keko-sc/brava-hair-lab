/* ══════════════════════════════════════════════════════════════════
   BRAVA HAIR LAB · main.js
   Mecanismos reutilizados del proyecto Escobar: revelados, titulares
   partidos en líneas, cifras que cuentan, nav que se compacta, capa a
   pantalla completa y WhatsApp flotante.
   Los 24 protocolos se leen de assets/docs/02-CATALOGO.json: ese
   archivo es el origen de los datos, aquí no hay ninguno escrito.
   ══════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  /* WhatsApp y reservas. Un solo sitio: si cambian, cambian en toda la web. */
  var WA_NUMERO = "573205830720";          // +57 320 583 0720
  var WA_MENSAJE = "Hola, vengo de la web de BRAVA y quiero agendar mi valoración.";
  var AGENDA = "https://bravahairlab.site.agendapro.com/co";

  var RUTA = "assets/docs/02-CATALOGO.json";
  var CAT = null;

  var q  = function (s, r) { return (r || document).querySelector(s); };
  var qa = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reducido = matchMedia("(prefers-reduced-motion: reduce)").matches;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function safe(fn, n) { try { fn(); } catch (e) { if (window.console) console.warn("[" + n + "]", e); } }
  function frase1(t) { if (!t) return ""; var i = t.indexOf(". "); return i > 0 ? t.slice(0, i + 1) : t; }

  /* ═══════════ 1 · El menú: altura real medida, no estimada ═══════════ */
  function initNav() {
    var nav = q("[data-nav]");
    if (!nav) return;

    var medir = function () {
      var h = Math.round(nav.getBoundingClientRect().height);
      if (h > 0) {
        document.documentElement.style.setProperty("--nav-real", h + "px");
        // Encima de la portada ya solo está el menú: la banda de aviso
        // se fue al final de la página.
        document.documentElement.style.setProperty("--tope", h + "px");
      }
      // La portada se ajusta para que la primera pantalla termine en la
      // banda de sellos completa y la tira de nombres quede por debajo.
      var banda = q("#apto");
      if (banda) {
        var bh = Math.round(banda.getBoundingClientRect().height);
        if (bh > 0) document.documentElement.style.setProperty("--banda-h", bh + "px");
      }
    };
    medir();
    if (window.ResizeObserver) new ResizeObserver(medir).observe(nav);
    window.addEventListener("resize", medir);
    window.addEventListener("load", medir);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(medir);

    var marcar = function () {
      nav.classList.toggle("is-fija", window.scrollY > 24);
      medir();
    };
    marcar();
    window.addEventListener("scroll", marcar, { passive: true });

    var burger = q("[data-burger]"), menu = q("[data-menu]");
    if (!burger || !menu) return;
    function abrir(si) {
      burger.setAttribute("aria-expanded", String(si));
      if (si) {
        menu.hidden = false;
        requestAnimationFrame(function () { menu.classList.add("is-abierto"); });
      } else {
        menu.classList.remove("is-abierto");
        setTimeout(function () { if (burger.getAttribute("aria-expanded") === "false") menu.hidden = true; }, 400);
      }
    }
    burger.addEventListener("click", function () { abrir(burger.getAttribute("aria-expanded") !== "true"); });
    qa("a, button", menu).forEach(function (a) { a.addEventListener("click", function () { abrir(false); }); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") abrir(false); });
  }

  /* ═══════════ 2 · Titulares partidos en líneas ═══════════ */
  function partirLineas(el) {
    var nodos = [], grupos = [], texto = el.innerHTML;
    el.dataset.original = texto;
    // Cada palabra a un span para medir dónde rompe la línea
    el.innerHTML = el.textContent.replace(/\s+/g, " ").trim()
      .split(" ").map(function (p) { return '<i class="w">' + esc(p) + "</i>"; }).join(" ");
    // <br> explícitos del HTML original se respetan partiendo por ellos
    if (/<br\s*\/?>/i.test(texto)) {
      el.innerHTML = texto.split(/<br\s*\/?>/i).map(function (tr) {
        return '<span class="ln"><span class="ln-i">' + tr.trim() + "</span></span>";
      }).join("\n");
      return;
    }
    nodos = qa(".w", el);
    var arriba = null, actual = null;
    nodos.forEach(function (n) {
      var t = Math.round(n.offsetTop);
      if (arriba === null || Math.abs(t - arriba) > 4) { arriba = t; actual = []; grupos.push(actual); }
      actual.push(n.textContent);
    });
    el.innerHTML = grupos.map(function (g, i) {
      return '<span class="ln"><span class="ln-i">' + esc(g.join(" ")) + (i < grupos.length - 1 ? "\n" : "") + "</span></span>";
    }).join("");
  }
  function initSplit() { qa("[data-split]").forEach(function (el) { safe(function () { partirLineas(el); }, "split"); }); }

  /* ═══════════ 3 · Revelados, escalonados y cifras ═══════════ */
  function contar(el) {
    if (!el || el.dataset.contando) return;
    el.dataset.contando = "1";
    var fin = parseInt(el.getAttribute("data-count"), 10) || 0, ini = performance.now();
    (function paso(t) {
      var p = Math.min(1, (t - ini) / 1100);
      el.textContent = String(Math.round(fin * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(paso); else el.textContent = String(fin);
    })(ini);
  }
  function initReveals() {
    var objetivos = qa(".reveal, [data-split], [data-count], [data-escalonado]");
    if (!objetivos.length) return;
    function mostrar(el) {
      el.classList.add("is-visible");
      if (el.hasAttribute("data-split")) el.classList.add("is-in");
      if (el.hasAttribute("data-count")) contar(el);
    }
    if (!("IntersectionObserver" in window)) { objetivos.forEach(mostrar); return; }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { mostrar(e.target); io.unobserve(e.target); } });
    }, { threshold: 0.05, rootMargin: "0px 0px -5% 0px" });
    objetivos.forEach(function (el) { io.observe(el); });
    // Red de seguridad: pase lo que pase, a los 4 s está todo visible
    setTimeout(function () { objetivos.forEach(mostrar); }, 4000);
  }

  /* ═══════════ 4 · Huecos de foto
     Cada hueco apunta a un archivo. Si el archivo existe, la foto lo
     rellena. Sustituir una foto = dejar el archivo en su sitio. ═══════ */
  /* Antes esto probaba el archivo con new Image() y el src se asignaba de
     inmediato: el navegador se descargaba los veintitantos huecos de golpe y
     el loading="lazy" llegaba tarde, cuando la imagen ya estaba en memoria.
     Ahora el <img> entra en el DOM con sus atributos puestos ANTES del src,
     así que la carga diferida la decide el navegador de verdad. El hueco que
     no tenga archivo se queda con la trama: el onerror retira la imagen. */
  function esDelHero(fig) { return !!(fig.closest && fig.closest("[data-escenas]")); }

  function montarFoto(fig) {
    if (fig.dataset.probado === "si") return;
    var archivo = fig.getAttribute("data-archivo");
    if (!archivo) return;
    fig.dataset.probado = "si";

    var img = document.createElement("img");
    img.alt = "";                                  // hasta que cargue no anuncia nada
    img.decoding = "async";
    if (esDelHero(fig)) {
      // La portada se ve de entrada: no tiene sentido diferirla.
      img.loading = "eager";
      img.setAttribute("fetchpriority", "high");
    } else {
      img.loading = "lazy";
    }
    img.addEventListener("load", function () {
      img.alt = fig.getAttribute("title") || "";
      fig.classList.add("llena");
      document.dispatchEvent(new CustomEvent("foto-lista", { detail: fig }));
    });
    img.addEventListener("error", function () {
      // Hueco todavía sin foto: fuera la imagen, se queda la trama de marca.
      if (img.parentNode) img.parentNode.removeChild(img);
      fig.dataset.probado = "";
    });
    fig.insertBefore(img, fig.firstChild);
    img.src = archivo;                             // el src, lo último
  }
  function initFotos() { qa("[data-foto]").forEach(montarFoto); }

  /* ═══════════ 5 · Capas a pantalla completa ═══════════
     El estado vive aquí. Ojo con scrollY: el archivo va en modo estricto y
     window.scrollY es de solo lectura, así que si esta declaración falta,
     asignarlo lanza excepción y la capa no llega a abrirse. */
  var capaActiva = null, focoPrevio = null, scrollY = 0;
  /* Las capas se apilan: desde el catálogo se abre la ficha encima y al
     cerrarla se vuelve al catálogo. Solo al cerrar la última se devuelve
     el scroll de la página. */
  var pila = [];

  function abrirCapa(capa) {
    if (!capa) return;
    if (capaActiva && capaActiva !== capa) {
      var debajo = capaActiva;
      pila.push(debajo);
      debajo.classList.remove("esta-abierta");
      setTimeout(function () { if (pila.indexOf(debajo) !== -1) debajo.hidden = true; }, 320);
    } else if (!capaActiva) {
      focoPrevio = document.activeElement;
      scrollY = window.scrollY;
      document.body.style.top = -scrollY + "px";
      document.body.classList.add("capa-abierta");
    }
    capa.hidden = false;
    requestAnimationFrame(function () { capa.classList.add("esta-abierta"); });
    capaActiva = capa;
    var x = q(".capa-x", capa); if (x) x.focus();
  }
  function cerrarCapa() {
    if (!capaActiva) return;
    var capa = capaActiva;
    capa.classList.remove("esta-abierta");
    setTimeout(function () { if (capaActiva !== capa) capa.hidden = true; }, 320);

    var debajo = pila.pop();
    if (debajo) {                       // vuelve a la capa que había debajo
      capaActiva = debajo;
      debajo.hidden = false;
      requestAnimationFrame(function () { debajo.classList.add("esta-abierta"); });
      var xb = q(".capa-x", debajo); if (xb) xb.focus();
      return;
    }
    capaActiva = null;
    setTimeout(function () { capa.hidden = true; }, 320);
    document.body.classList.remove("capa-abierta");
    document.body.style.top = "";
    window.scrollTo(0, scrollY);
    if (focoPrevio && focoPrevio.focus) focoPrevio.focus();
  }
  document.addEventListener("keydown", function (e) {
    if (!capaActiva) return;
    if (e.key === "Escape") { e.preventDefault(); cerrarCapa(); return; }
    if (capaActiva.id === "capa-protocolo") {
      if (e.key === "ArrowRight") { e.preventDefault(); moverDetalle(1); }
      if (e.key === "ArrowLeft")  { e.preventDefault(); moverDetalle(-1); }
    }
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest) return;
    if (e.target.closest("[data-capa-cerrar]")) cerrarCapa();
    var f = e.target.closest("[data-detalle]");
    if (f) moverDetalle(parseInt(f.getAttribute("data-detalle"), 10));
  });

  /* ═══════════ 7 · Catálogo ═══════════ */
  var PESTANAS = { fiber: ["fiber-alineacion", "fiber-ritual"], scalp: ["scalp-experiencia", "scalp-rootlounge"], addon: ["addon"] };
  var GRUPO_FOTO = {
    "fiber-alineacion":  { r: "4:5", t: "Alineaciones moleculares: la misma clienta, mismo encuadre, cabello distinto según el sistema." },
    "fiber-ritual":      { r: "1:1", t: "The Ritual Menu: detalle de textura y producto más que de personas." },
    "scalp-experiencia": { r: "3:2", t: "SCALP · Experiencias." },
    "scalp-rootlounge":  { r: "4:5", t: "SCALP · Root Lounge." },
    "addon":             { r: "1:1", t: "Add-ons." }
  };
  var NOMBRE_GRUPO = {
    "fiber-alineacion": "BRAVA FIBER · Alineaciones moleculares",
    "fiber-ritual": "BRAVA FIBER · The Ritual Menu",
    "scalp-experiencia": "BRAVA SCALP · Experiencias",
    "scalp-rootlounge": "BRAVA SCALP · Root Lounge",
    "addon": "Add-Ons"
  };
  var NOMBRE_FAMILIA = { fiber: "BRAVA FIBER", scalp: "BRAVA SCALP", addon: "Add-Ons" };
  var famActiva = "fiber";

  function protocolo(id) { return CAT.protocolos.filter(function (p) { return p.id === id; })[0] || null; }
  function figuraHTML(p, clase) {
    var g = GRUPO_FOTO[p.familia] || { r: "1:1", t: "" };
    return '<figure class="' + (clase || "arco-sm") + '" data-foto="' + esc(p.foto) + '" data-ratio="' + esc(g.r) + '"' +
      ' data-archivo="assets/img/' + esc(String(p.foto).toLowerCase()) + '.webp"' +
      ' title="' + esc(g.t + " Protocolo: " + p.nombre + ".") + '">' +
      '<span class="trama" aria-hidden="true"></span><span class="foto-tag">' + esc(p.foto) + '</span></figure>';
  }
  function datoCorto(p) {
    var d = p.datos || {}, k = Object.keys(d);
    if (d["Duración"]) return d["Duración"];
    if (d["Duración estimada"]) return d["Duración estimada"];
    if (d["Frecuencia recomendada"]) return "Cada ciclo";
    return k.length ? String(d[k[0]]).split("·")[0].trim().slice(0, 26) : "";
  }
  function tarjetaHTML(p) {
    var corto = datoCorto(p);
    return '<button class="tarjeta' + (p.destacado ? " tarjeta-destacada" : "") + '" type="button" data-protocolo="' + esc(p.id) + '">' +
      '<span class="tarjeta-top"><span class="tarjeta-nombre">' + esc(p.nombre) + '</span>' +
      (corto ? '<span class="tarjeta-meta">' + esc(corto) + '</span>' : '') + '</span>' +
      '<span class="tarjeta-sub">' + esc(p.subtitulo || "") + '</span>' +
      '<span class="tarjeta-txt">' + esc(frase1(p.descripcion)) + '</span>' +
      '<span class="tarjeta-para"><span class="tarjeta-para-et">Indicado si</span> ' + esc(frase1(p.idealPara || "—")) + '</span>' +
      '<span class="tarjeta-mas">Ver el protocolo</span>' +
    '</button>';
  }

  /* ── El catálogo entero, dentro de la capa ──
     En la página solo queda el bloque de entrada. Aquí van las tres familias
     en píldoras y, debajo, sus protocolos en tarjetas. */
  function construirCatalogoCapa() {
    var capa = q("#capa-catalogo"); if (!capa || !CAT) return;
    capa.innerHTML =
      '<header class="capa-cab">' +
        '<p class="capa-marca">El catálogo · 24 protocolos</p>' +
        '<button class="capa-x" type="button" data-capa-cerrar aria-label="Cerrar el catálogo">' +
          '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>' +
        '</button></header>' +
      '<div class="capa-scroll"><div class="capa-dentro">' +
        '<nav class="fam-tabs" role="tablist" aria-label="Familias de protocolo">' +
          Object.keys(PESTANAS).map(function (f) {
            var n = CAT.protocolos.filter(function (p) { return PESTANAS[f].indexOf(p.familia) !== -1; }).length;
            return '<button class="fam" type="button" role="tab" data-fam="' + f + '"' +
              ' aria-selected="' + (f === famActiva) + '" aria-controls="cat-panel">' +
              esc(NOMBRE_FAMILIA[f]) + ' <span>' + n + '</span></button>';
          }).join("") +
        '</nav>' +
        '<div class="cat-panel" id="cat-panel" role="tabpanel" data-cat-panel></div>' +
      '</div></div>';
    pintarFamilia(famActiva);
  }
  function pintarFamilia(f) {
    if (!PESTANAS[f]) return;
    famActiva = f;
    qa("#capa-catalogo .fam").forEach(function (b) {
      b.setAttribute("aria-selected", String(b.getAttribute("data-fam") === f));
    });
    var panel = q("[data-cat-panel]"); if (!panel) return;
    panel.innerHTML = PESTANAS[f].map(function (g) {
      var ps = CAT.protocolos.filter(function (p) { return p.familia === g; });
      if (!ps.length) return "";
      return '<div class="cat-bloque">' +
        '<p class="cat-bloque-t">' + esc((NOMBRE_GRUPO[g] || g).split(" · ").pop()) +
          '<span>' + ps.length + '</span></p>' +
        '<div class="tarjetas">' + ps.map(tarjetaHTML).join("") + "</div></div>";
    }).join("");
    var s = q("#capa-catalogo .capa-scroll"); if (s) s.scrollTop = 0;
  }

  function montarCatalogo() {
    construirCatalogoCapa();
    document.addEventListener("click", function (e) {
      if (!e.target.closest) return;
      var fam = e.target.closest("#capa-catalogo .fam");
      if (fam) { pintarFamilia(fam.getAttribute("data-fam")); return; }
      var t = e.target.closest("[data-protocolo]");
      if (t) abrirDetalle(t.getAttribute("data-protocolo"));
    });
  }

  /* Detalle en capa, con flechas */
  var lista = [], indice = 0;
  function abrirDetalle(id) {
    var p = protocolo(id); if (!p) return;
    var fams = PESTANAS[famActiva] || [];
    if (fams.indexOf(p.familia) === -1) {
      Object.keys(PESTANAS).forEach(function (k) { if (PESTANAS[k].indexOf(p.familia) !== -1) fams = PESTANAS[k]; });
    }
    lista = CAT.protocolos.filter(function (x) { return fams.indexOf(x.familia) !== -1; });
    indice = lista.map(function (x) { return x.id; }).indexOf(id);
    if (indice < 0) indice = 0;
    pintarDetalle();
    abrirCapa(q("#capa-protocolo"));
  }
  function moverDetalle(paso) {
    if (!lista.length) return;
    indice = (indice + paso + lista.length) % lista.length;
    pintarDetalle();
  }
  /* El contexto editorial del grupo —la ciencia, las ideas, los avisos, los
     descansos— ya no ocupa la sección: se lee aquí, plegado, al abrir
     cualquier protocolo de ese grupo. */
  function contextoHTML(familia) {
    var fuente = q('[data-contexto="' + familia + '"]');
    if (!fuente) return "";
    return '<details class="detalle-ctx"><summary>Sobre ' + esc(NOMBRE_GRUPO[familia] || "este grupo") +
      "</summary><div class=\"detalle-ctx-in\">" + fuente.innerHTML + "</div></details>";
  }

  function pintarDetalle() {
    var capa = q("#capa-protocolo"), p = lista[indice];
    if (!capa || !p) return;
    var d = p.datos || {}, dl = "";
    if (p.resultado) dl += "<div><dt>Resultado</dt><dd>" + esc(p.resultado) + "</dd></div>";
    if (p.idealPara) dl += "<div><dt>Ideal para</dt><dd>" + esc(p.idealPara) + "</dd></div>";
    Object.keys(d).forEach(function (k) { dl += "<div><dt>" + esc(k) + "</dt><dd>" + esc(d[k]) + "</dd></div>"; });
    dl += '<div><dt>Precio</dt><dd><span class="pendiente">PENDIENTE: precio</span></dd></div>';

    capa.innerHTML =
      '<header class="capa-cab">' +
        '<p class="capa-marca">' + esc(NOMBRE_GRUPO[p.familia] || "Protocolo") + '</p>' +
        '<button class="capa-x" type="button" data-capa-cerrar aria-label="Cerrar">' +
          '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>' +
        '</button></header>' +
      '<div class="capa-scroll"><div class="capa-dentro"><article class="detalle">' +
        figuraHTML(p, "arco detalle-fig") +
        '<div class="detalle-cuerpo">' +
          '<h2 class="detalle-t" tabindex="-1">' + esc(p.nombre) + '</h2>' +
          '<p class="detalle-sub">' + esc(p.subtitulo || "") + '</p>' +
          '<p>' + esc(p.descripcion) + '</p>' +
          '<dl class="detalle-datos">' + dl + '</dl>' +
          (p.incluye && p.incluye.length
            ? '<p class="detalle-sub">Incluye</p><ul class="detalle-lista">' +
              p.incluye.map(function (i) { return "<li>" + esc(i) + "</li>"; }).join("") + "</ul>" : "") +
          (p.avisoEspecial ? '<p class="detalle-aviso">' + esc(p.avisoEspecial) + "</p>" : "") +
        '</div></article>' + contextoHTML(p.familia) + '</div></div>' +
      '<div class="capa-pie"><span class="capa-indice">' + (indice + 1) + " / " + lista.length + '</span>' +
        '<span class="capa-nav">' +
          '<button class="capa-flecha" type="button" data-detalle="-1">← Anterior</button>' +
          '<button class="capa-flecha" type="button" data-detalle="1">Siguiente →</button>' +
        '</span></div>';
    initFotos();
    var h = q(".detalle-t", capa); if (h) h.focus({ preventScroll: true });
    var s = q(".capa-scroll", capa); if (s) s.scrollTop = 0;
  }

  /* ═══════════ 8 · Buscador de protocolo ═══════════ */
  var DIB = {
    liso:     "M15 7 L15 37 M22 7 L22 37 M29 7 L29 37",
    ondulado: "M15 7 C21 13 9 19 15 25 C21 31 9 34 15 37 M29 7 C35 13 23 19 29 25 C35 31 23 34 29 37",
    rizado:   "M16 7 C25 11 7 15 16 19 C25 23 7 27 16 31 C25 34 9 36 16 38 M30 7 C39 11 21 15 30 19 C39 23 21 27 30 31",
    afro:     "M16 7 C27 9 6 12 16 14 C27 16 6 19 16 21 C27 23 6 26 16 28 C27 30 6 33 16 35 C24 36 12 38 16 39"
  };
  var F_ESTADO = { sana: "para cabello sano", leve: "para cabello un poco maltratado", danada: "para cabello bastante dañado y poroso", sos: "para cabello que se estira y se quiebra" };
  var F_PATRON = { liso: "liso", ondulado: "ondulado", rizado: "rizado", afro: "muy rizado o afro" };
  var F_OBJ = { alisar: "alisar el cabello", frizz: "controlar el frizz", reparar: "reparar el daño", nutrir: "nutrir e hidratar", grosor: "dar grosor y cuerpo", scalp: "cuidar el cuero cabelludo", color: "proteger el color" };

  var sel = { objetivo: null, patron: null, estado: null, condiciones: [] };
  var PASOS = ["1", "2", "3", "4", "r"], paso = "1";

  function etiqueta(eje, id) { var e = (CAT.ejes[eje] || []).filter(function (o) { return o.id === id; })[0]; return e ? e.label : id; }
  function motivoCond(id) { var c = (CAT.ejes.condicion || []).filter(function (o) { return o.id === id; })[0]; return c && c.motivo ? c.motivo : "No es apto en tu caso."; }
  function regla(id) { var r = (CAT.reglas_extra || []).filter(function (x) { return x.id === id; })[0]; return r ? r.texto : ""; }

  function calcular(s) {
    var conds = (s.condiciones || []).filter(function (c) { return c !== "ninguna"; });
    var principal = [], comple = [], descartes = [];
    CAT.protocolos.forEach(function (p) {
      var r = p.reglas || {}, motivo = null;
      var choque = conds.filter(function (c) { return (r.excluye || []).indexOf(c) !== -1; })[0];
      if (choque) motivo = motivoCond(choque);
      else if ((r.estado || []).indexOf(s.estado) === -1) motivo = "No está indicado " + (F_ESTADO[s.estado] || "para ese estado") + ".";
      else if ((r.patron || []).indexOf(s.patron) === -1) motivo = "No está indicado para cabello " + (F_PATRON[s.patron] || "de ese patrón") + ".";
      else if (!(r.objetivo || []).length) motivo = "Es un servicio de acabado: no se elige por objetivo.";
      else if ((r.objetivo || []).indexOf(s.objetivo) === -1) motivo = "No está orientado a " + (F_OBJ[s.objetivo] || "ese objetivo") + ".";
      if (motivo) { descartes.push({ p: p, motivo: motivo }); return; }
      if (p.id === "diagnostico-ia") return;
      if (p.esComplemento) comple.push(p); else principal.push(p);
    });
    var prec = function (p) { var r = p.reglas || {}; return (4 - (r.patron || []).length) + (4 - (r.estado || []).length) + (7 - (r.objetivo || []).length); };
    principal.sort(function (a, b) { return prec(b) - prec(a); });
    var tambien = principal.slice(4); principal = principal.slice(0, 4);

    var notas = [], hayAlin = principal.some(function (p) { return p.familia === "fiber-alineacion"; });
    if (hayAlin) {
      var sh = protocolo("shield");
      if (sh) {
        descartes = descartes.filter(function (x) { return x.p.id !== "shield"; });
        if (comple.indexOf(sh) === -1) comple.unshift(sh);
        notas.push({ para: "shield", texto: regla("shield_con_alineacion") });
      }
    }
    var hayDetox = principal.some(function (p) { return p.id === "detox-360"; });
    if (comple.some(function (p) { return p.id === "oiling"; }) && (hayAlin || hayDetox)) {
      notas.push({ para: "oiling", texto: regla("oiling_incompatible") });
    }
    return { principal: principal, comple: comple, tambien: tambien, descartes: descartes, notas: notas,
             diag: protocolo("diagnostico-ia"), textoDiag: regla("diagnostico_siempre") };
  }

  /* Cuando no hay coincidencia se busca el mensaje que corresponda.
     Nunca una pantalla vacía. */
  function mensajeSinResultado(s) {
    var bloque = CAT.mensajes_sin_resultado;
    if (!bloque || !bloque.reglas) return null;
    for (var i = 0; i < bloque.reglas.length; i++) {
      var r = bloque.reglas[i], c = r.cuando || {}, encaja = true;
      Object.keys(c).forEach(function (k) { if (s[k] !== c[k]) encaja = false; });
      if (encaja) return r;
    }
    return null;
  }

  var recomendado = "";      // el nombre del protocolo principal recomendado
  function mensajeWA(marcados) {
    var l = ["Hola BRAVA Hair Lab. Usé el buscador de protocolo de la web.", ""];
    l.push("Lo que busco: " + etiqueta("objetivo", sel.objetivo));
    l.push("Mi cabello es: " + etiqueta("patron", sel.patron));
    l.push("Lo siento: " + etiqueta("estado", sel.estado));
    var c = sel.condiciones.filter(function (x) { return x !== "ninguna"; });
    if (c.length) l.push("A tener en cuenta: " + c.map(function (x) { return etiqueta("condicion", x); }).join(", "));
    l.push("");
    if (marcados.length) { l.push("Me interesan estos protocolos:"); marcados.forEach(function (n) { l.push("· " + n); }); }
    else if (recomendado) l.push("El buscador me recomendó: " + recomendado);
    else l.push("Todavía no marqué ningún protocolo.");
    l.push("", "Quiero agendar mi valoración.");
    return l.join("\n");
  }
  function enlaceWA(t) { return "https://wa.me/" + WA_NUMERO + "?text=" + encodeURIComponent(t || WA_MENSAJE); }

  function opcionHTML(eje, o, dib) {
    return '<button class="opcion" type="button" data-eje="' + eje + '" data-valor="' + esc(o.id) + '">' +
      (dib && DIB[o.id] ? '<svg class="opcion-dib" viewBox="0 0 44 44" aria-hidden="true"><path d="' + DIB[o.id] + '"/></svg>' : "") +
      '<span class="opcion-txt">' + esc(o.label) + '</span><span class="opcion-marca" aria-hidden="true"></span></button>';
  }

  function construirBuscador() {
    var capa = q("#capa-buscador"); if (!capa) return;
    var e = CAT.ejes;
    capa.innerHTML =
      '<header class="capa-cab">' +
        '<p class="capa-marca">✦ Buscador de protocolo</p>' +
        '<ol class="capa-guia">' +
          '<li data-guia="1" aria-current="step"><span aria-hidden="true">1</span> Qué buscas</li>' +
          '<li data-guia="2"><span aria-hidden="true">2</span> Tu cabello</li>' +
          '<li data-guia="3"><span aria-hidden="true">3</span> Cómo lo sientes</li>' +
          '<li data-guia="4"><span aria-hidden="true">4</span> Situaciones</li>' +
        '</ol>' +
        '<button class="capa-x" type="button" data-capa-cerrar aria-label="Cerrar el buscador">' +
          '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>' +
        '</button></header>' +
      '<div class="capa-scroll"><div class="capa-dentro">' +
        '<section class="paso-c" data-paso="1">' +
          '<h2 class="capa-titulo" tabindex="-1">¿Qué buscas?</h2>' +
          '<p class="capa-sub">Cuatro preguntas. Te decimos qué protocolos encajan con tu cabello y por qué, solo con lo que hacemos aquí.</p>' +
          '<div class="opciones opciones-2">' + e.objetivo.map(function (o) { return opcionHTML("objetivo", o); }).join("") + "</div>" +
        "</section>" +
        '<section class="paso-c" data-paso="2" hidden>' +
          '<button class="volver" type="button" data-ir="1">← Volver</button>' +
          '<h2 class="capa-titulo" tabindex="-1">¿Cómo es tu cabello?</h2><p class="capa-sub">Elige el que más se parezca.</p>' +
          '<div class="opciones opciones-2">' + e.patron.map(function (o) { return opcionHTML("patron", o, true); }).join("") + "</div>" +
        "</section>" +
        '<section class="paso-c" data-paso="3" hidden>' +
          '<button class="volver" type="button" data-ir="2">← Volver</button>' +
          '<h2 class="capa-titulo" tabindex="-1">¿Cómo lo sientes?</h2><p class="capa-sub">Sé honesta: de esto depende lo que te podamos ofrecer.</p>' +
          '<div class="opciones">' + e.estado.map(function (o) { return opcionHTML("estado", o); }).join("") + "</div>" +
        "</section>" +
        '<section class="paso-c" data-paso="4" hidden>' +
          '<button class="volver" type="button" data-ir="3">← Volver</button>' +
          '<h2 class="capa-titulo" tabindex="-1">¿Alguna de estas situaciones?</h2><p class="capa-sub">Puedes marcar varias, o marcar «Ninguna».</p>' +
          '<div class="opciones">' + e.condicion.map(function (o) { return opcionHTML("condicion", o); }).join("") + "</div>" +
          '<div class="capa-acciones"><button class="btn btn-acento" type="button" data-ver>Ver mi resultado</button></div>' +
        "</section>" +
        '<section class="paso-c" data-paso="r" hidden></section>' +
      "</div></div>" +
      '<div class="capa-pie"><span>' + esc(CAT.avisos.cierre_buscador) + "</span></div>";
    capa.addEventListener("click", alClicar);
  }

  function irAPaso(p) {
    paso = p;
    qa("#capa-buscador .paso-c").forEach(function (s) { s.hidden = s.getAttribute("data-paso") !== p; });
    var n = PASOS.indexOf(p);
    qa("#capa-buscador .capa-guia li").forEach(function (li, i) {
      li.classList.toggle("hecho", i < n);
      if (i === n) li.setAttribute("aria-current", "step"); else li.removeAttribute("aria-current");
    });
    var s = q("#capa-buscador .capa-scroll"); if (s) s.scrollTop = 0;
    var h = q('#capa-buscador .paso-c[data-paso="' + p + '"] .capa-titulo, #capa-buscador .paso-c[data-paso="' + p + '"] .res-titulo');
    if (h) h.focus({ preventScroll: true });
  }

  function alClicar(ev) {
    var t = ev.target;
    var ir = t.closest("[data-ir]"); if (ir) { irAPaso(ir.getAttribute("data-ir")); return; }
    var op = t.closest(".opcion");
    if (op) {
      var eje = op.getAttribute("data-eje"), val = op.getAttribute("data-valor");
      if (eje === "condicion") {
        var L = sel.condiciones;
        if (val === "ninguna") sel.condiciones = L.indexOf("ninguna") === -1 ? ["ninguna"] : [];
        else { L = L.filter(function (c) { return c !== "ninguna"; }); var i = L.indexOf(val); if (i === -1) L.push(val); else L.splice(i, 1); sel.condiciones = L; }
        qa('#capa-buscador .opcion[data-eje="condicion"]').forEach(function (b) {
          b.classList.toggle("elegida", sel.condiciones.indexOf(b.getAttribute("data-valor")) !== -1);
        });
        return;
      }
      sel[eje] = val;
      qa('#capa-buscador .opcion[data-eje="' + eje + '"]').forEach(function (b) { b.classList.toggle("elegida", b === op); });
      var sig = { objetivo: "2", patron: "3", estado: "4" }[eje];
      if (sig) setTimeout(function () { irAPaso(sig); }, reducido ? 0 : 170);
      return;
    }
    if (t.closest("[data-ver]")) { mostrarResultado(); return; }
    if (t.closest("[data-reiniciar]")) {
      sel = { objetivo: null, patron: null, estado: null, condiciones: [] };
      qa("#capa-buscador .opcion").forEach(function (b) { b.classList.remove("elegida"); });
      irAPaso("1"); return;
    }
    var item = t.closest(".res-item");
    if (item && t.tagName !== "INPUT") {
      var c = item.querySelector("input");
      if (c) { c.checked = !c.checked; item.classList.toggle("elegido", c.checked); }
    }
    if (item) refrescarWA();
  }

  function itemHTML(p, marcado) {
    return '<div class="res-item' + (marcado ? " elegido" : "") + '">' +
      '<label class="res-cab"><input type="checkbox" data-nombre="' + esc(p.nombre) + '"' + (marcado ? " checked" : "") + ">" +
      '<span><span class="res-nombre">' + esc(p.nombre) + '</span><span class="res-sub">' + esc(p.subtitulo || "") + "</span></span></label>" +
      '<p class="res-que">' + esc(frase1(p.descripcion)) + "</p>" +
      '<p class="res-porque"><strong>Por qué encaja contigo:</strong> ' + esc(p.porQue || "") + "</p></div>";
  }

  /* El enlace de WhatsApp del buscador se mantiene armado en todo momento:
     con lo que esté marcado, o con el protocolo recomendado si no se marcó
     nada. Así un solo clic abre WhatsApp, sin pasos intermedios. */
  function refrescarWA() {
    var wa = q("[data-wa-buscador]"); if (!wa) return;
    var marcados = qa("#capa-buscador .res-item input:checked").map(function (i) { return i.getAttribute("data-nombre"); });
    var txt = mensajeWA(marcados);
    wa.setAttribute("href", enlaceWA(txt));
    var caja = q("[data-wa-msg]"); if (caja) { caja.hidden = false; caja.textContent = txt; }
  }

  function mostrarResultado() {
    var r = calcular(sel), panel = q('#capa-buscador .paso-c[data-paso="r"]');
    if (!panel) return;
    // El primero de la lista es el que se recomienda: su nombre viaja en el
    // mensaje de WhatsApp aunque la clienta no marque nada.
    recomendado = r.principal.length ? r.principal[0].nombre : "";
    var resumen = etiqueta("objetivo", sel.objetivo) + " · cabello " + etiqueta("patron", sel.patron).toLowerCase() + " · " + etiqueta("estado", sel.estado).toLowerCase();
    var html = "";

    var bloqueDesc = function () {
      return '<div class="bloque-res"><details class="descartes"><summary>Qué descartamos y por qué (' + r.descartes.length + ")</summary>" +
        '<div class="descartes-lista">' + r.descartes.map(function (d) {
          return '<div><span class="desc-n">' + esc(d.p.nombre) + '</span><span class="desc-m">' + esc(d.motivo) + "</span></div>";
        }).join("") + "</div></details></div>";
    };
    var bloqueWA = function () {
      return '<div class="wa-caja"><h3>Llévate tu selección</h3>' +
        '<p class="res-que">Marca los protocolos que te interesan y armamos el mensaje con tu selección.</p>' +
        '<div class="capa-acciones">' +
          '<a class="btn btn-acento" href="' + AGENDA + '" target="_blank" rel="noopener">Agendar en línea</a>' +
          '<a class="btn btn-wa" href="#" target="_blank" rel="noopener" data-wa-buscador>Escribir por WhatsApp</a>' +
          '<button class="volver" type="button" data-reiniciar>← Empezar de nuevo</button>' +
        "</div><pre class=\"wa-msg\" data-wa-msg hidden></pre></div>";
    };

    if (r.principal.length === 0) {
      var m = mensajeSinResultado(sel);
      var sug = (m && m.sugiere ? m.sugiere : ["diagnostico-ia"]).map(protocolo).filter(Boolean);
      html += '<h2 class="res-titulo capa-titulo" tabindex="-1">' + esc(m ? m.titulo : "Esto lo vemos contigo") + "</h2>" +
        '<p class="capa-sub">' + esc(resumen) + "</p>" +
        '<div class="sin-res"><span class="trama" aria-hidden="true"></span>' +
          '<p class="sin-res-et">Por qué te decimos esto</p>' +
          "<p>" + esc(m ? m.texto : r.textoDiag) + "</p></div>" +
        '<div class="res-lista">' + sug.map(function (p) { return itemHTML(p, true); }).join("") + "</div>" +
        bloqueDesc() + bloqueWA();
    } else {
      html += '<h2 class="res-titulo capa-titulo" tabindex="-1">Esto encaja con tu cabello</h2>' +
        '<p class="capa-sub">' + esc(resumen) + "</p>" +
        '<div class="res-lista">' + r.principal.map(function (p) { return itemHTML(p, true); }).join("") + "</div>";
      if (r.tambien.length) {
        html += '<p class="tambien">También encajan, aunque son menos específicos para tu caso: ' +
          r.tambien.map(function (p) { return esc(p.nombre); }).join(" · ") + ".</p>";
      }
      var comps = r.comple.slice(); if (r.diag) comps.push(r.diag);
      if (comps.length) {
        html += '<div class="bloque-res"><h3>Complementos</h3>';
        comps.forEach(function (p) {
          html += itemHTML(p, false);
          r.notas.forEach(function (n) { if (n.para === p.id && n.texto) html += '<p class="nota-regla">' + esc(n.texto) + "</p>"; });
          if (p.id === "diagnostico-ia" && r.textoDiag) html += '<p class="nota-regla">' + esc(r.textoDiag) + "</p>";
        });
        html += "</div>";
      }
      html += bloqueDesc() + bloqueWA();
    }
    panel.innerHTML = html;
    refrescarWA();
    irAPaso("r");
  }

  function initBotones() {
    document.addEventListener("click", function (e) {
      var c = e.target.closest && e.target.closest("[data-abre-catalogo]");
      if (c) { e.preventDefault(); if (CAT) abrirCapa(q("#capa-catalogo")); return; }
      var b = e.target.closest && e.target.closest("[data-abre-capa]");
      if (!b) return;
      e.preventDefault();
      if (!CAT) return;
      abrirCapa(q("#capa-buscador"));
      irAPaso(paso === "r" ? "r" : "1");
    });
  }

  /* ═══════════ 9 · WhatsApp y reservas ═══════════ */
  function initWA() {
    // Todos los enlaces de WhatsApp de la página salen de aquí: mismo
    // número y mismo mensaje, y siempre en pestaña nueva.
    qa("[data-wa-simple]").forEach(function (a) {
      a.setAttribute("href", enlaceWA(WA_MENSAJE));
      a.setAttribute("target", "_blank");
      a.setAttribute("rel", "noopener");
    });
    // Lo mismo con la reserva en línea.
    qa("[data-agenda]").forEach(function (a) {
      a.setAttribute("href", AGENDA);
      a.setAttribute("target", "_blank");
      a.setAttribute("rel", "noopener");
    });
    // El botón flotante aparece al pasar la portada
    var fl = q(".wa-flotante"), hero = q(".hero");
    if (!fl || !hero) return;
    if (!("IntersectionObserver" in window)) { fl.classList.add("se-ve"); return; }
    new IntersectionObserver(function (es) {
      fl.classList.toggle("se-ve", !es[0].isIntersecting);
    }, { threshold: 0 }).observe(hero);
  }

  /* ═══════════ 10 bis · La galería "El Lab, por dentro" ═══════════
     Dos marcos quietos, uno al lado del otro. No se mueven, no giran y no
     cambian de tamaño: lo único que cambia es la imagen de dentro. Las
     cuatro parejas se relevan con el scroll y cada una aguanta el
     equivalente a una pantalla entera antes de dar paso a la siguiente.
     Por qué no se bloquea ni se secuestra el scroll: los marcos se quedan
     con position:sticky, que es del navegador, y GSAP solo LEE la posición
     de scroll (scrub) para cruzar las opacidades. No hay pin, ni listeners
     de rueda, ni scroll programado.
     Sin GSAP o con movimiento reducido, la sección se queda "suelta": las
     ocho una debajo de otra, sin sticky. */
  function initReel() {
    var caja = q("[data-reel]"), escena = q("[data-escena-reel]");
    if (!caja || !escena) return;
    var marcos = qa("[data-marco]", escena);
    var tomas = qa(".reel-toma", escena);
    if (!marcos.length || !tomas.length) return;

    /* ── Cada hueco: primero vídeo, si no imagen ── */
    tomas.forEach(function (hueco) {
      var vid = hueco.getAttribute("data-video");
      if (!vid) { montarFoto(hueco); return; }
      fetch(vid, { method: "HEAD" }).then(function (r) {
        if (!r.ok) throw new Error("sin vídeo");
        var v = document.createElement("video");
        v.src = vid; v.muted = true; v.loop = true; v.playsInline = true;
        v.setAttribute("muted", ""); v.setAttribute("playsinline", "");
        v.preload = "metadata"; v.tabIndex = -1;
        v.setAttribute("aria-label", hueco.getAttribute("title") || "");
        hueco.insertBefore(v, hueco.firstChild);
        hueco.classList.add("llena", "es-video");
        mirarVideo(v);
      }).catch(function () { montarFoto(hueco); });
    });

    function mirarVideo(v) {
      if (reducido || !("IntersectionObserver" in window)) return;
      new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) { var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); }
          else v.pause();
        });
      }, { threshold: .25 }).observe(v);
    }

    if (!window.gsap || !window.ScrollTrigger || !gsap.matchMedia) {
      caja.classList.add("suelto");
      return;
    }
    gsap.registerPlugin(ScrollTrigger);

    gsap.matchMedia()
      .add("(prefers-reduced-motion: reduce)", function () {
        caja.classList.add("suelto");
        return function () { caja.classList.remove("suelto"); };
      })
      .add("(prefers-reduced-motion: no-preference)", function () {
        /* El ritmo, en unidades de la línea de tiempo:
             espera 1,00 · cambio 0,25 · espera 1,00 · cambio 0,25 …
           Cuatro esperas y tres cambios = 4,75. El recorrido de la sección
           son 560vh menos el alto de la escena (~94vh), así que una espera
           sale a ~98vh: una pantalla entera, como se pidió. */
        var ESPERA = 1, CAMBIO = .25;
        var tl = gsap.timeline({
          defaults: { ease: "power1.inOut" },
          scrollTrigger: {
            trigger: caja, start: "top top", end: "bottom bottom",
            scrub: true, invalidateOnRefresh: true
          }
        });

        marcos.forEach(function (marco) {
          var fotos = qa(".reel-toma", marco);
          gsap.set(fotos, { opacity: 0, yPercent: 0 });
          if (fotos[0]) gsap.set(fotos[0], { opacity: 1 });
          fotos.forEach(function (f, k) {
            if (k === 0) return;
            var en = k * (ESPERA + CAMBIO) - CAMBIO;   // donde empieza el cambio
            // La que se va: se funde y sube un poco dentro del marco.
            tl.to(fotos[k - 1], { opacity: 0, yPercent: -4, duration: CAMBIO }, en);
            // La que entra: se funde desde un poco más abajo.
            tl.fromTo(f, { opacity: 0, yPercent: 4 },
                         { opacity: 1, yPercent: 0, duration: CAMBIO }, en);
          });
        });
        // La última pareja también aguanta su pantalla entera antes del final.
        tl.to({}, { duration: ESPERA }, 3 * (ESPERA + CAMBIO) + ESPERA - ESPERA);

        return function () {
          tl.scrollTrigger && tl.scrollTrigger.kill();
          tl.kill();
          gsap.set(tomas, { clearProps: "opacity,transform" });
        };
      });
  }


  /* ═══════════ 11 · Sin parallax en las fotos ═══════════
     Aquí había un parallax que movía la imagen dentro de su marco entre el
     -5 % y el +5 % de su alto. Pero la imagen mide justo lo que el marco
     (object-fit:cover, inset:0), así que al desplazarla se destapaba el
     borde y la foto salía cortada por arriba o por abajo. Para que un
     parallax así funcione la imagen tiene que ser MÁS ALTA que su marco;
     como no lo es, las fotos se quedan quietas. */

  /* ═══════════ 11 bis · El cruce de los dos pisos ═══════════
     El Piso 1 sale hacia arriba mientras el Piso 2 entra desde abajo; se
     solapan un momento y el segundo acaba cubriendo al primero. El scroll
     es el nativo: los dos bloques van con position:sticky y GSAP solo
     desplaza y atenúa enganchado al scroll (scrub), sin pin ni bloqueo.
     Solo en escritorio y solo si no se ha pedido menos movimiento. */
  function initPisos() {
    var caja = q("[data-pisos]"); if (!caja) return;
    var pisos = qa(".piso", caja);
    if (pisos.length < 2 || reducido || !window.gsap || !window.ScrollTrigger) return;
    if (!gsap.matchMedia) return;
    gsap.registerPlugin(ScrollTrigger);

    var uno = pisos[0], dos = pisos[1];
    gsap.matchMedia().add("(min-width:1081px)", function () {
      caja.classList.add("cruce");
      // Los reveals mueven el mismo transform que vamos a animar: aquí
      // estorban, así que los dos pisos entran ya visibles.
      pisos.forEach(function (el) { el.classList.remove("reveal"); el.classList.add("is-visible"); });
      // El alto lo manda el CSS y es el mismo para los dos, así que el
      // segundo tapa al primero entero sin que haya que igualarlos aquí.
      // Antes se igualaban en píxeles desde el JS y el valor se quedaba
      // viejo al cambiar de tamaño la ventana.

      var ventana = { trigger: dos, start: "top bottom", end: "top 18%", scrub: true };
      // El primero se retira SOLO con escala y atenuado, sin desplazarse hacia
      // arriba. Un yPercent negativo lo metía por detrás del menú fijo estando
      // en su posición sticky, y ahí la tarjeta se recortaba por arriba. La
      // escala encoge desde el centro, así que el borde de arriba solo puede
      // bajar: ningún piso pasa nunca por detrás de la barra.
      var sale = gsap.to(uno, {
        scale: .94, ease: "none", scrollTrigger: ventana
      });
      // ...pero el atenuado espera a que de verdad se estén solapando: si
      // no, el primero se ve apagado cuando todavía está solo en pantalla.
      var apaga = gsap.to(uno, {
        opacity: .3, ease: "none",
        scrollTrigger: { trigger: dos, start: "top 62%", end: "top 20%", scrub: true }
      });
      var entra = gsap.fromTo(dos,
        { yPercent: 7, scale: .975 },
        { yPercent: 0, scale: 1, ease: "none", scrollTrigger: ventana });

      return function () {
        [sale, apaga, entra].forEach(function (t) {
          t.scrollTrigger && t.scrollTrigger.kill(); t.kill();
        });
        gsap.set(pisos, { clearProps: "all" });
        pisos.forEach(function (el) { el.classList.add("reveal"); });
        caja.classList.remove("cruce");
      };
    });
  }


  /* ═══════════ 12 · El marco de la portada ═══════════
     Cuatro escenas que se funden. Solo rota si hay al menos dos fotos de
     verdad cargadas: cuatro tramas idénticas rotando no aportan nada, así
     que mientras falten las fotos el marco se queda quieto y los mandos
     no aparecen. No se detiene al pasar el cursor por encima: solo deja de
     rotar cuando la portada sale de la pantalla. */
  function initEscenas() {
    var caja = q("[data-escenas]"); if (!caja) return;

    // Un grupo por panel. La portada A tiene uno; la B, dos (Fiber y Scalp).
    var grupos = qa("[data-escena-grupo]", caja);
    if (!grupos.length) grupos = [caja];
    grupos = grupos.map(function (g) {
      return { raiz: g, escenas: qa(".escena", g), tag: q("[data-tag-escena]", g) };
    }).filter(function (g) { return g.escenas.length; });
    if (!grupos.length) return;

    var total = Math.min.apply(null, grupos.map(function (g) { return g.escenas.length; }));
    if (total < 2) return;

    var mandos = q("[data-mandos]"), botones = qa("[data-puntos] button");
    // Un índice por panel y un turno: la B tiene dos mitades y no deben
    // cambiar a la vez. El reloj va al doble de rápido y alterna el panel.
    // Cada panel puede arrancar en una escena distinta: así las dos
    // mitades de la B nunca muestran la misma imagen a la vez.
    var idx = grupos.map(function (g) {
      var n = parseInt(g.raiz.getAttribute("data-escena-grupo"), 10);
      return isNaN(n) ? 0 : n;
    });
    var turno = 0, reloj = null, aLaVista = true;

    function conFoto() {
      // Cuenta los índices en los que TODOS los paneles tienen foto
      var n = 0;
      for (var k = 0; k < total; k++) {
        var todos = grupos.every(function (g) { return g.escenas[k].classList.contains("llena"); });
        if (todos) n++;
      }
      return n;
    }
    function puedeRotar() { return !reducido && conFoto() >= 2; }

    function pintar(gi) {
      var g = grupos[gi], n = idx[gi];
      g.escenas.forEach(function (e, k) { e.classList.toggle("esta-activa", k === n); });
      if (g.tag) {
        g.tag.textContent = g.escenas[n].getAttribute("data-foto") || "";
        g.tag.parentNode.hidden = g.escenas[n].classList.contains("llena");
      }
      if (gi === 0) {
        botones.forEach(function (b, k) {
          if (k === n) b.setAttribute("aria-current", "true"); else b.removeAttribute("aria-current");
        });
      }
    }
    function avanzar(gi, paso) {
      idx[gi] = ((idx[gi] + paso) % total + total) % total;
      pintar(gi);
    }
    /* Movimiento manual: mueve los dos, pero cada uno desde donde estaba,
       así el desfase se mantiene. */
    var arranque = idx.slice();   // el desfase de partida, para no perderlo
    function ir(n) {
      grupos.forEach(function (g, gi) {
        var base = (typeof n === "number" ? n + arranque[gi] : idx[gi]);
        idx[gi] = ((base % total) + total) % total;
        pintar(gi);
      });
    }
    function mover(paso) {
      grupos.forEach(function (g, gi) { avanzar(gi, paso); });
    }
    function parar() { clearInterval(reloj); reloj = null; }
    function arrancar() {
      parar();
      if (!puedeRotar() || !aLaVista) return;
      // 3,2 s por panel: con dos paneles el reloj late cada 1,6 s y va
      // alternando, así cada uno cambia cada 3,2 s pero nunca a la vez.
      reloj = setInterval(function () {
        avanzar(turno % grupos.length, 1);
        turno++;
      }, 3200 / grupos.length);
    }
    function revisar() {
      var hay = conFoto() >= 2;
      if (mandos) mandos.hidden = !hay;
      if (hay) arrancar(); else { parar(); ir(0); }
    }
    document.addEventListener("foto-lista", revisar);

    // Sobran los puntos que no correspondan a ninguna escena
    botones.forEach(function (b, k) {
      if (k >= total) { var li = b.parentNode; if (li && li.parentNode) li.parentNode.removeChild(li); return; }
      b.addEventListener("click", function () { ir(k); arrancar(); });
    });
    botones = qa("[data-puntos] button");
    qa("[data-escena-ir]").forEach(function (b) {
      b.addEventListener("click", function () { mover(parseInt(b.getAttribute("data-escena-ir"), 10)); arrancar(); });
    });

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) {
        aLaVista = es[0].isIntersecting;
        if (aLaVista) arrancar(); else parar();
      }, { threshold: 0 }).observe(caja);
    }
    ir(0);
    revisar();
  }

  /* ═══════════ 13 · Marquesina con los nombres del catálogo ═══════════ */
  function initMarquesina() {
    var pista = q("[data-marquesina]");
    if (!pista || !CAT || !CAT.protocolos) return;
    var nombres = CAT.protocolos.map(function (p) { return p.nombre; });
    var tanda = nombres.map(function (n) {
      return "<span>" + esc(n) + '</span><i aria-hidden="true">✦</i>';
    }).join("");
    pista.innerHTML = tanda + tanda;   // duplicada: el bucle no da tirones
  }

  /* ═══════════ 14 · Comparador antes / después ═══════════ */
  function initComparadores() {
    qa("[data-comparador]").forEach(function (c) {
      var r = q(".cmp-rango", c); if (!r) return;
      var pintar = function () { c.style.setProperty("--p", r.value + "%"); };
      r.addEventListener("input", pintar);
      pintar();
      // Arrastrar sobre la figura mueve el tirador, no solo el control
      var mover = function (e) {
        var caja = c.getBoundingClientRect();
        var v = Math.min(100, Math.max(0, ((e.clientX - caja.left) / caja.width) * 100));
        r.value = String(v); pintar();
      };
      var soltar = function () {
        window.removeEventListener("pointermove", mover);
        window.removeEventListener("pointerup", soltar);
      };
      c.addEventListener("pointerdown", function (e) {
        mover(e);
        window.addEventListener("pointermove", mover);
        window.addEventListener("pointerup", soltar);
      });
    });
  }



  function initAnyo() { var n = q("[data-anyo]"); if (n) n.textContent = String(new Date().getFullYear()); }

  /* ═══════════ Arranque ═══════════ */
  function arrancar() {
    safe(initNav, "nav");
    safe(initAnyo, "anyo");
    safe(initFotos, "fotos");
    safe(initWA, "wa");
    safe(initBotones, "botones");
    safe(initEscenas, "escenas");
    safe(initComparadores, "comparadores");

    var alFinal = function () {
      safe(initSplit, "split");
      safe(initReveals, "reveals");
      safe(initPisos, "pisos");
      safe(initReel, "reel");
    };

    fetch(RUTA, { cache: "no-cache" })
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (d) {
        CAT = d;
        safe(montarCatalogo, "catalogo");
        safe(construirBuscador, "buscador");
        safe(initFotos, "fotos");
        safe(initMarquesina, "marquesina");
      })
      .catch(function (err) {
        if (window.console) console.warn("[catalogo]", err);
        qa("[data-catalogo]").forEach(function (d) {
          d.innerHTML = '<p class="cargando">No se pudo leer el catálogo (' + esc(err.message || "error") +
            "). Las tarjetas salen de assets/docs/02-CATALOGO.json y la página tiene que abrirse desde el servidor local.</p>";
        });
      })
      .then(function () {
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(alFinal);
        else alFinal();
      });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", arrancar);
  else arrancar();
})();
