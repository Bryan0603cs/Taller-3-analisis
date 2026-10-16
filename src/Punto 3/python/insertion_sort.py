
import json
import multiprocessing
import statistics
import time
from pathlib import Path


# ==========================================
# 1. ALGORITMO INSERTION SORT
# ==========================================

def insertion_sort(arreglo):
    for i in range(1, len(arreglo)):
        actual = arreglo[i]
        j = i - 1

        while j >= 0 and arreglo[j] > actual:
            arreglo[j + 1] = arreglo[j]
            j -= 1

        arreglo[j + 1] = actual

    return arreglo


# ==========================================
# 2. LECTURA DE ARCHIVOS
# ==========================================

def leer_arreglo(ruta):
    with open(ruta, "r") as archivo:
        return [int(linea) for linea in archivo]


# ==========================================
# 3. MEDICIÓN EN UN PROCESO INDEPENDIENTE
# ==========================================

def ejecutar_ordenamiento(numeros, conexion):
    try:
        copia = numeros.copy()

        inicio = time.perf_counter_ns()
        insertion_sort(copia)
        fin = time.perf_counter_ns()

        tiempo_ms = (fin - inicio) / 1_000_000

        # Verificación fuera del intervalo medido
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


def medir_con_limite(numeros, limite_segundos):
    contexto = multiprocessing.get_context("spawn")
    receptor, emisor = contexto.Pipe(duplex=False)

    proceso = contexto.Process(
        target=ejecutar_ordenamiento,
        args=(numeros, emisor)
    )

    proceso.start()
    emisor.close()

    proceso.join(timeout=limite_segundos)

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
            raise RuntimeError("El arreglo no quedó ordenado")

        return respuesta["tiempo_ms"], "correcto"

    receptor.close()
    raise RuntimeError(
        f"El proceso terminó sin devolver resultados. "
        f"Código de salida: {proceso.exitcode}"
    )


# ==========================================
# 4. ESTIMACIÓN DE TIEMPOS
# ==========================================

def estimar_tiempo(n, variante, ultima_medicion):
    if ultima_medicion is None:
        return None

    n_anterior = ultima_medicion["n"]
    tiempo_anterior = ultima_medicion["promedio_ms"]

    # Caso ascendente: O(n)
    # Casos aleatorio y descendente: O(n²)
    exponente = 1 if variante == "ascendente" else 2

    estimacion = tiempo_anterior * (
            n / n_anterior
    ) ** exponente

    return {
        "tipo": "estimado",
        "tiempo_estimado_ms": estimacion,
        "metodo_estimacion": f"Extrapolación O(n^{exponente})",
        "referencia_n": n_anterior,
        "referencia_promedio_ms": tiempo_anterior,
        "motivo": "Tiempo previsto superior a cinco minutos"
    }


# ==========================================
# 5. EXPERIMENTO COMPLETO
# ==========================================

def main():

    base = Path(__file__).resolve().parent.parent

    carpeta_datos = base / "datos" / "datos"

    carpeta_resultados = (
            base / "resultados" / "python" / "insertion_sort"
    )

    carpeta_resultados.mkdir(
        parents=True,
        exist_ok=True
    )

    tamanos = [1000, 10000, 100000, 1000000]

    variantes = [
        "aleatorio",
        "ascendente",
        "descendente"
    ]

    repeticiones = 5
    limite_segundos = 300
    limite_ms = limite_segundos * 1000

    ultimas_mediciones = {
        "aleatorio": None,
        "ascendente": None,
        "descendente": None
    }

    # Procesamos primero cada variante para conservar
    # sus referencias de medición anteriores.
    resultados_por_tamano = {
        n: {
            "algoritmo": "Insertion Sort",
            "lenguaje": "Python",
            "tamano": n,
            "repeticiones_solicitadas": repeticiones,
            "limite_segundos": limite_segundos,
            "resultados": {}
        }
        for n in tamanos
    }

    for variante in variantes:

        print(f"\n========== {variante.upper()} ==========")

        for n in tamanos:

            print(f"\nTamaño: {n}")

            estimacion = estimar_tiempo(
                n,
                variante,
                ultimas_mediciones[variante]
            )

            # Evitar ejecuciones que se prevén demasiado largas.
            if (
                    estimacion is not None
                    and estimacion["tiempo_estimado_ms"] > limite_ms
            ):
                resultados_por_tamano[n]["resultados"][variante] = (
                    estimacion
                )

                print(
                    "Tiempo estimado: "
                    f"{estimacion['tiempo_estimado_ms'] / 1000:.2f} s"
                )
                print("Prueba omitida: resultado estimado")
                continue

            ruta = carpeta_datos / f"{variante}_{n}.txt"

            if not ruta.exists():
                raise FileNotFoundError(
                    f"No se encontró el archivo: {ruta}"
                )

            numeros = leer_arreglo(ruta)

            if len(numeros) != n:
                raise ValueError(
                    f"{ruta.name} contiene {len(numeros)} "
                    f"números, pero se esperaban {n}"
                )

            tiempos = []
            agotado = False

            for i in range(repeticiones):

                tiempo_ms, estado = medir_con_limite(
                    numeros,
                    limite_segundos
                )

                if estado == "tiempo_agotado":
                    agotado = True
                    print(
                        f"Ejecución {i + 1}: "
                        "superó los cinco minutos"
                    )
                    break

                tiempos.append(tiempo_ms)

                print(
                    f"Ejecución {i + 1}: "
                    f"{tiempo_ms:.4f} ms"
                )

            if len(tiempos) == repeticiones:

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
                # No inventamos las mediciones faltantes.
                # Conservamos las realizadas y estimamos
                # usando el último tamaño completado.
                estimacion = estimar_tiempo(
                    n,
                    variante,
                    ultimas_mediciones[variante]
                )

                resultado = {
                    "tipo": "estimado",
                    "tiempos_medidos_ms": tiempos,
                    "repeticiones_completadas": len(tiempos),
                    "motivo": (
                        "Una ejecución superó cinco minutos"
                        if agotado
                        else "No se completaron las cinco mediciones"
                    )
                }

                if estimacion is not None:
                    resultado.update({
                        "tiempo_estimado_ms":
                            estimacion["tiempo_estimado_ms"],
                        "metodo_estimacion":
                            estimacion["metodo_estimacion"],
                        "referencia_n":
                            estimacion["referencia_n"],
                        "referencia_promedio_ms":
                            estimacion["referencia_promedio_ms"]
                    })
                else:
                    resultado["tiempo_estimado_ms"] = None
                    resultado["metodo_estimacion"] = (
                        "Sin referencia previa suficiente"
                    )

                resultados_por_tamano[n]["resultados"][variante] = (
                    resultado
                )

                print("Prueba incompleta; resultado registrado")

            # Liberar memoria del arreglo leído.
            del numeros

    # ==========================================
    # 6. GUARDAR LOS CUATRO JSON
    # ==========================================

    for n in tamanos:

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

    print("\nTODAS LAS PRUEBAS FINALIZARON")


# Necesario para multiprocessing en macOS.
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
