#!/usr/bin/env python3
"""Genera index.html cifrado de la app TO BE.
Uso: python3 tools/build.py <app_fuente.html> <PIN>
- app_fuente.html: la app sin cifrar (la versión del artifact de Claude).
- El PIN NO se guarda en el repositorio.
Escribe ./index.html y actualiza la versión de caché de sw.js."""
import os, sys, base64, json, re, time
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, "tools")
src_path, pin = sys.argv[1], sys.argv[2]
src = open(src_path, encoding="utf8").read()
inst = open(os.path.join(T, "install.js"), encoding="utf8").read()
i = src.rfind("</body>")
src = src[:i] + inst + src[i:] if i != -1 else src + inst
it = 1_000_000
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(pin.encode())
ct = AESGCM(key).encrypt(iv, src.encode("utf8"), None)
payload = json.dumps({"s": base64.b64encode(salt).decode(), "i": base64.b64encode(iv).decode(), "n": it, "c": base64.b64encode(ct).decode()})
lock = open(os.path.join(T, "lock.html"), encoding="utf8").read()
lock = (lock.replace("__PAYLOAD__", payload)
            .replace('placeholder="Contraseña"', 'placeholder="PIN" inputmode="numeric"')
            .replace("'Contraseña incorrecta'", "'PIN incorrecto'")
            .replace('<meta name="apple-mobile-web-app-capable" content="yes">', '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">', 1)
            .replace("</body>", inst + "</body>", 1))
open(os.path.join(ROOT, "index.html"), "w", encoding="utf8").write(lock)
sw = os.path.join(ROOT, "sw.js")
s = open(sw, encoding="utf8").read()
s = re.sub(r"const CACHE = 'tobe-[^']*';", f"const CACHE = 'tobe-{time.strftime('%Y%m%d%H%M')}';", s)
open(sw, "w", encoding="utf8").write(s)
print("OK index.html", len(lock), "bytes")
