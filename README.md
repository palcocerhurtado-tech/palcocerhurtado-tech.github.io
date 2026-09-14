# Portfolio interactivo — Pablo Alcocer Hurtado

Dos versiones del mismo portfolio:

| Archivo | Uso |
|---|---|
| `portfolio-standalone.html` | **Un solo archivo, todo incluido.** Doble clic y abre. Ideal para compartir o subir rápido. |
| `index.html` + `styles.css` + `app.js` + `assets/` | **Versión para GitHub Pages.** Más limpia para editar y mantener. |

## Subir a GitHub Pages (recomendado)

1. Crea un repo nuevo llamado `portfolio` en tu cuenta `palcocerhurtado-tech` (público).
2. Sube **el contenido de esta carpeta** (los 4 archivos + la carpeta `assets`; no hace falta el standalone).
3. En el repo: `Settings` → `Pages` → Source: `Deploy from a branch` → Branch: `main` / `/root` → `Save`.
4. Espera 1–3 minutos y abre: `https://palcocerhurtado-tech.github.io/portfolio/`

## Qué incluye

- Boot loader estilo "archon-os" con barra de progreso
- Starfield de partículas doradas que reacciona al ratón (hero y contacto)
- Sistema orbital animado con los logos Archon / ADV / QuantBot
- Título con animación letra a letra, marquee infinito de skills
- Cursor magnético personalizado + botones magnéticos
- Tarjetas con efecto tilt 3D
- Timeline de experiencia que se dibuja al hacer scroll
- Contadores animados (6+ proyectos, 8+ certs, 3+ marcas)
- **Terminal interactiva**: `help`, `about`, `projects`, `open quantbot`, `skills`, `cv`, `contact`, `goto projects`, `theme teal`, `lang en`, `sudo hire-me`…
- Bilingüe ES/EN (incluida la terminal)
- Accesible: respeta `prefers-reduced-motion`, navegación por teclado

## Editar contenido

- Textos ES/EN: array `T` al principio de `app.js`
- Proyectos y enlaces: `index.html` (sección `#projects`) y `term.projects` en `app.js`
- Colores: variables `--gold`, `--bg`… al inicio de `styles.css`
- Tu foto y CV: añade `pablo-alcocer-portrait.jpg` / tu PDF a `assets/` y enlázalos donde quieras

Después de editar los archivos sueltos, regenera el standalone:

```bash
cd portfolio && python3 -c "
import base64,re,pathlib
html=pathlib.Path('index.html').read_text()
css=pathlib.Path('styles.css').read_text(); js=pathlib.Path('app.js').read_text()
html=re.sub(r'src=\"(assets/[^\"]+\.png)\"',lambda m:'src=\"data:image/png;base64,'+base64.b64encode(pathlib.Path(m.group(1)).read_bytes()).decode()+'\"',html)
html=re.sub(r'href=\"(assets/[^\"]+\.png)\"',lambda m:'href=\"data:image/png;base64,'+base64.b64encode(pathlib.Path(m.group(1)).read_bytes()).decode()+'\"',html)
html=html.replace('<link rel=\"stylesheet\" href=\"styles.css\">','<style>'+css+'</style>').replace('<script src=\"app.js\"></script>','<script>'+js+'</script>')
pathlib.Path('portfolio-standalone.html').write_text(html)
"
```
