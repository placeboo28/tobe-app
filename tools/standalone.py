#!/usr/bin/env python3
"""Genera la app TO BE independiente (sin el runtime del panel de Claude) a partir del
panel publicado como artifact: incrusta los datos de cada dataset, d3 y un sustituto de `dash`.
Uso: python3 tools/standalone.py <index_panel.html> <carpeta_datos> <d3.min.js> <salida.html>
- index_panel.html: el archivo files/index.html del artifact del panel (texto de la página).
- carpeta_datos: un JSON por dataset, con el nombre del dataset (kpis.json, ventas_mr.json, ...).
- d3.min.js: d3 v7 (npm i d3@7 → node_modules/d3/dist/d3.min.js).
Este script no contiene datos ni el PIN."""
import json, sys, os, glob
from datetime import datetime
page_path, data_dir, d3_path, out = sys.argv[1:5]
data = {os.path.basename(f)[:-5]: json.load(open(f, encoding='utf8')) for f in sorted(glob.glob(os.path.join(data_dir, '*.json')))}
page = open(page_path, encoding='utf8').read()
links='\n'.join(l for l in page.split('\n') if l.startswith('<link'))
page='\n'.join(l for l in page.split('\n') if not l.startswith('<link'))
d3=open(d3_path,encoding='utf8').read()
# Imágenes guardadas como /_blob/<id> en el panel: se incrustan desde <carpeta_datos>/../blobs/<id>.<ext> si existen
import base64, mimetypes
_bd=os.path.join(os.path.dirname(os.path.abspath(data_dir)),'blobs')
for _f in glob.glob(os.path.join(_bd,'*')):
    _id=os.path.splitext(os.path.basename(_f))[0]; _mt=mimetypes.guess_type(_f)[0] or 'application/octet-stream'
    page=page.replace('/_blob/'+_id,'data:%s;base64,%s'%(_mt,base64.b64encode(open(_f,'rb').read()).decode()))
DIAS=['lunes','martes','miércoles','jueves','viernes','sábado','domingo']
MESES=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
_f=max((r.get('fecha') or '') for r in data.get('cierres_caja',[{'fecha':''}]))
if _f:
    _d=datetime.strptime(_f,'%Y-%m-%d'); stamp=f"{DIAS[_d.weekday()]} {_d.day} de {MESES[_d.month-1]} de {_d.year}"
else:
    stamp=datetime.now().strftime('%d/%m/%Y')
shim='''<script>
window.__TOBE_DATA__ = %s;
(function(){
  var D = window.__TOBE_DATA__, calcs = {}, cache = {}, cbs = [];
  function get(id){
    if (D[id]) return {status:'ok', data:D[id]};
    if (calcs[id]) { if (!(id in cache)) { try { var c = calcs[id]; cache[id] = c.fn.apply(null, c.inputs.map(function(i){ return get(i).data; })); } catch(e) { console.error(id, e); cache[id] = null; } }
      return cache[id] ? {status:'ok', data:cache[id]} : {status:'error', data:[]}; }
    return {status:'error', data:[]};
  }
  var link = (location.hash || '').slice(1);
  window.dash = {
    colors: ['#2F6FDB','#E07A1F','#7B4FD6','#0F9AA8','#B8860B','#1E9E6A','#D0225F','#8B5A2B'],
    calc: function(id, o){ calcs[id] = o; },
    data: get,
    onData: function(f){ cbs.push(f); setTimeout(f, 0); },
    params: function(){ return {}; },
    setLink: function(t){ try { history.replaceState(null, '', '#' + t); } catch(e){} }
  };
  window.addEventListener('load', function(){ if (link) { var b = document.querySelector('.tab[data-tab="' + link + '"]'); if (b) b.click(); } });
})();
</script>''' % json.dumps(data, ensure_ascii=False, separators=(',',':'))
tokens='''<style>
:root{--font-anthropic-sans:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--font-anthropic-serif:"Lora",Georgia,serif;
--color-bg:#F6F5F2;--color-panel:#FFFFFF;--color-fg:#1D1D1B;--color-fg-muted:#6B6A66;--color-border-line:#E3E1DC;--color-ok:#1E9E6A;--color-bad:#C62D52;
--cds-border:#E3E1DC;--cds-chart-axis:#9A988F;--cds-chart-grid:#ECEAE5;--cds-chart-muted:#B9B6AE;--cds-dur-slow:.4s;
--cds-font-size-body:15px;--cds-font-size-caption:12.5px;--cds-font-size-heading:16px;--cds-font-size-title:26px;--cds-font-weight-medium:600;
--cds-gap-lg:20px;--cds-gap-md:14px;--cds-gap-sm:8px;--cds-pad-lg:18px;--cds-pad-sm:10px;--cds-pad-xs:6px;--cds-radius:14px;
--cds-shadow-popover:0 8px 24px rgba(0,0,0,.14);--cds-surface-popover:#FFFFFF}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--color-bg:#141413;--color-panel:#1F1E1C;--color-fg:#F1EFEA;--color-fg-muted:#A6A39B;--color-border-line:#34322E;--cds-border:#34322E;--cds-chart-axis:#7D7A72;--cds-chart-grid:#2B2A27;--cds-chart-muted:#5E5B55;--cds-surface-popover:#262522;--color-ok:#3FBF8A;--color-bad:#F0628A}}
:root[data-theme="dark"]{--color-bg:#141413;--color-panel:#1F1E1C;--color-fg:#F1EFEA;--color-fg-muted:#A6A39B;--color-border-line:#34322E;--cds-border:#34322E;--cds-chart-axis:#7D7A72;--cds-chart-grid:#2B2A27;--cds-chart-muted:#5E5B55;--cds-surface-popover:#262522}
html,body{margin:0;background:var(--color-bg);color:var(--color-fg);font-family:var(--font-anthropic-sans);font-size:var(--cds-font-size-body);-webkit-text-size-adjust:100%%}
#dash-root{padding:max(12px,env(safe-area-inset-top)) var(--dash-gutter,16px) 40px}
.dash-skeleton{min-height:120px;border-radius:10px;background:linear-gradient(90deg,var(--cds-chart-grid),transparent,var(--cds-chart-grid));background-size:200%% 100%%;animation:sk 1.4s infinite}
@keyframes sk{to{background-position:-200%% 0}}
.app-foot{max-width:1180px;margin:18px auto 0;color:var(--color-fg-muted);font-size:12px;text-align:center}
</style>'''.replace('%%','%')
html=f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>TO BE · Gestión</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&family=Lora:ital@0;1&family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">
{tokens}
</head><body><div id="dash-root">
<p class="app-stamp" style="max-width:1180px;margin:0 auto 8px;color:var(--color-fg-muted);font-size:13px;text-align:right">Actualizado hasta el <strong style="color:var(--color-fg)">{stamp}</strong></p>
<script>{d3}</script>
{shim}
{page}
<p class="app-foot">Actualizado hasta el {stamp}</p>
</div></body></html>'''
open(out,'w',encoding='utf8').write(html)
print('OK',len(html))
