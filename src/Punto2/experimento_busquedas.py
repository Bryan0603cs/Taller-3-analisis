from pathlib import Path
import importlib.util
import json
import math
import multiprocessing
import statistics
import time

TAMANOS = [1000, 10000, 100000, 1000000]
REPETICIONES = 5
LIMITE_SEGUNDOS = 300

BASE = Path(__file__).resolve().parent
DATOS = BASE.parent / "Punto 3" / "datos" / "datos"
CLAVES = BASE / "claves"
SALIDA = BASE / "resultados" / "python"
SALIDA.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("busquedas", BASE / "Busquedas.py")
busquedas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(busquedas)

ALGORITMOS = {
    "lineal": busquedas.lineal,
    "binaria": busquedas.binaria,
    "ternaria": busquedas.ternaria,
    "salto": busquedas.salto,
    "interpolacion": busquedas.interpolacion,
    "exponencial": busquedas.exponencial,
}

def leer(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return [int(x.strip()) for x in f if x.strip()]

def ejecutar_lote(nombre, arreglo, claves, conexion):
    try:
        funcion = ALGORITMOS[nombre]
        checksum = 0
        inicio = time.perf_counter_ns()
        for clave in claves:
            checksum += funcion(arreglo, clave)
        fin = time.perf_counter_ns()
        conexion.send({
            "ns_por_busqueda": (fin - inicio) / len(claves),
            "checksum": checksum
        })
    except Exception as e:
        conexion.send({"error": str(e)})
    finally:
        conexion.close()

def medir(nombre, arreglo, claves):
    ctx = multiprocessing.get_context("spawn")
    receptor, emisor = ctx.Pipe(duplex=False)
    proceso = ctx.Process(
        target=ejecutar_lote,
        args=(nombre, arreglo, claves, emisor)
    )
    proceso.start()
    emisor.close()
    proceso.join(timeout=LIMITE_SEGUNDOS)

    if proceso.is_alive():
        proceso.terminate()
        proceso.join()
        receptor.close()
        return None, "tiempo_agotado"

    if receptor.poll():
        r = receptor.recv()
        receptor.close()
        if "error" in r:
            raise RuntimeError(r["error"])
        return r["ns_por_busqueda"], "correcto"

    receptor.close()
    raise RuntimeError("El proceso terminó sin resultado")

def factor_estimacion(nombre, n_anterior, n):
    if nombre == "lineal":
        return n / n_anterior
    if nombre == "salto":
        return math.sqrt(n / n_anterior)
    if nombre in ("binaria", "ternaria", "exponencial"):
        return math.log2(n) / math.log2(n_anterior)
    if nombre == "interpolacion":
        return math.log(max(2, math.log(n))) / math.log(max(2, math.log(n_anterior)))
    return n / n_anterior

def guardar(nombre, n, contenido):
    ruta = SALIDA / f"{nombre}_{n}.json"
    ruta.write_text(json.dumps(contenido, indent=2, ensure_ascii=False), encoding="utf-8")

def experimento_crecimiento():
    ultima_medicion = {nombre: None for nombre in ALGORITMOS}

    for n in TAMANOS:
        arreglo = leer(DATOS / f"ascendente_{n}.txt")
        claves = leer(CLAVES / f"claves_{n}.txt")
        print(f"\n===== n={n} =====")

        for nombre in ALGORITMOS:
            tiempos = []
            agotado = False

            for rep in range(REPETICIONES):
                valor, estado = medir(nombre, arreglo, claves)
                if estado == "tiempo_agotado":
                    agotado = True
                    break
                tiempos.append(valor)
                print(f"{nombre} rep {rep+1}: {valor:.3f} ns/búsqueda")

            if not agotado and len(tiempos) == REPETICIONES:
                r = {
                    "algoritmo": nombre,
                    "lenguaje": "Python",
                    "n": n,
                    "tipo": "medido",
                    "unidad": "ns_por_busqueda",
                    "repeticiones_ns": tiempos,
                    "promedio_ns": statistics.mean(tiempos),
                    "desviacion_ns": statistics.stdev(tiempos)
                }
                ultima_medicion[nombre] = {
                    "n": n,
                    "promedio_ns": r["promedio_ns"]
                }
            else:
                ref = ultima_medicion[nombre]
                if ref is None:
                    raise RuntimeError(f"No hay referencia para estimar {nombre} n={n}")
                factor = factor_estimacion(nombre, ref["n"], n)
                r = {
                    "algoritmo": nombre,
                    "lenguaje": "Python",
                    "n": n,
                    "tipo": "estimado",
                    "unidad": "ns_por_busqueda",
                    "promedio_ns": ref["promedio_ns"] * factor,
                    "metodo_estimacion": f"Extrapolación desde n={ref['n']} según complejidad teórica",
                    "motivo": "El lote de 1.000 búsquedas superó cinco minutos"
                }
                print(f"{nombre}: ESTIMADO {r['promedio_ns']:.3f} ns/búsqueda")

            guardar(nombre, n, r)

def experimento_posiciones():
    n = 1_000_000
    arreglo = leer(DATOS / f"ascendente_{n}.txt")
    posiciones = {
        "inicio": arreglo[0],
        "centro": arreglo[n // 2],
        "final": arreglo[-1]
    }
    salida = {}

    for nombre in ALGORITMOS:
        salida[nombre] = {}
        for posicion, clave in posiciones.items():
            claves = [clave] * 1000
            tiempos = []
            agotado = False

            for rep in range(REPETICIONES):
                valor, estado = medir(nombre, arreglo, claves)
                if estado == "tiempo_agotado":
                    agotado = True
                    break
                tiempos.append(valor)

            if agotado:
                salida[nombre][posicion] = {
                    "clave": clave,
                    "tipo": "no_medido",
                    "motivo": "El lote superó cinco minutos"
                }
            else:
                salida[nombre][posicion] = {
                    "clave": clave,
                    "tipo": "medido",
                    "promedio_ns": statistics.mean(tiempos),
                    "desviacion_ns": statistics.stdev(tiempos),
                    "repeticiones_ns": tiempos
                }

            print(nombre, posicion, salida[nombre][posicion])

    (SALIDA / "posiciones_1000000.json").write_text(
        json.dumps(salida, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

if __name__ == "__main__":
    experimento_crecimiento()
    experimento_posiciones()
