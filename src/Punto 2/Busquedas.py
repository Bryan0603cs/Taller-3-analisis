import math


def lineal(arr, objetivo):
    for i in range(len(arr)):
        if arr[i] == objetivo:
            return i
    return -1


def binaria(arr, objetivo):
    inicio = 0
    fin = len(arr) - 1

    while inicio <= fin:
        medio = inicio + (fin - inicio) // 2

        if arr[medio] == objetivo:
            return medio

        if arr[medio] < objetivo:
            inicio = medio + 1
        else:
            fin = medio - 1

    return -1


def ternaria(arr, objetivo):
    inicio = 0
    fin = len(arr) - 1

    while inicio <= fin:
        tercio = (fin - inicio) // 3

        medio1 = inicio + tercio
        medio2 = fin - tercio

        if arr[medio1] == objetivo:
            return medio1

        if arr[medio2] == objetivo:
            return medio2

        if objetivo < arr[medio1]:
            fin = medio1 - 1
        elif objetivo > arr[medio2]:
            inicio = medio2 + 1
        else:
            inicio = medio1 + 1
            fin = medio2 - 1

    return -1


def salto(arr, objetivo):
    n = len(arr)

    if n == 0:
        return -1

    salto = int(math.sqrt(n))
    anterior = 0
    actual = salto

    while anterior < n and arr[min(actual, n) - 1] < objetivo:
        anterior = actual
        actual += salto

        if anterior >= n:
            return -1

    while anterior < min(actual, n):
        if arr[anterior] == objetivo:
            return anterior

        if arr[anterior] > objetivo:
            return -1

        anterior += 1

    return -1


def interpolacion(arr, objetivo):
    inicio = 0
    fin = len(arr) - 1

    while (inicio <= fin and
           objetivo >= arr[inicio] and
           objetivo <= arr[fin]):

        if arr[inicio] == arr[fin]:
            return inicio if arr[inicio] == objetivo else -1

        pos = inicio + (
                (objetivo - arr[inicio]) * (fin - inicio)
                // (arr[fin] - arr[inicio])
        )

        if arr[pos] == objetivo:
            return pos

        if arr[pos] < objetivo:
            inicio = pos + 1
        else:
            fin = pos - 1

    return -1


def exponencial(arr, objetivo):
    n = len(arr)

    if n == 0:
        return -1

    if arr[0] == objetivo:
        return 0

    i = 1

    while i < n and arr[i] <= objetivo:
        i *= 2

    return binaria_rango(
        arr,
        objetivo,
        i // 2,
        min(i, n - 1)
    )


def binaria_rango(arr, objetivo, inicio, fin):
    while inicio <= fin:
        medio = inicio + (fin - inicio) // 2

        if arr[medio] == objetivo:
            return medio

        if arr[medio] < objetivo:
            inicio = medio + 1
        else:
            fin = medio - 1

    return -1