
import json
import multiprocessing
import statistics
import time
from pathlib import Path


# ==========================================
# CONFIGURACIÓN
# ==========================================

GUARDAR_RESULTADOS = True

TAMANOS = [1000, 10000, 100000, 1000000]
VARIANTES = ["aleatorio", "ascendente", "descendente"]

REPETICIONES = 5
LIMITE_SEGUNDOS = 300


# ==========================================
# 1. DUAL-PIVOT QUICKSORT
# ==========================================

def dual_pivot_quicksort(arreglo):

    if len(arreglo) <= 1:
        return arreglo

    pila = [(0, len(arreglo) - 1)]

    while pila:

        izquierda, derecha = pila.pop()

        if izquierda >= derecha:
            continue

        # Primer y último elemento como pivotes
        if arreglo[izquierda] > arreglo[derecha]:
            arreglo[izquierda], arreglo[derecha] = (
                arreglo[derecha], arreglo[izquierda]
            )

        pivote1 = arreglo[izquierda]
        pivote2 = arreglo[derecha]

        menor = izquierda + 1
        actual = menor
        mayor = derecha - 1

        while actual <= mayor:

            if arreglo[actual] < pivote1:

                arreglo[actual], arreglo[menor] = (
                    arreglo[menor], arreglo[actual]
                )

                menor += 1

            elif arreglo[actual] >= pivote2:

                while (
                        arreglo[mayor] > pivote2
                        and actual < mayor
                ):
                    mayor -= 1

                arreglo[actual], arreglo[mayor] = (
                    arreglo[mayor], arreglo[actual]
                )

                mayor -= 1

                if arreglo[actual] < pivote1:

                    arreglo[actual], arreglo[menor] = (
                        arreglo[menor], arreglo[actual]
                    )

                    menor += 1

            actual += 1

        menor -= 1
        mayor += 1

        arreglo[izquierda], arreglo[menor] = (
            arreglo[menor], arreglo[izquierda]
        )

        arreglo[derecha], arreglo[mayor] = (
            arreglo[mayor], arreglo[derecha]
        )

        # Subarreglos pendientes
        pila.append((izquierda, menor - 1))

        if pivote1 < pivote2:
            pila.append((menor + 1, mayor - 1))

        pila.append((mayor + 1, derecha))

    return arreglo


# ==========================================
# 2. LEER ARCHIVOS
# ==========================================

def leer_arreglo(ruta):

    with open(ruta, "r") as archivo:
        return [int(linea) for linea in archivo]


# ==========================================
# 3. EJECUCIÓN INDEPENDIENTE
# ==========================================

def ejecutar_ordenamiento(numeros, conexion):

    try:
        copia = numeros.copy()

        inicio = time.perf_counter_ns()

        dual_pivot_quicksort(copia)

        fin = time.perf_counter_ns()

        tiempo_ms = (fin - inicio) / 1_000_000

        correcto = all(
            copia[i] <= copia[i + 1]
            for i in range(len(copia) - 1)
        )

        conexion.send({
            "tiempo_ms": tiempo_ms,
            "correcto": correcto
        })

    except Exception as error:

        conexion.send({
            "error": str(error)
        })

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
# 4. ESTIMAR TIEMPOS
# ==========================================

def estimar_tiempo(n, referencia):

    if referencia is None:
        return None

    n_anterior = referencia["n"]
    tiempo_anterior = referencia["promedio_ms"]

    # Extrapolación conservadora cuadrática
    # para evitar pruebas excesivamente largas.
    estimacion_ms = tiempo_anterior * (
            n / n_anterior
    ) ** 2

    return {
        "tipo": "estimado",
        "tiempo_estimado_ms": estimacion_ms,
        "metodo_estimacion": "Extrapolación cuadrática O(n²)",
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
            / "dual_pivot_quicksort"
    )

    resultados_por_tamano = {
        n: {
            "algoritmo": "Dual-Pivot QuickSort",
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
