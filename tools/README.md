# Herramientas de publicación — TO BE

La app se publica **cifrada** (AES-GCM, clave derivada del PIN con PBKDF2). En este repositorio no hay ningún dato en claro ni el PIN.

Para regenerar `index.html` a partir de la app sin cifrar:

```
pip install cryptography
python3 tools/build.py ruta/a/app_fuente.html <PIN>
git add index.html sw.js && git commit -m "Actualización datos" && git push
```

`sw.js` cambia de versión en cada build para que los móviles cojan la nueva.

## Generar la app desde el panel

El origen es el panel de Claude (artifact del Dashboard "Panel de gestión To Be Group"): su página `files/index.html` y un JSON por dataset.

```
npm i d3@7
python3 tools/standalone.py index_panel.html carpeta_datos/ node_modules/d3/dist/d3.min.js app_fuente.html
python3 tools/build.py app_fuente.html <PIN>
```
