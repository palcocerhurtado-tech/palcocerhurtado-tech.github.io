/* ═══════════════════════════════════════════════════════
   Pablo Alcocer Hurtado — Interactive Portfolio
   Particles · GSAP scroll · Terminal · Magnetic UI · i18n
   ═══════════════════════════════════════════════════════ */
(() => {
  "use strict";

  const $  = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const hasGSAP = typeof gsap !== "undefined";
  const isTouch = matchMedia("(hover: none), (pointer: coarse)").matches;

  if (hasGSAP && window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger, ScrollToPlugin);

  /* ────────────────────────────────────────────────
     i18n
  ──────────────────────────────────────────────── */
  const T = {
    es: {
      navPos: "Posicionamiento", navProj: "Proyectos", navExp: "Experiencia", navTerm: "Terminal", navCont: "Contacto",
      eyebrow: "Pablo Alcocer Hurtado · IA + Marketing Creativo",
      heroCopy: "Diseño automatizaciones, productos digitales y experiencias de marca con una idea clara: que la creatividad no se quede en presentación, que funcione como sistema.",
      ctaProj: "Ver proyectos", ctaTerm: "Probar terminal",
      s1h: "IA aplicada", s1b: "Criterio comercial, no ruido técnico.",
      s2h: "Marketing",   s2b: "Estrategia, narrativa y conversión.",
      s3h: "Sistemas",    s3b: "Procesos, datos y producto digital.",
      scrollHint: "scroll ↓",
      posK: "Posicionamiento", posH: "No vendo herramientas. Diseño sistemas.",
      posB: "Mi perfil vive en el cruce entre inteligencia artificial, marketing creativo, automatización, operaciones y creación digital. No construyo soluciones genéricas: diseño ecosistemas únicos para cada desafío operativo.",
      p1h: "Consultor IA", p1b: "Aterrizo inteligencia artificial en procesos concretos, desde una automatización de emails hasta una digitalización de base de datos pasando por un organigrama automático para redes sociales.",
      p2h: "Marketing creativo", p2b: "Construyo mensajes, campañas y experiencias, todo lo necesario para el éxito rotundo de una marca.",
      p3h: "Automatización", p3b: "Conecto herramientas, datos y decisiones. Usando Make, n8n, Claude o Python automatizo procesos que ahorran tiempo y dinero a las empresas.",
      p4h: "Producto digital", p4b: "Prototipo webs, asistentes, plantillas y bots, todo lo que una empresa necesita para posicionarse como la más puntera del mercado.",
      prjK: "Showcase", prjH: "Un ecosistema de proyectos, no una lista de repos.",
      prjB: "Cada proyecto representa una dirección: consultoría IA, automatización, producto digital o identidad.",
      d1: "La marca y laboratorio de consultoría donde convierto operaciones de e-commerce en sistemas automatizados, auditables y medibles con IA.",
      d2: "Bot de trading algorítmico para Binance Spot: señales, estrategia Elliott Wave Proxy, gestión de riesgo, backtesting y modo paper/live.",
      d3: "Plataforma de producción creativa con IA que une generación de assets, vídeo, lip sync y pipelines agentic end-to-end.",
      d4: "Asistente local-first de terminal para macOS, con memoria SQLite, contexto del sistema, Gemini/Ollama y conectores personales.",
      d5: "Plantilla pública de tarjeta de contacto digital con QR y vCard, pensada para clonarse y publicarse fácilmente con GitHub Pages.",
      d6: "Repositorio de identidad pública en GitHub: base para mostrar perfil, enlaces, proyectos y presencia técnica personal.",
      vp: "Ver proyecto ↗",
      termK: "Modo hacker", termH: "Navega mi portfolio como en una terminal.",
      termB: 'Escribe <code>help</code> para ver los comandos. Prueba <code>projects</code>, <code>cv</code> o <code>sudo hire-me</code>.',
      expK: "Perfil", expH: "Perfil, experiencia y formación",
      r1: "Consultor y auditor de IA · 2026–presente", e1: "Diseño e implementación de flujos de IA aplicada a operaciones e-commerce.",
      r2: "Colaborador digital · 2025–2026",           e2: "Apoyo en proyectos de formación y contenido digital.",
      r3: "Atención al público · 2022–2024",           e3: "Gestión de clientes y logística de almacén.",
      st1: "Proyectos construidos", st2: "Certificaciones", st3: "Marcas creadas",
      edu1: "Grado Superior Marketing y Publicidad", edu2: "Bachillerato Ciencias Sociales", edu3: "Halifax High School, Canadá",
      certH: "Certificaciones",
      ctK: "Contacto",
      ctH: "Si tienes una idea, un proceso roto o un proyecto que necesita forma digital, podemos convertirlo en sistema.",
      ctMail: "Email", ctCopy: "Copiar email", ctClick: "click para copiar",
      built: "Hecho con IA, café y automatizaciones",
      term: {
        cvNote: "CV PDF: colócalo en /assets y enlázalo aquí.",
        welcome: ["PABLO ALCOCER HURTADO — terminal v2.6", "Escribe 'help' para ver los comandos disponibles.", ""],
        help: [
          "Comandos disponibles:",
          "  help          → esta ayuda",
          "  about         → quién soy",
          "  projects      → lista de proyectos",
          "  open <name>   → abre un proyecto (p. ej. open quantbot)",
          "  skills        → stack técnico",
          "  experience    → experiencia",
          "  cv            → descarga / CV",
          "  contact       → cómo contactarme",
          "  goto <sec>    → scroll a una sección (top, projects, contact…)",
          "  theme gold|teal|crimson → cambia el acento",
          "  lang es|en    → cambia el idioma",
          "  clear         → limpia la terminal",
          "  sudo hire-me  → …inténtalo",
        ],
        about: [
          "Consultor IA + marketing creativo + automatización.",
          "No vendo herramientas: diseño sistemas que trabajan mientras duermes.",
        ],
        projectsList: [
          "  archon        → Archon Consultancies",
          "  quantbot      → QuantBot trading",
          "  openstudio    → OpenStudio AI video",
          "  advarchon     → ADV Archon asistente local",
          "  tarjeta       → Tarjeta contacto",
          "  identity      → palcocerhurtado-tech",
          "",
          "Usa: open <nombre>",
        ],
        skills: [
          "IA:        Claude, LLMs, agentes, RAG",
          "Autom.:    Make, n8n, Python, APIs",
          "Web:       Next.js, HTML/CSS/JS, GA4",
          "Ads/Data:  Google Ads, Meta Ads",
          "Trading:   Python, Binance API, backtesting",
        ],
        experience: [
          "2026–hoy   Archon Consultancies / ZC — Consultor IA",
          "2025–2026  Cegos — Colaborador digital",
          "2022–2024  Almacenes Manuel Martínez — Atención al público",
        ],
        contactInfo: [
          "email:     palcocerhurtado@gmail.com",
          "linkedin:  /in/pablo-alcocer-hurtado",
          "github:    palcocerhurtado-tech",
          "web:       archonconsultancies.com",
        ],
        projects: {
          archon:     { name: "Archon Consultancies", url: "https://github.com/palcocerhurtado-tech/archon-consultancies" },
          quantbot:   { name: "QuantBot", url: "https://github.com/palcocerhurtado-tech/quantbot" },
          openstudio: { name: "OpenStudio", url: "https://github.com/palcocerhurtado-tech" },
          advarchon:  { name: "ADV Archon", url: "https://github.com/palcocerhurtado-tech/adv-archon" },
          tarjeta:    { name: "Tarjeta contacto", url: "https://github.com/palcocerhurtado-tech/tarjeta-contacto-plantilla" },
          identity:   { name: "palcocerhurtado-tech", url: "https://github.com/palcocerhurtado-tech" },
        },
        sections: {
          top: "#top", positioning: "#positioning", projects: "#projects",
          terminal: "#terminal-sec", experience: "#experience", contact: "#contact",
        },
        notFound: (c) => `comando no encontrado: ${c} — escribe 'help'`,
        opening: (p) => `abriendo ${p.name} ↗`,
        goto: (s) => `navegando a #${s}…`,
        themeSet: (t) => `acento cambiado a ${t}`,
        langSet: (l) => `idioma cambiado a ${l.toUpperCase()}`,
        cleared: ["", "terminal limpia."],
        sudo: ["[sudo] contraseña para pablo: ********", "Acceso concedido ✔", "Despidiendo al reclutador aburrido… contratado 🎉", ""],
        unknownSection: (s) => `sección desconocida: ${s}`,
      },
      boot: ["archon-os boot v2.6…", "loading modules: ia ✔ marketing ✔ automation ✔", "portfolio ready ✓"],
    },
    en: {
      navPos: "Positioning", navProj: "Projects", navExp: "Experience", navTerm: "Terminal", navCont: "Contact",
      eyebrow: "Pablo Alcocer Hurtado · AI + Creative Marketing",
      heroCopy: "I design automations, digital products and brand experiences with one clear idea: creativity should not stay in a presentation — it should work as a system.",
      ctaProj: "See projects", ctaTerm: "Try the terminal",
      s1h: "Applied AI",  s1b: "Commercial thinking, no technical noise.",
      s2h: "Marketing",   s2b: "Strategy, narrative and conversion.",
      s3h: "Systems",     s3b: "Processes, data and digital product.",
      scrollHint: "scroll ↓",
      posK: "Positioning", posH: "I don't sell tools. I design systems.",
      posB: "My profile lives at the intersection of artificial intelligence, creative marketing, automation, operations and digital creation. I don't build generic solutions: I design unique ecosystems for each operational challenge.",
      p1h: "AI Consultant", p1b: "I apply AI to concrete processes: email automation, database digitization, automatic org charts for social media.",
      p2h: "Creative Marketing", p2b: "I build messages, campaigns and experiences — everything needed for a brand's resounding success.",
      p3h: "Automation", p3b: "I connect tools, data and decisions. Using Make, n8n, Claude or Python I automate processes that save companies time and money.",
      p4h: "Digital Product", p4b: "I prototype webs, assistants, templates and bots — everything a company needs to position itself at the cutting edge.",
      prjK: "Showcase", prjH: "An ecosystem of projects, not a list of repos.",
      prjB: "Each project represents a direction: AI consulting, automation, digital product or identity.",
      d1: "The consulting brand and lab where I turn e-commerce operations into automated, auditable and measurable systems with AI.",
      d2: "Algorithmic trading bot for Binance Spot: signals, Elliott Wave Proxy strategy, risk management, backtesting and paper/live mode.",
      d3: "Creative AI production platform unifying asset generation, video, lip sync and agentic end-to-end pipelines.",
      d4: "Local-first terminal assistant for macOS with SQLite memory, system context, Gemini/Ollama and personal connectors.",
      d5: "Public digital contact card template with QR and vCard, designed to be cloned and published easily with GitHub Pages.",
      d6: "Public identity repository on GitHub: base for showcasing profile, links, projects and personal technical presence.",
      vp: "View project ↗",
      termK: "Hacker mode", termH: "Navigate my portfolio like a terminal.",
      termB: 'Type <code>help</code> to see the commands. Try <code>projects</code>, <code>cv</code> or <code>sudo hire-me</code>.',
      expK: "Profile", expH: "Profile, experience & education",
      r1: "AI Consultant & Auditor · 2026–present", e1: "Design and implementation of AI-applied flows for e-commerce operations.",
      r2: "Digital Collaborator · 2025–2026",       e2: "Support on training and digital content projects.",
      r3: "Customer Service · 2022–2024",           e3: "Client management and warehouse logistics.",
      st1: "Projects built", st2: "Certifications", st3: "Brands created",
      edu1: "Higher Degree in Marketing & Advertising", edu2: "Social Sciences Baccalaureate", edu3: "Halifax High School, Canada",
      certH: "Certifications",
      ctK: "Contact",
      ctH: "If you have an idea, a broken process or a project that needs digital form, we can turn it into a system.",
      ctMail: "Email", ctCopy: "Copy email", ctClick: "click to copy",
      built: "Built with AI, coffee and automations",
      term: {
        cvNote: "CV PDF: drop it in /assets and link it here.",
        welcome: ["PABLO ALCOCER HURTADO — terminal v2.6", "Type 'help' to see available commands.", ""],
        help: [
          "Available commands:",
          "  help          → this help",
          "  about         → who I am",
          "  projects      → project list",
          "  open <name>   → open a project (e.g. open quantbot)",
          "  skills        → tech stack",
          "  experience    → experience",
          "  cv            → download / CV",
          "  contact       → how to reach me",
          "  goto <sec>    → scroll to a section (top, projects, contact…)",
          "  theme gold|teal|crimson → change accent",
          "  lang es|en    → change language",
          "  clear         → clear the terminal",
          "  sudo hire-me  → …try it",
        ],
        about: [
          "AI consultant + creative marketing + automation.",
          "I don't sell tools: I design systems that work while you sleep.",
        ],
        projectsList: [
          "  archon        → Archon Consultancies",
          "  quantbot      → QuantBot trading",
          "  openstudio    → OpenStudio AI video",
          "  advarchon     → ADV Archon local assistant",
          "  tarjeta       → Contact card",
          "  identity      → palcocerhurtado-tech",
          "",
          "Use: open <name>",
        ],
        skills: [
          "AI:        Claude, LLMs, agents, RAG",
          "Autom.:    Make, n8n, Python, APIs",
          "Web:       Next.js, HTML/CSS/JS, GA4",
          "Ads/Data:  Google Ads, Meta Ads",
          "Trading:   Python, Binance API, backtesting",
        ],
        experience: [
          "2026–now   Archon Consultancies / ZC — AI Consultant",
          "2025–2026  Cegos — Digital Collaborator",
          "2022–2024  Almacenes Manuel Martínez — Customer Service",
        ],
        contactInfo: [
          "email:     palcocerhurtado@gmail.com",
          "linkedin:  /in/pablo-alcocer-hurtado",
          "github:    palcocerhurtado-tech",
          "web:       archonconsultancies.com",
        ],
        projects: {
          archon:     { name: "Archon Consultancies", url: "https://github.com/palcocerhurtado-tech/archon-consultancies" },
          quantbot:   { name: "QuantBot", url: "https://github.com/palcocerhurtado-tech/quantbot" },
          openstudio: { name: "OpenStudio", url: "https://github.com/palcocerhurtado-tech" },
          advarchon:  { name: "ADV Archon", url: "https://github.com/palcocerhurtado-tech/adv-archon" },
          tarjeta:    { name: "Tarjeta contacto", url: "https://github.com/palcocerhurtado-tech/tarjeta-contacto-plantilla" },
          identity:   { name: "palcocerhurtado-tech", url: "https://github.com/palcocerhurtado-tech" },
        },
        sections: {
          top: "#top", positioning: "#positioning", projects: "#projects",
          terminal: "#terminal-sec", experience: "#experience", contact: "#contact",
        },
        notFound: (c) => `command not found: ${c} — type 'help'`,
        opening: (p) => `opening ${p.name} ↗`,
        goto: (s) => `navigating to #${s}…`,
        themeSet: (t) => `accent changed to ${t}`,
        langSet: (l) => `language switched to ${l.toUpperCase()}`,
        cleared: ["", "terminal cleared."],
        sudo: ["[sudo] password for pablo: ********", "Access granted ✔", "Firing the boring recruiter… hired 🎉", ""],
        unknownSection: (s) => `unknown section: ${s}`,
      },
      boot: ["archon-os boot v2.6…", "loading modules: ai ✔ marketing ✔ automation ✔", "portfolio ready ✓"],
    },
  };

  let lang = "es";

  function applyI18n() {
    const dict = T[lang];
    $$("[data-i18n]").forEach((el) => {
      const k = el.getAttribute("data-i18n");
      if (dict[k] !== undefined) el.innerHTML = dict[k];
    });
    document.documentElement.lang = lang;
  }

  function setLang(l) {
    lang = l;
    applyI18n();
    $("#btn-es").classList.toggle("active", l === "es");
    $("#btn-en").classList.toggle("active", l === "en");
    termDict = T[lang].term;
  }
  window.setLang = setLang;

  /* ────────────────────────────────────────────────
     Boot loader
  ──────────────────────────────────────────────── */
  function boot() {
    const loader = $("#loader"), fill = $("#bootFill"), text = $("#bootText");
    const lines = T[lang].boot;
    let i = 0, p = 0;
    body = document.body;
    body.classList.add("loading");

    const tick = setInterval(() => {
      p = Math.min(100, p + Math.random() * 18 + 6);
      fill.style.width = p + "%";
      if (i < lines.length && p > (i + 1) * (100 / (lines.length + 1))) {
        text.textContent += lines[i] + "\n";
        i++;
      }
      if (p >= 100) {
        clearInterval(tick);
        setTimeout(() => {
          loader.classList.add("done");
          body.classList.remove("loading");
          introAnimations();
        }, 350);
      }
    }, 170);
  }
  let body = document.body;

  /* ────────────────────────────────────────────────
     Starfield particles (hero + contact)
  ──────────────────────────────────────────────── */
  function starfield(canvas, density = 9000) {
    const ctx = canvas.getContext("2d");
    if (isTouch) density = Math.round(density * 2.6);
    let w, h, stars = [], raf, mouse = { x: -9999, y: -9999 };
    let running = false, inView = true, docHidden = document.hidden;

    function resize() {
      w = canvas.width = canvas.offsetWidth * devicePixelRatio;
      h = canvas.height = canvas.offsetHeight * devicePixelRatio;
      const count = Math.floor((canvas.offsetWidth * canvas.offsetHeight) / density);
      stars = Array.from({ length: count }, () => ({
        x: Math.random() * w, y: Math.random() * h,
        r: (Math.random() * 1.4 + 0.4) * devicePixelRatio,
        vx: (Math.random() - 0.5) * 0.12 * devicePixelRatio,
        vy: (Math.random() - 0.5) * 0.12 * devicePixelRatio,
        tw: Math.random() * Math.PI * 2,
        ts: Math.random() * 0.02 + 0.008,
      }));
    }

    function step() {
      if (!running) return;
      ctx.clearRect(0, 0, w, h);
      for (const s of stars) {
        s.x += s.vx; s.y += s.vy; s.tw += s.ts;
        if (s.x < 0) s.x = w; if (s.x > w) s.x = 0;
        if (s.y < 0) s.y = h; if (s.y > h) s.y = 0;
        const tw = 0.55 + Math.sin(s.tw) * 0.45;
        const dx = s.x - mouse.x, dy = s.y - mouse.y;
        const dist = Math.hypot(dx, dy);
        const near = dist < 120 * devicePixelRatio;
        const rad = s.r * (near ? 2.1 : 1);
        ctx.beginPath();
        ctx.arc(s.x, s.y, rad, 0, Math.PI * 2);
        ctx.fillStyle = near
          ? `rgba(240,207,134,${0.55 + tw * 0.45})`
          : `rgba(247,239,224,${0.18 + tw * 0.4})`;
        ctx.fill();
        if (near) {
          ctx.beginPath();
          ctx.moveTo(s.x, s.y);
          ctx.lineTo(mouse.x, mouse.y);
          ctx.strokeStyle = `rgba(217,180,101,${0.14 * (1 - dist / (120 * devicePixelRatio))})`;
          ctx.lineWidth = devicePixelRatio * 0.6;
          ctx.stroke();
        }
      }
      raf = requestAnimationFrame(step);
    }

    canvas.parentElement.addEventListener("mousemove", (e) => {
      const r = canvas.getBoundingClientRect();
      mouse.x = (e.clientX - r.left) * devicePixelRatio;
      mouse.y = (e.clientY - r.top) * devicePixelRatio;
    });
    canvas.parentElement.addEventListener("mouseleave", () => { mouse.x = mouse.y = -9999; });

    addEventListener("resize", resize);
    resize();

    function sync() {
      const want = !reducedMotion && inView && !docHidden;
      if (want && !running) { running = true; step(); }
      else if (!want && running) { running = false; cancelAnimationFrame(raf); }
    }
    new IntersectionObserver((es) => { inView = es.some((e) => e.isIntersecting); sync(); },
      { threshold: 0.02 }).observe(canvas);
    document.addEventListener("visibilitychange", () => { docHidden = document.hidden; sync(); });
    if (!reducedMotion) { running = true; step(); } else { /* draw one static frame */ running = true; step(); running = false; cancelAnimationFrame(raf); }

    return { pause: () => cancelAnimationFrame(raf), resume: () => { if (!reducedMotion) step(); } };
  }

  /* ────────────────────────────────────────────────
     Scroll progress, topbar state, active nav
  ──────────────────────────────────────────────── */
  function scrollUI() {
    const bar = $("#progress"), topbar = $("#topbar");
    const links = $$(".nav-links a");
    const secs = ["top", "positioning", "projects", "terminal-sec", "experience", "contact"];

    function onScroll() {
      const sc = scrollY;
      const max = document.documentElement.scrollHeight - innerHeight;
      bar.style.width = (max > 0 ? (sc / max) * 100 : 0) + "%";
      topbar.classList.toggle("scrolled", sc > 30);
    }
    addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          links.forEach((a) => a.classList.toggle("active", a.getAttribute("href") === "#" + e.target.id));
        }
      });
    }, { rootMargin: "-40% 0px -50% 0px" });
    secs.forEach((id) => { const el = document.getElementById(id); if (el) io.observe(el); });
  }

  /* ────────────────────────────────────────────────
     Smooth anchor scrolling
  ──────────────────────────────────────────────── */
  function smoothAnchors() {
    $$('a[href^="#"]').forEach((a) => {
      a.addEventListener("click", (e) => {
        const id = a.getAttribute("href");
        if (id.length < 2) return;
        const target = $(id);
        if (!target) return;
        e.preventDefault();
        document.body.classList.remove("loading");
        $("#loader")?.classList.add("done");
        if (hasGSAP && window.ScrollToPlugin) {
          gsap.to(window, { scrollTo: { y: target, offsetY: 70 }, duration: 1, ease: "power3.inOut" });
        } else {
          target.scrollIntoView({ behavior: "smooth" });
        }
        history.replaceState(null, "", id);
      });
    });
  }

  /* ────────────────────────────────────────────────
     Magnetic elements
  ──────────────────────────────────────────────── */
  function magnetic() {
    if (reducedMotion || !matchMedia("(hover:hover)").matches) return;
    $$(".magnetic").forEach((el) => {
      el.addEventListener("mousemove", (e) => {
        const r = el.getBoundingClientRect();
        const x = e.clientX - r.left - r.width / 2;
        const y = e.clientY - r.top - r.height / 2;
        if (hasGSAP) gsap.to(el, { x: x * 0.25, y: y * 0.25, duration: 0.3, ease: "power2.out" });
        else el.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
      });
      el.addEventListener("mouseleave", () => {
        if (hasGSAP) gsap.to(el, { x: 0, y: 0, duration: 0.55, ease: "elastic.out(1,0.4)" });
        else el.style.transform = "";
      });
    });
  }

  /* ────────────────────────────────────────────────
     Custom cursor
  ──────────────────────────────────────────────── */
  function cursor() {
    const ring = $("#cursor"), dot = $("#cursorDot");
    if (!matchMedia("(hover:hover) and (pointer:fine)").matches) return;
    let rx = innerWidth / 2, ry = innerHeight / 2, tx = rx, ty = ry;
    addEventListener("mousemove", (e) => {
      tx = e.clientX; ty = e.clientY;
      dot.style.left = tx + "px"; dot.style.top = ty + "px";
      const t = e.target;
      document.body.classList.toggle("cursor-hover", !!t.closest("a, button, .magnetic, input, [data-tilt]"));
    });
    (function loop() {
      rx += (tx - rx) * 0.16; ry += (ty - ry) * 0.16;
      ring.style.left = rx + "px"; ring.style.top = ry + "px";
      requestAnimationFrame(loop);
    })();
  }

  /* ────────────────────────────────────────────────
     3D tilt cards
  ──────────────────────────────────────────────── */
  function tilt() {
    if (reducedMotion || !matchMedia("(hover:hover)").matches) return;
    $$("[data-tilt]").forEach((card) => {
      let raf = null;
      card.addEventListener("mousemove", (e) => {
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - 0.5;
        const py = (e.clientY - r.top) / r.height - 0.5;
        if (raf) cancelAnimationFrame(raf);
        raf = requestAnimationFrame(() => {
          card.style.transform = `perspective(800px) rotateY(${px * 9}deg) rotateX(${-py * 9}deg) translateY(-4px)`;
        });
      });
      card.addEventListener("mouseleave", () => {
        card.style.transition = "transform .5s ease, border-color .3s";
        card.style.transform = "";
        setTimeout(() => (card.style.transition = ""), 500);
      });
    });
  }

  /* ────────────────────────────────────────────────
     GSAP intro + scroll reveals
  ──────────────────────────────────────────────── */
  function introAnimations() {
    if (!hasGSAP) return;
    if (reducedMotion) return;

    // hero entrance
    const h1 = $("h1");
    if (h1 && !h1.dataset.split) {
      h1.dataset.split = "1";
      const walk = (node) => {
        [...node.childNodes].forEach((child) => {
          if (child.nodeType === 3) {
            const frag = document.createDocumentFragment();
            for (const word of child.textContent.split(/(\s+)/)) {
              if (!word) continue;
              if (/^\s+$/.test(word)) { frag.append(word); continue; }
              const w = document.createElement("span");
              w.style.cssText = "display:inline-block;white-space:nowrap;";
              for (const ch of word) {
                const s = document.createElement("span");
                s.className = "char"; s.textContent = ch;
                w.append(s);
              }
              frag.append(w);
            }
            child.replaceWith(frag);
          } else if (child.nodeType === 1) walk(child);
        });
      };
      walk(h1);
      gsap.from($$("h1 .char", document), {
        y: 60, opacity: 0, rotateX: -80, stagger: 0.016, duration: 0.9, ease: "power3.out",
      });
    }
    gsap.from([".hero-sub", ".cta-row", ".signal-strip", ".hero-visual", ".eyebrow"], {
      y: 26, opacity: 0, duration: 0.8, stagger: 0.09, delay: 0.35, ease: "power2.out",
    });

    // reveals
    $$(".reveal").forEach((el) => {
      gsap.from(el, {
        y: 34, opacity: 0, duration: 0.75, ease: "power2.out",
        scrollTrigger: { trigger: el, start: "top 86%" },
      });
    });

    // section headers slide
    $$(".sec-head").forEach((el) => {
      gsap.from(el.children, {
        y: 30, opacity: 0, duration: 0.8, stagger: 0.12, ease: "power2.out",
        scrollTrigger: { trigger: el, start: "top 85%" },
      });
    });

    // experience line draws
    const line = $("#expProgress");
    if (line) {
      gsap.to(line, {
        scaleY: 1, ease: "none",
        scrollTrigger: {
          trigger: ".exp-list", start: "top 75%", end: "bottom 45%", scrub: 0.6,
        },
      });
    }

    // counters
    $$(".stat-num").forEach((el) => {
      const end = +el.dataset.count;
      ScrollTrigger.create({
        trigger: el, start: "top 88%", once: true,
        onEnter: () => {
          gsap.fromTo(el, { textContent: 0 }, {
            textContent: end, duration: 1.6, ease: "power1.out",
            snap: { textContent: 1 }, onUpdate: function () { el.textContent = Math.round(+el.textContent); },
          });
        },
      });
    });

    // hero parallax out
    gsap.to(".hero-grid", {
      yPercent: -8, opacity: 0.25, ease: "none",
      scrollTrigger: { trigger: ".hero", start: "bottom bottom", end: "bottom 30%", scrub: true },
    });
  }

  /* ────────────────────────────────────────────────
     Terminal
  ──────────────────────────────────────────────── */
  let termDict = null;

  const Terminal = (() => {
    const bodyEl = () => $("#termBody");
    let history = [], hIndex = -1;

    function print(text, cls = "ok") {
      const el = document.createElement("div");
      el.className = "term-line " + cls;
      el.textContent = text;
      bodyEl().append(el);
      bodyEl().scrollTop = bodyEl().scrollHeight;
    }
    function printHTML(html, cls = "ok") {
      const el = document.createElement("div");
      el.className = "term-line " + cls;
      el.innerHTML = html;
      bodyEl().append(el);
      bodyEl().scrollTop = bodyEl().scrollHeight;
    }
    const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

    function welcome() {
      bodyEl().innerHTML = "";
      termDict.welcome.forEach((l) => print(l, "gold"));
    }

    function exec(raw) {
      const input = raw.trim();
      print(input, "cmd");
      if (!input) return;
      history.push(input);
      hIndex = history.length;

      const [cmd, ...args] = input.split(/\s+/);
      const arg = args.join(" ").toLowerCase();

      switch (cmd.toLowerCase()) {
        case "help": termDict.help.forEach((l) => print(l, "ok")); break;
        case "about": termDict.about.forEach((l) => print(l, "ok")); break;
        case "projects": termDict.projectsList.forEach((l) => print(l, "ok")); break;
        case "skills": termDict.skills.forEach((l) => print(l, "gold")); break;
        case "experience": termDict.experience.forEach((l) => print(l, "ok")); break;
        case "contact": {
          termDict.contactInfo.forEach((l) => print(l, "ok"));
          printHTML(`<a href="mailto:palcocerhurtado@gmail.com">send email ↗</a>`, "teal");
          break;
        }
        case "cv":
          printHTML(`<a href="https://github.com/palcocerhurtado-tech" target="_blank">github.com/palcocerhurtado-tech ↗</a>`, "teal");
          print(termDict.cvNote, "dim");
          break;
        case "open": {
          const p = termDict.projects[arg];
          if (p) { printHTML(`<a href="${p.url}" target="_blank">${termDict.opening(p)}</a>`, "gold"); window.open(p.url, "_blank"); }
          else print(termDict.notFound("open " + arg), "dim");
          break;
        }
        case "goto": {
          const sec = termDict.sections[arg];
          if (sec) {
            print(termDict.goto(arg), "teal");
            const target = $(sec);
            if (hasGSAP && window.ScrollToPlugin) gsap.to(window, { scrollTo: { y: target, offsetY: 70 }, duration: 1, ease: "power3.inOut" });
            else target.scrollIntoView({ behavior: "smooth" });
          } else print(termDict.unknownSection(arg), "dim");
          break;
        }
        case "theme": {
          const themes = { gold: "#d9b465", teal: "#70c7b7", crimson: "#e0566b" };
          if (themes[arg]) {
            document.documentElement.style.setProperty("--gold", themes[arg]);
            document.documentElement.style.setProperty("--gold2", themes[arg]);
            print(termDict.themeSet(arg), "gold");
          } else print("uso: theme gold|teal|crimson", "dim");
          break;
        }
        case "lang": {
          if (arg === "es" || arg === "en") { setLang(arg); print(termDict.langSet(arg), "gold"); }
          else print("uso: lang es|en", "dim");
          break;
        }
        case "clear": bodyEl().innerHTML = ""; termDict.cleared.forEach((l) => print(l, "dim")); break;
        case "sudo":
          if (arg === "hire-me") { typeLines(termDict.sudo); }
          else print("uso: sudo hire-me", "dim");
          break;
        case "whoami": print("pablo — archon-os", "teal"); break;
        case "ls": print("projects/  experience.txt  contact.md  cv.pdf  secrets/", "ok"); break;
        case "cat": {
          if (arg === "cv.pdf") exec("cv");
          else if (arg === "contact.md") exec("contact");
          else if (arg === "experience.txt") exec("experience");
          else if (arg === "secrets") print("permiso denegado 😏", "dim");
          else print(`cat: ${arg || ""}: no such file`, "dim");
          break;
        }
        default: print(termDict.notFound(cmd), "dim");
      }
      print("", "ok");
    }

    function typeLines(lines) {
      let li = 0;
      const next = () => {
        if (li >= lines.length) { print("", "ok"); return; }
        const text = lines[li++];
        let ci = 0;
        const el = document.createElement("div");
        el.className = "term-line gold";
        bodyEl().append(el);
        const tw = setInterval(() => {
          el.textContent = text.slice(0, ++ci);
          bodyEl().scrollTop = bodyEl().scrollHeight;
          if (ci >= text.length) { clearInterval(tw); setTimeout(next, 260); }
        }, 16);
      };
      next();
    }

    function init() {
      welcome();
      $("#termForm").addEventListener("submit", (e) => {
        e.preventDefault();
        const inp = $("#termInput");
        exec(inp.value);
        inp.value = "";
      });
      $("#termInput").addEventListener("keydown", (e) => {
        if (e.key === "ArrowUp") { e.preventDefault(); if (hIndex > 0) $("#termInput").value = history[--hIndex]; }
        if (e.key === "ArrowDown") { e.preventDefault(); if (hIndex < history.length - 1) $("#termInput").value = history[++hIndex]; else { hIndex = history.length; $("#termInput").value = ""; } }
        if (e.key === "Tab") { e.preventDefault(); /* simple tab completion */ }
      });
      // clicking the terminal focuses the input
      $("#terminal").addEventListener("click", () => $("#termInput").focus());
    }

    return { init, exec };
  })();

  /* ────────────────────────────────────────────────
     Contact copy + burger
  ──────────────────────────────────────────────── */
  function misc() {
    if (!hasGSAP) $$(".stat-num").forEach((el) => (el.textContent = el.dataset.count));
    const copyBtn = $("#copyMail");
    copyBtn?.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText("palcocerhurtado@gmail.com"); } catch {}
      const em = copyBtn.querySelector("em");
      const old = em.textContent;
      em.textContent = lang === "es" ? "¡copiado! ✔" : "copied! ✔";
      setTimeout(() => (em.textContent = old), 1800);
    });

    $("#burger")?.addEventListener("click", () => {
      const nav = $(".nav");
      const open = nav.classList.toggle("open");
      document.body.classList.toggle("menu-open", open);
      const b = $("#burger");
      b.classList.toggle("active", open);
      b.setAttribute("aria-expanded", String(open));
    });
    $$(".nav-links a").forEach((a) => a.addEventListener("click", () => {
      $(".nav").classList.remove("open");
      document.body.classList.remove("menu-open");
      $("#burger")?.classList.remove("active");
      $("#burger")?.setAttribute("aria-expanded", "false");
    }));
  }

  /* ────────────────────────────────────────────────
     Init
  ──────────────────────────────────────────────── */
  termDict = T[lang].term;
  document.addEventListener("DOMContentLoaded", () => {
    applyI18n();
    boot();
    scrollUI();
    smoothAnchors();
    magnetic();
    cursor();
    tilt();
    misc();
    Terminal.init();
    if (isTouch) buildTermChips();
    starfield($("#stars"));
    starfield($("#stars2"), 12000);
  });

  /* ────────────────────────────────────────────────
     iOS Safari: keep --app-height synced with the visual
     viewport (address bar collapse breaks 100vh/100svh)
  ──────────────────────────────────────────────── */
  const setAppHeight = () => document.documentElement.style.setProperty("--app-height", `${window.innerHeight}px`);
  addEventListener("resize", setAppHeight);
  setAppHeight();

  /* ────────────────────────────────────────────────
     Terminal quick-command chips (touch devices)
  ──────────────────────────────────────────────── */
  function buildTermChips() {
    const form = $("#termForm");
    if (!form) return;
    const chips = document.createElement("div");
    chips.className = "term-chips";
    chips.setAttribute("aria-label", "Comandos rápidos");
    ["help", "projects", "skills", "contact", "theme teal", "sudo hire-me"].forEach((c) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "term-chip";
      b.textContent = c;
      b.addEventListener("click", () => {
        $("#termInput").value = c;
        form.requestSubmit();
      });
      chips.append(b);
    });
    form.after(chips);
  }
})();
