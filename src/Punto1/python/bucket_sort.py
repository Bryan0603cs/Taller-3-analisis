
import json
import math
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
# 1. BUCKET SORT
# ==========================================

def insertion_sort_cubeta(cubeta):

    for i in range(1, len(cubeta)):

        actual = cubeta[i]
        j = i - 1

        while j >= 0 and cubeta[j] > actual:

            cubeta[j + 1] = cubeta[j]
            j -= 1

        cubeta[j + 1] = actual


def bucket_sort(arreglo):

    n = len(arreglo)

    if n <= 1:
        return arreglo

    minimo = min(arreglo)
    maximo = max(arreglo)

    if minimo == maximo:
        return arreglo

    # Una cantidad de cubetas proporcional
    # a la raíz cuadrada del tamaño.
    cantidad_cubetas = max(1, math.isqrt(n))

    cubetas = [
        [] for _ in range(cantidad_cubetas)
    ]

    rango = maximo - minimo + 1

    # Distribuir los números en cubetas.
    for numero in arreglo:

        indice = (
                (numero - minimo)
                * cantidad_cubetas
                // rango
        )

        cubetas[indice].append(numero)

    # Ordenar cada cubeta y unir resultados.
    posicion = 0

    for cubeta in cubetas:

        insertion_sort_cubeta(cubeta)

        for numero in cubeta:

            arreglo[posicion] = numero
            posicion += 1

    return arreglo


# ==========================================
# 2. LEER ARCHIVOS
# ==========================================

def leer_arreglo(ruta):

    with open(
            ruta,
            "r",
            encoding="utf-8"
    ) as archivo:

        return [int(linea) for linea in archivo]


# ==========================================
# 3. EJECUTAR Y MEDIR
# ==========================================

def ejecutar_ordenamiento(numeros, conexion):

    try:

        copia = numeros.copy()

        inicio = time.perf_counter_ns()

        bucket_sort(copia)

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
# 4. ESTIMACIÓN DE TIEMPOS
# ==========================================

def estimar_tiempo(n, referencia):

    if referencia is None:
        return None

    n_anterior = referencia["n"]
    tiempo_anterior = referencia["promedio_ms"]

    # Estimación basada en una distribución
    # aproximadamente uniforme de los datos.
    factor = n / n_anterior

    estimacion_ms = tiempo_anterior * factor

    return {
        "tipo": "estimado",
        "tiempo_estimado_ms": estimacion_ms,
        "metodo_estimacion": (
            "Extrapolación lineal aproximada O(n), "
            "suponiendo distribución uniforme"
        ),
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
            / "bucket_sort"
    )

    resultados_por_tamano = {
        n: {
            "algoritmo": "Bucket Sort",
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

    if GUARDAR_RESULTADOS:

        carpeta_resultados.mkdir(
            parents=True,
            exist_ok=True
        )

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

            else:

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
                        "motivo": (
                            "Límite de cinco minutos alcanzado"
                        )
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

            # Guardar después de cada caso.
            if GUARDAR_RESULTADOS:

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

                print(f"Avance guardado: {archivo_json}")

    # ==========================================
    # 6. GUARDAR RESULTADOS FINALES
    # ==========================================

    if GUARDAR_RESULTADOS:

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
