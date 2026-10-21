from pathlib import Path
import json
import csv
import math
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
RESULTADOS = BASE / "resultados"
SALIDA = BASE / "graficas"
SALIDA.mkdir(parents=True, exist_ok=True)

ALGORITMOS = ["lineal", "binaria", "ternaria", "salto", "interpolacion", "exponencial"]
TAMANOS = [1000, 10000, 100000, 1000000]

def cargar(lang, alg, n):
    ruta = RESULTADOS / lang / f"{alg}_{n}.json"
    return json.loads(ruta.read_text(encoding="utf-8"))

def valor_ms(r):
    return r["promedio_ns"] / 1_000_000

def crecimiento(lang):
    plt.figure(figsize=(10, 6))
    for alg in ALGORITMOS:
        ys = [valor_ms(cargar(lang, alg, n)) for n in TAMANOS]
        plt.plot(TAMANOS, ys, marker="o", label=alg)
        for x, y, n in zip(TAMANOS, ys, TAMANOS):
            r = cargar(lang, alg, n)
            if r.get("tipo") == "estimado":
                plt.annotate("estimado", (x, y), fontsize=7)

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Tamaño del arreglo (n)")
    plt.ylabel("Tiempo promedio por búsqueda (ms)")
    plt.title(f"Crecimiento de algoritmos de búsqueda - {lang.capitalize()}")
    plt.grid(True, which="both", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(SALIDA / f"crecimiento_{lang}.png", dpi=220)
    plt.close()

def comparacion():
    java = [valor_ms(cargar("java", a, 1_000_000)) for a in ALGORITMOS]
    python = [valor_ms(cargar("python", a, 1_000_000)) for a in ALGORITMOS]

    x = list(range(len(ALGORITMOS)))
    ancho = 0.38

    plt.figure(figsize=(11, 6))
    plt.bar([i - ancho/2 for i in x], java, width=ancho, label="Java")
    plt.bar([i + ancho/2 for i in x], python, width=ancho, label="Python")
    plt.yscale("log")
    plt.xticks(x, ALGORITMOS, rotation=20)
    plt.ylabel("Tiempo promedio por búsqueda (ms)")
    plt.title("Compilado frente a interpretado - n = 1.000.000")
    plt.legend()
    plt.tight_layout()
    plt.savefig(SALIDA / "java_vs_python_1000000.png", dpi=220)
    plt.close()

def tablas_posicion(lang):
    ruta = RESULTADOS / lang / "posiciones_1000000.json"
    datos = json.loads(ruta.read_text(encoding="utf-8"))

    salida = SALIDA / f"tabla_posiciones_{lang}.csv"
    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["algoritmo", "inicio_ms", "centro_ms", "final_ms"])
        for alg in ALGORITMOS:
            fila = [alg]
            for pos in ["inicio", "centro", "final"]:
                d = datos[alg][pos]
                fila.append(
                    "" if "promedio_ns" not in d
                    else d["promedio_ns"] / 1_000_000
                )
            w.writerow(fila)

    return datos

if __name__ == "__main__":
    crecimiento("java")
    crecimiento("python")
    comparacion()
    tablas_posicion("java")
    tablas_posicion("python")
    print("Gráficas y tablas creadas en:", SALIDA)
