
import json
import math
import multiprocessing
import statistics
import time
from pathlib import Path


# ==========================================
# CONFIGURACIÓN
# ==========================================

# False: ejecutar sin guardar JSON
# True: ejecutar y guardar JSON
GUARDAR_RESULTADOS = True

TAMANOS = [1000, 10000, 100000, 1000000]
VARIANTES = ["aleatorio", "ascendente", "descendente"]

REPETICIONES = 5
LIMITE_SEGUNDOS = 300


# ==========================================
# 1. ALGORITMO MERGE SORT
# ==========================================

def merge_sort(arreglo):

    auxiliar = [0] * len(arreglo)

    def ordenar(inicio, fin):

        if fin - inicio <= 1:
            return

        medio = (inicio + fin) // 2

        ordenar(inicio, medio)
        ordenar(medio, fin)

        i = inicio
        j = medio
        k = inicio

        # Mezclar las dos mitades ordenadas
        while i < medio and j < fin:

            if arreglo[i] <= arreglo[j]:
                auxiliar[k] = arreglo[i]
                i += 1
            else:
                auxiliar[k] = arreglo[j]
                j += 1

            k += 1

        # Copiar elementos restantes
        while i < medio:
            auxiliar[k] = arreglo[i]
            i += 1
            k += 1

        while j < fin:
            auxiliar[k] = arreglo[j]
            j += 1
            k += 1

        # Pasar los elementos ordenados al arreglo
        for posicion in range(inicio, fin):
            arreglo[posicion] = auxiliar[posicion]

    ordenar(0, len(arreglo))

    return arreglo


# ==========================================
# 2. LEER ARCHIVOS
# ==========================================

def leer_arreglo(ruta):

    with open(ruta, "r") as archivo:
        return [int(linea) for linea in archivo]


# ==========================================
# 3. EJECUTAR Y MEDIR
# ==========================================

def ejecutar_ordenamiento(numeros, conexion):

    try:
        copia = numeros.copy()

        inicio = time.perf_counter_ns()

        merge_sort(copia)

        fin = time.perf_counter_ns()

        tiempo_ms = (fin - inicio) / 1_000_000

        # Verificar ordenamiento fuera de la medición
        correcto = all(
            copia[i] <= copia[i + 1]
            for i in range(len(copia) - 1)
        )

        conexion.send({
            "tiempo_ms": tiempo_ms,
            "correcto": correcto
        })

    except Exception as error:

        conexion.send({"error": str(error)})

    finally:
        conexion.close()


