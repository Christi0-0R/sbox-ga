# Demo para la captura de la diapositiva 11.
# Uso (desde la raíz del repo):  PYTHONPATH=. python demo_cifrado.py
import json
from src.cifrado import cifrar, descifrar, sha256

info = json.load(open("resultados/final/sboxes/estatica_1000.json"))
sbox = info["sbox"]
print(f"S-box: {info['variante']}, semilla {info['semilla']}  ->  NL = {info['nl']}, delta = {info['delta']}")

mensaje = "Taller de Investigacion II - ITM 2026".encode()
c = cifrar(mensaje, sbox)
d = descifrar(c, sbox)

print("Original :", mensaje.decode())
print("Cifrado  :", c.hex(" ")[:71], "...")
print("Descifrado:", d.decode())
print("SHA-256 original  :", sha256(mensaje))
print("SHA-256 descifrado:", sha256(d))
print("Coinciden:", sha256(mensaje) == sha256(d))




