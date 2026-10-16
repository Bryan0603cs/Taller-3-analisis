
import random
from pathlib import Path

random.seed(42)

carpeta = Path("datos")
carpeta.mkdir(exist_ok=True)

tamanos = [1000, 10000, 100000, 1000000]

for n in tamanos:
    numeros = [
        random.randint(10000000, 99999999)
        for _ in range(n)
    ]

    variantes = {
        "aleatorio": numeros,
        "ascendente": sorted(numeros),
        "descendente": sorted(numeros, reverse=True)
    }

    for nombre, arreglo in variantes.items():
        ruta = carpeta / f"{nombre}_{n}.txt"

        with open(ruta, "w") as archivo:
            for numero in arreglo:
                archivo.write(f"{numero}\n")

    print(f"Archivos generados para n = {n}")