def medir_con_limite(numeros):

    contexto = multiprocessing.get_context("spawn")

    receptor, emisor = contexto.Pipe(duplex=False)

    proceso = contexto.Process(
        target=ejecutar_ordenamiento,
        args=(numeros, emisor)
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

        respuesta = receptor.recv()
        receptor.close()

        if "error" in respuesta:
            raise RuntimeError(respuesta["error"])

        if not respuesta["correcto"]:
            raise RuntimeError(
                "El arreglo no quedó correctamente ordenado"
            )

        return respuesta["tiempo_ms"], "correcto"

    receptor.close()

    raise RuntimeError(
        "El proceso terminó sin devolver resultados"
    )


# ==========================================
# 4. ESTIMACIÓN DE TIEMPOS
# ==========================================

def estimar_tiempo(n, referencia):

    if referencia is None:
        return None

    n_anterior = referencia["n"]
    tiempo_anterior = referencia["promedio_ms"]

    # Merge Sort: O(n log n)
    factor = (
            (n * math.log2(n))
            /
            (n_anterior * math.log2(n_anterior))
    )

    estimacion_ms = tiempo_anterior * factor

    return {
        "tipo": "estimado",
        "tiempo_estimado_ms": estimacion_ms,
        "metodo_estimacion": "Extrapolación O(n log n)",
        "referencia_n": n_anterior,
        "referencia_promedio_ms": tiempo_anterior
    }


# ==========================================
# 5. EXPERIMENTO COMPLETO
# ==========================================

def main():

    base = Path(__file__).resolve().parent.parent

    carpeta_datos = base / "datos" / "datos"

    carpeta_resultados = (
            base
            / "resultados"
            / "python"
            / "merge_sort"
    )

    resultados_por_tamano = {
        n: {
            "algoritmo": "Merge Sort",
            "lenguaje": "Python",
            "tamano": n,
            "repeticiones_solicitadas": REPETICIONES,
            "limite_segundos": LIMITE_SEGUNDOS,
            "resultados": {}
        }
        for n in TAMANOS
    }

    ultimas_mediciones = {
        variante: None
        for variante in VARIANTES
    }

    for variante in VARIANTES:

        print(f"\n========== {variante.upper()} ==========")

        for n in TAMANOS:

            print(f"\nTamaño: {n}")

            estimacion = estimar_tiempo(
                n,
                ultimas_mediciones[variante]
            )

            if (
                    estimacion is not None
                    and estimacion["tiempo_estimado_ms"]
                    > LIMITE_SEGUNDOS * 1000
            ):

                estimacion["motivo"] = (
                    "Tiempo previsto superior a cinco minutos"
                )

                resultados_por_tamano[n]["resultados"][variante] = (
                    estimacion
                )

                print(
                    "Tiempo estimado: "
                    f"{estimacion['tiempo_estimado_ms'] / 1000:.2f} s"
                )

                continue

            ruta = carpeta_datos / f"{variante}_{n}.txt"

            if not ruta.exists():
                raise FileNotFoundError(
                    f"No se encontró: {ruta}"
                )

            numeros = leer_arreglo(ruta)

            if len(numeros) != n:
                raise ValueError(
                    f"Se esperaban {n} números en {ruta.name}"
                )

            tiempos = []

            for i in range(REPETICIONES):

                tiempo_ms, estado = medir_con_limite(
                    numeros
                )

                if estado == "tiempo_agotado":

                    print(
                        f"Ejecución {i + 1}: "
                        "superó cinco minutos"
                    )

                    break

                tiempos.append(tiempo_ms)

                print(
                    f"Ejecución {i + 1}: "
                    f"{tiempo_ms:.4f} ms"
                )

            if len(tiempos) == REPETICIONES:

                promedio = statistics.mean(tiempos)
                desviacion = statistics.stdev(tiempos)

                resultados_por_tamano[n]["resultados"][variante] = {
                    "tipo": "medido",
                    "tiempos_ms": tiempos,
                    "promedio_ms": promedio,
                    "desviacion_estandar_ms": desviacion
                }

                ultimas_mediciones[variante] = {
                    "n": n,
                    "promedio_ms": promedio
                }

                print(f"Promedio: {promedio:.4f} ms")
                print(f"Desviación: {desviacion:.4f} ms")

            else:

                estimacion = estimar_tiempo(
                    n,
                    ultimas_mediciones[variante]
                )

                resultado = {
                    "tipo": "estimado",
                    "tiempos_medidos_ms": tiempos,
                    "repeticiones_completadas": len(tiempos),
                    "motivo": "Límite de cinco minutos alcanzado"
                }

                if estimacion is not None:
                    resultado.update(estimacion)
                else:
                    resultado["tiempo_estimado_ms"] = None
                    resultado["metodo_estimacion"] = (
                        "Sin referencia previa suficiente"
                    )

                resultados_por_tamano[n]["resultados"][variante] = (
                    resultado
                )

            del numeros

    # ==========================================
    # 6. GUARDAR RESULTADOS
    # ==========================================

    if GUARDAR_RESULTADOS:

        carpeta_resultados.mkdir(
            parents=True,
            exist_ok=True
        )

        for n in TAMANOS:

            archivo_json = carpeta_resultados / f"{n}.json"

            with open(
                    archivo_json,
                    "w",
                    encoding="utf-8"
            ) as archivo:

                json.dump(
                    resultados_por_tamano[n],
                    archivo,
                    indent=4,
                    ensure_ascii=False
                )

            print(f"\nGuardado: {archivo_json}")

    else:

        print(
            "\nPruebas terminadas. "
            "No se guardaron archivos JSON."
        )

    print("\nEXPERIMENTO FINALIZADO")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
