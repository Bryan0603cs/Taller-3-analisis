from pathlib import Path
import json
import math

BASE = Path(__file__).resolve().parent
P1 = BASE.parent / "Punto 3" / "resultados"
P2 = BASE / "resultados"

def tiempo_ordenamiento(lang):
    candidatos = []
    carpeta = P1 / lang

    for algoritmo in carpeta.iterdir():
        if not algoritmo.is_dir():
            continue

        ruta = algoritmo / "1000000.json"
        if not ruta.exists():
            continue

        d = json.loads(ruta.read_text(encoding="utf-8"))
        r = d["resultados"]["aleatorio"]

        if r["tipo"] == "medido":
            t = r["promedio_ms"]
        else:
            t = r["tiempo_estimado_ms"]

        candidatos.append((t, d["algoritmo"]))

    return min(candidatos)

def tiempo_busqueda(lang, algoritmo):
    d = json.loads(
        (P2 / lang / f"{algoritmo}_1000000.json").read_text(encoding="utf-8")
    )
    return d["promedio_ns"] / 1_000_000

for lang in ["java", "python"]:
    orden_ms, algoritmo = tiempo_ordenamiento(lang)
    lineal_ms = tiempo_busqueda(lang, "lineal")
    binaria_ms = tiempo_busqueda(lang, "binaria")

    print("\n", lang.upper())
    print("Mejor ordenamiento:", algoritmo, f"{orden_ms:.6f} ms")
    print("Lineal:", f"{lineal_ms:.9f} ms/búsqueda")
    print("Binaria:", f"{binaria_ms:.9f} ms/búsqueda")

    diferencia = lineal_ms - binaria_ms

    if diferencia <= 0:
        print("Con estas mediciones no existe un punto de cruce favorable.")
        continue

    limite = orden_ms / diferencia
    k = math.floor(limite) + 1

    print("Inecuación:")
    print(f"{orden_ms:.6f} + k({binaria_ms:.9f}) < k({lineal_ms:.9f})")
    print(f"k > {limite:.3f}")
    print("Desde k =", k, "búsquedas conviene ordenar + búsqueda binaria.")
