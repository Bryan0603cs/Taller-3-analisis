from pathlib import Path
import random

TAMANOS = [1000, 10000, 100000, 1000000]
SEMILLA = 20261020

BASE = Path(__file__).resolve().parent
DATOS = BASE.parent / "Punto 3" / "datos" / "datos"
SALIDA = BASE / "claves"
SALIDA.mkdir(parents=True, exist_ok=True)

def leer(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return [int(x.strip()) for x in f if x.strip()]

for n in TAMANOS:
    arreglo = leer(DATOS / f"ascendente_{n}.txt")
    conjunto = set(arreglo)
    rng = random.Random(SEMILLA + n)

    # 500 claves presentes.
    posiciones = rng.sample(range(n), 500)
    presentes = [arreglo[i] for i in posiciones]

    # 500 claves ausentes de 8 dígitos.
    ausentes = []
    usados = set()
    while len(ausentes) < 500:
        x = rng.randint(10_000_000, 99_999_999)
        if x not in conjunto and x not in usados:
            ausentes.append(x)
            usados.add(x)

    claves = presentes + ausentes
    rng.shuffle(claves)

    ruta = SALIDA / f"claves_{n}.txt"
    ruta.write_text("\n".join(map(str, claves)), encoding="utf-8")
    print(f"{ruta.name}: 500 presentes + 500 ausentes")
